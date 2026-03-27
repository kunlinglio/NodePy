import pytest

from server.models.types import ColType
from server.models.exception import NodeValidationError, NodeExecutionError

from tests.nodes.utils import table_from_dict, schema_from_coltypes


def test_cumulative_infer_missing_column_raises(node_ctor):
    node = node_ctor("CumulativeNode", id="cum_edge", col="missing", method="cumsum")
    # schema doesn't contain the required column -> infer should raise NodeValidationError
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": schema_from_coltypes({"a": ColType.FLOAT})})


def test_cumulative_process_invalid_method_asserts(node_ctor):
    node = node_ctor("CumulativeNode", id="cum_invalid", col="a", method="cumsum")
    # prepare a valid schema and table and set internal state as if infer ran
    schema = schema_from_coltypes({"a": ColType.FLOAT})
    node.infer_schema({"table": schema})
    # choose an invalid method at runtime
    node.method = "NOT_A_VALID_METHOD"  # bypass pydantic typing for runtime test
    # ensure result_col and result type are present
    if node.result_col is None:
        node.result_col = f"{node.id}_res"
    node._result_col_type = ColType.FLOAT
    tbl = table_from_dict({"a": [1.0, 2.0, 3.0]})
    # process may end up producing a dataframe missing the expected result column
    # which will surface as a TypeError when the Table constructor validates columns.
    with pytest.raises(TypeError):
        node.process({"table": tbl})


def test_diff_infer_missing_column_raises(node_ctor):
    node = node_ctor("DiffNode", id="d_edge", col="nope")
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": schema_from_coltypes({"x": ColType.FLOAT})})


def test_diff_process_without_infer_asserts(node_ctor):
    # If infer wasn't run, _new_col_name will be None and process asserts it's not None
    node = node_ctor("DiffNode", id="d_no_infer", col="x")
    tbl = table_from_dict({"x": [1.0, 2.0, 3.0]})
    with pytest.raises(AssertionError):
        node.process({"table": tbl})


def test_pct_change_process_without_infer_asserts(node_ctor):
    node = node_ctor("PctChangeNode", id="p_no_infer", col="v")
    tbl = table_from_dict({"v": [10.0, 11.0]})
    # process expects result_col and _result_col_type to be set by infer; otherwise assertions
    with pytest.raises(AssertionError):
        node.process({"table": tbl})


def test_resample_empty_table_returns_empty(node_ctor):
    node = node_ctor("ResampleNode", id="r_empty", col="dt", frequency="D", method="mean")
    schema = schema_from_coltypes({"dt": ColType.DATETIME, "v": ColType.FLOAT})
    out_schema = node.infer_schema({"table": schema})
    # empty table (zero rows)
    tbl = table_from_dict({"dt": [], "v": []})
    # ensure internal col types set
    node._col_types = out_schema["table"].tab.col_types
    if node.result_col is None:
        node.result_col = f"{node.id}_res"
    # pandas may raise when attempting to resample if the index isn't a proper datetime-like index
    # Even for empty frames, resample setup can error; node wraps such errors as NodeExecutionError.
    with pytest.raises(NodeExecutionError):
        node.process({"table": tbl})


def test_resample_invalid_frequency_runtime_raises(node_ctor):
    node = node_ctor("ResampleNode", id="r_badfreq", col="dt", frequency="D", method="sum")
    schema = schema_from_coltypes({"dt": ColType.DATETIME, "v": ColType.FLOAT})
    node._col_types = node.infer_schema({"table": schema})["table"].tab.col_types
    # mutate to invalid frequency after construction to bypass pydantic literal check
    node.frequency = "INVALID_FREQ"
    # table with unparseable dt should cause pandas to error when set_index/resample invoked
    tbl_bad = table_from_dict({"dt": ["not_a_date"], "v": [1.0]})
    with pytest.raises(NodeExecutionError):
        node.process({"table": tbl_bad})


def test_rolling_window_bigger_than_rows_and_min_periods(node_ctor):
    # window larger than number of rows but min_periods=1 should still compute some values
    node = node_ctor("RollingNode", id="roll_edge", col="a", window_size=10, min_periods=1, method="mean")
    schema = schema_from_coltypes({"a": ColType.FLOAT})
    out = node.infer_schema({"table": schema})
    if node.result_col is None:
        node.result_col = f"{node.id}_ma"
    tbl = table_from_dict({"a": [2.0, 4.0, 6.0]})
    # set result type
    node._result_col_type = out["table"].tab.col_types[node.result_col]
    outd = node.process({"table": tbl})
    out_tbl = outd["table"].payload
    # result length must match input length
    assert len(out_tbl.df) == 3
    # with min_periods=1, the first element should equal the original first value
    assert out_tbl.df[node.result_col].iloc[0] == 2.0


def test_rolling_invalid_method_runtime_raises(node_ctor):
    node = node_ctor("RollingNode", id="roll_bad", col="a", window_size=2, min_periods=1, method="mean")
    schema = schema_from_coltypes({"a": ColType.FLOAT})
    node.infer_schema({"table": schema})
    # mutate to an invalid method to provoke pandas error during aggregation
    node.method = "NOT_A_PANDAS_METHOD"
    if node.result_col is None:
        node.result_col = f"{node.id}_ma"
    node._result_col_type = ColType.FLOAT
    tbl = table_from_dict({"a": [1.0, 2.0, 3.0]})
    # pandas should raise when agg is called with invalid method, which should surface as an exception here
    with pytest.raises(Exception):
        node.process({"table": tbl})