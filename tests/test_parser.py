import unittest

import six

from pyacd.parser import parse_attribute, parse_attributes, parse_parameter, \
    parse_parameters, parse_section, parse_sections, parse_application, parse_acd
from pyacd import acd

class TestParser(unittest.TestCase):

    # def setUp(self):
    #     #instanciate parser
    #     self.parser = AcdParser()

    def test_parse_attribute(self):
        attribute = parse_attribute('documentation: "Read and write (return) sequences"')
        self.assertEqual(attribute.name, 'documentation')
        self.assertEqual(attribute.value,'Read and write (return) sequences')

    def test_parse_attributes_list(self):
        attributes_list = parse_attributes("""
            groups: "Data retrieval, Edit"
            relations: "EDAM_topic:0090 Data search and retrieval"
            relations: "EDAM_operation:1813 Sequence retrieval"
            relations: "EDAM_operation:2121 Sequence file processing"
        """)
        self.assertEqual(attributes_list[0].name, 'groups')
        self.assertEqual(attributes_list[0].value, 'Data retrieval, Edit')
        self.assertEqual(attributes_list[1].name, 'relations')
        self.assertEqual(attributes_list[1].value, 'EDAM_topic:0090 Data search and retrieval')

    def test_parse_parameter(self):
        parameter = parse_parameter("""
            string: myparameter [
            information: "parameter information"
            prompt: "test prompt"
            needed: "yes"
            additional: "no"
        ]""")
        self.assertEqual(parameter.name, 'myparameter')
        self.assertEqual(parameter.attributes['information']['default_value'], 'parameter information')
        self.assertEqual(parameter.attributes['prompt']['default_value'], 'test prompt')

    def test_parse_boolean_values(self):
        parameter = parse_parameter("""
            string: myparameter [
            needed: "yes"
            additional: "no"
        ]""")
        self.assertEqual(parameter.attributes['needed']['default_value'], True)
        self.assertEqual(parameter.attributes['additional']['default_value'], False)
        parameter = parse_parameter("""
            string: myparameter [
            needed: "Y"
            additional: "N"
        ]""")
        self.assertEqual(parameter.attributes['needed']['default_value'], True)
        self.assertEqual(parameter.attributes['additional']['default_value'], False)
        parameter = parse_parameter("""
            string: myparameter [
            needed: "y"
            additional: "n"
        ]""")
        self.assertEqual(parameter.attributes['needed']['default_value'], True)
        self.assertEqual(parameter.attributes['additional']['default_value'], False)
        parameter = parse_parameter("""
            string: myparameter [
            needed: "true"
            additional: "false"
        ]""")
        self.assertEqual(parameter.attributes['needed']['default_value'], True)
        self.assertEqual(parameter.attributes['additional']['default_value'], False)
        def bad_value_parse():
            parse_parameter("""
                string: myparameter [
                needed: "W"
            ]""")
        self.assertRaises(acd.InvalidAcdPropertyValue, bad_value_parse)

    def test_parse_parameters(self):
        parameters_list = parse_parameters("""
        string: myparameter [
            information: "parameter information"
        ]

        string: myparameterZ [
            information: "parameter 2 information"
        ]
        """)
        self.assertEqual(len(parameters_list),2)
        self.assertIsInstance(parameters_list[0], acd.Parameter)
        self.assertIsInstance(parameters_list[1], acd.Parameter)

    def test_parse_section(self):
        section = parse_section("""
        section: input [
              information: "Input section"
              type: "page"
            ]

              boolean: feature [
                information: "Use feature information"
                relations: "EDAM_data:2527 Parameter"
              ]

              seqall: sequence [
                parameter: "Y"
                type: "gapany"
                features: "$(feature)"
                relations: "EDAM_data:0849 Sequence record"
              ]

            endsection: input
        """)
        self.assertEqual(section.name,"input")

    def test_parse_section_with_var(self):
        section = parse_section('''
section: output [
  information: "Output section"
  type: "page"
]


variable: isdual "@($(display) == D)"

  xygraph: graph [
    standard: "@($(display) != none)"
    multiple: "@( $(isdual) ? 2 : 4)"
    nullok: "Y"
    nulldefault: "@($(display) == none)"
    relations: "EDAM_data:2167 Nucleic acid density plot"
    sequence: "Y"
  ]

  report: outfile [
    standard: "@($(display) == none)"
    taglist: "float:a float:c float:g float:t float:at float:gc"
    rformat: "table"
    knowntype: "density output"
    nullok: "Y"
    nulldefault: "@($(display) != none)"
    relations: "EDAM_data:2167 Nucleic acid density plot"
  ]

endsection: output
''')
        six.print_(section)
