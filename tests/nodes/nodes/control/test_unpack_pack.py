import pytest

from server.models.data import Data, Table
from server.models.exception import NodeParameterError, NodeExecutionError, NodeValidationError
from server.models.types import ColType

from tests.nodes.utils import (
    table_from_dict,
    schema_from_coltypes,
    make_schema,
    make_data,
)


def test_unpack_construct_invalid(node_ctor):
    # empty cols should raise parameter error
    with pytest.raises(NodeParameterError):
        node_ctor("UnpackNode", id="u_invalid", cols=[])


def test_unpack_infer_missing_col_raises(node_ctor):
    # infer should raise when requested cols are not present in the input row schema
    node = node_ctor("UnpackNode", id="u_infer_err", cols=["a", "b"])
    # provide a row schema that lacks 'b'
    row_schema = schema_from_coltypes({"a": ColType.INT})
    with pytest.raises(NodeValidationError):
        node.infer_schema({"row": row_schema})


def test_unpack_process_success(node_ctor):
    # unpack a single-row table into separate outputs and remaining row
    one_row = table_from_dict({"a": [1], "b": ["x"], "c": [10]}, col_types={"a": ColType.INT, "b": ColType.STR, "c": ColType.INT, "_index": ColType.INT})
    node = node_ctor("UnpackNode", id="u_ok", cols=["a", "b"])

    out_schema = node.infer_schema({"row": one_row.extract_schema()})
    assert "a" in out_schema and "b" in out_schema and "unpacked_row" in out_schema

    out = node.execute({"row": one_row})
    # check primitive outputs
    assert out["a"].payload == 1
    assert out["b"].payload == "x"
    # unpacked_row should be a Table without a and b columns
    rem = out["unpacked_row"].payload
    assert isinstance(rem, Table)
    assert "a" not in rem.df.columns and "b" not in rem.df.columns
    # remaining column c must exist
    assert "c" in rem.df.columns


def test_unpack_process_multiple_rows_raises(node_ctor):
    # process should raise if the row contains more than one row
    tbl = table_from_dict({"a": [1, 2], "b": ["x", "y"]}, col_types={"a": ColType.INT, "b": ColType.STR, "_index": ColType.INT})
    node = node_ctor("UnpackNode", id="u_multi", cols=["a"])
    node.infer_schema({"row": tbl.extract_schema()})
    with pytest.raises(NodeExecutionError):
        node.execute({"row": tbl})


def test_pack_construct_invalid(node_ctor):
    # empty cols list is invalid
    with pytest.raises(NodeParameterError):
        node_ctor("PackNode", id="p_invalid", cols=[])


def test_pack_infer_and_process_without_base_row(node_ctor):
    # packing primitive inputs into a single-row table
    node = node_ctor("PackNode", id="p_simple", cols=["x", "y"])

    # infer schemas: inputs are primitives
    in_schemas = {"x": make_schema("int"), "y": make_schema("str")}
    out_schema = node.infer_schema(in_schemas)
    assert "packed_row" in out_schema

    # execute with primitive data inputs
    inputs = {"x": make_data(42), "y": make_data("hello")}
    out = node.execute(inputs)
    packed = out["packed_row"].payload
    assert isinstance(packed, Table)
    # single row
    assert packed.df.shape[0] == 1
    # columns present
    assert "x" in packed.df.columns and "y" in packed.df.columns
    # values match
    assert int(packed.df.iloc[0]["x"]) == 42
    assert str(packed.df.iloc[0]["y"]) == "hello"


def test_pack_with_base_row(node_ctor):
    # packing with a base_row that already has columns
    base = table_from_dict({"a": [100]}, col_types={"a": ColType.INT, "_index": ColType.INT})
    node = node_ctor("PackNode", id="p_base", cols=["newcol"])
    # infer using base_row + newcol input schema
    out_schema = node.infer_schema({"base_row": base.extract_schema(), "newcol": make_schema("int")})
    assert "packed_row" in out_schema

    # execute with base_row and newcol
    inputs = {"base_row": base, "newcol": make_data(7)}
    out = node.execute(inputs)
    packed = out["packed_row"].payload
    assert isinstance(packed, Table)
    assert packed.df.shape[0] == 1
    # both original and new columns present
    assert "a" in packed.df.columns and "newcol" in packed.df.columns
    assert int(packed.df.iloc[0]["newcol"]) == 7


def test_pack_missing_input_raises(node_ctor):
    # when some required input column is missing, execute should raise
    node = node_ctor("PackNode", id="p_missing", cols=["x", "y"])
    # infer schemas expecting x and y
    node.infer_schema({"x": make_schema("int"), "y": make_schema("str")})
    # only provide one input
    inputs = {"x": make_data(1)}
    with pytest.raises(NodeExecutionError):
        node.execute(inputs)