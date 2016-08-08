import unittest
import os
from glob import glob

from nose_parameterized import parameterized
from ruamel.yaml import load

from pyacd.parser import parse_acd

ACDTEST_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), \
                          '../tests/acd')

def get_tests():
    tests = []
    acd_list = glob(ACDTEST_DIR+'/*.acd')
    for acd_path in acd_list:
        tests.append([acd_path])
    return  tests


class TestParseAcd(unittest.TestCase):

    @parameterized.expand(get_tests())
    def parse_command_line(self, acd_path):
        try:
            acd_string = open(acd_path, 'r').read()
            acd_object = parse_acd(acd_string)
            print acd_object.application.name, acd_object.parameter_names(), \
                [section.name for section in acd_object.sections]
        except Exception as exc:
            print "Failure parsing ACD file {0}".format(acd_path)
            raise exc
