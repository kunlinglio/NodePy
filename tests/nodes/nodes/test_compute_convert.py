import pytest

from server.models.exception import NodeExecutionError, NodeParameterError
from server.models.types import ColType
from server.models.schema import Schema, TableSchema

from tests.nodes.utils import table_from_dict, schema_from_coltypes, make_data


def test_to_string_node_simple(node_ctor):
    n = node_ctor("ToStringNode", id="ts1")
    out = n.process({"input": make_data(123)})
    assert out["output"].payload == "123"

    out2 = n.process({"input": make_data(True)})
    assert out2["output"].payload == "True"

    out3 = n.process({"input": make_data(3.14)})
    assert out3["output"].payload == "3.14"


def test_to_int_node_bool_float_round_and_str(node_ctor):
    # bool -> int
    n_bool = node_ctor("ToIntNode", id="ti_bool", method="FLOOR")
    out = n_bool.process({"input": make_data(True)})
    assert out["output"].payload == 1

    # float rounding behavior
    n_floor = node_ctor("ToIntNode", id="ti_floor", method="FLOOR")
    assert n_floor.process({"input": make_data(3.9)})["output"].payload == 3

    n_ceil = node_ctor("ToIntNode", id="ti_ceil", method="CEIL")
    assert n_ceil.process({"input": make_data(3.1)})["output"].payload == 4

    n_round = node_ctor("ToIntNode", id="ti_round", method="ROUND")
    assert n_round.process({"input": make_data(2.5)})["output"].payload == round(2.5)

    # string integer
    n_str = node_ctor("ToIntNode", id="ti_str", method="FLOOR")
    assert n_str.process({"input": make_data("42")})["output"].payload == 42
    # string float -> round according to method
    assert n_floor.process({"input": make_data("4.9")})["output"].payload == 4

    # invalid string conversion should raise NodeExecutionError
    with pytest.raises(NodeExecutionError):
        n_str.process({"input": make_data("not_a_number")})


def test_to_float_node_success_and_error(node_ctor):
    n = node_ctor("ToFloatNode", id="tf1")
    assert n.process({"input": make_data(True)})["output"].payload == 1.0
    assert n.process({"input": make_data(2)})["output"].payload == 2.0
    assert n.process({"input": make_data("3.5")})["output"].payload == 3.5

    with pytest.raises(NodeExecutionError):
        n.process({"input": make_data("bad_float")})


def test_to_bool_node_various_inputs(node_ctor):
    n = node_ctor("ToBoolNode", id="tb1")
    assert n.process({"input": make_data(0)})["output"].payload is False
    assert n.process({"input": make_data(2)})["output"].payload is True
    assert n.process({"input": make_data(0.0)})["output"].payload is False
    assert n.process({"input": make_data(1.2)})["output"].payload is True

    # strings true-like
    assert n.process({"input": make_data("true")})["output"].payload is True
    assert n.process({"input": make_data("YES")})["output"].payload is True
    assert n.process({"input": make_data("0")})["output"].payload is False
    assert n.process({"input": make_data("no")})["output"].payload is False

    with pytest.raises(NodeExecutionError):
        n.process({"input": make_data("maybe")})


def test_col_to_string_node_infer_process_and_hint(node_ctor):
    tbl = table_from_dict({"a": [1, 2]})
    node = node_ctor("ColToStringNode", id="cts1", col="a")
    # infer_output_schemas should append the result column schema
    out_schema = node.infer_output_schemas({"table": tbl.extract_schema()})
    assert "table" in out_schema
    # hint should include column choices
    hint = node.hint({"table": tbl.extract_schema()}, {})
    assert "col_choices" in hint

    # process conversion
    node._col_types = out_schema["table"].tab.col_types.copy()
    out = node.process({"table": tbl})
    res_tbl = out["table"].payload
    assert all(isinstance(x, str) for x in res_tbl.df[node.result_col])


def test_col_to_int_node_conversion_and_errors(node_ctor):
    tbl = table_from_dict({"a": [True, 3.7, "5", "bad"]})
    # test with ROUND method
    node = node_ctor("ColToIntNode", id="cti1", col="a", method="ROUND")
    # infer to set _col_types and default result_col
    out_schema = node.infer_output_schemas({"table": tbl.extract_schema()})
    node._col_types = out_schema["table"].tab.col_types.copy()

    # process should raise when encountering an unparsable string "bad"
    with pytest.raises(NodeExecutionError):
        node.process({"table": tbl})

    # create a good table with convertible values
    good_tbl = table_from_dict({"a": [True, 2.3, "7"]})
    node2 = node_ctor("ColToIntNode", id="cti2", col="a", method="FLOOR")
    out_schema2 = node2.infer_output_schemas({"table": good_tbl.extract_schema()})
    node2._col_types = out_schema2["table"].tab.col_types.copy()
    out = node2.process({"table": good_tbl})
    res_tbl = out["table"].payload
    assert list(res_tbl.df[node2.result_col]) == [1, 2, 7]


def test_col_to_float_node_conversion_and_error(node_ctor):
    tbl = table_from_dict({"a": [True, 2, "3.14", "x"]})
    node = node_ctor("ColToFloatNode", id="ctf1", col="a")
    out_schema = node.infer_output_schemas({"table": tbl.extract_schema()})
    node._col_types = out_schema["table"].tab.col_types.copy()

    with pytest.raises(NodeExecutionError):
        node.process({"table": tbl})

    good = table_from_dict({"a": [False, 1, "2.5"]})
    node2 = node_ctor("ColToFloatNode", id="ctf2", col="a")
    out_schema2 = node2.infer_output_schemas({"table": good.extract_schema()})
    node2._col_types = out_schema2["table"].tab.col_types.copy()
    out = node2.process({"table": good})
    res_tbl = out["table"].payload
    assert all(isinstance(v, float) for v in res_tbl.df[node2.result_col])


def test_col_to_bool_node_conversion_and_error(node_ctor):
    tbl = table_from_dict({"a": [0, 1, "true", "no", "unknown"]})
    node = node_ctor("ColToBoolNode", id="ctb1", col="a")
    out_schema = node.infer_output_schemas({"table": tbl.extract_schema()})
    node._col_types = out_schema["table"].tab.col_types.copy()

    with pytest.raises(NodeExecutionError):
        node.process({"table": tbl})

    good = table_from_dict({"a": [0, 1, "yes", "false"]})
    node2 = node_ctor("ColToBoolNode", id="ctb2", col="a")
    out_schema2 = node2.infer_output_schemas({"table": good.extract_schema()})
    node2._col_types = out_schema2["table"].tab.col_types.copy()
    out = node2.process({"table": good})
    res_tbl = out["table"].payload
    # values should be booleans or convertible
    assert list(res_tbl.df[node2.result_col]) == [False, True, True, False]


def test_col_node_parameter_validation(node_ctor):
    # empty column name should raise at construction/validation time
    with pytest.raises(NodeParameterError):
        node_ctor("ColToStringNode", id="bad1", col="   ")

    with pytest.raises(NodeParameterError):
        node_ctor("ColToIntNode", id="bad2", col="", method="FLOOR")

    with pytest.raises(NodeParameterError):
        node_ctor("ColToFloatNode", id="bad3", col="")

    with pytest.raises(NodeParameterError):
        node_ctor("ColToBoolNode", id="bad4", col="")
