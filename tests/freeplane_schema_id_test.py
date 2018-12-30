import pytest
from .context import FreeplaneSchema


@pytest.fixture
def freeplane_document():
    return FreeplaneSchema()


def test_freeplane_schema_id_find_node_by_id(freeplane_document):
    freeplane_document.add_node_by_id(freeplane_document.root_node, node_id="ID_01")
    result = freeplane_document.get_node_by_id("ID_01")

    assert result.attrib[freeplane_document.A_ID] == "ID_01"


def test_freeplane_schema_id_create_two_node_same_id(freeplane_document):
    freeplane_document.add_node_by_id(freeplane_document.root_node, node_id="ID_01")

    try:
        freeplane_document.add_node_by_id(freeplane_document.root_node, node_id="ID_01")
    except freeplane_document.FreeplaneIDAlreadyExist:
        assert True
    except:
        assert False


def test_freeplane_schema_id_request_node_with_non_existing_id(freeplane_document):
    result = freeplane_document.get_node_by_id("NON_EXISTING_ID")
    assert result is None
