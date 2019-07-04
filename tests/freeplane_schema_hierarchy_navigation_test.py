import pytest
from .context import FreeplaneSchema


@pytest.fixture
def freeplane_document_as_initialized():
    return FreeplaneSchema()


@pytest.fixture
def freeplane_document_one_children():
    a = FreeplaneSchema()
    a.create_basic_node(a.get_node_by_id('root'), a.get_node_by_id('root'))
    return a


@pytest.fixture
def freeplane_document_two_children_level():
    a = FreeplaneSchema()
    a.create_basic_node(a.get_node_by_id('root'), a.get_node_by_id('root'), node_id='level1')
    a.create_basic_node(a.get_node_by_id('root'), a.get_node_by_id('level1'), node_id='level2')
    return a


@pytest.fixture
def freeplane_document_two_children_level_two_nodes_at_level2():
    a = FreeplaneSchema()
    a.create_basic_node(a.get_node_by_id('root'), a.get_node_by_id('root'), node_id='level1')
    a.create_basic_node(a.get_node_by_id('root'), a.get_node_by_id('level1'), node_id='level21')
    a.create_basic_node(a.get_node_by_id('root'), a.get_node_by_id('level1'), node_id='level22')
    return a


def test_freeplane_schema_get_children_no_hierarchy(freeplane_document_as_initialized):
    results = freeplane_document_as_initialized.get_node_immediate_children(
        freeplane_document_as_initialized.get_node_by_id('root'))

    assert len(results) == 0


def test_freeplane_schema_get_children_one_level(freeplane_document_one_children):
    results = freeplane_document_one_children.get_node_immediate_children(
        freeplane_document_one_children.get_node_by_id('root'))

    assert len(results) == 1


def test_freeplane_schema_get_children_one_level_with_two_level_hierarchy(freeplane_document_two_children_level):
    results = freeplane_document_two_children_level.get_node_immediate_children(
        freeplane_document_two_children_level.get_node_by_id('root'))

    assert len(results) == 1


def test_freeplane_schema_get_children_second_level_with_two_level_hierarchy(freeplane_document_two_children_level):
    results = freeplane_document_two_children_level.get_node_immediate_children(
        freeplane_document_two_children_level.get_node_by_id('level1'))

    assert len(results) == 1


def test_freeplane_schema_get_children_second_level_with_two_level_hierarchy_two_node_at_level2(
        freeplane_document_two_children_level_two_nodes_at_level2):
    results = freeplane_document_two_children_level_two_nodes_at_level2.get_node_immediate_children(
        freeplane_document_two_children_level_two_nodes_at_level2.get_node_by_id('level1'))

    assert len(results) == 2
