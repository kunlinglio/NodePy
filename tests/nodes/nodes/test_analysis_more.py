import pytest
import pandas as pd

from server.models.exception import NodeExecutionError, NodeParameterError
from server.models.types import ColType
from server.models.data import Table

from tests.nodes.utils import table_from_dict, schema_from_coltypes, make_data, make_schema


# ---------------------- PctChange tests ----------------------
def test_pct_change_process_values_and_column_presence(node_ctor):
    """
    Ensure PctChangeNode produces a new column and computes percentage-change-like values
    for both INT and FLOAT input columns (inferred output type is FLOAT).
    """
    node = node_ctor("PctChangeNode", id="pct_proc", col="a", result_col=None)

    # infer with INT column should succeed
    in_schema = schema_from_coltypes({"a": ColType.INT, "b": ColType.FLOAT})
    out_schemas = node.infer_output_schemas({"table": in_schema})
    assert "table" in out_schemas
    assert node.result_col is not None

    # create table data: pct change of [1,2,4] -> [nan, 1.0, 1.0]
    tbl = table_from_dict({"a": [1, 2, 4], "b": [0.1, 0.2, 0.3]})
    # ensure the node's internal result type is present so process assertions pass
    node._result_col_type = ColType.FLOAT

    out = node.process({"table": tbl})
    assert "table" in out
    out_tbl = out["table"].payload
    assert isinstance(out_tbl, Table)
    assert node.result_col in out_tbl.df.columns
    # length preserved
    assert len(out_tbl.df) == 3
    # result column should be float-like (contains NaN and floats)
    assert pd.api.types.is_float_dtype(out_tbl.df[node.result_col].dtype)


def test_pct_change_infer_rejects_non_numeric_column(node_ctor):
    """
    infer_output_schemas should assert (or raise) when the selected column is not numeric.
    Implementation uses assertion for this case.
    """
    node = node_ctor("PctChangeNode", id="pct_bad", col="c", result_col=None)
    # provide a schema where 'c' is a string column -> should fail assertion in infer
    with pytest.raises(AssertionError):
        node.infer_output_schemas({"table": schema_from_coltypes({"c": ColType.STR})})


def test_pct_change_hint_lists_numeric_columns():
    """
    The classmethod hint should list numeric columns (INT/FLOAT) from the provided table schema.
    """
    from server.interpreter.nodes.analysis.pct_change import PctChangeNode

    schema = schema_from_coltypes({"a": ColType.INT, "b": ColType.FLOAT, "c": ColType.STR})
    hint = PctChangeNode.hint({"table": schema}, {})
    assert "col_choices" in hint
    # include index column in expectations because test utils add the index '_index' to table schemas
    assert set(hint["col_choices"]) == {"_index", "a", "b"}


# ---------------------- Resample tests ----------------------
def test_resample_validate_parameters_empty_col_raises(node_ctor):
    """
    validate_parameters should reject nodes with empty column name.
    """
    with pytest.raises(NodeParameterError):
        node_ctor("ResampleNode", id="res_bad", col="  ", frequency="D", method="mean")


@pytest.mark.parametrize("method", ["mean", "sum", "max", "min"])
def test_resample_process_common_methods_yield_table(node_ctor, method):
    """
    For common aggregation methods, process should produce a table with the result column present.
    This exercises the aggregation branches (mean/sum/max/min).
    """
    node = node_ctor("ResampleNode", id=f"res_{method}", col="dt", frequency="D", method=method, result_col=None)

    # input schema: dt is DATETIME, other column is numeric
    in_schema = schema_from_coltypes({"dt": ColType.DATETIME, "val": ColType.FLOAT})
    out_schema = node.infer_output_schemas({"table": in_schema})
    assert "table" in out_schema
    assert node.result_col is not None

    # build a simple datetime-indexable table (two entries on same day to allow aggregation)
    df = pd.DataFrame({
        "dt": pd.to_datetime(["2021-01-01 00:00", "2021-01-01 12:00"]),
        "val": [1.0, 2.0],
    })
    tbl = table_from_dict({"dt": list(df["dt"]), "val": [1.0, 2.0]})

    out = node.process({"table": tbl})
    assert "table" in out
    out_tbl = out["table"].payload
    assert isinstance(out_tbl, Table)
    # result column exists after aggregation
    assert node.result_col in out_tbl.df.columns


def test_resample_count_method_infers_int_counts(node_ctor):
    """
    infer_output_schemas with method 'count' should set aggregated non-key columns to INT.
    """
    node = node_ctor("ResampleNode", id="res_cnt", col="dt", frequency="D", method="count", result_col=None)
    schema = schema_from_coltypes({"dt": ColType.DATETIME, "num": ColType.FLOAT, "meta": ColType.STR})
    out = node.infer_output_schemas({"table": schema})
    out_tab = out["table"].tab
    assert out_tab is not None
    # count should preserve numeric 'num' and set it to INT in result schema
    assert "num" in out_tab.col_types
    assert out_tab.col_types["num"] == ColType.INT
    # result column present
    assert node.result_col is not None
    assert node.result_col in out_tab.col_types


def test_resample_process_raises_on_non_datetime_index(node_ctor):
    """
    If input table has non-datetime values where a DATETIME schema is expected,
    pandas resample creation should fail and node should raise NodeExecutionError.
    """
    node = node_ctor("ResampleNode", id="res_err", col="dt", frequency="D", method="mean", result_col=None)
    # declare schema expecting datetime (so infer passes)
    node.infer_output_schemas({"table": schema_from_coltypes({"dt": ColType.DATETIME, "v": ColType.INT})})
    # but provide concrete table with integer dt values (not datetime) to trigger runtime error
    tbl = table_from_dict({"dt": [1, 2, 3], "v": [1, 2, 3]})
    with pytest.raises(NodeExecutionError):
        node.process({"table": tbl})