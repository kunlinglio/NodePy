import pytest

from server.models.exception import NodeExecutionError, NodeValidationError, NodeParameterError
from server.models.types import ColType

from tests.nodes.utils import table_from_dict, make_data, schema_from_coltypes, make_schema


# ---------------------- CustomScriptNode tests ----------------------
def test_custom_script_success(node_ctor):
    node = node_ctor(
        "CustomScriptNode",
        id="c1",
        input_ports={"x": "int"},
        output_ports={"y": "int"},
        script="def script(x):\n    return {'y': x + 1}"
    )

    out = node.process({"x": make_data(41)})
    assert "y" in out
    assert out["y"].payload == 42


def test_custom_script_missing_function_raises(node_ctor):
    node = node_ctor(
        "CustomScriptNode",
        id="c2",
        input_ports={"x": "int"},
        output_ports={"y": "int"},
        script="a = 1"
    )

    with pytest.raises(NodeExecutionError):
        node.process({"x": make_data(1)})


def test_custom_script_non_dict_return_raises(node_ctor):
    node = node_ctor(
        "CustomScriptNode",
        id="c3",
        input_ports={"x": "int"},
        output_ports={"y": "int"},
        script="def script(x):\n    return 5"
    )

    with pytest.raises(NodeExecutionError):
        node.process({"x": make_data(1)})


def test_custom_script_missing_output_key_raises(node_ctor):
    node = node_ctor(
        "CustomScriptNode",
        id="c4",
        input_ports={"x": "int"},
        output_ports={"y": "int"},
        script="def script(x):\n    return {}"
    )

    with pytest.raises(NodeExecutionError):
        node.process({"x": make_data(1)})


def test_custom_script_hint_contains_template(node_ctor):
    node = node_ctor(
        "CustomScriptNode",
        id="c5",
        input_ports={"x": "int"},
        output_ports={"y": "int"},
        script="def script(x):\n    return {'y': x}"
    )

    hint = node.hint({}, {})
    assert "script_template" in hint
    assert isinstance(hint["script_template"], str)


# ---------------------- GetCellNode / SetCellNode tests ----------------------
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


def test_getcell_infer_errors(node_ctor):
    # missing column in schema should raise validation error
    node = node_ctor("GetCellNode", id="g4", col="missing", row=0)
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": schema_from_coltypes({"a": ColType.INT})})

    # missing row param and no 'row' input should raise
    node2 = node_ctor("GetCellNode", id="g5", col="a", row=None)
    with pytest.raises(NodeValidationError):
        node2.infer_schema({"table": schema_from_coltypes({"a": ColType.INT})})


def test_setcell_infer_and_process(node_ctor):
    # infer type mismatch between value and column
    node = node_ctor("SetCellNode", id="s1", col="a", row=None)
    with pytest.raises(NodeValidationError):
        node.infer_schema({
            "table": schema_from_coltypes({"a": ColType.INT}),
            "value": make_schema("float"),
        })

    # process normal update
    tbl = table_from_dict({"a": [1, 2, 3]})
    node2 = node_ctor("SetCellNode", id="s2", col="a", row=1)
    # set column types so process can construct output Table
    node2._col_types = tbl.payload.col_types
    out = node2.process({"table": tbl, "value": make_data(99)})
    assert "table" in out
    out_tbl = out["table"].payload
    assert list(out_tbl.df["a"]) == [1, 99, 3]

    # out of bounds
    node3 = node_ctor("SetCellNode", id="s3", col="a", row=10)
    with pytest.raises(NodeExecutionError):
        node3.process({"table": tbl, "value": make_data(5)})


# ---------------------- Unpack / Pack node tests ----------------------
def test_unpack_validate_and_infer_errors(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("UnpackNode", id="u1", cols=[])

    node = node_ctor("UnpackNode", id="u2", cols=["x", "y"])
    # infer with missing column should raise
    with pytest.raises(NodeValidationError):
        node.infer_output_schemas({"row": schema_from_coltypes({"x": ColType.INT})})


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