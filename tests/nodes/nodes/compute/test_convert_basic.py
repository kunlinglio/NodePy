import pytest

from server.models.exception import NodeExecutionError
from server.models.types import ColType

from tests.nodes.utils import make_data, table_from_dict, schema_from_coltypes


# ---------------------- Primitive convert nodes ----------------------
def test_to_string_node(node_ctor):
    node = node_ctor("ToStringNode", id="ts1")
    out = node.process({"input": make_data(123)})
    assert out["output"].payload == "123"

    out2 = node.process({"input": make_data(3.14)})
    assert out2["output"].payload == "3.14"

    out3 = node.process({"input": make_data(True)})
    assert out3["output"].payload == "True"


def test_to_int_node_methods_and_errors(node_ctor):
    # FLOOR
    n_floor = node_ctor("ToIntNode", id="ti_floor", method="FLOOR")
    out = n_floor.process({"input": make_data(3.7)})
    assert out["output"].payload == 3

    # CEIL
    n_ceil = node_ctor("ToIntNode", id="ti_ceil", method="CEIL")
    out2 = n_ceil.process({"input": make_data(3.1)})
    assert out2["output"].payload == 4

    # ROUND
    n_round = node_ctor("ToIntNode", id="ti_round", method="ROUND")
    out3 = n_round.process({"input": make_data(2.3)})
    assert out3["output"].payload == 2

    # string numeric
    out4 = n_floor.process({"input": make_data("5")})
    assert out4["output"].payload == 5

    # string float
    out5 = n_floor.process({"input": make_data("6.9")})
    assert out5["output"].payload == 6

    # invalid string => NodeExecutionError
    with pytest.raises(NodeExecutionError):
        n_floor.process({"input": make_data("not_a_number")})


def test_to_float_node_and_errors(node_ctor):
    node = node_ctor("ToFloatNode", id="tf1")
    out = node.process({"input": make_data(3)})
    assert out["output"].payload == float(3)

    out2 = node.process({"input": make_data("2.5")})
    assert out2["output"].payload == 2.5

    with pytest.raises(NodeExecutionError):
        node.process({"input": make_data("nan_value")})


def test_to_bool_node_valid_and_invalid(node_ctor):
    node = node_ctor("ToBoolNode", id="tb1")
    # ints/floats
    assert node.process({"input": make_data(0)})["output"].payload is False
    assert node.process({"input": make_data(1)})["output"].payload is True
    assert node.process({"input": make_data(0.0)})["output"].payload is False
    assert node.process({"input": make_data(2.3)})["output"].payload is True

    # strings yes/no/true/false
    assert node.process({"input": make_data("true")})["output"].payload is True
    assert node.process({"input": make_data("False")})["output"].payload is False
    assert node.process({"input": make_data("yes")})["output"].payload is True
    assert node.process({"input": make_data("0")})["output"].payload is False

    # invalid string
    with pytest.raises(NodeExecutionError):
        node.process({"input": make_data("maybe")})


# ---------------------- Column convert nodes ----------------------
def test_col_to_string_node(node_ctor):
    tbl = table_from_dict({"a": [1, 2, 3]})
    node = node_ctor("ColToStringNode", id="cts1", col="a", result_col="a_str")
    schema = schema_from_coltypes({"a": ColType.INT})
    out_schema = node.infer_schema({"table": schema})
    assert "table" in out_schema
    # process
    node._col_types = out_schema["table"].tab.col_types
    out = node.process({"table": tbl})
    out_tbl = out["table"].payload
    assert list(out_tbl.df["a_str"]) == ["1", "2", "3"]


def test_col_to_int_node_success_and_error(node_ctor):
    tbl_good = table_from_dict({"x": [1.0, 2.9, 1.0, 4.0]})
    node = node_ctor("ColToIntNode", id="cti1", col="x", result_col="x_int", method="FLOOR")
    schema = schema_from_coltypes({"x": ColType.FLOAT})
    out_schema = node.infer_schema({"table": schema})
    node._col_types = out_schema["table"].tab.col_types
    out = node.process({"table": tbl_good})
    out_tbl = out["table"].payload
    # floor: 1.0->1, 2.9->2, True->1, "4"->4
    assert list(out_tbl.df["x_int"]) == [1, 2, 1, 4]

    # invalid string in column should raise NodeExecutionError
    tbl_bad = table_from_dict({"x": [1.0, "bad", 3.0]})
    node2 = node_ctor("ColToIntNode", id="cti2", col="x", result_col="x_int2", method="ROUND")
    schema2 = schema_from_coltypes({"x": ColType.STR})
    node2.infer_schema({"table": schema2})
    # ensure _col_types set for process
    node2._col_types = node2._col_types or schema2.tab.col_types
    with pytest.raises(NodeExecutionError):
        node2.process({"table": tbl_bad})


def test_col_to_float_node_success_and_error(node_ctor):
    tbl = table_from_dict({"y": [1, "2.5", 3]})
    node = node_ctor("ColToFloatNode", id="ctf1", col="y", result_col="y_f")
    schema = schema_from_coltypes({"y": ColType.STR})
    out_schema = node.infer_schema({"table": schema})
    node._col_types = out_schema["table"].tab.col_types
    out = node.process({"table": tbl})
    out_tbl = out["table"].payload
    assert list(out_tbl.df["y_f"]) == [1.0, 2.5, 3.0]

    tbl_bad = table_from_dict({"y": ["nope"]})
    node2 = node_ctor("ColToFloatNode", id="ctf_bad", col="y", result_col="y_f2")
    node2.infer_schema({"table": schema})
    node2._col_types = node2._col_types or schema.tab.col_types
    with pytest.raises(NodeExecutionError):
        node2.process({"table": tbl_bad})


def test_col_to_bool_node_success_and_error(node_ctor):
    tbl = table_from_dict({"b": [0, 1, "yes", "no", "True"]})
    node = node_ctor("ColToBoolNode", id="ctb1", col="b", result_col="b_bool")
    schema = schema_from_coltypes({"b": ColType.STR})
    out_schema = node.infer_schema({"table": schema})
    node._col_types = out_schema["table"].tab.col_types
    out = node.process({"table": tbl})
    out_tbl = out["table"].payload
    assert list(out_tbl.df["b_bool"]) == [False, True, True, False, True]

    tbl_bad = table_from_dict({"b": ["maybe"]})
    node2 = node_ctor("ColToBoolNode", id="ctb_bad", col="b", result_col="b_bool2")
    node2.infer_schema({"table": schema})
    node2._col_types = node2._col_types or schema.tab.col_types
    with pytest.raises(NodeExecutionError):
        node2.process({"table": tbl_bad})