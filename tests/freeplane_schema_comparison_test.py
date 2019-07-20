import pytest
import os
from .context import FreeplaneSchema

INPUT_FILE_NO_MODIFICATIONS = os.path.join("input", "test_input_no_modifications.mm")

@pytest.fixture
def empty_freeplane_document(logger_during_tests):
    return FreeplaneSchema(inherited_logger=logger_during_tests)


@pytest.fixture
def same_empty_freeplane_document(logger_during_tests):
    return FreeplaneSchema(inherited_logger=logger_during_tests)


@pytest.fixture
def not_freeplane_schema_object():
    return object()


@pytest.fixture
def freeplane_document1(logger_during_tests):
    a = FreeplaneSchema(inherited_logger=logger_during_tests)
    a.read_document(INPUT_FILE_NO_MODIFICATIONS)
    return a


@pytest.fixture
def freeplane_document2(logger_during_tests):
    a = FreeplaneSchema(inherited_logger=logger_during_tests)
    a.read_document(INPUT_FILE_NO_MODIFICATIONS)
    return a


def test_freeplane_schema_detect_wrong_object(empty_freeplane_document, not_freeplane_schema_object):
    with pytest.raises(empty_freeplane_document.FreeplaneObjectNotFreeplaneDocument):
        empty_freeplane_document.compare_against_reference_document(not_freeplane_schema_object)


def test_freeplane_schema_comparison_same_file(empty_freeplane_document, same_empty_freeplane_document):
    assert not empty_freeplane_document.compare_report_available
    empty_freeplane_document.compare_against_reference_document(same_empty_freeplane_document)
    assert empty_freeplane_document.compare_report_available
    empty_freeplane_document._clear_compare_report()
    assert not empty_freeplane_document.compare_report_available


def test_freeplane_schema_full_featured_same_file(freeplane_document1, freeplane_document2):
    assert not freeplane_document1.compare_report_available
    freeplane_document1.compare_against_reference_document(freeplane_document2, test_node_text=True)
    assert freeplane_document1.compare_report_available
    freeplane_document1._clear_compare_report()
    assert not freeplane_document1.compare_report_available

    pass
