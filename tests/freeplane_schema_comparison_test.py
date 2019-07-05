import pytest
from .context import FreeplaneSchema


@pytest.fixture
def freeplane_document(logger_during_tests):
    return FreeplaneSchema(inherited_logger=logger_during_tests)


@pytest.fixture
def same_freeplane_document(logger_during_tests):
    return FreeplaneSchema(inherited_logger=logger_during_tests)


@pytest.fixture
def not_freeplane_schema_object():
    return object()


def test_freeplane_schema_detect_wrong_object(freeplane_document, not_freeplane_schema_object):
    with pytest.raises(freeplane_document.FreeplaneObjectNotFreeplaneDocument):
        freeplane_document.compare_against(not_freeplane_schema_object)


def test_freeplane_schema_comparison_same_file(freeplane_document, same_freeplane_document):
    freeplane_document.compare_against(same_freeplane_document)
