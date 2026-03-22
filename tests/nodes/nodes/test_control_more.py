import pytest

from server.models.exception import NodeExecutionError, NodeParameterError, NodeValidationError
from server.models.types import ColType

from tests.nodes.utils import table_from_dict, make_data, schema_from_coltypes


def test_pack_with_base_row_appends_columns(node_ctor):
    base = table_from_dict({"existing": [5]})
    node = node_ctor("PackNode", id="p_base", cols=["a", "b"])
    # prepare input_schemas: base_row present and primitive inputs
    out_schema = node.infer_schema(
        {
            "base_row": base.extract_schema(),
            "a": make_data(1).extract_schema(),
            "b": make_data(2).extract_schema(),
        }
    )
    assert "packed_row" in out_schema

    # set _col_types as infer would
    node._col_types = out_schema["packed_row"].tab.col_types

    out = node.process({"base_row": base, "a": make_data(1), "b": make_data(2)})
    packed = out["packed_row"].payload
    # ensure existing column preserved and new columns appended
    assert list(packed.df["existing"]) == [5]
    assert list(packed.df["a"]) == [1]
    assert list(packed.df["b"]) == [2]


def test_unpack_infer_removes_unpacked_columns(node_ctor):
    node = node_ctor("UnpackNode", id="u_infer", cols=["x", "y"])
    schema = schema_from_coltypes({"x": ColType.INT, "y": ColType.INT, "z": ColType.INT})
    out = node.infer_output_schemas({"row": schema})
    # unpacked_row should be present and should not include x,y
    assert "unpacked_row" in out
    rem = out["unpacked_row"].tab.col_types
    assert "x" not in rem and "y" not in rem and "z" in rem


def test_cell_validate_and_hint(node_ctor):
    # invalid col name should raise
    with pytest.raises(NodeParameterError):
        node_ctor("GetCellNode", id="bad_get", col="   ")
    with pytest.raises(NodeParameterError):
        node_ctor("SetCellNode", id="bad_set", col="")

    # hint should include column choices when table schema provided
    node = node_ctor("GetCellNode", id="g_hint", col="a", row=0)
    hint = node.hint({"table": schema_from_coltypes({"a": ColType.INT, "b": ColType.INT})}, {})
    assert "col_choices" in hint and "a" in hint["col_choices"]

    node2 = node_ctor("SetCellNode", id="s_hint", col="a", row=0)
    hint2 = node2.hint({"table": schema_from_coltypes({"a": ColType.INT})}, {})
    assert "col_choices" in hint2


# Additional tests to cover more control-node behavior

def test_getcell_basic_and_row_input(node_ctor):
    tbl = table_from_dict({"a": [10, 20, 30]})
    node = node_ctor("GetCellNode", id="g1", col="a", row=1)
    # tests call process directly; ensure inferred type is set to avoid internal assertion
    node._infered_value_type = ColType.INT

    out = node.process({"table": tbl})
    assert out["value"].payload == 20

    # override row via input
    out2 = node.process({"table": tbl, "row": make_data(2)})
    assert out2["value"].payload == 30


def test_getcell_negative_index_and_out_of_bounds(node_ctor):
    tbl = table_from_dict({"a": [1, 2, 3]})
    node = node_ctor("GetCellNode", id="g2", col="a", row=-1)
    # ensure inferred type is present for process assertions
    node._infered_value_type = ColType.INT

    out = node.process({"table": tbl})
    assert out["value"].payload == 3

    node_bad = node_ctor("GetCellNode", id="g3", col="a", row=10)
    with pytest.raises(NodeExecutionError):
        node_bad.process({"table": tbl})


def test_setcell_infer_and_process(node_ctor):
    # infer type mismatch between value and column
    node = node_ctor("SetCellNode", id="s1", col="a", row=None)
    with pytest.raises(NodeValidationError):
        node.infer_schema({
            "table": schema_from_coltypes({"a": ColType.INT}),
            "value": make_data(1.23).extract_schema(),  # float vs int to trigger mismatch
        })

    # process normal update
    tbl = table_from_dict({"a": [1, 2, 3]})
    node2 = node_ctor("SetCellNode", id="s2", col="a", row=1)
    # set column types so process can construct output Table
    node2._col_types = tbl.extract_schema().tab.col_types
    out = node2.process({"table": tbl, "value": make_data(99)})
    assert "table" in out
    out_tbl = out["table"].payload
    assert list(out_tbl.df["a"]) == [1, 99, 3]

    # out of bounds
    node3 = node_ctor("SetCellNode", id="s3", col="a", row=10)
    with pytest.raises(NodeExecutionError):
        node3.process({"table": tbl, "value": make_data(5)})


def test_unpack_process_errors_and_success(node_ctor):
    node = node_ctor("UnpackNode", id="u3", cols=["x", "y"])
    # row must have exactly one row
    tbl2 = table_from_dict({"x": [1, 2], "y": [3, 4]})
    with pytest.raises(NodeExecutionError):
        node.process({"row": tbl2})

    # missing column in single-row input
    tbl_single = table_from_dict({"x": [10]})
    with pytest.raises(NodeExecutionError):
        node.process({"row": tbl_single})

    # success case
    tbl_ok = table_from_dict({"x": [7], "y": [8], "z": [9]})
    node.infer_output_schemas({"row": schema_from_coltypes({"x": ColType.INT, "y": ColType.INT, "z": ColType.INT})})
    out = node.process({"row": tbl_ok})
    assert out["x"].payload == 7
    assert out["y"].payload == 8
    assert "unpacked_row" in out


def test_pack_validate_and_process(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("PackNode", id="p1", cols=[])

    node = node_ctor("PackNode", id="p2", cols=["a", "b"])
    # missing inputs for required columns should raise
    with pytest.raises(NodeExecutionError):
        node.process({})

    # success
    node2 = node_ctor("PackNode", id="p3", cols=["a", "b"])
    node2._col_types = {"a": ColType.INT, "b": ColType.INT}
    out = node2.process({"a": make_data(1), "b": make_data(2)})
    assert "packed_row" in out
    packed = out["packed_row"].payload
    assert list(packed.df["a"]) == [1]
    assert list(packed.df["b"]) == [2]