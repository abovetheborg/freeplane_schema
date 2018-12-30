import pytest
import os
from .context import FreeplaneSchema

OUTPUT_PREFIX = os.path.join("output", "text_output_")


@pytest.fixture
def freeplane_document():
    return FreeplaneSchema()


def test_freeplane_schema_node_style_set_node_style_fork_on_root_node(freeplane_document, style='fork'):
    filename = OUTPUT_PREFIX + "style_fork.mm"
    freeplane_document.set_node_style_by_id('root', style)
    freeplane_document.write_document(filename)

    assert freeplane_document.get_node_style_by_id('root') == style


def test_freeplane_schema_node_style_set_default_style(freeplane_document):
    filename = OUTPUT_PREFIX + "style_default.mm"

    freeplane_document.set_node_style_by_id('root', 'default')
    freeplane_document.write_document(filename)
    assert freeplane_document.get_node_style_by_id('root') == 'default'


def test_freeplane_schema_node_style_set_node_style_bubble_on_root_node(freeplane_document, style='bubble'):
    filename = OUTPUT_PREFIX + "style_bubble.mm"
    freeplane_document.set_node_style_by_id('root', style)
    freeplane_document.write_document(filename)

    assert freeplane_document.get_node_style_by_id('root') == style


def test_freeplane_schema_node_style_set_not_existing_node_style_on_root_node(freeplane_document, style='not existing'):
    try:
        freeplane_document.set_node_style_by_id('root', style)
    except freeplane_document.FreeplaneBadValueForStyleError:
        assert True

# TODO all those test on another node but 'root'
