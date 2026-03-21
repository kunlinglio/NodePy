import pandas as pd
import pytest

from server.models.data import Data, Table
from server.models.exception import NodeExecutionError, NodeParameterError
from server.models.types import ColType

from tests.nodes.utils import table_from_dict


def test_rolling_begin_validate_and_too_large_window(node_ctor):
    # invalid window_size should raise at construction/validation time
    with pytest.raises(NodeParameterError):
        node_ctor("ForRollingWindowBeginNode", id="rb_bad", window_size=0, pair_id=1)

    # window size larger than rows should raise when iterating
    tbl = table_from_dict({"a": [1, 2]})
    begin = node_ctor("ForRollingWindowBeginNode", id="rb1", window_size=3, pair_id=1)
    with pytest.raises(NodeExecutionError):
        # materialize the generator to trigger the check
        list(begin.iter_loop({"table": tbl}))


def test_rolling_begin_iter_windows(node_ctor):
    # window_size == len -> single window equal to full table
    tbl = table_from_dict({"x": [10, 20, 30]})
    begin_full = node_ctor("ForRollingWindowBeginNode", id="rb_full", window_size=3, pair_id=2)
    windows_full = list(begin_full.iter_loop({"table": tbl}))
    assert len(windows_full) == 1
    w0 = windows_full[0]["window"]
    assert isinstance(w0.payload, Table)
    assert list(w0.payload.df["x"]) == [10, 20, 30]
    assert w0.payload.col_types == tbl.payload.col_types

    # window_size < len -> multiple overlapping windows
    begin = node_ctor("ForRollingWindowBeginNode", id="rb2", window_size=2, pair_id=2)
    windows = list(begin.iter_loop({"table": tbl}))
    assert len(windows) == 2
    # first window should contain rows [10,20], second [20,30]
    assert list(windows[0]["window"].payload.df["x"]) == [10, 20]
    assert list(windows[1]["window"].payload.df["x"]) == [20, 30]
    # col_types should be preserved on each yielded window
    for item in windows:
        assert item["window"].payload.col_types == tbl.payload.col_types


def test_rolling_end_collect_and_finalize_integration(node_ctor):
    # integration: use begin.iter_loop to produce windows, collect with end, finalize
    tbl = table_from_dict({"v": [1, 2, 3, 4]})
    begin = node_ctor("ForRollingWindowBeginNode", id="rb_int_begin", window_size=2, pair_id=10)
    end = node_ctor("ForRollingWindowEndNode", id="rb_int_end", pair_id=10)

    # ensure internal storage is cleared
    end._outputs_tables = []

    # simulate interpreter loop
    for out in begin.iter_loop({"table": tbl}):
        # each out is {"window": Data(payload=Table(...))}
        end.end_iter_loop(out)

    combined = end.finalize_loop()
    assert "table" in combined
    combined_tbl = combined["table"].payload
    # The finalize implementation drops the '_index' column before returning.
    # The concatenated values from windows with window_size=2 over 4 rows should be:
    # windows: [1,2], [2,3], [3,4] -> concatenated rows: [1,2,2,3,3,4]
    # Since each window is a table, concatenation results in stacked rows; check the 'v' series length and values.
    assert list(combined_tbl.df["v"]) == [1, 2, 2, 3, 3, 4]
    # combined col_types should come from the first window's col_types and include expected keys
    assert isinstance(combined_tbl.col_types, dict)
    # original table had at least column 'v' and index column
    assert "v" in combined_tbl.col_types

    # also check finalize with no collected windows returns an empty table (col_types may vary)
def test_rolling_end_finalize_empty(node_ctor):
    end_empty = node_ctor("ForRollingWindowEndNode", id="rb_empty", pair_id=11)
    end_empty._outputs_tables = []
    out = end_empty.finalize_loop()
    assert "table" in out
    tbl = out["table"].payload
    assert isinstance(tbl, Table)
    assert tbl.df.empty
    # Some implementations include only the index column in col_types for empty tables.
    # Accept either an empty mapping or one that contains only the index column.
    assert isinstance(tbl.col_types, dict)
    assert tbl.col_types == {} or (len(tbl.col_types) == 1 and Table.INDEX_COL in tbl.col_types)