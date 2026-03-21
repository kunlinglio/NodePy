import pytest

from server.models.exception import NodeParameterError

# Parameter validation tests for ColTo* nodes
# These tests assert that nodes validate their constructor parameters correctly
# (e.g., non-empty column names, result column not equal to input column,
# and illegal column names such as names that start with reserved '_' prefix).


def test_col_to_string_param_validation(node_ctor):
    # empty/whitespace column name should raise
    with pytest.raises(NodeParameterError):
        node_ctor("ColToStringNode", id="cts_bad1", col="   ")

    # result_col equal to col should raise
    with pytest.raises(NodeParameterError):
        node_ctor("ColToStringNode", id="cts_bad2", col="a", result_col="a")

    # illegal result column name (starts with underscore) should raise
    with pytest.raises(NodeParameterError):
        node_ctor("ColToStringNode", id="cts_bad3", col="a", result_col="_illegal")


def test_col_to_int_param_validation(node_ctor):
    # empty/whitespace column name should raise
    with pytest.raises(NodeParameterError):
        node_ctor("ColToIntNode", id="cti_bad1", col="  ", method="FLOOR")

    # result_col equal to col should raise
    with pytest.raises(NodeParameterError):
        node_ctor("ColToIntNode", id="cti_bad2", col="num", result_col="num", method="ROUND")

    # illegal result column name (starts with underscore) should raise
    with pytest.raises(NodeParameterError):
        node_ctor("ColToIntNode", id="cti_bad3", col="num", result_col="_x", method="CEIL")


def test_col_to_float_param_validation(node_ctor):
    # empty/whitespace column name should raise
    with pytest.raises(NodeParameterError):
        node_ctor("ColToFloatNode", id="ctf_bad1", col="", )

    # result_col equal to col should raise
    with pytest.raises(NodeParameterError):
        node_ctor("ColToFloatNode", id="ctf_bad2", col="val", result_col="val")

    # illegal result column name (starts with underscore) should raise
    with pytest.raises(NodeParameterError):
        node_ctor("ColToFloatNode", id="ctf_bad3", col="val", result_col="_bad")


def test_col_to_bool_param_validation(node_ctor):
    # empty/whitespace column name should raise
    with pytest.raises(NodeParameterError):
        node_ctor("ColToBoolNode", id="ctb_bad1", col="   ")

    # result_col equal to col should raise
    with pytest.raises(NodeParameterError):
        node_ctor("ColToBoolNode", id="ctb_bad2", col="flag", result_col="flag")

    # illegal result column name (starts with underscore) should raise
    with pytest.raises(NodeParameterError):
        node_ctor("ColToBoolNode", id="ctb_bad3", col="flag", result_col="_hidden")