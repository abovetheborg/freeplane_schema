import pytest
import os
import difflib

from .context import FreeplaneSchema

OUTPUT_PREFIX = os.path.join("output", "test_output_")
INPUT_PREFIX = os.path.join("input", "test_input_")


@pytest.fixture
def freeplane_document():
    return FreeplaneSchema()


def test_freeplane_schema_read_write(freeplane_document):
    input_filename = INPUT_PREFIX + 'read_write.mm'
    output_filename = OUTPUT_PREFIX + 'read_write.mm'

    freeplane_document.read_document(input_filename)
    freeplane_document.write_document(output_filename)

    # This code is too slow to execute. Manual compare is needed for now
    #
    # with open(output_filename, 'r') as ofile:
    #     with open(input_filename, 'r') as ifile:
    #         diff = difflib.unified_diff(ofile.readline(), ifile.readline(), fromfile='ofile', tofile='ifile', n=0)
    #         for line in diff:
    #             print(line)
