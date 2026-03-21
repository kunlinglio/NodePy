import pandas as pd
import pytest

from server.models.data import Data, Table
from server.models.types import ColType
from tests.nodes.utils import schema_from_coltypes, table_from_dict


def test_for_each_row_iter_and_finalize(node_ctor):
    # prepare a simple table with two rows
    tbl = table_from_dict({"a": [1, 2], "b": ["x", "y"]})
    schema = schema_from_coltypes({"a": ColType.INT, "b": ColType.STR})

    begin = node_ctor("ForEachRowBeginNode", id="for_begin", pair_id=1)
    end = node_ctor("ForEachRowEndNode", id="for_end", pair_id=1)

    # infer schemas for begin and end nodes
    out_schema = begin.infer_schema({"table": tbl.extract_schema()})
    assert "row" in out_schema

    out_schema_end = end.infer_schema({"row": out_schema["row"]})
    assert "table" in out_schema_end

    # iterate rows using begin.iter_loop and collect with end node
    yielded = list(begin.iter_loop({"table": tbl}))
    assert len(yielded) == 2
    # each yielded item contains a 'row' table with a single row
    assert yielded[0]["row"].payload.df.shape[0] == 1
    assert yielded[1]["row"].payload.df.shape[0] == 1

    # feed each yielded row to end.end_iter_loop then finalize
    for it in yielded:
        end.end_iter_loop(it)
    result = end.finalize_loop()
    assert "table" in result
    combined = result["table"].payload
    # combined table should have two rows and preserve original columns
    assert combined.df.shape[0] == 2
    assert isinstance(tbl.payload, Table)
    assert set(combined.df.columns) >= set(tbl.payload.df.columns)


def test_for_each_row_finalize_empty(node_ctor):
    # finalize_loop should return an empty table when nothing was collected
    end = node_ctor("ForEachRowEndNode", id="for_end_empty", pair_id=2)
    res = end.finalize_loop()
    assert "table" in res
    assert isinstance(res["table"].payload, Table)
    assert res["table"].payload.df.empty


def test_begin_iter_missing_input_raises(node_ctor):
    begin = node_ctor("ForEachRowBeginNode", id="for_begin_missing", pair_id=3)
    # missing 'table' input should trigger assertion inside iter_loop
    with pytest.raises(AssertionError):
        list(begin.iter_loop({}))


def test_end_iter_and_process_behavior(node_ctor):
    # ensure end.process returns empty dict as implementation indicates
    end = node_ctor("ForEachRowEndNode", id="for_end_proc", pair_id=4)
    # process is a no-op for the end node per implementation
    out = end.process({"row": Data(payload=Table(df=pd.DataFrame({"a": [1]}), col_types={"a": ColType.INT}))})
    assert out == {}