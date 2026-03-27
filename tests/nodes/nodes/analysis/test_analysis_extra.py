import pytest

from server.models.exception import NodeExecutionError
from server.models.types import ColType

from tests.nodes.utils import table_from_dict, schema_from_coltypes


def test_resample_infer_count_and_mean_behaviour(node_ctor):
    # schema: dt is datetime, a is float, b is str, c is int
    schema = schema_from_coltypes({
        "dt": ColType.DATETIME,
        "a": ColType.FLOAT,
        "b": ColType.STR,
        "c": ColType.INT,
    })

    # method = count: non-aggregatable types should be kept but converted to INT (count)
    node_count = node_ctor("ResampleNode", id="r_count", col="dt", frequency="D", method="count")
    out_count = node_count.infer_schema({"table": schema})
    assert "table" in out_count
    col_types_count = out_count["table"].tab.col_types
    # result_col must exist and be DATETIME
    assert node_count.result_col is not None
    assert col_types_count[node_count.result_col] == ColType.DATETIME
    # 'a' and 'c' should be present and set to INT (count returns int)
    assert col_types_count["a"] == ColType.INT
    assert col_types_count["c"] == ColType.INT
    # 'b' (str) should also be present but as INT due to count semantics
    assert "b" in col_types_count and col_types_count["b"] == ColType.INT

    # method = mean: non-aggregatable columns should be dropped; int->float for mean
    node_mean = node_ctor("ResampleNode", id="r_mean", col="dt", frequency="D", method="mean")
    out_mean = node_mean.infer_schema({"table": schema})
    col_types_mean = out_mean["table"].tab.col_types
    # result_col present and DATETIME
    assert node_mean.result_col is not None
    assert col_types_mean[node_mean.result_col] == ColType.DATETIME
    # 'a' (float) should remain
    assert "a" in col_types_mean and col_types_mean["a"] == ColType.FLOAT
    # 'c' was INT and mean should make it FLOAT
    assert "c" in col_types_mean and col_types_mean["c"] == ColType.FLOAT
    # 'b' (str) should be removed for mean aggregation
    assert "b" not in col_types_mean


def test_resample_process_aggregations_and_errors(node_ctor):
    from datetime import datetime, timedelta

    base = datetime(2022, 1, 1)
    tbl = table_from_dict({
        "dt": [base, base + timedelta(hours=6), base + timedelta(days=1)],
        "v": [1.0, 3.0, 5.0],
    })

    # valid method 'sum' should succeed
    node_sum = node_ctor("ResampleNode", id="r_proc_sum", col="dt", frequency="D", method="sum")
    # ensure result_col and _col_types set before process
    if node_sum.result_col is None:
        node_sum.result_col = f"{node_sum.id}_res"
    # infer to get _col_types
    schema = schema_from_coltypes({"dt": ColType.DATETIME, "v": ColType.FLOAT})
    node_sum._col_types = node_sum.infer_schema({"table": schema})["table"].tab.col_types
    out = node_sum.process({"table": tbl})
    out_tbl = out["table"].payload
    # Day1 sum = 1.0 + 3.0 = 4.0, Day2 sum = 5.0
    assert pytest.approx(list(out_tbl.df["v"])[0], rel=1e-6) == 4.0
    assert pytest.approx(list(out_tbl.df["v"])[1], rel=1e-6) == 5.0

    # invalid method should raise NodeExecutionError at runtime
    node_bad_method = node_ctor("ResampleNode", id="r_bad", col="dt", frequency="D", method="mean")
    # monkeypatch to an invalid method to simulate runtime error
    node_bad_method.method = "NOT_A_METHOD"  # bypass typing for test
    if node_bad_method.result_col is None:
        node_bad_method.result_col = f"{node_bad_method.id}_res"
    node_bad_method._col_types = node_bad_method.infer_schema({"table": schema})["table"].tab.col_types
    with pytest.raises(NodeExecutionError):
        node_bad_method.process({"table": tbl})

    # invalid frequency or bad datetime values should raise NodeExecutionError
    # instantiate with a valid literal then mutate `frequency` to avoid pydantic validation
    node_bad_freq = node_ctor("ResampleNode", id="r_freq_bad", col="dt", frequency="D", method="sum")
    # now set an invalid frequency at runtime to trigger the resample error during process
    node_bad_freq.frequency = "INVALID"
    if node_bad_freq.result_col is None:
        node_bad_freq.result_col = f"{node_bad_freq.id}_res"
    node_bad_freq._col_types = node_bad_freq.infer_schema({"table": schema})["table"].tab.col_types
    # using non-parseable dates in table to trigger pandas error in set_index/resample
    tbl_bad = table_from_dict({"dt": ["not_a_date"], "v": [1.0]})
    with pytest.raises(NodeExecutionError):
        node_bad_freq.process({"table": tbl_bad})


def test_rolling_sum_infer_preserves_type(node_ctor):
    # For method 'sum' the result_col type should be same as input column type
    node_sum = node_ctor("RollingNode", id="roll_sum", col="a", window_size=3, min_periods=1, method="sum")
    schema_int = schema_from_coltypes({"a": ColType.INT})
    out = node_sum.infer_schema({"table": schema_int})
    assert node_sum.result_col is not None
    # sum should preserve INT input -> INT result
    assert out["table"].tab.col_types[node_sum.result_col] == ColType.INT

    # mean would produce float
    node_mean = node_ctor("RollingNode", id="roll_mean", col="a", window_size=3, min_periods=1, method="mean")
    out2 = node_mean.infer_schema({"table": schema_int})
    assert out2["table"].tab.col_types[node_mean.result_col] == ColType.FLOAT


def test_stats_hint_lists_numeric_columns(node_ctor):
    # stats.hint should return numeric column choices only
    node = node_ctor("StatsNode", id="st_hint", col="x")
    schema = schema_from_coltypes({"x": ColType.FLOAT, "y": ColType.STR, "z": ColType.INT})
    hint = node.hint({"table": schema}, {})
    assert "col_choices" in hint
    # numeric columns x and z should be present, y should be absent
    assert "x" in hint["col_choices"]
    assert "z" in hint["col_choices"]
    assert "y" not in hint["col_choices"]