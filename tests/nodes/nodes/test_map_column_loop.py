import pandas as pd
import pytest

from server.models.data import Data, Table
from server.models.exception import NodeParameterError
from server.models.schema import Schema
from server.models.types import ColType

from tests.nodes.utils import table_from_dict, schema_from_coltypes, make_data


def test_mapcolumn_begin_validate_and_iter_and_hint(node_ctor):
    # empty/whitespace column name should raise during construction/validation
    # include pair_id to satisfy required control-structure base node parameter
    with pytest.raises(NodeParameterError):
        node_ctor("MapColumnBeginNode", id="mb_bad", col="   ", pair_id=1)

    # valid begin node
    tbl = table_from_dict({"a": [1, 2], "b": [10, 20]})
    begin = node_ctor("MapColumnBeginNode", id="mb1", col="a", pair_id=1)

    # iter_loop should yield one item per row with 'cell' and 'remains'
    items = list(begin.iter_loop({"table": tbl}))
    assert len(items) == 2
    # cells should be values from column 'a'
    assert items[0]["cell"].payload == 1
    assert items[1]["cell"].payload == 2
    # remains payload should be a Table with the corresponding row values preserved
    assert isinstance(items[0]["remains"].payload, Table)
    assert items[0]["remains"].payload.df.iloc[0]["b"] == 10
    assert items[1]["remains"].payload.df.iloc[0]["b"] == 20

    # hint should include column choices
    hint = begin.hint({"table": tbl.extract_schema()}, {})
    assert "col_choices" in hint
    assert "a" in hint["col_choices"] and "b" in hint["col_choices"]


def test_mapcolumn_begin_infer_output_schemas(node_ctor):
    # infer_output_schemas should return a 'cell' primitive schema and a 'remains' table schema
    begin = node_ctor("MapColumnBeginNode", id="mb2", col="a", pair_id=2)
    in_schema = schema_from_coltypes({"a": ColType.INT, "b": ColType.INT, Table.INDEX_COL: ColType.INT})
    out = begin.infer_output_schemas({"table": in_schema})
    assert "cell" in out and "remains" in out
    # 'remains' should be a table schema that contains both columns
    assert out["remains"].tab is not None
    assert "a" in out["remains"].tab.col_types and "b" in out["remains"].tab.col_types


def test_mapcolumn_end_infer_conflict_and_collect_finalize(node_ctor):
    # If result_col collides with existing column name, infer_output_schemas should raise
    end_conflict = node_ctor("MapColumnEndNode", id="me_conflict", result_col="b", pair_id=3)
    cell_schema = Schema(type=Schema.Type.INT)
    remains_schema = schema_from_coltypes({"a": ColType.INT, "b": ColType.INT, Table.INDEX_COL: ColType.INT})
    with pytest.raises(NodeParameterError):
        end_conflict.infer_output_schemas({"cell": cell_schema, "remains": remains_schema})

    # Normal use: collect several iterations and finalize into combined table
    end = node_ctor("MapColumnEndNode", id="me1", result_col="mapped", pair_id=4)
    # clear any shared buffer (PrivateAttr default might be reused across instances)
    end._output_rows = []

    # create two loop outputs and feed into end_iter_loop
    row1_tbl = Table(df=pd.DataFrame({"a": [1]}), col_types={"a": ColType.INT, Table.INDEX_COL: ColType.INT})
    row2_tbl = Table(df=pd.DataFrame({"a": [2]}), col_types={"a": ColType.INT, Table.INDEX_COL: ColType.INT})

    out1 = {"cell": Data(payload=100), "remains": Data(payload=row1_tbl)}
    out2 = {"cell": Data(payload=200), "remains": Data(payload=row2_tbl)}

    end.end_iter_loop(out1)
    end.end_iter_loop(out2)

    combined = end.finalize_loop()
    assert "table" in combined
    tbl = combined["table"].payload
    # result column should be present as the first column inserted by end_iter_loop
    assert "mapped" in tbl.df.columns
    assert list(tbl.df["mapped"]) == [100, 200]
    # other columns (like 'a') should also be present and preserved
    assert "a" in tbl.df.columns
    assert list(tbl.df["a"]) == [1, 2]
    # col_types should include the mapped column and original columns
    assert "mapped" in tbl.col_types
    assert "a" in tbl.col_types