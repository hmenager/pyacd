import unittest
import os

from nose_parameterized import parameterized
from ruamel.yaml import load

from pyacd.qaparser import parse_qa
from pyacd.parser import parse_acd

QATEST_PATH = '/usr/share/EMBOSS/test/qatest.dat'
ACDTEST_DIR = '/usr/share/EMBOSS/acd'

def get_tests():
    qa_string = ''
    qa_name = ''
    app_name = ''
    tests = []
    with open(QATEST_PATH, 'r') as qa_lines:
        for qa_line in qa_lines:
            if qa_line.startswith('ID '):
                qa_name = qa_line[3:-1]
            if qa_line.startswith('AP '):
                app_name = qa_line[3:-1]
            qa_string += qa_line
            if qa_line.startswith('//'):
                acd_path = ACDTEST_DIR + '/' + app_name + '.acd'
                tests.append([acd_path, qa_string, qa_name])
    return  tests


class TestParseCommandLine(unittest.TestCase):

    @parameterized.expand(get_tests())
    def test_parse_command_line(self, acd_path, qa_string, qa_name):
        try:
            acd_string = open(acd_path, 'r').read()
            acd_object = parse_acd(acd_string)
            qa_test = parse_qa(qa_string)
            job_order = qa_test.parse_command_lines(acd_object)
            return job_order
        except Exception as exc:
            print "Failure parsing QA test {0} for ACD {1}".format(qa_name,
         acd_path)
            raise exc
