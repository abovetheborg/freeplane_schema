import pytest
import os
import filecmp
from lxml import etree as ET
from lxml.html import etree as ETH
from .context import FreeplaneSchema

INPUT_TEST_HTML_CONTENT = os.path.join("input", "test_html_doc_for_freeplane.html")
INPUT_TEST_READ_NODE_NOTE = os.path.join("input", "test_input_html_note.mm")
INPUT_TEST_READ_NODE_NOTE_WRONG_TYPE = os.path.join("input", "test_input_html_note_wrong_type_defined.mm")
INPUT_TEST_READ_NODE_NOTE_NO_TYPE = os.path.join("input", "test_input_html_note_no_type_defined.mm")

OUTPUT_PREFIX = os.path.join("output", "text_output_")


@pytest.fixture
def html_string_raw():
    with open(INPUT_TEST_HTML_CONTENT) as html_file:
        a = html_file.read()
    return a


@pytest.fixture
def html_string_interpreted():
    a = ET.parse(INPUT_TEST_HTML_CONTENT).getroot()
    return a


@pytest.fixture
def not_html_string():
    a = "<ht fldf d><"
    return a


@pytest.fixture
def freeplane_document(logger_during_tests):
    a = FreeplaneSchema(inherited_logger=logger_during_tests)
    return a


@pytest.fixture
def freeplane_document_with_html_note(logger_during_tests):
    a = FreeplaneSchema(inherited_logger=logger_during_tests)
    a.read_document(INPUT_TEST_READ_NODE_NOTE)
    return a


@pytest.fixture
def freeplane_document_with_html_note_wrong_type(logger_during_tests):
    a = FreeplaneSchema(inherited_logger=logger_during_tests)
    a.read_document(INPUT_TEST_READ_NODE_NOTE_WRONG_TYPE)
    return a


@pytest.fixture
def freeplane_document_with_html_note_no_type(logger_during_tests):
    a = FreeplaneSchema(inherited_logger=logger_during_tests)
    a.read_document(INPUT_TEST_READ_NODE_NOTE_NO_TYPE)
    return a


def test_node_note_read_html_note(freeplane_document_with_html_note):
    filename = OUTPUT_PREFIX + 'html_note.html'
    note_text = freeplane_document_with_html_note.get_node_note_by_id(node_id='root')

    with open(filename, "w") as text_file:
        text_file.write(note_text)

    assert filecmp.cmp(filename, INPUT_TEST_HTML_CONTENT, shallow=False)


def test_node_note_read_html_note_with_wrong_type_defined(freeplane_document_with_html_note_wrong_type):
    note_text = freeplane_document_with_html_note_wrong_type.get_node_note_by_id(node_id='root')
    assert note_text is None


def test_node_note_read_html_note_without_note(freeplane_document):
    note_text = freeplane_document.get_node_note_by_id(node_id='root')
    assert note_text is None


def test_node_note_read_html_note_no_type_defined(freeplane_document_with_html_note_no_type):
    with pytest.raises(freeplane_document_with_html_note_no_type.FreeplaneRichContentTagNotProperlyDefined):
        note_text = freeplane_document_with_html_note_no_type.get_node_note_by_id(node_id='root')


def test_node_note_read_html_note_bad_node(freeplane_document):
    with pytest.raises(freeplane_document.FreeplaneNodeNotExisting):
        note_text = freeplane_document.get_node_note_by_id(node_id='bad_node_id')


def test_html_read_raw(freeplane_document, html_string_raw, not_html_string):
    filename_html = OUTPUT_PREFIX + "add_html_note.mm"
    filename_not_html = OUTPUT_PREFIX + "add_not_html_note.mm"

    # assert not freeplane_document._string_is_valid_html(non_html)
    # assert freeplane_document._string_is_valid_html(html_string_raw)

    freeplane_document.set_node_note_by_id('root', html_string_raw)
    freeplane_document.write_document(filename_html)

    freeplane_document.set_node_note_by_id('root', not_html_string)
    freeplane_document.write_document(filename_not_html, pretty_print_it=True)

# def test_html_read_interpreted(html_string_interpreted):
# print(ET.dump(html_string_interpreted))
