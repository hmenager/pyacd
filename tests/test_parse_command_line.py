import unittest
import os

from nose_parameterized import parameterized
from ruamel.yaml import load

from pyacd.qaparser import parse_cl_line, parse_cl_lines, parse_app_ref, \
    parse_file_group, parse_qa, parse_file_pattern, parse_in_line, \
    parse_in_lines, parse_ti_line, parse_uc_line, parse_rq_line, \
    parse_cc_line, parse_cc_lines
from pyacd.parser import parse_acd

QATEST_TARGET_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), \
                                 '../tests/qa')
def get_tests():
    tests = []
    test_map = load(open(QATEST_TARGET_DIR + '/qa_tests.yml', 'r'))
    for test in test_map.keys():
        qa_name = test
        acd_name = test_map[qa_name]
        qa_path = QATEST_TARGET_DIR + '/' + qa_name + '.qa'
        acd_path = QATEST_TARGET_DIR + '/' + acd_name + '.acd'
        tests.append([acd_path, qa_path])
    return  tests


class TestParseCommandLine(unittest.TestCase):

    @parameterized.expand(get_tests())
    def parse_command_line(self, acd_path, qa_path):
        try:
            qa_string = open(qa_path, 'r').read()
            acd_string = open(acd_path, 'r').read()
            acd_object = parse_acd(acd_string)
            qa_test = parse_qa(qa_string)
            job_order = qa_test.parse_command_lines(acd_object)
            return job_order
        except Exception as exc:
            print "Failure parsing QA test {0} for ACD {1}".format(qa_path, acd_path)
            raise exc
