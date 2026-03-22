import pytest
from typing import Literal, Dict, Any

from server.interpreter.nodes.control.control_struc_base_node import ControlStrucBaseNode
from server.interpreter.nodes.base_node import BaseNode
from server.interpreter.nodes.context import NodeContext


def _make_concrete_control_class(pair_type_value: Literal["BEGIN", "END"]):
    """
    Create a minimal concrete subclass of ControlStrucBaseNode to allow instantiation
    for testing. Implements all abstract methods from BaseNode with simple stubs.
    """

    class _ConcreteControl(ControlStrucBaseNode):
        # required by ControlStrucBaseNode
        pair_id: int

        @property
        def pair_type(self) -> Literal["BEGIN", "END"]:
            return pair_type_value  # type: ignore[return-value]

        # Minimal required BaseNode implementations
        def validate_parameters(self) -> None:
            # no-op for tests
            return

        def port_def(self):
            # no inputs / outputs required for these tests
            return [], []

        def infer_output_schemas(self, input_schemas: Dict[str, Any]):
            return {}

        def process(self, input: Dict[str, Any]):
            return {}

    # return the class so tests can instantiate it
    return _ConcreteControl


def test_control_struc_pair_info_and_is_control(global_config):
    """
    Ensure concrete control nodes expose correct pair_info and are detected as control structures.
    """
    ConcreteBegin = _make_concrete_control_class("BEGIN")
    ConcreteEnd = _make_concrete_control_class("END")

    begin = ConcreteBegin(id="begin1", type="ConcreteBegin", pair_id=123, context=global_config)
    end = ConcreteEnd(id="end1", type="ConcreteEnd", pair_id=456, context=global_config)

    # is_control_struc should report True
    assert begin.is_control_struc() is True
    assert end.is_control_struc() is True

    # get_control_info should return (pair_id, pair_type)
    assert begin.get_control_info() == (123, "BEGIN")
    assert end.get_control_info() == (456, "END")

    # pair_info property (on the instance) should match as well
    assert begin.pair_info == (123, "BEGIN")
    assert end.pair_info == (456, "END")


def test_non_control_node_returns_none(node_ctor):
    """
    Non-control nodes should not be identified as control structures and get_control_info should return None.
    """
    # Use an existing registered non-control node to ensure behavior
    node = node_ctor("PackNode", id="pack1", cols=["a"])
    assert node.is_control_struc() is False
    assert node.get_control_info() is None