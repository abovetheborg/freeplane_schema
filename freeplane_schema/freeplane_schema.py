import os
import logging
import uuid
import time
import json
import hashlib


from lxml import etree as ET
from lxml.html import etree as ETH

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

        self.xml_root_element = ET.Element(self.T_MAP, version=self.V_MAP_VERSION)
        self.root_node = self.create_basic_node(self.xml_root_element, self.xml_root_element)
        # TODO do not automaticall create a node with a gnenerated id upon initiatilzation of this class

        self.document_compare_report = list()

    @property
    def logger(self):
        return self._logger

    @property
    def compare_report_available(self):
        return not (self.document_compare_report is None or len(self.document_compare_report) == 0)

    @property
    def list_of_identical_nodes(self):
        identical_nodes = self._list_of_node_per_diff_status(self.V_DIFF_IDENTICAL)
        return identical_nodes

    @property
    def list_of_modified_nodes(self):
        modified_nodes = self._list_of_node_per_diff_status(self.V_DIFF_MODIFIED)
        return modified_nodes

    @property
    def list_of_deleted_nodes(self):
        deleted_nodes = self._list_of_node_per_diff_status(self.V_DIFF_DELETED)
        return deleted_nodes

    @property
    def list_of_not_checked_nodes(self):
        unchecked_nodes = self._list_of_node_per_diff_status(self.V_DIFF_NOT_CHECKED)
        return unchecked_nodes

    def _list_of_node_per_diff_status(self, status):
        if status in self.V_VALID_DIFF_STATUS:
            self.logger.debug('_list_of_node_per_diff_status: Extracting for {0}'.format(status))
            if self.compare_report_available:
                self.logger.debug('_list_of_node_per_diff_status: Compare report exists and parsing it')
                list_of_nodes = list()
                for ndr in self.document_compare_report:
                    self.logger.debug(
                        '_list_of_node_per_diff_status: Parsing report for node_id: {0}'.format(ndr[self.K_NODE_ID]))
                    if ndr[self.K_DIFF_TYPE] == status:
                        self.logger.debug(
                            '_list_of_node_per_diff_status: {0} is {1}'.format(ndr[self.K_NODE_ID], status))
                        list_of_nodes.append(ndr)
                    else:
                        self.logger.debug(
                            'list_of_identical_node: node_id: {0} is NOT {1}'.format(ndr[self.K_NODE_ID], status))

                return list_of_nodes

            else:
                raise self.FreeplaneCompareReportNotAvailable
        else:
            raise self.FreeplaneDiffStatusNotValid

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
            hook_node = ET.parse(self.mapstyle_file).getroot()
            self.root_node.append(hook_node)

        if pretty_print_it:
            self.indent(temp_xml_root, 0)
        ET.ElementTree(temp_xml_root).write(filename)

    def read_document(self, filename):
        """

        :param filename:
        :return:
        """
        self.temp_xml_root_element = ET.parse(filename).getroot()

        is_a_true_freeplane_file = False

        # TODO: Make a real check on the freeplane file format
        if True:
            is_a_true_freeplane_file = True

        if is_a_true_freeplane_file:
            self.xml_root_element = self.temp_xml_root_element
            self.root_node = self.xml_root_element.findall(self.T_NODE)[0]
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

    def get_node_by_id(self, node_id) -> ET.Element:
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

    def get_node_note_by_id(self, node_id=None):
        node = self.get_node_by_id(node_id)

        if node is None:
            raise self.FreeplaneNodeNotExisting
        else:
            richcontent_node = node.find(self.T_RICHCONTENT)
            if richcontent_node is None:
                self.logger.debug('get_node_note_by_id: No richcontent tag under {0}'.format(node_id))
                a = None
            else:
                if self.A_TYPE in richcontent_node.attrib:
                    if richcontent_node.attrib[self.A_TYPE] == self.V_TYPE_NOTE:
                        note_elements = richcontent_node.find('html')
                        a = ETH.tostring(note_elements)
                    else:
                        self.logger.debug(
                            'get_node_note_by_id: richcontent tag under {0} is not of type note'.format(node_id))
                        a = None
                else:
                    self.logger.debug('get_node_note_by_id: richencontent tag exists but no type defined')
                    raise self.FreeplaneRichContentTagNotProperlyDefined

        if a is not None:
            a = a.decode('ascii')
        return a

    def set_node_note_by_id(self, node_id, note_text):
        """

        :param node_id:
        :param note_text:
        :return:
        """

        node = self.get_node_by_id(node_id)

        if node is None:
            raise self.FreeplaneNodeNotExisting
        else:
            if self.get_node_note_by_id(node_id) is None:
                self.logger.debug('set_node_note_by_id: No Note find under {0}.  Creating one now...'.format(node_id))
            else:
                self.logger.debug('set_node_note_by_id: Note exist under {0} and will override it'.format(node_id))
                richcontent_node = node.find(self.T_RICHCONTENT)
                node.remove(richcontent_node)
                del richcontent_node

            richcontent_node = ET.SubElement(node, self.T_RICHCONTENT)
            richcontent_node.set(self.A_TYPE, self.V_TYPE_NOTE)

            if self._string_is_valid_html(note_text):
                local_html_doc = ETH.fromstring(note_text)
            else:

                # Raw text is crashing freeplane.  Will try to wrap the note in an HTML document

                local_html_doc = ET.Element('html')
                head = ET.SubElement(local_html_doc, 'head')
                body = ET.SubElement(local_html_doc, 'body')

                # Sanitize: Remove rogue bracket < >
                note_text = note_text.replace('&', '&amp;')
                note_text = note_text.replace('<', '&lt;')
                note_text = note_text.replace('>', '&gt;')

                data = '<p>%s</p>' % note_text.replace('\n', '<br />')

                p = ET.fromstring(data)
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
                    new_attribute_node = ET.SubElement(node, self.T_ATTRIBUTE)
                    new_attribute_node.set(self.A_NAME, attribute_name)
                else:
                    # Check all attribute to see if one matches the "attribute_name"
                    for atrb in attributes:
                        if atrb.attrib[self.A_NAME] == attribute_name:
                            new_attribute_node = atrb
                            break

                if 'new_attribute_node' not in locals():
                    # Condition where there is already attributes, but none matches "attribute_name"
                    new_attribute_node = ET.SubElement(node, self.T_ATTRIBUTE)
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

    def compare_against_reference_document(self, other, test_node_text=False, test_node_note=False):
        if not isinstance(other, self.__class__):
            raise self.FreeplaneObjectNotFreeplaneDocument

        self._clear_compare_report()

        list1 = [self.get_node_by_id('root')]
        list2 = [other.get_node_by_id('root')]
        list_of_ndr = []

        node1 = None
        node2 = None

        treated_node1 = []
        modified_node1 = []
        in_structure1_only = []

        modified_node2 = []
        in_structure2_only = []

        while len(list1) > 0:
            self.logger.debug('compare_against_reference: --- Start of list1 iteration ---')
            self.logger.debug('compare_against_reference: length of list1:\t\t\t{0}'.format(len(list1)))
            self.logger.debug('compare_against_reference: length of list2:\t\t\t{0}'.format(len(list2)))

            node1 = list1.pop()
            # Append children of node 1 to list1
            list1 = list1 + self.get_node_immediate_children(node1)
            if node1.tag == self.T_NODE:
                self.logger.debug('compare_against_reference: Element is a node, proceeding with iteration')
                pass
            else:
                self.logger.debug('compare_against_reference: Element is NOT a node... skipping iteration')
                continue

            # Add node1 to treated_node1
            treated_node1.append(node1.attrib[self.A_ID])
            self.logger.debug('compare_against_reference: length of treated_node1:\t{0}'.format(len(treated_node1)))

            # Look for node1 in other object
            node2 = other.get_node_by_id(node1.attrib[self.A_ID])

            if node2 is None:
                self.logger.debug('compare_against_reference: node1 not present in reference document -> new node')
                # Exists in 1 but not in 2 -> implies new node
                in_structure1_only.append(node1.attrib[self.A_ID])
                ndr = self.create_node_diff_report_for_new(node1.attrib[self.A_ID])
            else:
                self.logger.debug(
                    'compare_against_reference: node1 present in reference document -> modified/identical')
                # Exists in 1 and 2 -> Can either be a modified or not
                ndr = self.compare_node(node1, node2, test_node_text=test_node_text, test_node_note=test_node_note)

                if ndr[self.K_DIFF_TYPE] == self.V_DIFF_MODIFIED:
                    self.logger.debug('compare_against_reference: node1 is modified compared to node2')
                    modified_node1.append(node1.attrib[self.A_ID])
                elif ndr[self.K_DIFF_TYPE] == self.V_DIFF_IDENTICAL:
                    self.logger.debug('compare_against_reference: node1 is identical to node2')
                    pass
                elif ndr[self.K_DIFF_TYPE] == self.V_DIFF_NOT_CHECKED:
                    self.logger.debug('compare_against_reference: Could not conclude with current tests')
                    # This condition shouldn't be hit once a proper implementation of compare_node is done
                    pass

                list_of_ndr.append(ndr)

        node1 = None
        node2 = None

        while len(list2) > 0:
            self.logger.debug('compare_against_reference: --- Start of list2 iteration ---')
            self.logger.debug('compare_against_reference: length of list1:\t\t\t{0}'.format(len(list1)))
            self.logger.debug('compare_against_reference: length of list2:\t\t\t{0}'.format(len(list2)))

            node2 = list2.pop()
            if node2.tag == self.T_NODE:
                self.logger.debug('compare_against_reference: Element is a node, proceeding with iteration')
                pass
            else:
                self.logger.debug('compare_against_reference: Element is NOT a node... skipping iteration')
                continue

            list2 = list2 + other.get_node_immediate_children(node2)

            if node2.attrib[other.A_ID] in treated_node1:
                self.logger.debug(
                    'compare_against_reference: node2 already treated in node1 iteration... skipping iteration')
                continue

            node1 = self.get_node_by_id(node2.attrib[self.A_ID])

            if node1 is None:
                self.logger.debug('compare_against_reference: node2 not present in this document -> deleted node')
                # exists in 2 but not in 1 -> implies a deleted node
                in_structure2_only.append(node2.attrib[other.A_ID])
                ndr = self.create_node_diff_report_for_deleted(node2.attrib[other.A_ID])
            else:
                # We shouldn't have a else here. The thing should blow up
                raise

            list_of_ndr.append(ndr)

        self.document_compare_report = list_of_ndr
        pass

    def _clear_compare_report(self):
        self.logger.debug(
            '_clear_compare_report: Report contains {0} element(s)'.format(len(self.document_compare_report)))
        self.document_compare_report = list()

    def initialize_diff_report_for_node_id(self, node_id):
        node_diff_report = {self.K_NODE_ID: node_id,
                            self.K_DIFF_TYPE: self.V_DIFF_NOT_CHECKED,
                            self.K_CHECK_METHODS: []}
        return node_diff_report

    def create_node_diff_report_for_new(self, node_id):
        node_diff_report = self.initialize_diff_report_for_node_id(node_id=node_id)
        node_diff_report[self.K_DIFF_TYPE] = self.V_DIFF_NEW
        return node_diff_report

    def create_node_diff_report_for_deleted(self, node_id):
        node_diff_report = self.initialize_diff_report_for_node_id(node_id=node_id)
        node_diff_report[self.K_DIFF_TYPE] = self.V_DIFF_DELETED
        return node_diff_report

    def compare_node(self, node1, node2, test_node_text=False, test_node_note=False):
        if node1.attrib[self.A_ID] != node2.attrib[self.A_ID]:
            raise self.FreeplaneCannotCompareNodeWithDifferentID

        test_excerpt = dict()
        # CONSTANTS
        TEST_NAME_NODE_TEXT = 'node_text'
        TEST_NAME_NODE_NOTE = 'node_note'

        self.logger.debug('compare_node: Initializing node diff report')
        node_diff_report = self.initialize_diff_report_for_node_id(node_id=node1.attrib[self.A_ID])

        is_identical = None

        if test_node_text:
            self.logger.debug('compare_node: --- Testing for text difference ---')
            # Condition to run test:
            #   - At least one node has the TEXT attribute.  If one doesn't, they are deemed different
            if self.A_TEXT in node1.attrib and self.A_TEXT in node2.attrib:
                self.logger.debug('compare_node: Both node have TEXT attribute')
                if is_identical is None:
                    self.logger.debug('compare_node: is_identical was None')
                    is_identical = True
                is_identical = is_identical & self.diff_node_text(node1, node2)
                self.logger.debug('compare_node: is_identical is now: {0}'.format(is_identical))
                test_excerpt[TEST_NAME_NODE_TEXT] = self.V_DIFF_TEST_EXECUTED
                self.logger.debug('compare_node: test_excerpt is now: {0}'.format(test_excerpt))
            elif not (self.A_TEXT in node1.attrib and self.A_TEXT in node2.attrib):
                # Test cannot execute
                test_excerpt[TEST_NAME_NODE_TEXT] = self.V_DIFF_TEST_ATTEMPTED_CONDITIONS_NOT_MET
                self.logger.debug('compare_node: test_excerpt is now: {0}'.format(test_excerpt))
            else:
                is_identical = False
                test_excerpt[TEST_NAME_NODE_TEXT] = self.V_DIFF_TEST_EXECUTED
                self.logger.debug('compare_node: test_excerpt is now: {0}'.format(test_excerpt))
        else:
            self.logger.debug('compare_node: --- NOT Testing for text difference ---')
            test_excerpt[TEST_NAME_NODE_TEXT] = self.V_DIFF_TEST_NOT_ATTEMPTED
            self.logger.debug('compare_node: test_excerpt is now: {0}'.format(test_excerpt))

        if test_node_note:
            self.logger.debug('compare_node: --- Testing for note difference ---')
            # Condition to run test:
            #   - At least one node has the 'richcontent' tag with a TYPE=NOTE attribute.
            #   If one doesn't, they are deemed different
            # book[@location='US']
            xpathstring = self.T_RICHCONTENT + '[@' + self.A_TYPE + '="' + self.V_TYPE_NOTE + '"]'
            richcontent_node1 = node1.find(xpathstring)
            richcontent_node2 = node2.find(xpathstring)

            if richcontent_node1 is not None and richcontent_node2 is not None:
                self.logger.debug('compare_node: Both node have a note')
                if is_identical is None:
                    self.logger.debug('compare_node: is_identical was None')
                    is_identical = True
                is_identical = is_identical & self.diff_node_note(richcontent_node1, richcontent_node2)
                self.logger.debug('compare_node: is_identical is now: {0}'.format(is_identical))
                test_excerpt[TEST_NAME_NODE_NOTE] = self.V_DIFF_TEST_EXECUTED
                self.logger.debug('compare_node: test_excerpt is now: {0}'.format(test_excerpt))
            elif richcontent_node1 is None and richcontent_node2 is None:
                # Test cannot execute
                test_excerpt[TEST_NAME_NODE_NOTE] = self.V_DIFF_TEST_ATTEMPTED_CONDITIONS_NOT_MET
                self.logger.debug('compare_node: test_excerpt is now: {0}'.format(test_excerpt))
            else:
                is_identical = False
                test_excerpt[TEST_NAME_NODE_NOTE] = self.V_DIFF_TEST_EXECUTED
                self.logger.debug('compare_node: test_excerpt is now: {0}'.format(test_excerpt))
        else:
            self.logger.debug('compare_node: --- NOT Testing for note difference ---')
            test_excerpt[TEST_NAME_NODE_NOTE] = self.V_DIFF_TEST_NOT_ATTEMPTED
            self.logger.debug('compare_node: test_excerpt is now: {0}'.format(test_excerpt))

        node_diff_report[self.K_CHECK_METHODS].append(test_excerpt)

        if is_identical is None:
            node_diff_report[self.K_DIFF_TYPE] = self.V_DIFF_NOT_CHECKED
        elif is_identical:
            node_diff_report[self.K_DIFF_TYPE] = self.V_DIFF_IDENTICAL
        else:
            node_diff_report[self.K_DIFF_TYPE] = self.V_DIFF_MODIFIED

        return node_diff_report

    def diff_node_text(self, node1, node2):
        return node1.attrib[self.A_TEXT] == node2.attrib[self.A_TEXT]

    def diff_node_note(self, richcontent_node1, richconente_node2):
        text1 = ET.tostring(richcontent_node1)
        text2 = ET.tostring(richconente_node2)
        self.logger.debug('diff_node_note: node1 note is: {0}'.format(text1))
        self.logger.debug('diff_node_note: node2 note is: {0}'.format(text2))
        return text1 == text2

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

    class FreeplaneObjectNotFreeplaneDocument(FreeplaneError):
        """
        Will be raised if we expected a FreeplaneSchema instance and we didn't receive one
        """

    class FreeplaneCannotCompareNodeWithDifferentID(FreeplaneError):
        """
        Will be raised when a request or node compare is done agains two nodes with different ID.
        The whole code works on the assumption that ID are unique
        """

    class FreeplaneCompareReportNotAvailable(FreeplaneError):
        """
        Will be raised when a request for compare report element is done without a compare report available
        """

    class FreeplaneDiffStatusNotValid(FreeplaneError):
        """
        Will be raised when attemptig to use a invalid diff status
        """

    class FreeplaneRichContentTagNotProperlyDefined(FreeplaneError):
        """
        Will be raised when the richcontent tag doesn't havbe a TYPE attribute set
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

    # Import dictionary keys
    K_NODE_ID = 'node_id'
    K_DIFF_TYPE = 'diff_type'
    K_CHECK_METHODS = 'check_methods'

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

    V_DIFF_NOT_CHECKED = 'not_checked'
    V_DIFF_NEW = 'new'
    V_DIFF_MODIFIED = 'modified'
    V_DIFF_DELETED = 'deleted'
    V_DIFF_IDENTICAL = 'identical'

    V_VALID_DIFF_STATUS = [V_DIFF_NOT_CHECKED, V_DIFF_NEW, V_DIFF_MODIFIED, V_DIFF_DELETED, V_DIFF_IDENTICAL]

    V_DIFF_TEST_NOT_ATTEMPTED = 'NOT ATTEMPTED'
    V_DIFF_TEST_ATTEMPTED_CONDITIONS_NOT_MET = 'ATTEMPTED BUT CONDITIONS NOT MET'
    V_DIFF_TEST_EXECUTED = 'EXECUTED'

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

        new_node = ET.SubElement(parent_node, self.T_NODE)
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
    def get_node_immediate_children(root_node):
        return root_node.getchildren()

    def node_contains_note(self, my_node: ET.Element) -> bool:
        return my_node.find(self.T_RICHCONTENT) is not None

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

    def _string_is_valid_html(self, string):
        try:
            a = ETH.fromstring(string).find('.//*') is not None
            self.logger.debug('_string_is_valid_html: The string is recognized as HTML')
        except ET.XMLSyntaxError as e:
            self.logger.debug('_string_is_valid_html: The string is NOT recognized as HTML')
            a = False
        return a
