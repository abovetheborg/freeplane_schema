import pytest
import filecmp
import os
import errno
from freeplane_schema.freeplane_schema import FreeplaneSchema

DOCUMENT_STANDARDS = "freeplane_standards.mm"
OUTPUT_PREFIX = os.path.join("output", "text_output_")


def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e:  # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred


@pytest.fixture
def freeplane_document():
    return FreeplaneSchema()


def test_freeplane_schema_document_write(freeplane_document):
    filename = OUTPUT_PREFIX + "minimal_document.mm"
    freeplane_document.write_document(filename)
    assert True


def test_freeplane_schema_document_read(freeplane_document,filename=DOCUMENT_STANDARDS):
    freeplane_document.read_document(filename)
    assert True


def test_freeplane_schema_read_write_consistency(freeplane_document,filename=DOCUMENT_STANDARDS):
    new_filename = OUTPUT_PREFIX + "rewritten_" + filename

    silentremove(new_filename)

    freeplane_document.read_document(filename)
    freeplane_document.write_document(new_filename)
    assert filecmp.cmp(filename,new_filename, shallow=False)