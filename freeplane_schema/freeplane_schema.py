import os
import logging
import uuid
import time
import json
import hashlib

from xml.etree.ElementTree import Element, SubElement, ElementTree, parse, fromstring, tostring


class FreeplaneSchema(object):
    """
    classdocs

    Node tag
        LOCALIZED_TEXT: Refers to predefined/internal value
            eg.: 'new_mindmap' will be displayed as "New Mindmap" if the UI is in English

        TEXT: User defined text string
    """

    def __init__(self, mapstyle_file=None, inherited_logger=None):
        """
        Upon init, will create a new document
        """

        self._logger = (inherited_logger or self._build_logger())
        self.logger.debug('INIT: Current working directory is:\t{0}'.format(os.getcwd()))
        self.logger.debug('INIT: Class definition file:\t\t\t{0}'.format(os.path.dirname(os.path.realpath(__file__))))

        if mapstyle_file is None:
            # TODO: Correct this default location which seems to not be working when used as a module
            self.mapstyle_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                              "resources",
                                              "mapstyles.xml")
        else:
            self.mapstyle_file = mapstyle_file

        self.logger.debug('INIT: Mapstyle location:\t\t\t\t{0}'.format(os.path.join(os.getcwd(), self.mapstyle_file)))

        self.xml_root_element = Element(self.T_MAP, version=self.V_MAP_VERSION)
        self.root_node = self.create_basic_node(self.xml_root_element, self.xml_root_element)
        # TODO do not automaticall create a node with a gnenerated id upon initiatilzation of this class

    @property
    def logger(self):
        return self._logger

    def _build_logger(self):
        logger = logging.getLogger(self.__module__)
        logger.addHandler(logging.NullHandler())
        return logger

    def write_document(self, filename, pretty_print_it = False, add_map_styles=False):
        """

        :param filename:
        :return:
        """

        self.logger.debug('write_document:\tfilename: {0}\n'
                          '\t\t\t\t\t\t\t\t\t\t\t\tpretty_print_it: {1}\n'
                          '\t\t\t\t\t\t\t\t\t\t\t\tadd_map_style: {2}'.format(filename,pretty_print_it,add_map_styles))
        temp_xml_root = self.xml_root_element

        if add_map_styles:
            hook_node = parse(self.mapstyle_file).getroot()
            self.root_node.append(hook_node)

        if pretty_print_it:
            self.indent(temp_xml_root, 0)

        ElementTree(temp_xml_root).write(file_or_filename=filename)

    def read_document(self, filename):
        """

        :param filename:
        :return:
        """
        self.temp_xml_root_element = parse(filename).getroot()

        is_a_true_freeplane_file = False

        # TODO: Make a real check on the freeplane file format
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

    def get_node_by_id(self, node_id) -> Element:
        """

        :param node_id: Unique identifier used to find the node.
        :return: ElementTree.Element object
        """
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

            # TODO Add case where a not already exist

            # Raw text is crashing freeplane.  Will try to wrap the note in an HTML document

            local_html_doc = Element('html')
            head = SubElement(local_html_doc, 'head')
            body = SubElement(local_html_doc, 'body')

            # Remove rogue bracket < >
            note_text = note_text.replace('&', '&amp;')
            note_text = note_text.replace('<', '&lt;')
            note_text = note_text.replace('>', '&gt;')

            data = '<p>%s</p>' % note_text.replace('\n', '<br />')

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

    class FreeplaneExpectedParentNode(FreeplaneError):
        """
        Will be raised if we try to create a node without specifying the parent
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
        if parent_node is None:
            raise self.FreeplaneExpectedParentNode

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

    @staticmethod
    def current_milli_time():
        return int(round(time.time() * 1000))

    @staticmethod
    def get_node_children(root_node):
        return tuple(root_node.iter())

    def create_stable_hashable_node_representation(self, my_node: Element, include_note=False) -> str:
        d = my_node.attrib
        if include_note:
            if self.node_contains_note(my_node):
                d['zzNote'] = self.get_note_content_string(my_node)

        return json.dumps(d, sort_keys=True, ensure_ascii=True)

    @staticmethod
    def create_hash_from_representation(rep: str) -> str:
        m = hashlib.sha1()
        m.update(rep.encode())
        return m.hexdigest()

    def node_contains_note(self, my_node: Element) -> bool:
        return my_node.find(self.T_RICHCONTENT) is not None

    def get_note_content_string(self, my_node) -> str:
        return self.get_note_content_bytes(my_node).decode()

    def get_note_content_bytes(self, my_node) -> bytes:
        if self.node_contains_note(my_node):
            note = my_node.find(self.T_RICHCONTENT)
            return tostring(note)
        else:
            # TODO put an exception here
            return None

    def compute_node_hash(self, seed_node, include_note=True):
        all_hashes = dict()
        id_set = set()
        children_node = self.get_node_children(seed_node)
        for elem in children_node:
            if elem.tag == self.T_NODE:
                rep = self.create_stable_hashable_node_representation(elem, include_note=include_note)
                hashed_rep = self.create_hash_from_representation(rep)

                all_hashes[elem.attrib[self.A_ID]] = (elem, hashed_rep)
                id_set = set(all_hashes.keys())

        return all_hashes, id_set


    def indent(self, elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i