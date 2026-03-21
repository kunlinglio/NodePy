import pytest

from server.models.exception import NodeExecutionError, NodeValidationError, NodeParameterError
from server.models.types import ColType

from tests.nodes.utils import table_from_dict, schema_from_coltypes, make_data


def test_col_compare_basic_numeric_and_hint(node_ctor):
    tbl = table_from_dict({"a": [1, 2, 3], "b": [1, 0, 3]})
    node = node_ctor("ColCompareNode", id="cc_eq", op="EQ", col1="a", col2="b", result_col="eq")
    # infer schema should succeed
    out_schema = node.infer_schema({"table": tbl.extract_schema()})
    assert "table" in out_schema

    # execute and verify equality results
    out = node.execute({"table": tbl})
    res_tbl = out["table"].payload
    assert list(res_tbl.df["eq"]) == [True, False, True]

    # test GT operation
    node_gt = node_ctor("ColCompareNode", id="cc_gt", op="GT", col1="a", col2="b", result_col="gt")
    node_gt.infer_schema({"table": tbl.extract_schema()})
    out2 = node_gt.execute({"table": tbl})
    assert list(out2["table"].payload.df["gt"]) == [False, True, False]

    # hint should provide choices for numeric/bool columns
    hint = node.hint({"table": tbl.extract_schema()}, {})
    assert "col1_choices" in hint and "col2_choices" in hint
    assert "a" in hint["col1_choices"] and "b" in hint["col2_choices"]


def test_col_compare_type_mismatch_raises(node_ctor):
    # columns with different types should trigger NodeValidationError during infer
    tbl = table_from_dict({"a": [1, 2], "b": [True, False]})
    # force types: a is INT (inferred), b is BOOL
    tbl.payload.col_types["b"] = ColType.BOOL
    node = node_ctor("ColCompareNode", id="cc_mis", op="EQ", col1="a", col2="b", result_col="r")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": tbl.extract_schema()})


def test_col_with_prim_compare_using_param_and_input(node_ctor):
    tbl = table_from_dict({"v": [1, 2, 3]})
    # use parameter constant
    node_param = node_ctor("ColWithPrimCompareNode", id="cp_param", op="GT", col="v", const=1, result_col="gt_p")
    out_schema = node_param.infer_schema({"table": tbl.extract_schema()})
    assert "table" in out_schema
    out = node_param.execute({"table": tbl})
    assert list(out["table"].payload.df["gt_p"]) == [False, True, True]

    # use const provided as input (schema + runtime data)
    node_in = node_ctor("ColWithPrimCompareNode", id="cp_in", op="LTE", col="v", result_col="leq")
    # provide const as input schema (int)
    const_schema = make_data(2).extract_schema()
    out_schema2 = node_in.infer_schema({"table": tbl.extract_schema(), "const": const_schema})
    assert "table" in out_schema2
    # execute with actual const Data
    out2 = node_in.execute({"table": tbl, "const": make_data(2)})
    assert list(out2["table"].payload.df["leq"]) == [True, True, False]


def test_col_with_prim_compare_missing_const_raises(node_ctor):
    tbl = table_from_dict({"v": [1]})
    # neither const param nor const input provided -> infer should raise
    node = node_ctor("ColWithPrimCompareNode", id="cp_missing", op="EQ", col="v", result_col="r")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": tbl.extract_schema()})


def test_col_with_prim_compare_const_type_mismatch_raises(node_ctor):
    # column is INT but const input schema is FLOAT -> infer should raise
    tbl = table_from_dict({"v": [1, 2]})
    node = node_ctor("ColWithPrimCompareNode", id="cp_mismatch", op="EQ", col="v", result_col="r")
    # provide a float schema for 'const'
    const_schema = make_data(1.5).extract_schema()
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": tbl.extract_schema(), "const": const_schema})