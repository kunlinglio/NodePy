import pytest

from server.models.exception import NodeParameterError
from server.models.schema import Schema
from server.models.types import ColType

# Import node classes to directly instantiate and trigger parameter validation
from server.interpreter.nodes.control.custom import CustomScriptNode
from server.interpreter.nodes.control.cell import GetCellNode, SetCellNode
from server.interpreter.nodes.control.unpack import UnpackNode, PackNode
from server.interpreter.nodes.control.loop.for_each_row import ForEachRowBeginNode, ForEachRowEndNode
from server.interpreter.nodes.control.loop.map_column import MapColumnBeginNode, MapColumnEndNode
from server.interpreter.nodes.control.loop.for_rolling_window import ForRollingWindowBeginNode, ForRollingWindowEndNode


def test_validate_parameters_type_mismatch_customscript(global_config):
    # Constructing with wrong `type` should raise NodeParameterError from validate_parameters
    with pytest.raises(NodeParameterError):
        CustomScriptNode(
            type="WrongType",
            id="n1",
            context=global_config,
            input_ports={"x": "int"},
            output_ports={"y": "int"},
            script="def script(x):\n    return {'y': x}"
        )


def test_validate_parameters_type_mismatch_get_set_cell(global_config):
    with pytest.raises(NodeParameterError):
        GetCellNode(
            type="BadType",
            id="n2",
            context=global_config,
            col="a",
            row=0
        )

    with pytest.raises(NodeParameterError):
        SetCellNode(
            type="NotSetCell",
            id="n3",
            context=global_config,
            col="a",
            row=0
        )


def test_validate_parameters_type_mismatch_unpack_pack(global_config):
    with pytest.raises(NodeParameterError):
        UnpackNode(
            type="WrongUnpack",
            id="n4",
            context=global_config,
            cols=["x"]
        )

    with pytest.raises(NodeParameterError):
        PackNode(
            type="WrongPack",
            id="n5",
            context=global_config,
            cols=["a"]
        )


def test_validate_parameters_type_mismatch_loop_nodes(global_config):
    # ForEachRow begin/end pair
    with pytest.raises(NodeParameterError):
        ForEachRowBeginNode(
            type="BadBegin",
            id="n6",
            context=global_config,
            pair_id=1
        )
    with pytest.raises(NodeParameterError):
        ForEachRowEndNode(
            type="BadEnd",
            id="n7",
            context=global_config,
            pair_id=1
        )

    # MapColumn begin/end
    with pytest.raises(NodeParameterError):
        MapColumnBeginNode(
            type="BadMapBegin",
            id="n8",
            context=global_config,
            col="a",
            pair_id=2
        )
    with pytest.raises(NodeParameterError):
        MapColumnEndNode(
            type="BadMapEnd",
            id="n9",
            context=global_config,
            result_col="r",
            pair_id=2
        )

    # Rolling window begin/end
    with pytest.raises(NodeParameterError):
        ForRollingWindowBeginNode(
            type="BadRWBegin",
            id="n10",
            context=global_config,
            window_size=1,
            pair_id=3
        )
    with pytest.raises(NodeParameterError):
        ForRollingWindowEndNode(
            type="BadRWEnd",
            id="n11",
            context=global_config,
            pair_id=3
        )


def test_hint_empty_branches_for_nodes():
    # Many hint implementations return empty dict when required keys are absent.
    # We call hint() classmethods directly to exercise these empty-branch returns.

    # GetCellNode.hint expects 'table' in input_schemas to provide col_choices
    assert GetCellNode.hint({}, {}) == {}

    # SetCellNode.hint similarly returns empty hint when no table provided
    assert SetCellNode.hint({}, {}) == {}

    # UnpackNode.hint requires 'cols' in current_params to provide outputs; empty otherwise
    assert UnpackNode.hint({}, {}) == {}

    # PackNode.hint requires 'cols' in current_params; empty otherwise
    assert PackNode.hint({}, {}) == {}

    # MapColumnBeginNode.hint requires 'table' schema; without it should return either
    # an empty dict or a dict with an empty 'col_choices' list depending on implementation.
    hint_map = MapColumnBeginNode.hint({}, {})
    assert hint_map == {} or hint_map == {"col_choices": []}

    # MapColumnEndNode.hint isn't specialized; default BaseNode.hint returns {}
    assert MapColumnEndNode.hint({}, {}) == {}

    # ForEachRow and ForRollingWindow hints rely on table presence — absent -> {}
    assert ForEachRowBeginNode.hint({}, {}) == {}
    assert ForRollingWindowBeginNode.hint({}, {}) == {}