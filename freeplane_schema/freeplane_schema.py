import uuid
import time

from xml.etree.ElementTree import Element, SubElement, ElementTree, parse, fromstring


class FreeplaneSchema(object):
    """
    classdocs

    Node tag
        LOCALIZED_TEXT: Refers to predefined/internal value
            eg.: 'new_mindmap' will be displayed as "New Mindmap" if the UI is in English

        TEXT: User defined text string
    """

    def __init__(self):
        """
        Upon init, will create a new document
        """

        self.xml_root_element = Element(self.T_MAP, version=self.V_MAP_VERSION)
        self.root_node = self.create_basic_node(self.xml_root_element, self.xml_root_element)

        # self.root_node = SubElement(self.xml_root_element, self.T_NODE)
        # self.root_node.set(self.A_ID, uuid.uuid4().hex)
        # self.root_node.set(self.A_LOCALIZED_TEXT, self.V_NEW_MINDMAP)

    def write_document(self, filename):
        """

        :param filename:
        :return:
        """
        ElementTree(self.xml_root_element).write(file_or_filename=filename)

    def read_document(self, filename):
        """

        :param filename:
        :return:
        """
        self.temp_xml_root_element = parse(filename).getroot()

        is_a_true_freeplane_file = False

        # Checks go here, for now checks are passing
        if True:
            is_a_true_freeplane_file = True

        if is_a_true_freeplane_file:
            self.xml_root_element = self.temp_xml_root_element
            del self.temp_xml_root_element

    def set_node_text_by_id(self, node_id, text):
        """

        :param node_id: ID of node th change the text of.
        Special values are:
            'root': will get the root node
        :param text:
        :return:
        """

        node = self.get_node_by_id(node_id)

        if node is None:
            raise self.FreeplaneNodeNotExisting
        else:
            # check if "LOCALIZED_TEXT" is set.  Will need to be unset to have user defined text
            if self.A_LOCALIZED_TEXT in node.attrib:
                # Remove LOCALIZED_TEXT fom the attribute list
                del node.attrib[self.A_LOCALIZED_TEXT]

            node.set(self.A_TEXT, text)

    def get_node_text_by_id(self, node_id):
        """

        :param node_id:
        :return:
        """

        node = self.get_node_by_id(node_id)

        if node is None:
            raise self.FreeplaneNodeNotExisting
        else:
            if self.A_LOCALIZED_TEXT in node.attrib:
                return node.attrib[self.A_LOCALIZED_TEXT]
            elif self.A_TEXT in node.attrib:
                return node.attrib[self.A_TEXT]
            else:
                return None

    def set_node_style_by_id(self, id, style):
        """

        :param id:
        :param style:
        :return:
        """

        if style in self.V_ALLOWED_STYLE:

            node = self.get_node_by_id(id)

            if node is None:
                raise self.FreeplaneNodeNotExisting
            else:
                if style == self.V_STYLE_DEFAULT:
                    if self.A_STYLE in node.attrib:
                        del node.attrib[self.A_STYLE]
                else:
                    node.set(self.A_STYLE, style)

        else:
            raise self.FreeplaneBadValueForStyleError

    def get_node_style_by_id(self, node_id):
        """

        :param node_id:
        :return:
        """

        node = self.get_node_by_id(node_id)

        if node is None:
            raise self.FreeplaneNodeNotExisting
        else:
            if self.A_STYLE in node.attrib:
                return node.attrib[self.A_STYLE]
            else:
                return self.V_STYLE_DEFAULT

    def add_node_by_id(self, parent_node, node_id=None):
        self.create_basic_node(self.xml_root_element, parent_node, node_id)

    def get_node_by_id(self, node_id):
        xpathstring = self.create_xpathstring_for_id(node_id)
        xmatch = self.root_node.findall(xpathstring)

        if len(xmatch) == 0:
            return None
        elif len(xmatch) == 1:
            return xmatch[0]
        else:
            raise self.FreeplaneIDNotUniqueError

    def add_node_note_by_id(self, node_id, note_text):
        """

        :param node_id:
        :param note_text:
        :return:
        """

        node = self.get_node_by_id(node_id)

        if node is None:
            raise self.FreeplaneNodeNotExisting
        else:
            # Check if node already has a note
            richcontent_node = node.find(self.T_RICHCONTENT)
            if richcontent_node is None:
                richcontent_node = SubElement(node, self.T_RICHCONTENT)
                richcontent_node.set(self.A_TYPE, self.V_TYPE_NOTE)

            # Raw text is crashing freeplane.  Will try to wrap the note in an HTML document

            local_html_doc = Element('html')
            head = SubElement(local_html_doc, 'head')
            body = SubElement(local_html_doc, 'body')

            # Remove rogue bracket < >
            note_text = note_text.replace('&', '&amp;')
            note_text = note_text.replace('<', '&lt;')
            note_text = note_text.replace('>', '&gt;')

            data = '<p>%s</p>' % note_text.replace('\n', '<br />')
            # print(data)
            p = fromstring(data)
            body.append(p)

            richcontent_node.insert(1, local_html_doc)

    def set_attribute_by_id(self, node_id, attribute_name=None, attribute_value=None, attribute_dict=None):
        node = self.get_node_by_id(node_id)

        if node is None:
            raise self.FreeplaneNodeNotExisting
        else:
            if attribute_dict is None and attribute_name is not None and attribute_value is not None:
                attributes = node.findall(self.T_ATTRIBUTE)

                if len(attributes) == 0:
                    # No attributes exists on the node. We need to create a new node
                    new_attribute_node = SubElement(node, self.T_ATTRIBUTE)
                    new_attribute_node.set(self.A_NAME, attribute_name)
                else:
                    # Check all attribute to see if one matches the "attribute_name"
                    for atrb in attributes:
                        if atrb.attrib[self.A_NAME] == attribute_name:
                            new_attribute_node = atrb
                            break

                if 'new_attribute_node' not in locals():
                    # Condition where there is already attributes, but none matches "attribute_name"
                    new_attribute_node = SubElement(node, self.T_ATTRIBUTE)
                    new_attribute_node.set(self.A_NAME, attribute_name)

                new_attribute_node.set(self.A_VALUE, attribute_value)

            elif attribute_name is None and attribute_value is None and attribute_dict is not None:
                if isinstance(attribute_dict, dict):
                    for key in attribute_dict:
                        self.set_attribute_by_id(node_id, attribute_name=key, attribute_value=attribute_dict[key])
                else:
                    raise self.FreeplaneExpectedDictionnary

            else:
                raise self.FreeplaneInconsistentParameterPassed

    def get_attribute_by_id(self, node_id, attribute_name=None):
        results = {}
        node = self.get_node_by_id(node_id)

        if node is None:
            raise self.FreeplaneNodeNotExisting
        else:
            attributes = node.findall(self.T_ATTRIBUTE)

            if len(attributes) == 0:
                return None
            else:
                for atrb in attributes:
                    if attribute_name is None:
                        results[atrb.attrib[self.A_NAME]] = atrb.attrib[self.A_VALUE]
                    elif atrb.attrib[self.A_NAME] == attribute_name:
                        results[atrb.attrib[self.A_NAME]] = atrb.attrib[self.A_VALUE]

            return results

    def set_node_position_by_id(self, node_id, position):

        if position in self.V_ALLOWED_POSITION:
            node = self.get_node_by_id(node_id)

            if node is None:
                raise self.FreeplaneNodeNotExisting
            else:
                if position == self.V_POSITION_DEFAULT:
                    if self.A_POSITION in node.attrib:
                        del node.attrib[self.A_POSITION]
                else:
                    node.set(self.A_POSITION, position)
        else:
            raise self.FreeplaneBadValueForPosition

    def get_node_position_by_id(self, node_id):
        node = self.get_node_by_id(node_id)

        if node is None:
            raise self.FreeplaneNodeNotExisting
        else:
            if self.A_POSITION in node.attrib:
                return node.attrib[self.A_POSITION]
            else:
                return self.V_POSITION_DEFAULT

    class FreeplaneError(Exception):
        pass

    class FreeplaneIDNotUniqueError(FreeplaneError):
        """
        Will be raised if a xpath search with an ID criteria returns more than one value

        :param expression -- input expression in which the error occured
        :param message -- explanation of the error
        """

    class FreeplaneNoSuchAttribute(FreeplaneError):
        """
        Will be raise if trying to access an attribute not existing on a particular node
        """

    class FreeplaneBadValueForStyleError(FreeplaneError):
        """
        Will be raised when trying to assign a bad value for the attribute Style
        """

    class FreeplaneBadValueForPosition(FreeplaneError):
        """
        Will be raise if trying to assign a vad value for the Position attribute
        """

    class FreeplaneIDAlreadyExist(FreeplaneError):
        """
        Will be raised if we are trying to assign an id that already exists
        """
        #
        # def __init__(self, expression, message):
        #     self.expression = expression
        #     self.message = message

    class FreeplaneNodeNotExisting(FreeplaneError):
        """
        Will be raised if we are trying to assign an id that already exists
        """

    class FreeplaneExpectedDictionnary(FreeplaneError):
        """
        Will be raised if a dictionary was expected but not passed
        """

    class FreeplaneInconsistentParameterPassed(FreeplaneError):
        """
        WIll be rased if inconsistent parameter are passed
        """

    # Tag Constants
    T_MAP = "map"
    T_NODE = "node"
    T_RICHCONTENT = "richcontent"
    T_ATTRIBUTE = "attribute"

    # Attributes Constant
    A_ID = "ID"
    A_LOCALIZED_TEXT = "LOCALIZED_TEXT"
    A_TEXT = "TEXT"
    A_STYLE = "STYLE"
    A_CREATED = "CREATED"
    A_MODIFIED = "MODIFIED"
    A_TYPE = "TYPE"
    A_HIDDEN = "HIDDEN"
    A_NAME = 'NAME'
    A_VALUE = "VALUE"
    A_POSITION = "POSITION"

    # Value Constant
    V_MAP_VERSION = "freeplane 1.6.0"
    V_NEW_MINDMAP = "new_mindmap"

    V_STYLE_FORK = "fork"
    V_STYLE_BUBBLE = "bubble"
    V_STYLE_DEFAULT = "default"  # Special case where the STYLE attribute must be deleted
    V_ALLOWED_STYLE = [V_STYLE_BUBBLE, V_STYLE_DEFAULT, V_STYLE_FORK]

    V_TYPE_NOTE = 'NOTE'
    V_TYPE_DETAILS = 'DETAILS'

    V_HIDDEN_TRUE = "TRUE"
    V_HIDDEN_FALSE = "FALSE"

    V_POSITION_LEFT = 'left'
    V_POSITION_RIGHT = 'right'
    V_POSITION_DEFAULT = 'default'
    V_ALLOWED_POSITION = [V_POSITION_LEFT, V_POSITION_RIGHT, V_POSITION_DEFAULT]

    def create_xpathstring_for_id(self, id):
        if id == "root":
            xpathstring = "."
        else:
            # Find node by ID
            xpathstring = './/*[@' + self.A_ID + '="' + id + '"]'

        return xpathstring

    def create_basic_node(self, root_node, parent_node, node_id=None, localized_text=None):
        new_node = SubElement(parent_node, self.T_NODE)
        if node_id is None:
            new_node.set(self.A_ID, uuid.uuid4().hex)
        else:
            xpathstring = self.create_xpathstring_for_id(node_id)
            xmatch = root_node.findall(xpathstring)

            if len(xmatch) == 0:
                new_node.set(self.A_ID, node_id)
            else:
                raise self.FreeplaneIDAlreadyExist

        if localized_text is not None:
            new_node.set(self.A_LOCALIZED_TEXT, localized_text)

        time_stamp = str(self.current_milli_time())
        new_node.set(self.A_CREATED, time_stamp)
        new_node.set(self.A_MODIFIED, time_stamp)

        return new_node

    def current_milli_time(self):
        return int(round(time.time() * 1000))