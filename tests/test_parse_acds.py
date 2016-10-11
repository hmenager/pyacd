import unittest
import os
from glob import glob

from nose_parameterized import parameterized
from ruamel.yaml import load

from pyacd.parser import parse_acd

ACDTEST_DIR = '/usr/share/EMBOSS/acd'

def get_acds_list():
    tests = []
    acd_list = glob(ACDTEST_DIR+'/*.acd')
    for acd_path in acd_list:
        tests.append([acd_path])
    return  tests


class TestParseAcd(unittest.TestCase):

    @parameterized.expand(get_acds_list())
    def test_parse_command_line(self, acd_path):
        try:
            acd_string = open(acd_path, 'r').read()
            acd_object = parse_acd(acd_string)
            # sections count
            self.assertEqual(acd_string.count('endsection'),
                             len(acd_object.desc_sections()))
        except Exception as exc:
            print "Failure parsing ACD file {0}".format(acd_path)
            raise exc

