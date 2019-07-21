import pytest
import os
from .context import FreeplaneSchema

INPUT_FILE_NO_MODIFICATIONS = os.path.join("input", "test_input_no_modifications.mm")
INPUT_FILE_TEXT_MODIFICATIONS = os.path.join("input", "test_input_mod_text.mm")
INPUT_FILE_DELETED_NODE = os.path.join("input", "test_input_deleted_node.mm")
INPUT_FILE_NOTE_MODIFICATIONS = os.path.join("input", "test_input_modified_note.mm")

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


@pytest.fixture
def freeplane_document_deleted_node(logger_during_tests):
    a = FreeplaneSchema(inherited_logger=logger_during_tests)
    a.read_document(INPUT_FILE_DELETED_NODE)
    return a

@pytest.fixture
def freeplane_document_text_modified(logger_during_tests):
    a = FreeplaneSchema(inherited_logger=logger_during_tests)
    a.read_document(INPUT_FILE_TEXT_MODIFICATIONS)
    return a


@pytest.fixture
def freeplane_document_note_modified(logger_during_tests):
    a = FreeplaneSchema(inherited_logger=logger_during_tests)
    a.read_document(INPUT_FILE_NOTE_MODIFICATIONS)
    return a


def test_freeplane_schema_detect_wrong_object(empty_freeplane_document, not_freeplane_schema_object):
    with pytest.raises(empty_freeplane_document.FreeplaneObjectNotFreeplaneDocument):
        empty_freeplane_document.compare_against_reference_document(not_freeplane_schema_object)


def test_freeplane_schema_ask_for_report_results_without_report_being_available(freeplane_document1):
    with pytest.raises(freeplane_document1.FreeplaneCompareReportNotAvailable):
        a = freeplane_document1.list_of_identical_nodes


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

    list_of_identical_nodes = freeplane_document1.list_of_identical_nodes
    assert len(list_of_identical_nodes) == 49

    list_of_modified_nodes = freeplane_document1.list_of_modified_nodes
    assert len(list_of_modified_nodes) == 0

    list_of_deleted_nodes = freeplane_document1.list_of_deleted_nodes
    assert len(list_of_deleted_nodes) == 0

    list_of_unchecked_nodes = freeplane_document1.list_of_not_checked_nodes
    assert len(list_of_unchecked_nodes) == 24

    freeplane_document1._clear_compare_report()
    assert not freeplane_document1.compare_report_available


def test_freeplane_schema_deleted_node(freeplane_document1, freeplane_document_deleted_node):
    freeplane_document_deleted_node.compare_against_reference_document(freeplane_document1)

    list_of_deleted_nodes = freeplane_document_deleted_node.list_of_deleted_nodes
    assert len(list_of_deleted_nodes) == 1
    assert list_of_deleted_nodes[0][freeplane_document_deleted_node.K_NODE_ID] == 'ID_1829616131'


def test_freeplane_schema_text_modified(freeplane_document1, freeplane_document_text_modified):
    freeplane_document_text_modified.compare_against_reference_document(freeplane_document1, test_node_text=True)

    list_of_modified_nodes = freeplane_document_text_modified.list_of_modified_nodes
    assert len(list_of_modified_nodes) == 1
    assert list_of_modified_nodes[0][freeplane_document_text_modified.K_NODE_ID] == 'ID_499898058'


def test_freeplane_schema_note_modified(freeplane_document1, freeplane_document_note_modified):
    freeplane_document_note_modified.compare_against_reference_document(freeplane_document1, test_node_note=True)

    list_of_modified_nodes = freeplane_document_note_modified.list_of_modified_nodes
    assert len(list_of_modified_nodes) == 1
    assert list_of_modified_nodes[0][freeplane_document_note_modified.K_NODE_ID] == 'ID_1556354626'
