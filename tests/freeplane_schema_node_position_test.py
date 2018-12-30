import pytest
import os
from .context import FreeplaneSchema

OUTPUT_PREFIX = os.path.join("output", "text_output_")


@pytest.fixture
def freeplane_document():
    return FreeplaneSchema()


def test_freeplane_schema_set_node_position_left_on_root_node(freeplane_document):
    filename = OUTPUT_PREFIX + "position_left.mm"
    position = 'left'
    node_id = 'root'
    freeplane_document.set_node_position_by_id(node_id, position)
    freeplane_document.write_document(filename)

    assert freeplane_document.get_node_position_by_id(node_id) == position


def test_freeplane_schema_set_node_position_right_on_root_node(freeplane_document):
    filename = OUTPUT_PREFIX + "position_right.mm"
    position = 'right'
    node_id = 'root'
    freeplane_document.set_node_position_by_id(node_id, position)
    freeplane_document.write_document(filename)

    assert freeplane_document.get_node_position_by_id(node_id) == position


def test_freeplane_schema_set_node_position_badvalue_on_root_node(freeplane_document):
    position = 'bad_value'
    node_id = 'root'

    try:
        freeplane_document.set_node_position_by_id(node_id, position)
    except freeplane_document.FreeplaneBadValueForPosition:
        assert True
