import pytest
import os
from .context import FreeplaneSchema

OUTPUT_PREFIX = os.path.join("output", "text_output_")


@pytest.fixture
def freeplane_document():
    return FreeplaneSchema()


def test_freeplane_schema_customized_text_on_root_node(freeplane_document, text="text1"):
    filename = OUTPUT_PREFIX + "changed_text.mm"
    freeplane_document.set_node_text_by_id('root', text)
    freeplane_document.write_document(filename)

    assert freeplane_document.get_node_text_by_id('root') == text

    # This test still need to confirm
    #     It can handle non unique ID.  This particular check must ignore checks made at the set_id methode level
    #     to account for manual editing of the xml document
