import math
import pytest

from server.models.types import ColType
from server.models.exception import NodeParameterError, NodeValidationError, NodeExecutionError

from tests.nodes.utils import table_from_dict, schema_from_coltypes

import server.models.schema as schema_mod


def test_cumulative_parameter_validation_errors(node_ctor):
    # empty column name should raise at construction
    with pytest.raises(NodeParameterError):
        node_ctor("CumulativeNode", id="cum_err_1", col="   ", method="cumsum")

    # result_col starting with '_' is illegal
    with pytest.raises(NodeParameterError):
        node_ctor("CumulativeNode", id="cum_err_2", col="a", method="cumsum", result_col="_bad")


def test_cumulative_hint_and_process(node_ctor):
    node = node_ctor("CumulativeNode", id="cum_hint", col="val", method="cumsum")
    schema = schema_from_coltypes({"val": ColType.INT, "other": ColType.STR})
    hint = node.hint({"table": schema}, {})
    # hint should suggest numeric columns (val)
    assert "col_choices" in hint
    assert "val" in hint["col_choices"]

    # infer and process: use floats so cumsum result is float dtype
    schema2 = schema_from_coltypes({"val": ColType.FLOAT})
    out = node.infer_schema({"table": schema2})
    assert "table" in out
    tbl = table_from_dict({"val": [1.0, 2.0, 3.0]})
    # ensure internal state is present
    if node.result_col is None:
        node.result_col = f"{node.id}_cumsum"
    node._result_col_type = ColType.FLOAT
    outd = node.process({"table": tbl})
    res_tbl = outd["table"].payload
    assert list(res_tbl.df[node.result_col]) == [1.0, 3.0, 6.0]


def test_pct_change_infer_missing_column_raises(node_ctor):
    node = node_ctor("PctChangeNode", id="pct_err", col="missing")
    # schema doesn't contain 'missing'
    with pytest.raises(NodeValidationError):
        node.infer_schema({"table": schema_from_coltypes({"v": ColType.FLOAT})})


def test_pct_change_with_zero_previous(node_ctor):
    node = node_ctor("PctChangeNode", id="pct_zero", col="v")
    schema = schema_from_coltypes({"v": ColType.FLOAT})
    out_schema = node.infer_schema({"table": schema})
    assert "table" in out_schema
    # build table so second change is finite and third change has prev == 0 -> inf
    tbl = table_from_dict({"v": [100.0, 0.0, 50.0]})
    # ensure internals set
    if node.result_col is None:
        node.result_col = f"{node.id}_pct_change"
    node._result_col_type = ColType.FLOAT
    out = node.process({"table": tbl})
    vals = list(out["table"].payload.df[node.result_col])
    # (0 - 100) / 100 = -1.0
    assert pytest.approx(vals[1], rel=1e-9) == -1.0
    # (50 - 0) / 0 -> inf
    assert math.isinf(vals[2])


def test_diff_hint_and_name_collision(monkeypatch, node_ctor):
    # Simulate check_no_illegal_cols returning False for the default name twice to force renaming loop
    calls = {"count": 0}
    orig = schema_mod.check_no_illegal_cols

    # Create the schema first so schema construction uses the original check_no_illegal_cols.
    schema = schema_from_coltypes({"x": ColType.FLOAT, "y": ColType.INT})

    def fake_check(names, allow_index=False):
        calls["count"] += 1
        # return False the first two times to force the while loop in DiffNode.infer_output_schemas
        if calls["count"] <= 2:
            return False
        return orig(names, allow_index)

    # Monkeypatch after schema creation so the fake only affects the node's infer step.
    # Patch the name used inside the DiffNode module so the node's local import is affected.
    import server.interpreter.nodes.analysis.diff as diff_mod
    monkeypatch.setattr(diff_mod, "check_no_illegal_cols", fake_check)

    node = node_ctor("DiffNode", id="d_collide", col="x")
    out = node.infer_schema({"table": schema})
    # After infer, node._new_col_name should be set and not None
    assert node._new_col_name is not None
    assert node._new_col_name.startswith("x_diff")
    # hint should include numeric choices
    hint = node.hint({"table": schema}, {})
    assert "col_choices" in hint
    assert "x" in hint["col_choices"]


def test_diff_infer_and_process_basic(node_ctor):
    node = node_ctor("DiffNode", id="d_basic", col="x")
    schema = schema_from_coltypes({"x": ColType.FLOAT})
    out = node.infer_schema({"table": schema})
    assert "table" in out
    # process with sample data
    tbl = table_from_dict({"x": [10.0, 12.0, 15.0]})
    # ensure _new_col_name is set by infer
    assert node._new_col_name is not None
    outd = node.process({"table": tbl})
    res_tbl = outd["table"].payload
    # diffs are [2.0, 3.0]
    assert list(res_tbl.df[node._new_col_name]) == [2.0, 3.0]