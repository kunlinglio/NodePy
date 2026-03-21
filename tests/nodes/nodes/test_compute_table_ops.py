import pytest

from server.models.exception import NodeExecutionError, NodeParameterError, NodeValidationError
from server.models.types import ColType

from tests.nodes.utils import table_from_dict, schema_from_coltypes, make_data


def test_col_with_number_binop_basic_ops(node_ctor):
    tbl = table_from_dict({"x": [1, 2, 3]})
    n_add = node_ctor("ColWithNumberBinOpNode", id="n_add", op="ADD", col="x", result_col="x_add", num=10)
    # static analysis
    out_schema = n_add.infer_schema({"table": tbl.extract_schema()})
    assert "table" in out_schema
    # execute and verify results
    out = n_add.execute({"table": tbl})
    res_tbl = out["table"].payload
    assert list(res_tbl.df["x_add"].astype(int)) == [11, 12, 13]

    # COL_DIV_NUM by zero should raise at runtime
    n_div0 = node_ctor("ColWithNumberBinOpNode", id="n_div0", op="COL_DIV_NUM", col="x", result_col="x_div", num=0)
    n_div0.infer_schema({"table": tbl.extract_schema()})
    with pytest.raises(NodeExecutionError):
        n_div0.execute({"table": tbl})

    # NUM_DIV_COL where column contains zero -> should raise
    tbl_with_zero = table_from_dict({"x": [1, 0, 2]})
    n_num_div = node_ctor("ColWithNumberBinOpNode", id="n_num_div", op="NUM_DIV_COL", col="x", result_col="x_ndiv", num=10)
    n_num_div.infer_schema({"table": tbl_with_zero.extract_schema()})
    with pytest.raises(NodeExecutionError):
        n_num_div.execute({"table": tbl_with_zero})

    # POW operations produce floats when necessary
    n_pow = node_ctor("ColWithNumberBinOpNode", id="n_pow", op="COL_POW_NUM", col="x", result_col="x_pow", num=2)
    n_pow.infer_schema({"table": tbl.extract_schema()})
    out_pow = n_pow.execute({"table": tbl})
    assert list(out_pow["table"].payload.df["x_pow"]) == [1.0, 4.0, 9.0]


def test_col_with_number_binop_infer_errors(node_ctor):
    # missing num param and no 'num' input schema should raise NodeParameterError
    node = node_ctor("ColWithNumberBinOpNode", id="n_missing_num", op="ADD", col="x", result_col="r")
    with pytest.raises(NodeParameterError):
        node.infer_schema({"table": schema_from_coltypes({"x": ColType.INT})})

    # mismatched primitive type with table column should raise NodeValidationError
    node2 = node_ctor("ColWithNumberBinOpNode", id="n_mismatch", op="ADD", col="x", result_col="r", num=1)
    # table declares x as float but num is int: still allowed for many ops, but we can force mismatch by providing 'num' schema
    with pytest.raises(NodeValidationError):
        node2.infer_schema({"table": schema_from_coltypes({"x": ColType.STR}), "num": make_data(1).extract_schema()})


def test_col_with_bool_binop_basic_ops(node_ctor):
    # prepare table and ensure column typed as BOOL (use boolean payloads)
    tbl = table_from_dict({"b": [True, False, True]})
    tbl.payload.col_types["b"] = ColType.BOOL

    n_and = node_ctor("ColWithBoolBinOpNode", id="nb_and", op="AND", col="b", result_col="b_and")
    out_schema = n_and.infer_schema({"table": tbl.extract_schema(), "bool": make_data(True).extract_schema()})
    assert "table" in out_schema
    # provide a boolean payload for the primitive 'bool' input
    out = n_and.execute({"table": tbl, "bool": make_data(True)})
    assert list(out["table"].payload.df["b_and"].astype(int)) == [1, 0, 1]

    n_xor = node_ctor("ColWithBoolBinOpNode", id="nb_xor", op="XOR", col="b", result_col="b_xor")
    n_xor.infer_schema({"table": tbl.extract_schema(), "bool": make_data(True).extract_schema()})
    out2 = n_xor.execute({"table": tbl, "bool": make_data(True)})
    assert list(out2["table"].payload.df["b_xor"].astype(int)) == [0, 1, 0]

    # invalid column type for boolean operations should raise in infer
    tbl2 = table_from_dict({"b": [1, 2]})
    # ensure column type is not boolean
    tbl2.payload.col_types["b"] = ColType.INT
    bad_node = node_ctor("ColWithBoolBinOpNode", id="nb_bad", op="AND", col="b", result_col="r")
    with pytest.raises(NodeValidationError):
        bad_node.infer_schema({"table": tbl2.extract_schema(), "bool": make_data(True).extract_schema()})


def test_number_col_unary_ops_and_errors(node_ctor):
    tbl = table_from_dict({"n": [1, -2, 3]})
    # ABS
    n_abs = node_ctor("NumberColUnaryOpNode", id="nu_abs", op="ABS", col="n", result_col="n_abs")
    n_abs.infer_schema({"table": tbl.extract_schema()})
    out = n_abs.execute({"table": tbl})
    assert list(out["table"].payload.df["n_abs"]) == [1, 2, 3]

    # NEG
    n_neg = node_ctor("NumberColUnaryOpNode", id="nu_neg", op="NEG", col="n", result_col="n_neg")
    n_neg.infer_schema({"table": tbl.extract_schema()})
    out2 = n_neg.execute({"table": tbl})
    assert list(out2["table"].payload.df["n_neg"]) == [-1, 2, -3]

    # LOG on non-positive should raise
    tbl_log = table_from_dict({"v": [1.0, 0.0, 2.0]})
    n_log = node_ctor("NumberColUnaryOpNode", id="nu_log", op="LOG", col="v", result_col="v_log")
    n_log.infer_schema({"table": tbl_log.extract_schema()})
    with pytest.raises(NodeExecutionError):
        n_log.execute({"table": tbl_log})

    # SQRT on negative should raise
    tbl_sqrt = table_from_dict({"v": [4.0, -1.0]})
    n_sqrt = node_ctor("NumberColUnaryOpNode", id="nu_sqrt", op="SQRT", col="v", result_col="v_sqrt")
    n_sqrt.infer_schema({"table": tbl_sqrt.extract_schema()})
    with pytest.raises(NodeExecutionError):
        n_sqrt.execute({"table": tbl_sqrt})


def test_number_col_with_col_binop_and_division_errors(node_ctor):
    tbl = table_from_dict({"a": [2, 3], "b": [5, 0]})
    # ensure types are numeric
    node = node_ctor("NumberColWithColBinOpNode", id="nc_add", op="ADD", col1="a", col2="b", result_col="r")
    out_schema = node.infer_schema({"table": tbl.extract_schema()})
    assert "table" in out_schema
    out = node.execute({"table": tbl})
    assert list(out["table"].payload.df["r"]) == [7, 3]

    # DIV with zero in col2 should raise
    node_div = node_ctor("NumberColWithColBinOpNode", id="nc_div", op="DIV", col1="a", col2="b", result_col="r_div")
    node_div.infer_schema({"table": tbl.extract_schema()})
    with pytest.raises(NodeExecutionError):
        node_div.execute({"table": tbl})


def test_bool_col_with_col_binop(node_ctor):
    tbl = table_from_dict({"p": [True, False, True], "q": [False, True, True]})
    # set types to BOOL
    tbl.payload.col_types["p"] = ColType.BOOL
    tbl.payload.col_types["q"] = ColType.BOOL

    node = node_ctor("BoolColWithColBinOpNode", id="bc_and", op="AND", col1="p", col2="q", result_col="pq_and")
    node.infer_schema({"table": tbl.extract_schema()})
    out = node.execute({"table": tbl})
    assert list(out["table"].payload.df["pq_and"].astype(int)) == [0, 0, 1]

    # SUB (boolean difference) - ensure it doesn't crash and produces expected masking behavior
    node_sub = node_ctor("BoolColWithColBinOpNode", id="bcc_sub", op="SUB", col1="p", col2="q", result_col="pq_sub")
    node_sub.infer_schema({"table": tbl.extract_schema()})
    out2 = node_sub.execute({"table": tbl})
    # boolean subtraction interpreted as p & ~q
    assert list(out2["table"].payload.df["pq_sub"].astype(int)) == [1, 0, 0]