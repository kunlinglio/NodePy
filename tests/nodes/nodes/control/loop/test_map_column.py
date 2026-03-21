import pytest

from server.models.data import Data, Table
from server.models.exception import NodeParameterError
from server.models.types import ColType
from server.models.schema import Schema

from tests.nodes.utils import table_from_dict, schema_from_coltypes


def test_map_column_begin_iter_and_infer(node_ctor):
    # prepare a simple integer-only table with three rows to avoid dtype upcast issues
    tbl = table_from_dict({"x": [10, 20, 30], "z": [1, 2, 3]}, col_types={"x": ColType.INT, "z": ColType.INT, "_index": ColType.INT})
    schema = schema_from_coltypes({"x": ColType.INT, "z": ColType.INT})

    # ensure the DataFrame uses pandas nullable integer dtype so single-row slices keep integer dtype
    tbl.payload.df = tbl.payload.df.astype({"x": "Int64", "z": "Int64"})

    # create begin node that will map column 'x'
    begin = node_ctor("MapColumnBeginNode", id="map_begin", col="x", pair_id=1)

    # infer schema for begin node
    out_schema = begin.infer_schema({"table": tbl.extract_schema()})
    assert "cell" in out_schema
    assert "remains" in out_schema
    # 'cell' should be a primitive schema and 'remains' should be a table schema
    assert isinstance(out_schema["cell"], Schema)
    assert out_schema["remains"].type == Schema.Type.TABLE

    # iter_loop yields one item per row
    yielded = list(begin.iter_loop({"table": tbl}))
    assert len(yielded) == 3
    # each yielded item has 'cell' (primitive) and 'remains' (table with single row)
    for idx, item in enumerate(yielded):
        assert "cell" in item and "remains" in item
        # compare as ints to avoid dtype coercion issues
        assert int(item["cell"].payload) == int(tbl.payload.df.iloc[idx]["x"])
        remains_table = item["remains"].payload
        assert isinstance(remains_table, Table)
        # remains currently contains the single-row table (including original columns)
        assert remains_table.df.shape[0] == 1
        assert set(remains_table.df.columns) >= set(tbl.payload.df.columns)

def test_map_end_infer_conflict_raises(node_ctor):
    # prepare integer-only table and derive begin's output schemas
    tbl = table_from_dict({"x": [1, 2], "z": [9, 8]}, col_types={"x": ColType.INT, "z": ColType.INT, "_index": ColType.INT})
    tbl.payload.df = tbl.payload.df.astype({"x": "Int64", "z": "Int64"})
    begin = node_ctor("MapColumnBeginNode", id="map_begin2", col="x", pair_id=2)
    out_schema = begin.infer_schema({"table": tbl.extract_schema()})

    # create an end node that tries to use an existing column name as result_col
    # this should raise during infer_output_schemas because of name collision
    end_conflict = node_ctor("MapColumnEndNode", id="map_end_conflict", result_col="x", pair_id=2)
    with pytest.raises(NodeParameterError):
        end_conflict.infer_schema({"cell": out_schema["cell"], "remains": out_schema["remains"]})

def test_map_end_end_iter_and_finalize(node_ctor):
    # prepare a small integer-only table
    tbl = table_from_dict({"x": [7, 8, 9], "z": [3, 4, 5]}, col_types={"x": ColType.INT, "z": ColType.INT, "_index": ColType.INT})
    tbl.payload.df = tbl.payload.df.astype({"x": "Int64", "z": "Int64"})

    begin = node_ctor("MapColumnBeginNode", id="map_begin3", col="x", pair_id=3)
    end = node_ctor("MapColumnEndNode", id="map_end3", pair_id=3)

    # get schemas from begin
    out_schema = begin.infer_schema({"table": tbl.extract_schema()})
    assert "cell" in out_schema and "remains" in out_schema

    # infer for end node to ensure schema acceptance (should not raise)
    out_schema_end = end.infer_schema({"cell": out_schema["cell"], "remains": out_schema["remains"]})
    assert "table" in out_schema_end

    # iterate and collect outputs into end node
    for item in begin.iter_loop({"table": tbl}):
        end.end_iter_loop(item)

    result = end.finalize_loop()
    assert "table" in result
    combined = result["table"].payload
    # combined table should have same number of rows as original
    assert combined.df.shape[0] == tbl.payload.df.shape[0]
    # the default result_col should be present and columns should include original columns
    # result_col is generated as "<id>_mapped"
    expected_prefix = f"{end.id}_mapped"
    found_result_cols = [c for c in combined.df.columns if c.startswith(expected_prefix)]
    assert len(found_result_cols) == 1
    assert set(tbl.payload.df.columns).issubset(set(combined.df.columns))