import pandas as pd
import pytest

from server.models.data import Data, Table
from server.models.exception import NodeExecutionError
from server.models.types import ColType

from tests.nodes.utils import table_from_dict, schema_from_coltypes


def test_for_rolling_window_iter_and_finalize(node_ctor):
    # prepare a simple table with 5 rows
    tbl = table_from_dict({"v": list(range(5))})
    # create begin and end nodes with matching pair_id
    begin = node_ctor("ForRollingWindowBeginNode", id="rw_begin", pair_id=1, window_size=2)
    end = node_ctor("ForRollingWindowEndNode", id="rw_end", pair_id=1)

    # infer schema for the begin node
    out_schema = begin.infer_schema({"table": tbl.extract_schema()})
    assert "window" in out_schema

    # iterate windows and check each window size
    windows = list(begin.iter_loop({"table": tbl}))
    assert len(windows) == 4  # 5 rows, window_size=2 -> 4 windows
    for w in windows:
        assert "window" in w
        assert isinstance(w["window"].payload, Table)
        assert w["window"].payload.df.shape[0] == 2

    # feed to end node and finalize
    for w in windows:
        end.end_iter_loop(w)
    result = end.finalize_loop()
    assert "table" in result
    combined = result["table"].payload
    # combined rows should be windows_count * window_size
    assert combined.df.shape[0] == len(windows) * 2
    # original column should exist in combined table
    assert "v" in combined.df.columns


def test_for_rolling_window_window_too_large_raises(node_ctor):
    tbl = table_from_dict({"a": [1, 2, 3]})
    begin = node_ctor("ForRollingWindowBeginNode", id="rw_begin_large", pair_id=2, window_size=10)
    # iter_loop should raise NodeExecutionError when window_size > number of rows
    with pytest.raises(NodeExecutionError):
        list(begin.iter_loop({"table": tbl}))


def test_for_rolling_window_begin_process_not_implemented(node_ctor):
    tbl = table_from_dict({"a": [1, 2, 3]})
    begin = node_ctor("ForRollingWindowBeginNode", id="rw_begin_proc", pair_id=3, window_size=2)
    # process for begin node is not implemented
    with pytest.raises(NotImplementedError):
        begin.process({"table": tbl})


def test_for_rolling_window_end_finalize_empty(node_ctor):
    end = node_ctor("ForRollingWindowEndNode", id="rw_end_empty", pair_id=4)
    res = end.finalize_loop()
    assert "table" in res
    assert isinstance(res["table"].payload, Table)
    assert res["table"].payload.df.empty