import math
import pytest

from server.models.exception import NodeExecutionError, NodeParameterError
from server.models.types import ColType

from tests.nodes.utils import table_from_dict, schema_from_coltypes


# ---------------------- ResampleNode tests ----------------------
def test_resample_mean_and_count(node_ctor):
    node = node_ctor("ResampleNode", id="r1", col="dt", frequency="D", method="mean")
    # build schema: dt is datetime, v is float, s is int (int should be dropped for mean)
    schema = schema_from_coltypes({"dt": ColType.DATETIME, "v": ColType.FLOAT, "s": ColType.INT})
    out = node.infer_schema({"table": schema})
    assert "table" in out
    # process with two days of data; create datetimes so pandas resample works
    from datetime import datetime, timedelta
    base = datetime(2020, 1, 1)
    tbl = table_from_dict({
        "dt": [base, base + timedelta(days=1), base + timedelta(days=1)],
        "v": [1.0, 2.0, 4.0],
        "s": [1, 2, 3],
    })
    # ensure result_col exists for process / regeneration
    if node.result_col is None:
        node.result_col = f"{node.id}_resample"
    node._col_types = out["table"].tab.col_types
    outd = node.process({"table": tbl})
    assert "table" in outd
    out_tbl = outd["table"].payload
    # after daily resample, there should be 2 rows (one per day)
    assert len(out_tbl.df) == 2
    # mean of day1 is 1.0, day2 mean of [2.0,4.0] is 3.0
    # the result_col is the datetime index column; numeric aggregated values are in column 'v'
    assert pytest.approx(list(out_tbl.df["v"])[0], rel=1e-6) == 1.0
    assert pytest.approx(list(out_tbl.df["v"])[1], rel=1e-6) == 3.0


def test_resample_invalid_method_and_frequency(node_ctor):
    node = node_ctor("ResampleNode", id="r2", col="dt", frequency="D", method="mean")
    # invalid method at runtime (monkeypatch attribute) should raise NodeExecutionError in process
    node.method = "bad_method"  # bypass type system for test
    tbl = table_from_dict({"dt": ["2020-01-01"], "v": [1.0]})
    if node.result_col is None:
        node.result_col = f"{node.id}_resample"
    with pytest.raises(NodeExecutionError):
        node.process({"table": tbl})

    # invalid frequency should raise NodeExecutionError when creating resampler
    node2 = node_ctor("ResampleNode", id="r3", col="dt", frequency="D", method="mean")
    # set an invalid frequency string
    node2.frequency = "not_a_freq"
    if node2.result_col is None:
        node2.result_col = f"{node2.id}_resample"
    tbl2 = table_from_dict({"dt": ["not_a_date"], "v": [1.0]})
    # pandas will likely raise when attempting to set_index/resample; node should wrap in NodeExecutionError
    with pytest.raises(NodeExecutionError):
        node2.process({"table": tbl2})


# ---------------------- RollingNode tests ----------------------
def test_rolling_validate_parameters_and_infer(node_ctor):
    # invalid window size should raise at construction
    with pytest.raises(NodeParameterError):
        node_ctor("RollingNode", id="r_err", col="a", window_size=0, method="mean")

    # infer output schema: mean/std -> float, sum/min/max -> same as input
    node_mean = node_ctor("RollingNode", id="r_mean", col="a", window_size=2, method="mean")
    schema = schema_from_coltypes({"a": ColType.INT})
    out_mean = node_mean.infer_schema({"table": schema})
    res_col = node_mean.result_col
    assert res_col is not None
    assert out_mean["table"].tab.col_types[res_col] == ColType.FLOAT

    node_sum = node_ctor("RollingNode", id="r_sum", col="a", window_size=2, method="sum")
    out_sum = node_sum.infer_schema({"table": schema})
    assert node_sum.result_col is not None
    assert out_sum["table"].tab.col_types[node_sum.result_col] == ColType.INT

def test_rolling_process_computes_aggregations(node_ctor):
    node = node_ctor("RollingNode", id="r_proc", col="a", window_size=2, min_periods=1, method="mean")
    schema = schema_from_coltypes({"a": ColType.FLOAT})
    node.infer_schema({"table": schema})
    tbl = table_from_dict({"a": [1.0, 3.0, 5.0]})
    out = node.process({"table": tbl})
    out_tbl = out["table"].payload
    # window=2 mean: [1.0, (1+3)/2=2.0, (3+5)/2=4.0]
    res = list(out_tbl.df[node.result_col])
    assert pytest.approx(res[0], rel=1e-6) == 1.0
    assert pytest.approx(res[1], rel=1e-6) == 2.0
    assert pytest.approx(res[2], rel=1e-6) == 4.0


# ---------------------- StatsNode tests ----------------------
def test_stats_infer_and_process_int_column(node_ctor):
    node = node_ctor("StatsNode", id="s1", col="x")
    schema = schema_from_coltypes({"x": ColType.INT})
    out = node.infer_schema({"table": schema})
    # expected output ports present
    assert set(out.keys()) >= {"mean", "count", "sum", "std", "min", "max", "quantile_25", "quantile_50", "quantile_75"}

    tbl = table_from_dict({"x": [1, 2, 3, 4]})
    outd = node.process({"table": tbl})
    # check types and values
    assert pytest.approx(outd["mean"].payload, rel=1e-6) == 2.5
    assert outd["count"].payload == 4
    assert outd["sum"].payload == 10
    assert pytest.approx(outd["min"].payload, rel=1e-6) == 1
    assert pytest.approx(outd["max"].payload, rel=1e-6) == 4
    # quantiles: 25% = 1.75, 50% = 2.5, 75% = 3.25 (pandas default interpolation)
    assert pytest.approx(outd["quantile_25"].payload, rel=1e-6) == pytest.approx(1.75, rel=1e-6)
    assert pytest.approx(outd["quantile_50"].payload, rel=1e-6) == pytest.approx(2.5, rel=1e-6)
    assert pytest.approx(outd["quantile_75"].payload, rel=1e-6) == pytest.approx(3.25, rel=1e-6)

def test_stats_validate_parameters(node_ctor):
    with pytest.raises(NodeParameterError):
        node_ctor("StatsNode", id="s_err", col="  ")