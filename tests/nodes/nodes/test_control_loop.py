import pandas as pd
import pytest

from server.models.data import Data, Table
from server.models.types import ColType

from tests.nodes.utils import table_from_dict


def test_foreach_begin_iter_empty(node_ctor):
    """iter_loop should yield nothing for an empty table."""
    tbl = table_from_dict({})  # empty table
    begin = node_ctor("ForEachRowBeginNode", id="fb_empty", pair_id=1)

    gen = begin.iter_loop({"table": tbl})
    assert list(gen) == []


def test_foreach_begin_iter_single_and_multi(node_ctor):
    """iter_loop should yield one-row tables for each row in the input table."""
    tbl = table_from_dict({"a": [5, 6, 7]})
    begin = node_ctor("ForEachRowBeginNode", id="fb_multi", pair_id=1)

    yielded = list(begin.iter_loop({"table": tbl}))
    # should yield three iteration outputs
    assert len(yielded) == 3
    # each yielded item is a dict with key 'row' whose payload is a Table with single row
    values = [d["row"].payload.df.iloc[0]["a"] for d in yielded]
    assert values == [5, 6, 7]
    # col_types should be preserved for each yielded row
    for d in yielded:
        assert isinstance(d["row"].payload, Table)
        assert d["row"].payload.col_types == tbl.payload.col_types


def test_endnode_finalize_empty(node_ctor):
    """finalize_loop should return an empty table when no rows were collected."""
    end = node_ctor("ForEachRowEndNode", id="fe_empty", pair_id=1)
    # ensure internal buffer is empty
    end._output_rows = []
    out = end.finalize_loop()
    assert "table" in out
    result_tbl = out["table"].payload
    # empty dataframe and (usually) only index column present in col_types
    assert isinstance(result_tbl, Table)
    assert result_tbl.df.empty
    # Some Table implementations always include the index column; accept either empty or only index.
    assert result_tbl.col_types == {} or result_tbl.col_types == {Table.INDEX_COL: ColType.INT}


def test_full_loop_integration_collects_and_combines_rows(node_ctor):
    """Integration test: iterate with begin.iter_loop and collect via end.end_iter_loop."""
    tbl = table_from_dict({"x": [10, 20]})
    begin = node_ctor("ForEachRowBeginNode", id="fb_int", pair_id=1)
    end = node_ctor("ForEachRowEndNode", id="fe_int", pair_id=1)
    # ensure buffer clear
    end._output_rows = []

    # simulate interpreter loop: yield rows from begin and feed to end
    for out in begin.iter_loop({"table": tbl}):
        # out is like {"row": Data(payload=Table(...))}
        end.end_iter_loop(out)

    combined = end.finalize_loop()
    assert "table" in combined
    res_tbl = combined["table"].payload
    # should have two rows with the same values as original
    assert list(res_tbl.df["x"]) == [10, 20]
    # combined col_types should equal original table's col_types
    assert res_tbl.col_types == tbl.payload.col_types