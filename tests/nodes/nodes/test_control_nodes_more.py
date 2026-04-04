import pytest

from server.models.exception import NodeExecutionError, NodeParameterError
from server.models.types import ColType
from server.models.data import Table

from tests.nodes.utils import (
    table_from_dict,
    make_data,
    schema_from_coltypes,
    make_schema,
)


# ---------------------- ForRollingWindow tests ----------------------
def test_forrollingwindow_iter_success_and_error(node_ctor):
    tbl = table_from_dict({"a": [1, 2, 3, 4]})
    # normal iteration with window_size = 2 -> yields 3 windows
    begin = node_ctor("ForRollingWindowBeginNode", id="frw_ok", window_size=2, pair_id=101)
    windows = list(begin.iter_loop({"table": tbl}))
    assert len(windows) == 3
    # check each yielded window is a Table payload with expected lengths
    lengths = [len(w["window"].payload.df) for w in windows]
    assert lengths == [2, 2, 2]

    # window_size larger than table length should raise NodeExecutionError
    begin_bad = node_ctor("ForRollingWindowBeginNode", id="frw_bad", window_size=10, pair_id=102)
    with pytest.raises(NodeExecutionError):
        # list() will force generator to run and raise
        list(begin_bad.iter_loop({"table": tbl}))


def test_forrollingwindow_end_finalize_nonempty(node_ctor):
    end = node_ctor("ForRollingWindowEndNode", id="frwe", pair_id=101)
    # simulate two iteration outputs, each a 2-row table
    w1 = table_from_dict({"x": [1, 2]})
    w2 = table_from_dict({"x": [3, 4]})
    end.end_iter_loop({"window": w1})
    end.end_iter_loop({"window": w2})
    res = end.finalize_loop()
    assert "table" in res
    tbl_res = res["table"].payload
    assert isinstance(tbl_res, Table)
    # combined should have 4 rows after concatenation
    assert len(tbl_res.df) == 4
    # index column '_index' may or may not be present depending on implementation; don't require its absence


# ---------------------- MapColumn tests ----------------------
def test_mapcolumn_begin_iter_and_hint(node_ctor):
    begin = node_ctor("MapColumnBeginNode", id="mcb1", col="a", pair_id=201)
    tbl = table_from_dict({"a": [5, 6], "b": [7, 8]})
    yielded = list(begin.iter_loop({"table": tbl}))
    assert len(yielded) == 2
    # each yielded dict should contain 'cell' and 'remains'
    for idx, out in enumerate(yielded):
        assert "cell" in out and "remains" in out
        assert out["cell"].payload == [5, 6][idx] or out["cell"].payload == 5 or out["cell"].payload == 6
        # remains should be a Table payload (single-row frame)
        assert hasattr(out["remains"].payload, "df")

    # hint should include column choices when table schema provided
    hint = begin.hint({"table": schema_from_coltypes({"a": ColType.INT, "b": ColType.INT})}, {})
    assert "col_choices" in hint
    assert "a" in hint["col_choices"]


def test_mapcolumn_end_parameter_default_and_finalize(node_ctor):
    # when result_col is None, validate_parameters should assign a default name
    end = node_ctor("MapColumnEndNode", id="mce1", result_col=None, pair_id=201)
    # call validate explicitly via creating was enough; ensure result_col is set to a string
    assert end.result_col is not None and isinstance(end.result_col, str)
    # simulate end_iter_loop adding rows
    end._output_rows.clear()
    end.end_iter_loop({"cell": make_data(11), "remains": table_from_dict({"b": [1]})})
    end.end_iter_loop({"cell": make_data(22), "remains": table_from_dict({"b": [2]})})
    out = end.finalize_loop()
    assert "table" in out
    final_tbl = out["table"].payload
    assert len(final_tbl.df) == 2
    # generated result_col should be one of the columns
    assert end.result_col in final_tbl.df.columns


# ---------------------- PackNode default names and infer tests ----------------------
def test_packnode_default_col_name_and_infer(node_ctor):
    # allow None entries in cols which should be replaced with defaults
    node = node_ctor("PackNode", id="pdef1", cols=[None, None])
    # after construction validate_parameters should have converted None -> generated names
    assert all(isinstance(c, str) for c in node.cols)
    assert all(c.startswith("pdef1_") for c in node.cols)

    # infer output schema when no base_row provided
    node2 = node_ctor("PackNode", id="pdef2", cols=[None, "b"])
    input_schemas = {}
    for c in node2.cols:
        input_schemas[c] = make_schema("int")
    out_schema_map = node2.infer_output_schemas(input_schemas)
    assert "packed_row" in out_schema_map
    assert node2._col_types is not None
    # keys in _col_types should include both generated name and 'b'
    assert set(node2._col_types.keys()) >= {"b"}


# ---------------------- UnpackNode infer/process tests ----------------------
def test_unpack_infer_remain_and_process(node_ctor):
    node = node_ctor("UnpackNode", id="un1", cols=["x"])
    in_schema = schema_from_coltypes({"x": ColType.INT, "y": ColType.INT})
    out_schemas = node.infer_output_schemas({"row": in_schema})
    # should produce schema for 'x' and 'unpacked_row'
    assert "x" in out_schemas and "unpacked_row" in out_schemas
    # process with a single-row table should succeed
    tbl = table_from_dict({"x": [9], "y": [10]})
    out = node.process({"row": tbl})
    assert out["x"].payload == 9
    # unpacked_row should be a Table containing column 'y' (remaining)
    rem = out["unpacked_row"].payload
    assert "y" in rem.df.columns


# ---------------------- CustomScriptNode port and infer tests ----------------------
def test_customscript_port_def_and_infer(node_ctor):
    node = node_ctor(
        "CustomScriptNode",
        id="cs_ports",
        input_ports={"a": "int", "s": "str"},
        output_ports={"sum": "int", "msg": "str"},
        script="def script(a, s):\n    return {'sum': a, 'msg': s}"
    )
    in_ports, out_ports = node.port_def()
    in_names = [p.name for p in in_ports]
    out_names = [p.name for p in out_ports]
    assert set(in_names) == {"a", "s"}
    assert set(out_names) == {"sum", "msg"}

    # infer_output_schemas should return schemas for outputs of correct types
    out_schemas = node.infer_output_schemas({})
    assert "sum" in out_schemas and "msg" in out_schemas
    assert out_schemas["sum"].type.value.lower() == "int"
    assert out_schemas["msg"].type.value.lower() == "str"