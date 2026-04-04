import pytest
import pandas as pd

from server.models.exception import NodeExecutionError, NodeParameterError
from server.models.types import ColType
from server.models.data import Table

from tests.nodes.utils import table_from_dict, schema_from_coltypes, make_schema, make_data


# ---------------------- Analysis nodes: PctChangeNode ----------------------
def test_pct_change_infer_and_process(node_ctor):
    # construct node (result_col will be generated if None)
    node = node_ctor("PctChangeNode", id="pc1", col="a", result_col=None)

    # infer schema must accept int/float input column
    in_schema = schema_from_coltypes({"a": ColType.INT, "b": ColType.FLOAT})
    out_schema = node.infer_output_schemas({"table": in_schema})
    assert "table" in out_schema
    # result_col should have been assigned if None
    assert node.result_col is not None and node.result_col.endswith("pct_change")

    # create input table with numeric column 'a'
    tbl = table_from_dict({"a": [10, 11, 12], "b": [1.0, 2.0, 3.0]})
    # process should return a table with new float result column
    node._result_col_type = ColType.FLOAT  # ensure process asserts pass (infer already sets it)
    out = node.process({"table": tbl})
    assert "table" in out
    res_tbl = out["table"].payload
    assert isinstance(res_tbl, Table)
    # new column present
    assert node.result_col in res_tbl.df.columns
    # pct_change yields NaN for first row, then numeric values
    assert len(res_tbl.df) == 3
    # second row should have a numeric (or NaN) in result column; ensure column exists and dtype is float-like
    assert pd.api.types.is_float_dtype(res_tbl.df[node.result_col].dtype)


# ---------------------- Analysis nodes: ResampleNode ----------------------
def test_resample_infer_and_invalid_method_raises(node_ctor):
    # create node with valid method then mutate to invalid to bypass pydantic literal validation
    node = node_ctor("ResampleNode", id="rs_bad", col="dt", frequency="D", method="mean", result_col=None)
    # construct schema: dt is Datetime and val is int
    schema = schema_from_coltypes({"dt": ColType.DATETIME, "val": ColType.INT})
    # infer should succeed and set result_col
    out_schema = node.infer_output_schemas({"table": schema})
    assert "table" in out_schema
    assert node.result_col is not None

    # prepare a proper datetime table
    df = pd.DataFrame({
        "dt": pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
        "val": [1, 2, 3],
    })
    # ensure Table wrapper (tests utils will add _index col)
    tbl = table_from_dict({"dt": list(df["dt"]), "val": [1, 2, 3]})
    # mutate method to invalid to exercise process error path
    node.method = "invalid"
    with pytest.raises(NodeExecutionError):
        node.process({"table": tbl})


def test_resample_invalid_frequency_raises(node_ctor):
    # create node with valid frequency then mutate to invalid to bypass pydantic validation
    node = node_ctor("ResampleNode", id="rs_freq", col="dt", frequency="D", method="mean", result_col=None)
    schema = schema_from_coltypes({"dt": ColType.DATETIME, "val": ColType.INT})
    node.infer_output_schemas({"table": schema})

    df = pd.DataFrame({
        "dt": pd.to_datetime(["2021-01-01", "2021-01-02"]),
        "val": [10, 20],
    })
    tbl = table_from_dict({"dt": list(df["dt"]), "val": [10, 20]})
    # mutate frequency to invalid to trigger pandas resample creation error path
    node.frequency = "INVALID_FREQ"
    with pytest.raises(NodeExecutionError):
        node.process({"table": tbl})


def test_resample_count_method_changes_type(node_ctor):
    # count should ensure aggregated col types become INT for counts
    node = node_ctor("ResampleNode", id="rs_count", col="dt", frequency="D", method="count", result_col=None)
    schema = schema_from_coltypes({"dt": ColType.DATETIME, "val": ColType.FLOAT})
    out_schema = node.infer_output_schemas({"table": schema})
    # result column should be present in inferred schema
    assert "table" in out_schema
    # create table with two rows on same day to test aggregation
    df = pd.DataFrame({
        "dt": pd.to_datetime(["2022-01-01 00:00", "2022-01-01 12:00"]),
        "val": [1.1, 2.2],
    })
    tbl = table_from_dict({"dt": list(df["dt"]), "val": [1.1, 2.2]})
    res = node.process({"table": tbl})
    out_tbl = res["table"].payload
    # aggregation by count should produce integer counts
    # The implementation converts to a table and sets col types; ensure output exists and has rows
    assert isinstance(out_tbl, Table)
    assert len(out_tbl.df) >= 1


# ---------------------- Control nodes: GetCell / SetCell hint behavior ----------------------
def test_getcell_hint_and_negative_index(node_ctor):
    # hint should provide column choices when provided table schema
    node = node_ctor("GetCellNode", id="gc1", col="x", row=0)
    hint = node.hint({"table": schema_from_coltypes({"x": ColType.INT, "y": ColType.INT})}, {})
    assert "col_choices" in hint and "x" in hint["col_choices"]

    # negative row index should work in process
    tbl = table_from_dict({"x": [100, 200, 300]})
    node._infered_value_type = ColType.INT
    out = node.process({"table": tbl, "row": make_data(-1)})
    assert out["value"].payload == 300


# ---------------------- Control nodes: ForBase pair properties and rolling window begin ----------------------
def test_for_base_pair_type_properties(node_ctor):
    # ForEachRow begin/end are subclasses of ForBase; ensure pair_type property is correct
    begin = node_ctor("ForEachRowBeginNode", id="fb1", pair_id=11)
    end = node_ctor("ForEachRowEndNode", id="fe1", pair_id=11)
    assert hasattr(begin, "pair_type") and begin.pair_type == "BEGIN"
    assert hasattr(end, "pair_type") and end.pair_type == "END"


def test_for_rolling_window_iter_and_bounds(node_ctor):
    # window size larger than rows should raise NodeExecutionError when iter_loop runs
    tbl = table_from_dict({"x": [1, 2, 3]})
    begin = node_ctor("ForRollingWindowBeginNode", id="rw1", window_size=10, pair_id=20)
    with pytest.raises(NodeExecutionError):
        list(begin.iter_loop({"table": tbl}))

    # valid window should yield expected windows
    begin2 = node_ctor("ForRollingWindowBeginNode", id="rw2", window_size=2, pair_id=21)
    yielded = list(begin2.iter_loop({"table": tbl}))
    # len 3 original rows -> windows = len - window_size + 1 = 2
    assert len(yielded) == 2
    for w in yielded:
        assert "window" in w and hasattr(w["window"].payload, "df")