import pytest

from server.models.exception import NodeExecutionError, NodeParameterError, NodeValidationError
from server.models.types import ColType

from tests.nodes.utils import table_from_dict, make_data, schema_from_coltypes


def test_pack_with_base_row_appends_columns(node_ctor):
    base = table_from_dict({"existing": [5]})
    node = node_ctor("PackNode", id="p_base", cols=["a", "b"])
    # prepare input_schemas: base_row present and primitive inputs
    out_schema = node.infer_schema(
        {
            "base_row": base.extract_schema(),
            "a": make_data(1).extract_schema(),
            "b": make_data(2).extract_schema(),
        }
    )
    assert "packed_row" in out_schema

    # set _col_types as infer would
    node._col_types = out_schema["packed_row"].tab.col_types

    out = node.process({"base_row": base, "a": make_data(1), "b": make_data(2)})
    packed = out["packed_row"].payload
    # ensure existing column preserved and new columns appended
    assert list(packed.df["existing"]) == [5]
    assert list(packed.df["a"]) == [1]
    assert list(packed.df["b"]) == [2]


def test_unpack_infer_removes_unpacked_columns(node_ctor):
    node = node_ctor("UnpackNode", id="u_infer", cols=["x", "y"])
    schema = schema_from_coltypes({"x": ColType.INT, "y": ColType.INT, "z": ColType.INT})
    out = node.infer_output_schemas({"row": schema})
    # unpacked_row should be present and should not include x,y
    assert "unpacked_row" in out
    rem = out["unpacked_row"].tab.col_types
    assert "x" not in rem and "y" not in rem and "z" in rem


def test_cell_validate_and_hint(node_ctor):
    # invalid col name should raise
    with pytest.raises(NodeParameterError):
        node_ctor("GetCellNode", id="bad_get", col="   ")
    with pytest.raises(NodeParameterError):
        node_ctor("SetCellNode", id="bad_set", col="")

    # hint should include column choices when table schema provided
    node = node_ctor("GetCellNode", id="g_hint", col="a", row=0)
    hint = node.hint({"table": schema_from_coltypes({"a": ColType.INT, "b": ColType.INT})}, {})
    assert "col_choices" in hint and "a" in hint["col_choices"]

    node2 = node_ctor("SetCellNode", id="s_hint", col="a", row=0)
    hint2 = node2.hint({"table": schema_from_coltypes({"a": ColType.INT})}, {})
    assert "col_choices" in hint2