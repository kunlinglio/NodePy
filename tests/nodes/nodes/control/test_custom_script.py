import pytest

from server.models.exception import NodeExecutionError
from server.models.schema import Schema
from server.models.types import ColType

from tests.nodes.utils import make_schema, make_data

from server.models.data import Data

def test_custom_script_success(node_ctor):
    # simple script that sums two integer inputs
    script = """
def script(a, b):
    return {"sum": a + b}
"""
    node = node_ctor(
        "CustomScriptNode",
        id="cs_ok",
        input_ports={"a": "int", "b": "int"},
        output_ports={"sum": "int"},
        script=script,
    )

    # infer schemas for inputs
    in_schemas = {"a": make_schema("int"), "b": make_schema("int")}
    out_schemas = node.infer_schema(in_schemas)
    assert "sum" in out_schemas

    # execute with concrete Data
    out = node.execute({"a": make_data(2), "b": make_data(3)})
    assert "sum" in out
    assert isinstance(out["sum"], Data)
    assert out["sum"].payload == 5


def test_custom_script_missing_function_raises(node_ctor):
    # script does not define 'script' function
    bad_script = """
def not_script(a, b):
    return {"sum": a + b}
"""
    node = node_ctor(
        "CustomScriptNode",
        id="cs_no_func",
        input_ports={"a": "int", "b": "int"},
        output_ports={"sum": "int"},
        script=bad_script,
    )
    node.infer_schema({"a": make_schema("int"), "b": make_schema("int")})
    with pytest.raises(NodeExecutionError):
        node.execute({"a": make_data(1), "b": make_data(1)})


def test_custom_script_wrong_return_type_raises(node_ctor):
    # script returns a list instead of dict
    bad_script = """
def script(a, b):
    return [a, b]
"""
    node = node_ctor(
        "CustomScriptNode",
        id="cs_bad_return",
        input_ports={"a": "int", "b": "int"},
        output_ports={"sum": "int"},
        script=bad_script,
    )
    node.infer_schema({"a": make_schema("int"), "b": make_schema("int")})
    with pytest.raises(NodeExecutionError):
        node.execute({"a": make_data(1), "b": make_data(2)})


def test_custom_script_missing_output_key_raises(node_ctor):
    # script returns dict but missing expected output key
    bad_script = """
def script(a, b):
    return {"other": a + b}
"""
    node = node_ctor(
        "CustomScriptNode",
        id="cs_missing_key",
        input_ports={"a": "int", "b": "int"},
        output_ports={"sum": "int"},
        script=bad_script,
    )
    node.infer_schema({"a": make_schema("int"), "b": make_schema("int")})
    with pytest.raises(NodeExecutionError):
        node.execute({"a": make_data(1), "b": make_data(2)})


def test_custom_script_hint_template_present():
    # Directly call the class hint to verify script_template is provided
    from server.interpreter.nodes.control import custom as custom_mod

    hint = custom_mod.CustomScriptNode.hint({}, {})
    assert "script_template" in hint
    assert isinstance(hint["script_template"], str)