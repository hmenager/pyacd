"""
The acd module defines an object model for ACD files contents
"""
# pylint: disable=too-few-public-methods, missing-docstring
import sys
import os
import copy

import ruamel.yaml as yaml
import six

SEQUENCE_FORMATS = {
    'abi': {'try': True,
            'Nuc': True,
            'Pro': True,
            'Feat': False,
            'Gap': True,
            'Mset': False,
            'description': 'ABI trace file',
            'input': True},
    'acedb': {'try': True,
              'Nuc': True,
              'Pro': True,
              'Feat': False,
              'Gap': True,
              'Mset': False,
              'description': 'ACEDB sequence format',
              'input': True,
              'output': True,
              'Sngl': False,
              'Save': False},
    'asn1': {'Nuc': True,
             'Pro': True,
             'Feat': False,
             'Gap': True,
             'Mset': False,
             'description': 'NCBI ASN.1 format',
             'input': True,
             'output': True,
             'Sngl': False,
             'Save': False},
    'clustal': {'try': True,
                'Nuc': True,
                'Pro': True,
                'Feat': False,
                'Gap': True,
                'Mset': False,
                'description': 'Clustalw output format',
                'input': True,
                'output': True,
                'Sngl': False,
                'Save': True},
    'codata': {'try': True,
               'Nuc': True,
               'Pro': True,
               'Feat': True,
               'Gap': True,
               'Mset': False,
               'description': 'CODATA entry format',
               'input': True,
               'output': True,
               'Sngl': False,
               'Save': False},
    'das': {'Nuc': True,
            'Pro': True,
            'Feat': False,
            'Gap': True,
            'Mset': False,
            'description': 'DASSEQUENCE DAS any sequence',
            'input': False,
            'output': True,
            'Sngl': False,
            'Save': False},
    'dasdna': {'Nuc': True,
               'Pro': False,
               'Feat': False,
               'Gap': True,
               'Mset': False,
               'description': 'DASDNA DAS nucleotide-only sequence',
               'input': False,
               'output': True,
               'Sngl': False,
               'Save': False},
    'dbid': {'try': False,
             'Nuc': True,
             'Pro': True,
             'Feat': False,
             'Gap': True,
             'Mset': False,
             'description':
             'FASTA format variant with database name before ID'},
    'embl': {'try': True,
             'Nuc': True,
             'Pro': False,
             'Feat': True,
             'Gap': True,
             'Mset': False,
             'description': 'EMBL entry format'},
    'experiment': {'try': True,
                   'Nuc': True,
                   'Pro': True,
                   'Feat': False,
                   'Gap': True,
                   'Mset': False,
                   'description': 'Staden experiment file'},
    'fasta': {'try': True,
              'Nuc': True,
              'Pro': True,
              'Feat': False,
              'Gap': True,
              'Mset': False,
              'description': 'FASTA format including NCBI-style IDs'},
    'fastq': {'try': True,
              'Nuc': True,
              'Pro': False,
              'Feat': False,
              'Gap': False,
              'Mset': False,
              'description':
              'Fastq short read format ignoring quality scores'},
    'fastq-illumina': {'try': False,
                       'Nuc': True,
                       'Pro': False,
                       'Feat': False,
                       'Gap': False,
                       'Mset': False,
                       'description': 'Fastq Illumina 1.3 short read format'},
    'fastq-sanger': {'try': False,
                     'Nuc': True,
                     'Pro': False,
                     'Feat': False,
                     'Gap': False,
                     'Mset': False,
                     'description':
                     'Fastq short read format with Phred quality'},
    'fastq-solexa': {'try': False,
                     'Nuc': True,
                     'Pro': False,
                     'Feat': False,
                     'Gap': False,
                     'Mset': False,
                     'description':
                     'Fastq Solexa/Illumina 1.0 short read format'},
    'fitch': {'try': True,
              'Nuc': True,
              'Pro': True,
              'Feat': False,
              'Gap': True,
              'Mset': False,
              'description': 'Fitch program format'},
    'gcg': {'try': True,
            'Nuc': True,
            'Pro': True,
            'Feat': False,
            'Gap': True,
            'Mset': False,
            'description': 'GCG sequence format'},
    'genbank': {'try': True,
                'Nuc': True,
                'Pro': False,
                'Feat': True,
                'Gap': True,
                'Mset': False,
                'description': 'Genbank entry format'},
    'genpept': {'try': False,
                'Nuc': False,
                'Pro': True,
                'Feat': True,
                'Gap': True,
                'Mset': False,
                'description': 'Refseq protein entry format (alias)'},
    'gff2': {'try': True,
             'Nuc': True,
             'Pro': True,
             'Feat': True,
             'Gap': True,
             'Mset': False,
             'description': 'GFF feature file with sequence in the header'},
    'gff3': {'try': True,
             'Nuc': True,
             'Pro': True,
             'Feat': True,
             'Gap': True,
             'Mset': False,
             'description': 'GFF3 feature file with sequence'},
    'gifasta': {'try': False,
                'Nuc': True,
                'Pro': True,
                'Feat': False,
                'Gap': True,
                'Mset': False,
                'description':
                'FASTA format including NCBI-style GIs (alias)'},
    'hennig86': {'try': True,
                 'Nuc': True,
                 'Pro': True,
                 'Feat': False,
                 'Gap': True,
                 'Mset': False,
                 'description': 'Hennig86 output format'},
    'ig': {'try': False,
           'Nuc': True,
           'Pro': True,
           'Feat': False,
           'Gap': True,
           'Mset': False,
           'description': 'Intelligenetics sequence format'},
    'igstrict': {'try': True,
                 'Nuc': True,
                 'Pro': True,
                 'Feat': False,
                 'Gap': True,
                 'Mset': False,
                 'description':
                 'Intelligenetics sequence format strict parser'},
    'jackkniffer': {'try': True,
                    'Nuc': True,
                    'Pro': True,
                    'Feat': False,
                    'Gap': True,
                    'Mset': False,
                    'description':
                    'Jackknifer interleaved and non-interleaved formats'},
    'mase': {'try': False,
             'Nuc': True,
             'Pro': True,
             'Feat': False,
             'Gap': True,
             'Mset': False,
             'description': 'MASE program format'},
    'mega': {'try': True,
             'Nuc': True,
             'Pro': True,
             'Feat': False,
             'Gap': True,
             'Mset': False,
             'description': 'MEGA interleaved and non-interleaved formats'},
    'msf': {'try': True,
            'Nuc': True,
            'Pro': True,
            'Feat': False,
            'Gap': True,
            'Mset': False,
            'description': 'GCG MSF (multiple sequence file) file format'},
    'nbrf': {'try': True,
             'Nuc': True,
             'Pro': True,
             'Feat': True,
             'Gap': True,
             'Mset': False,
             'description': 'NBRF/PIR entry format'},
    'nexus': {'try': True,
              'Nuc': True,
              'Pro': True,
              'Feat': False,
              'Gap': True,
              'Mset': False,
              'description': 'NEXUS/PAUP interleaved format'},
    'pdb': {'try': True,
            'Nuc': False,
            'Pro': True,
            'Feat': False,
            'Gap': False,
            'Mset': False,
            'description': 'PDB protein databank format ATOM lines'},
    'pdbnuc': {'try': False,
               'Nuc': True,
               'Pro': False,
               'Feat': False,
               'Gap': False,
               'Mset': False,
               'description':
               'PDB protein databank format nucleotide ATOM lines'},
    'pdbnucseq': {'try': False,
                  'Nuc': True,
                  'Pro': False,
                  'Feat': False,
                  'Gap': False,
                  'Mset': False,
                  'description':
                  'PDB protein databank format nucleotide SEQRES lines'},
    'pdbseq': {'try': True,
               'Nuc': False,
               'Pro': True,
               'Feat': False,
               'Gap': False,
               'Mset': False,
               'description': 'PDB protein databank format SEQRES lines'},
    'pearson': {'try': True,
                'Nuc': True,
                'Pro': True,
                'Feat': False,
                'Gap': True,
                'Mset': False,
                'description':
                'Plain old FASTA format with IDs not parsed further'},
    'phylip': {'try': True,
               'Nuc': True,
               'Pro': True,
               'Feat': False,
               'Gap': True,
               'Mset': True,
               'description':
               'PHYLIP interleaved and non-interleaved formats'},
    'phylipnon': {'try': False,
                  'Nuc': True,
                  'Pro': True,
                  'Feat': False,
                  'Gap': True,
                  'Mset': True,
                  'description': 'PHYLIP non-interleaved format'},
    'raw': {'try': True,
            'Nuc': True,
            'Pro': True,
            'Feat': False,
            'Gap': False,
            'Mset': False,
            'description': 'Raw sequence with no non-sequence characters'},
    'refseqp': {'try': False,
                'Nuc': False,
                'Pro': True,
                'Feat': True,
                'Gap': True,
                'Mset': False,
                'description': 'RefseqP entry format'},
    'selex': {'try': False,
              'Nuc': True,
              'Pro': True,
              'Feat': False,
              'Gap': True,
              'Mset': False,
              'description': 'SELEX format'},
    'staden': {'try': False,
               'Nuc': True,
               'Pro': True,
               'Feat': False,
               'Gap': True,
               'Mset': True,
               'description': 'Old Staden package sequence format'},
    'stockholm': {'try': True,
                  'Nuc': True,
                  'Pro': True,
                  'Feat': False,
                  'Gap': True,
                  'Mset': False,
                  'description': 'Stockholm (pfam) format'},
    'strider': {'try': True,
                'Nuc': True,
                'Pro': True,
                'Feat': False,
                'Gap': True,
                'Mset': False,
                'description': 'DNA Strider output format'},
    'swiss': {'try': True,
              'Nuc': False,
              'Pro': True,
              'Feat': True,
              'Gap': True,
              'Mset': False,
              'description': 'SwissProt entry format'},
    'text': {'try': False,
             'Nuc': True,
             'Pro': True,
             'Feat': False,
             'Gap': True,
             'Mset': False,
             'description': 'Plain text'},
    'treecon': {'try': True,
                'Nuc': True,
                'Pro': True,
                'Feat': False,
                'Gap': True,
                'Mset': False,
                'description': 'Treecon output format'},
}

_ROOT = os.path.abspath(os.path.dirname(__file__))

def get_data_path(path):
    return os.path.join(_ROOT, 'data', path)

class Acd(object):
    """
    ACD description
    """
    def __init__(self, application=None, sections=None):
        self.application = application
        self.sections = sections or []

    def desc_parameters(self):
        parameters = []
        for section in self.sections:
            for parameter in section.desc_parameters():
                parameters.append(parameter)
        return parameters

    def desc_sections(self):
        sections = []
        for section in self.sections:
            for subsection in section.desc_sections():
                sections.append(subsection)
            sections.append(section)
        return sections

    def qualifier_names(self):
        return [qualifier for section in self.sections for parameter in
                section.parameters for qualifier in
                parameter.qualifiers.keys()]

    def parameter_by_name(self, name):
        partial_matches = []
        for parameter in self.desc_parameters():
            if parameter.name==name:
                return parameter
            elif parameter.name.startswith(name):
                partial_matches.append(parameter)
        if len(partial_matches)>0:
            return max(partial_matches,key=lambda parameter: len(
                parameter.name))
        return None

    def parameter_by_index(self, index):
        return [parameter for parameter in self.desc_parameters() if
                parameter.attributes['parameter']['default_value']==True][index]

    def parameter_by_qualifier_name(self, name):
        results = []
        for parameter in self.desc_parameters():
            for qualifier_name in parameter.qualifiers.keys():
                if name==qualifier_name:
                    results.append((parameter, qualifier_name,
                                    parameter.qualifiers[qualifier_name]))
                elif qualifier_name.startswith(name):
                    results.append((parameter, qualifier_name,
                                    parameter.qualifiers[qualifier_name]))
        return results

class UnknownAcdPropertyException(Exception):
    """
    Exception thrown when trying to set a value to an unknown property
    """
    def __init__(self, attribute_name, attribute_value, parameter_name):
        super(UnknownAcdPropertyException, self).__init__()
        self.attribute_name = attribute_name
        self.attribute_value = attribute_value
        self.parameter_name = parameter_name

    def __str__(self):
        template = 'trying to set unknown property "{0}" to "{1}" in ' +\
                   'parameter "{2}"'
        return template.format(self.attribute_name, self.attribute_value,
                               self.parameter_name)


class InvalidAcdPropertyValue(Exception):
    """
    Exception thrown when trying to set an invalid value to an ACD property
    """
    def __init__(self, attribute_name, attribute_value, parameter_name):
        super(InvalidAcdPropertyValue, self).__init__()
        self.attribute_name = attribute_name
        self.attribute_value = attribute_value
        self.parameter_name = parameter_name

    def __str__(self):
        template = 'trying to set value of property "{0}" to invalid value ' +\
                   '"{1}" in parameter "{2}"'
        return template.format(self.attribute_name, self.attribute_value,
                               self.parameter_name)

def set_att_def_value(attribute, value, att_name, el_name):
    if value.startswith('$') or value.startswith('@'):
        # computed attribute values
        attribute['default_value'] = value
    elif attribute['value_type']=='list':
        attribute['default_value'].append(value)
    elif attribute['value_type']=='bool':
        if value in ['yes', 'Y', 'y', 'true']:
            attribute['default_value'] = True
        elif value in ['no', 'N', 'n', 'false']:
            attribute['default_value'] = False
        else:
            raise InvalidAcdPropertyValue(att_name, value, el_name)
    elif attribute['value_type']=='float':
        attribute['default_value'] = float(value)
    elif attribute['value_type']=='int':
        attribute['default_value'] = int(value)
    elif attribute['value_type']=='str':
        attribute['default_value'] = str(value)
    elif attribute['value_type']=='str':
        attribute['default_value'] = str(value)

class ElementWithAttributes(object):
    """
    Abstract class to structure an ACD element that has some attributes
    """
    def set_attributes(self, attributes):
        """
        Set the values for the attributes of the element, based on
        the existing default values
        :param attributes: the attributes to be set
        :type attributes: dict
        :return:
        """
        # pylint: disable=no-member
        for attribute in attributes:
            if attribute.name in self.attributes:
                set_att_def_value(self.attributes[attribute.name], attribute.value, attribute.name, self.name)
                try:
                    set_att_def_value(self.attributes[attribute.name], attribute.value, attribute.name, self.name)
                except TypeError as terr:
                    six.print_("Error while trying to set value of attribute {0} to {1} in " \
                          "parameter {2}" \
                          "".format(attribute.name, attribute.value, self.name))
                    raise terr
            elif attribute.name in self.qualifiers:
                set_att_def_value(self.qualifiers[attribute.name], attribute.value, attribute.name, self.name)
                try:
                    set_att_def_value(self.qualifiers[attribute.name], attribute.value, attribute.name, self.name)
                except TypeError as terr:
                    six.print_("Error while trying to set value of qualifier {0} to " \
                               "{1} in parameter {2}".format(attribute.name,
                                                             attribute.value,
                                                             self.name))
                    raise terr
            else:
                raise UnknownAcdPropertyException(attribute.name,
                                                  attribute.value, self.name)


class Application(ElementWithAttributes):
    """
    ACD Application block
    """
    def __init__(self, name, attributes=None):
        """
        :param name: name of the application
        :type name: basestring
        :param attributes: attributes of the Application block
        :type attributes: dict
        """
        self.name = name
        self.attributes = {'documentation': {'default_value': '', 'value_type': 'str', 'description': 'Short description of the application function'},
                           'relations': {'default_value': [], 'value_type': 'list', 'description': ''},
                           'groups': {'default_value': '', 'value_type': 'str', 'description': 'Standard application group(s) for wossname and GUIs'},
                           'keywords': {'default_value': '', 'value_type': 'str', 'description': 'Set of keywords describing the application functionality'},
                           'gui': {'default_value': '', 'value_type': 'str', 'description': 'Suitability for launching in a GUI'},
                           'batch': {'default_value': '', 'value_type': 'str', 'description': 'Suitability for launching in a GUI'},
                           'embassy': {'default_value': '', 'value_type': 'str', 'description': 'EMBASSY package name'},
                           'external': {'default_value': '', 'value_type': 'str', 'description': 'Third party tool(s) required by this program'},
                           'cpu': {'default_value': '', 'value_type': 'str', 'description': 'Estimated maximum CPU usage'},
                           'supplier': {'default_value': '', 'value_type': 'str', 'description': 'Supplier name'},
                           'version': {'default_value': '', 'value_type': 'str', 'description': 'Version number'},
                           'nonemboss': {'default_value': '', 'value_type': 'str', 'description': 'Non-emboss application name for SoapLab'},
                           'executable': {'default_value': '', 'value_type': 'str', 'description': 'Non-emboss executable for SoapLab'},
                           'template': {'default_value': '', 'value_type': 'str', 'description': 'Commandline template for SoapLab\'s ACD files'},
                           'comment': {'default_value': '', 'value_type': 'str', 'description': 'Comment for SoapLab\'s ACD files'},
                           'obsolete': {'default_value': '', 'value_type': 'str', 'description': ''}}
        if attributes is not None:
            self.set_attributes(attributes)

class Variable(object):
    def __init__(self, name, expression):
        self.name = name
        self.expression = expression

class Section(ElementWithAttributes):
    """
    ACD parameters section block
    """
    def __init__(self, name, properties=None, children=None):
        """
        :param name: name of the section
        :type name: basestring
        :param properties: the properties to set
        :type properties: list
        :param parameters: the parameters of the section
        :type parameters: list
        """
        self.name = name
        self.properties = properties or []
        children = children or []
        self.parameters = []
        self.subsections = []
        self.variables = []
        for child in children:
            if isinstance(child, Section):
                self.subsections.append(child)
            elif isinstance(child, Parameter):
                self.parameters.append(child)
            elif isinstance(child, Variable):
                self.variables.append(child)

    def desc_parameters(self):
        parameters = []
        for section in self.subsections:
            for parameter in section.desc_parameters():
                parameters.append(parameter)
        for parameter in self.parameters:
            parameters.append(parameter)
        return parameters

    def desc_sections(self):
        sections = []
        for section in self.subsections:
            for section in section.desc_sections():
                sections.append(section)
            sections.append(section)
        return sections

INPUT = 'input parameter type'
""" input parameter type """

OUTPUT = 'output parameter type'
""" output parameter type """


class Parameter(ElementWithAttributes):
    """
    ACD Parameter block
    """
    type = INPUT
    """ type of the parameter, input or output """

    def __init__(self, name, datatype, attributes):
        """
        :param name: name of the parameter
        :type name: basestring
        :param datatype: the datatype of the parameter (one of the keys of
        PARAMETER_CLASSES
        :type datatype: dict
        :param attributes: attribute values for the parameter
        :type attributes: dict
        """
        self.name = name
        self.datatype = datatype
        self.attributes = copy.deepcopy(self.__class__.attributes)
        self.set_attributes(attributes)

    attributes = {'information': {'default_value': '', 'value_type': 'str', 'description': 'Information for menus etc., and default prompt'},
                  'prompt': {'default_value': '', 'value_type': 'str', 'description': 'Prompt (if information string is unclear)'},
                  'code': {'default_value': '', 'value_type': 'str', 'description': 'Code name for information/prompt to be looked up in standard table'},
                  'help': {'default_value': '', 'value_type': 'str', 'description': 'Text for help documentation'},
                  'parameter': {'default_value': False, 'value_type': 'bool', 
                                'description': 'Command line parameter. Can be on the command line with no qualifier name. Implies \'standard\' qualifier'},
                  'standard': {'default_value': False, 'value_type': 'bool', 
                                'description': 'Standard qualifier, value required. Interactive prompt if missing'},
                  'additional': {'default_value': False, 'value_type': 'bool', 
                                'description': 'Additional qualifier. Value required if -options is on the command line, or set by default'},
                  'missing': {'default_value': False, 'value_type': 'bool', 
                                'description': 'Allow with no value on the command line to set to \'\''},
                  'valid': {'default_value': '', 'value_type': 'str', 
                                'description': 'Help: String description of allowed values for -help output, used if the default help is nuclear'},
                  'expected': {'default_value': '', 'value_type': 'str', 
                                'description': 'Help: String description of the expected value for -help output, used if the default help is nuclear'},
                  'needed': {'default_value': True, 'value_type': 'bool', 
                                'description': 'Include in GUI form, used to hide options if they are unclear in GUIs'},
                  'knowntype': {'default_value': '', 'value_type': 'str', 
                                'description': 'Known standard type, used to define input and output types for workflows'},
                  'relations': {'default_value': [], 'value_type': 'str', 
                                'description': 'Relationships between this ACD item and others, defined as specially formatted text'},
                  'outputmodifier': {'default_value': False, 'value_type': 'bool', 
                                'description': 'Modifies the output in ways that can break parsers'},
                  'style': {'default_value': '', 'value_type': 'str', 
                                'description': 'Style for SoapLab\'s ACD files'},
                  'qualifier': {'default_value': '', 'value_type': 'str', 
                                'description': 'Qualifier name for SoapLab\'s ACD files'},
                  'template': {'default_value': '', 'value_type': 'str', 
                                'description': 'Commandline template for SoapLab\'s ACD files'},
                  'comment': {'default_value': '', 'value_type': 'str', 
                                'description': 'Comment for SoapLab\'s ACD files'},
                  'default': {'default_value': '', 'value_type': 'str', 
                                'description': 'Default value'},
                }

    qualifiers = {}

PARAMETER_CLASSES = {}

with open(get_data_path('datatypes.yml'), 'r') as datatypes_fh:
    datatypes = yaml.safe_load(datatypes_fh)
    for datatype, definition in datatypes.items():
        bases = (Parameter,)
        attributes = copy.deepcopy(Parameter.attributes)
        attributes.update({key: value for key, value in definition.get('attributes',{}).items()})
        qualifiers = copy.deepcopy(Parameter.qualifiers)
        qualifiers.update({key: value for key, value in definition.get('qualifiers',{}).items()})
        properties = {'description': definition.get('description'),
                      'attributes': attributes, 'qualifiers': qualifiers}
        new_class = type(datatype.capitalize()+'Parameter',
                                           bases, properties)
        PARAMETER_CLASSES[datatype] = new_class
        globals()[new_class.__name__] = new_class

def get_parameter(name, datatype, properties):
    """
    Build a Parameter object using its name, datatype and properties list
    :param name: name of the parameter
    :type name: basestring
    :param datatype: datatype of the parameter (must be a value of
    PARAMETER_CLASSES keys
    :type datatype: basestring
    :param properties: property values to be set in attributes or qualifiers
    :type properties: dict
    """
    return PARAMETER_CLASSES.get(datatype, Parameter)(name, datatype,
                                                      properties)


class Attribute(object):
    def __init__(self, name=None, value=None):
        self.name = name
        self.value = value
