import pytest
import os

from .context import FreeplaneSchema

OUTPUT_PREFIX = os.path.join("output", "text_output_")


@pytest.fixture
def freeplane_document():
    return FreeplaneSchema()


def test_freeplane_schema_attributes_set_single_attribute_on_root(freeplane_document):
    filename = OUTPUT_PREFIX + "set_single_attribute_on_root.mm"
    attribute_name = "Name of attribute"
    attribute_value = "Value of attribute"

    freeplane_document.set_attribute_by_id('root', attribute_name, attribute_value)

    # freeplane_document.write_document(filename)

    result = freeplane_document.get_attribute_by_id('root', attribute_name)

    assert result[attribute_name] == attribute_value


def test_freeplane_schema_attributes_set_two_attribute_on_root(freeplane_document):
    filename = OUTPUT_PREFIX + "set_single_attribute_on_root_twice.mm"
    attribute_name = "Name of attribute"
    attribute_value = "Value of attribute"

    attribute_name2 = "Name of attribute 2"
    attribute_value2 = "Value of attribute 2"

    freeplane_document.set_attribute_by_id('root', attribute_name, attribute_value)
    freeplane_document.set_attribute_by_id('root', attribute_name2, attribute_value2)

    freeplane_document.write_document(filename)

    result = freeplane_document.get_attribute_by_id('root', attribute_name)
    result2 = freeplane_document.get_attribute_by_id('root')

    assert result2[attribute_name] == attribute_value
    assert result[attribute_name] == attribute_value


def test_freeplane_schema_attributes_set_attribute_on_child(freeplane_document):
    freeplane_document.add_node_by_id(freeplane_document.get_node_by_id('root'), node_id="child 1")
    filename = OUTPUT_PREFIX + "set_single_attribute_on_child_twice.mm"
    attribute_name = "Name of attribute"
    attribute_value = "Value of attribute"

    freeplane_document.set_attribute_by_id('child 1', attribute_name, attribute_value)

    freeplane_document.write_document(filename)

    result = freeplane_document.get_attribute_by_id('child 1', attribute_name)
    result2 = freeplane_document.get_attribute_by_id('child 1')

    assert result[attribute_name] == attribute_value
    assert result2[attribute_name] == attribute_value


def test_freeplane_schema_attribute_set_attribute_on_root_with_dictionary(freeplane_document):
    attributes = {'Attribute 1': 'Value 1',
                  'Attribute 2': 'Value 2',
                  'Attribute 3': 'Value 3'}

    filename = OUTPUT_PREFIX + "set_single_attribute_on_root_with_dict.mm"

    freeplane_document.set_attribute_by_id('root', attribute_dict=attributes)

    freeplane_document.write_document(filename)

    result = freeplane_document.get_attribute_by_id('root')

    for key in result:
        assert result[key] == attributes[key]


def test_freeplane_schema_attribute_set_attribute_on_child_with_dictionary(freeplane_document):
    attributes = {'Attribute 1': 'Value 1',
                  'Attribute 2': 'Value 2',
                  'Attribute 3': 'Value 3'}

    filename = OUTPUT_PREFIX + "set_single_attribute_on_child_with_dict.mm"

    freeplane_document.add_node_by_id(freeplane_document.get_node_by_id('root'), node_id="child 1")
    freeplane_document.set_attribute_by_id('child 1', attribute_dict=attributes)

    freeplane_document.write_document(filename)

    result = freeplane_document.get_attribute_by_id('child 1')

    for key in result:
        assert result[key] == attributes[key]


# Not sure if this works...  It should failed because I am not passing any node_id parameter...
def test_feeplane_schema_attribute_pass_inconsistent_parameter(freeplane_document):
    attributes = {'Attribute 1': 'Value 1',
                  'Attribute 2': 'Value 2',
                  'Attribute 3': 'Value 3'}

    try:
        freeplane_document.set_attribute_by_id('root',
                                               attribute_dict=None,
                                               attribute_name="Name",
                                               attribute_value=None)
    except freeplane_document.FreeplaneInconsistentParameterPassed:
        assert True
    except:
        assert False
    else:
        assert False

    try:
        freeplane_document.set_attribute_by_id('root',
                                               attribute_dict=None,
                                               attribute_name=None,
                                               attribute_value="Value")
    except freeplane_document.FreeplaneInconsistentParameterPassed:
        assert True
    except:
        assert False
    else:
        assert False

    try:
        freeplane_document.set_attribute_by_id('root',
                                               attribute_dict=None,
                                               attribute_name=None,
                                               attribute_value=None)
    except freeplane_document.FreeplaneInconsistentParameterPassed:
        assert True
    except:
        assert False
    else:
        assert False

    try:
        freeplane_document.set_attribute_by_id('root',
                                               attribute_dict=attributes,
                                               attribute_name="Name",
                                               attribute_value=None)
    except freeplane_document.FreeplaneInconsistentParameterPassed:
        assert True
    except:
        assert False
    else:
        assert False

    try:
        freeplane_document.set_attribute_by_id('root',
                                               attribute_dict=attributes,
                                               attribute_name=None,
                                               attribute_value="Value")
    except freeplane_document.FreeplaneInconsistentParameterPassed:
        assert True
    except:
        assert False
    else:
        assert False

    try:
        freeplane_document.set_attribute_by_id('root',
                                               attribute_dict='not a dict',
                                               attribute_name=None,
                                               attribute_value="Value")
    except freeplane_document.FreeplaneInconsistentParameterPassed:
        assert True
    except:
        assert False
    else:
        assert False
