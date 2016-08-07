#!/usr/bin/env python
from ruamel.yaml import dump
import os
QATEST_PATH ='/usr/share/EMBOSS/test/qatest.dat'
QATEST_TARGET_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), \
                    '../tests/qa')
qa_string = ''
qa_name = ''
app_name = ''
tests = {}
with open(QATEST_PATH, 'r') as qa_lines:
    for qa_line in qa_lines:
        if qa_line.startswith('ID '):
            qa_name = qa_line[3:-1]
        if qa_line.startswith('AP '):
            app_name = qa_line[3:-1]
            print '<', qa_name, app_name, '>'
            tests[qa_name] = app_name
        qa_string += qa_line
        if qa_line.startswith('//'):
            with open(QATEST_TARGET_DIR + '/' + qa_name + '.qa', 'w') as \
                    qa_file:
                print QATEST_TARGET_DIR + '/' + qa_name + '.qa'
                qa_file.write(qa_string)
                qa_string = ''
                qa_name = ''
                qa_name = ''
    dump(tests, open(QATEST_TARGET_DIR + '/qa_tests.yml', 'w'),
         default_flow_style=False)
