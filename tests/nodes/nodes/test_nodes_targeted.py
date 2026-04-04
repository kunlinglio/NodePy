import pytest
import pandas as pd
from datetime import datetime

from server.models.exception import NodeExecutionError, NodeParameterError, NodeValidationError
from server.models.types import ColType
from server.models.data import Table

from tests.nodes.utils import table_from_dict, schema_from_coltypes, make_data, make_schema


# ---------------------- PctChange targeted branches ----------------------
def test_pctchange_validate_and_infer_errors(node_ctor):
    # empty column name should raise parameter error
    with pytest.raises(NodeParameterError):
        node_ctor("PctChangeNode", id="pc_err", col="", result_col=None)

    # infer should raise validation error when requested col missing in schema
    node = node_ctor("PctChangeNode", id="pc_inf", col="missing", result_col=None)
    # implementation uses assertions for missing column, so expect AssertionError
    with pytest.raises(AssertionError):
        node.infer_output_schemas({"table": schema_from_coltypes({"a": ColType.INT})})


# ---------------------- Resample targeted branches ----------------------
def test_resample_infer_removes_non_aggregatable_and_count_sets_int(node_ctor):
    node = node_ctor("ResampleNode", id="rs_inf", col="dt", frequency="D", method="mean", result_col=None)

    # construct schema with a DATETIME column, a numeric column and a non-aggregatable (STR) column
    schema_in = schema_from_coltypes({"dt": ColType.DATETIME, "num": ColType.INT, "meta": ColType.STR})
    out = node.infer_output_schemas({"table": schema_in})
    assert "table" in out
    out_tab = out["table"].tab
    assert out_tab is not None
    # 'meta' is non-aggregatable for mean, so it should be removed in the output schema
    assert "meta" not in out_tab.col_types
    # result_col was set
    assert node.result_col is not None

    # count method: other cols should be set to INT in output
    node_count = node  # reuse
    node_count.method = "count"
    out_count = node_count.infer_output_schemas({"table": schema_in})
    out_ct = out_count["table"].tab
    assert out_ct is not None
    # For count, ensure result_col present and numeric columns remain and be INT
    assert node_count.result_col in out_ct.col_types
    # For aggregated columns with count, non-key columns should be present as INT
    assert "num" in out_ct.col_types and out_ct.col_types["num"] == ColType.INT


def test_resample_process_invalid_frequency_raises_runtime(node_ctor):
    # construct with valid literals then mutate to an invalid frequency to exercise runtime error branch
    node = node_ctor("ResampleNode", id="rs_run", col="dt", frequency="D", method="mean", result_col=None)
    schema = schema_from_coltypes({"dt": ColType.DATETIME, "val": ColType.INT})
    node.infer_output_schemas({"table": schema})

    df = pd.DataFrame({"dt": pd.to_datetime(["2021-01-01", "2021-01-02"]), "val": [1, 2]})
    tbl = table_from_dict({"dt": list(df["dt"]), "val": [1, 2]})

    # mutate to an invalid frequency to trigger the resample creation error path
    node.frequency = "BAD_FREQ"
    with pytest.raises(NodeExecutionError):
        node.process({"table": tbl})


# ---------------------- Rolling targeted branches ----------------------
def test_rolling_validate_and_infer_result_types(node_ctor):
    # invalid window size
    with pytest.raises(NodeParameterError):
        node_ctor("RollingNode", id="r_bad", col="a", window_size=0, result_col=None, method="mean")

    # mean should yield FLOAT result type
    node_mean = node_ctor("RollingNode", id="r_mean", col="a", window_size=2, result_col=None, method="mean")
    schema = schema_from_coltypes({"a": ColType.INT, "b": ColType.FLOAT})
    out_mean = node_mean.infer_output_schemas({"table": schema})
    assert "table" in out_mean
    out_tab = out_mean["table"].tab
    assert out_tab is not None
    # result_col exists and is FLOAT for mean
    assert node_mean.result_col is not None
    assert out_tab.col_types[node_mean.result_col] == ColType.FLOAT

    # sum should preserve original column type (INT)
    node_sum = node_ctor("RollingNode", id="r_sum", col="a", window_size=2, result_col=None, method="sum")
    out_sum = node_sum.infer_output_schemas({"table": schema})
    out_tab_sum = out_sum["table"].tab
    assert out_tab_sum is not None
    assert out_tab_sum.col_types[node_sum.result_col] == ColType.INT


def test_rolling_hint_col_choices(node_ctor):
    node = node_ctor("RollingNode", id="r_hint", col="a", window_size=2, result_col=None, method="mean")
    schema = schema_from_coltypes({"a": ColType.FLOAT, "b": ColType.STR})
    hint = node.hint({"table": schema}, {})
    # only numeric columns should appear
    assert "col_choices" in hint
    assert "a" in hint["col_choices"]
    assert "b" not in hint["col_choices"]


# ---------------------- Control: GetCell / SetCell targeted branches ----------------------
def test_setcell_process_accepts_datetime_and_updates(node_ctor):
    # prepare a table with datetime column - tests.utils will infer col types
    ts1 = pd.Timestamp("2020-01-01T00:00:00Z")
    ts2 = pd.Timestamp("2020-01-02T00:00:00Z")
    tbl = table_from_dict({"a": [ts1, ts2]})
    # construct node to set a datetime cell
    node = node_ctor("SetCellNode", id="s_dt", col="a", row=1)
    # set _col_types to allow Table construction in process
    node._col_types = tbl.payload.col_types
    # set a new datetime value
    new_ts = pd.Timestamp("2021-05-05T05:05:05Z")
    out = node.process({"table": tbl, "value": make_data(new_ts)})
    assert "table" in out
    out_tbl = out["table"].payload
    # row 1 should be updated
    assert out_tbl.df.iloc[1]["a"] == new_ts


def test_getcell_infer_missing_column_raises(node_ctor):
    node = node_ctor("GetCellNode", id="g_err", col="nope", row=0)
    with pytest.raises(NodeValidationError):
        node.infer_output_schemas({"table": schema_from_coltypes({"a": ColType.INT})})


# ---------------------- ForBase and ForRollingWindow targeted branches ----------------------
def test_forbase_subclass_pair_type_and_iter(node_ctor):
    # create small concrete subclass of ForBaseBeginNode / ForBaseEndNode to exercise abstract behavior
    from server.interpreter.nodes.control.loop.for_base_node import ForBaseBeginNode, ForBaseEndNode

    class SmallBegin(ForBaseBeginNode):
        def validate_parameters(self) -> None:
            return

        def port_def(self):
            from server.models.schema import Pattern, Schema
            return [], []

        def infer_output_schemas(self, input_schemas):
            return {}

        def iter_loop(self, inputs):
            yield {}

        def process(self, input):
            # minimal implementation to satisfy abstract BaseNode requirements
            return {}

    class SmallEnd(ForBaseEndNode):
        def validate_parameters(self) -> None:
            return

        def port_def(self):
            return [], []

        def infer_output_schemas(self, input_schemas):
            return {}

        def end_iter_loop(self, loop_outputs):
            pass

        def finalize_loop(self):
            return {}

        def process(self, input):
            # minimal implementation to satisfy abstract BaseNode requirements
            return {}

    from server.interpreter.nodes.context import NodeContext
    from server.lib.FileManager import FileManager as FM
    from server.lib.FinancialDataManager import FinancialDataManager as FDM
    ctx = NodeContext(file_manager=FM(), financial_data_manager=FDM(), user_id=1, project_id=1)
    b = SmallBegin(type="SmallBegin", id="sb", context=ctx, pair_id=999)
    e = SmallEnd(type="SmallEnd", id="se", context=ctx, pair_id=999)
    assert b.pair_type == "BEGIN"
    assert e.pair_type == "END"
    # iter_loop yields
    got = list(b.iter_loop({}))
    assert isinstance(got, list)


def test_forrollingwindow_iter_yields_windows_preserving_coltypes(node_ctor):
    # normal case: window_size yields a number of windows and col_types preserved in window payload
    dates = pd.date_range("2020-01-01", periods=4, freq="D")
    tbl = table_from_dict({"time": list(dates), "v": [1, 2, 3, 4]})
    node = node_ctor("ForRollingWindowBeginNode", id="frw_ok", window_size=2, pair_id=321)
    wins = list(node.iter_loop({"table": tbl}))
    assert len(wins) == 3  # 4 rows with window 2 -> 3 windows
    for w in wins:
        assert "window" in w
        payload = w["window"].payload
        assert isinstance(payload, Table)
        # ensure column types still include original columns
        assert "v" in payload.col_types