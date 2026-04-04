import pytest
import pandas as pd

from server.models.exception import NodeExecutionError, NodeValidationError, NodeParameterError
from server.models.types import ColType
from server.models.data import Data, Table
from server.interpreter.nodes.control import custom as custom_mod

from tests.nodes.utils import (
    table_from_dict,
    make_data,
    schema_from_coltypes,
    make_schema,
)


# ---------------------- CustomScriptNode extra tests ----------------------
def test_custom_script_raises_internal_exception(node_ctor):
    # script defines script but raises internally -> NodeExecutionError
    node = node_ctor(
        "CustomScriptNode",
        id="cs_err",
        input_ports={"x": "int"},
        output_ports={"y": "int"},
        script="def script(x):\n    raise ValueError('boom')"
    )

    with pytest.raises(NodeExecutionError):
        node.process({"x": make_data(1)})


def test_custom_script_hint_template_cache(monkeypatch):
    # Force the template cache to None to exercise both file-read and cached branches.
    # Ensure we can call hint twice.
    custom_mod._TEMPLATE_CACHE = None
    # first call - should read file and set cache
    hint1 = custom_mod.CustomScriptNode.hint({}, {})
    assert "script_template" in hint1 and isinstance(hint1["script_template"], str)
    # second call - should use cached value
    hint2 = custom_mod.CustomScriptNode.hint({}, {})
    assert "script_template" in hint2 and isinstance(hint2["script_template"], str)
    # values should be equal (cached)
    assert hint1["script_template"] == hint2["script_template"]


# ---------------------- GetCellNode / SetCellNode parameter validation ----------------------
def test_getcell_validate_empty_col_raises(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("GetCellNode", id="g_empty", col="  ")


def test_setcell_validate_empty_col_raises(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("SetCellNode", id="s_empty", col="")


def test_getcell_process_column_missing_raises(node_ctor):
    tbl = table_from_dict({"a": [1, 2]})
    # create a node that asks for column 'b' which doesn't exist in the table
    node = node_ctor("GetCellNode", id="g_missing_col", col="b", row=0)
    # set inferred type so process assertions pass
    node._infered_value_type = ColType.INT
    with pytest.raises(NodeExecutionError):
        node.process({"table": tbl})


def test_setcell_process_column_missing_raises(node_ctor):
    tbl = table_from_dict({"a": [1, 2]})
    node = node_ctor("SetCellNode", id="s_missing_col", col="b", row=0)
    # set col types so process can run to the point of checking column existence
    node._col_types = tbl.payload.col_types
    with pytest.raises(NodeExecutionError):
        node.process({"table": tbl, "value": make_data(5)})


# ---------------------- ForEachRow loop begin / end tests ----------------------
def test_foreachrow_iter_and_finalize(node_ctor):
    tbl = table_from_dict({"x": [10, 20, 30]})
    begin = node_ctor("ForEachRowBeginNode", id="fr_begin", pair_id=1)
    # iterate and collect yielded rows
    yielded = list(begin.iter_loop({"table": tbl}))
    assert len(yielded) == 3
    for idx, row_out in enumerate(yielded):
        assert "row" in row_out
        assert isinstance(row_out["row"].payload, Table)
        # each yielded row has one-row dataframe
        assert len(row_out["row"].payload.df) == 1
        assert int(row_out["row"].payload.df.iloc[0]["x"]) == [10, 20, 30][idx]

    # End node finalize with no rows should return empty table
    end = node_ctor("ForEachRowEndNode", id="fr_end", pair_id=1)
    empty_result = end.finalize_loop()
    assert "table" in empty_result
    assert isinstance(empty_result["table"].payload, Table)
    assert empty_result["table"].payload.df.empty

    # Simulate multiple iteration outputs and finalize
    for i in range(3):
        row_data = table_from_dict({"x": [i]})
        end.end_iter_loop({"row": row_data})
    combined = end.finalize_loop()
    assert "table" in combined
    df = combined["table"].payload.df
    assert list(df["x"]) == [0, 1, 2]


# ---------------------- MapColumn begin / end tests ----------------------
def test_mapcolumn_infer_and_end_iter_finalize(node_ctor):
    # begin.infer_output_schemas should expose 'cell' and 'remains'
    begin = node_ctor("MapColumnBeginNode", id="mc_begin", col="a", pair_id=2)
    schema = begin.infer_output_schemas({
        "table": schema_from_coltypes({"a": ColType.INT, "b": ColType.INT})
    })
    assert "cell" in schema and "remains" in schema
    assert schema["cell"].type == schema["cell"].Type.INT or schema["cell"].to_coltype() == ColType.INT

    # end: test when result_col already exists -> NodeParameterError in infer_output_schemas
    end_conflict = node_ctor("MapColumnEndNode", id="mc_end_conflict", result_col="a", pair_id=2)
    with pytest.raises(NodeParameterError):
        end_conflict.infer_output_schemas({
            "cell": make_schema("int"),
            "remains": schema_from_coltypes({"a": ColType.INT, "b": ColType.INT})
        })

    # end: normal end_iter_loop and finalize_loop flow
    end = node_ctor("MapColumnEndNode", id="mc_end_ok", result_col=None, pair_id=2)
    # prepare remains row (a single-row table) and cell values, call end_iter_loop multiple times
    for val in [100, 200]:
        remains = table_from_dict({"b": [1]})
        # cell is a primitive Data
        cell = make_data(val)
        end.end_iter_loop({"cell": cell, "remains": remains})

    finalized = end.finalize_loop()
    assert "table" in finalized
    final_table = finalized["table"].payload
    # result_col is generated by default; find it and check values
    cols = list(final_table.df.columns)
    # result_col should be first column per implementation
    result_col = cols[0]
    assert list(final_table.df[result_col]) == [100, 200]
    # original remains column present
    assert "b" in cols


# ---------------------- Unpack / Pack additional tests ----------------------
def test_unpack_hint_and_process_errors(node_ctor):
    # hint should provide outputs list and cols_choices when current_params present
    node = node_ctor("UnpackNode", id="u_hint", cols=["x", "y"])
    hint = node.hint({"row": schema_from_coltypes({"x": ColType.INT, "y": ColType.INT, "z": ColType.INT})}, {"cols": ["x", "y"]})
    assert "outputs" in hint and "cols_choices" in hint
    assert "unpacked_row" in hint["outputs"]

    # process: multi-row input should raise
    node2 = node_ctor("UnpackNode", id="u_proc", cols=["x", "y"])
    tbl_multi = table_from_dict({"x": [1, 2], "y": [3, 4]})
    with pytest.raises(NodeExecutionError):
        node2.process({"row": tbl_multi})


def test_packnode_invalid_and_infer_and_process(node_ctor):
    # illegal column name (starts with underscore) should raise
    with pytest.raises(NodeParameterError):
        node_ctor("PackNode", id="p_bad", cols=["_illegal"])

    # infer with base_row path
    node = node_ctor("PackNode", id="p_infer", cols=["a", "b"])
    base_schema = schema_from_coltypes({"c": ColType.INT})
    input_schemas = {
        "base_row": base_schema,
        "a": make_schema("int"),
        "b": make_schema("int"),
    }
    out_schema = node.infer_output_schemas(input_schemas)
    assert "packed_row" in out_schema
    # ensure _col_types set
    assert node._col_types is not None
    # now do process: provide base_row (single-row) and a,b inputs
    base_row = table_from_dict({"c": [7]})
    res = node.process({"base_row": base_row, "a": make_data(1), "b": make_data(2)})
    assert "packed_row" in res
    packed = res["packed_row"].payload
    # verify columns include original base 'c' and new 'a','b'
    assert set(packed.df.columns) >= {"a", "b", "c"}
    # verify values
    assert int(packed.df.iloc[0]["a"]) == 1
    assert int(packed.df.iloc[0]["b"]) == 2
    assert int(packed.df.iloc[0]["c"]) == 7