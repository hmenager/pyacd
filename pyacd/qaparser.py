"""
  parser module for EMBOSS QA files
"""
from pyparsing import Optional, Suppress, Word, OneOrMore, ZeroOrMore, \
    printables, Group, alphanums, alphas, restOfLine, oneOf, nums
from .qa import ApplicationRef, FilePattern, FileGroup, Qa, CommandLine, \
    InputLine

# CL_PARAMETER = Optional((Suppress('--') | Suppress('-')) + Word(
#     alphas)('name')) + Word(printables)('value')
# CL_PARAMETERS = OneOrMore(Group(CL_PARAMETER(
#      'parameter')))('parameters')

TEST_ID = Suppress("ID") + Word(alphanums + '-')('id')

APPLICATION_REF = oneOf(['AP', 'AA', 'AQ']) + Word(alphas)('appname') + \
                  Optional(
    Suppress('AB') + Word(alphas)('embassypack'))
#APPLICATION_REF = Suppress("AP") + Word(alphas)('appname')
#APPLICATION_REF = Suppress('AA') + Word(alphas)('appname') + \
#                     Suppress('AB') + Word(alphas)('embassypack')
def _get_application_ref(token):
    return ApplicationRef(token['appname'], token.get('embassypack',None))
APPLICATION_REF.setParseAction(_get_application_ref)

CL_LINE = Suppress("CL") + restOfLine('line')
def _get_cl_line(token):
    return CommandLine(token['line'])
CL_LINE.setParseAction(_get_cl_line)

CL_LINES = Group(ZeroOrMore(CL_LINE))('cl_lines')
def _get_cl_lines(token):
    return token['cl_lines']
CL_LINES.setParseAction(_get_cl_lines)

IN_LINE = Suppress("IN") + restOfLine('line')
def _get_in_line(token):
    return InputLine(token['line'])
IN_LINE.setParseAction(_get_in_line)

IN_LINES = Group(ZeroOrMore(IN_LINE))('in_lines')
def _get_in_lines(token):
    return token['in_lines']
IN_LINES.setParseAction(_get_in_lines)

FILE_PATTERN = Suppress("FP") \
             + Optional(Word(nums))('count') \
             + Word(printables)('pattern')
def _get_file_pattern(token):
    return FilePattern(token['pattern'], int(token.get('count')) if
    token.get('count') else None)
FILE_PATTERN.setParseAction(_get_file_pattern)

FILE_GROUP = Suppress("FI") + Word(printables)('file') \
             + Optional(Suppress("FC") +  oneOf(['<','=','>'])(
    'lc_test_operator') + Word(nums)('lc_test_value')) \
             + Group(ZeroOrMore(FILE_PATTERN))('patterns') \
             + Optional(Suppress("FZ") + oneOf(['<','=','>'])(
    'size_test_operator') + Word(nums)('size_test_value'))
def _get_file_group(token):
    size_test = None
    if token.get('size_test_operator'):
        size_test = {'operator': token.get('size_test_operator'),
                     'value': int(token.get('size_test_value'))}
    lc_test = None
    if token.get('lc_test_operator'):
        lc_test = {'operator': token.get('lc_test_operator'),
                     'value': int(token.get('lc_test_value'))}
    return FileGroup(token['file'],line_count_test=lc_test,
                     patterns=token.get('patterns'),
                     size_test=size_test)
FILE_GROUP.setParseAction(_get_file_group)

FILE_GROUPS = Group(ZeroOrMore(FILE_GROUP))('files')
def _get_file_groups(token):
    return token['files']
FILE_GROUPS.setParseAction(_get_file_groups)

QA = TEST_ID + \
     Optional(Suppress('TI') & Word(nums)('time_limit')) & \
     Optional(Suppress('UC') & restOfLine('annotations')) & \
     Optional(Suppress('RQ') & restOfLine('requirements')) & \
     Optional(Suppress('CC') & restOfLine('comment')) + \
     APPLICATION_REF('appref') & CL_LINES & IN_LINES & FILE_GROUPS
def _get_qa(token):
    return Qa(token['id'],token.get('uc',None),token['appref'], command_lines=token[
        'cl_lines'], input_lines=token['in_lines'])
QA.setParseAction(_get_qa)

def parse_cl_line(string):
    return CL_LINE.parseString(string)[0]

def parse_cl_lines(string):
    return CL_LINES.parseString(string)

def parse_in_line(string):
    return IN_LINE.parseString(string)[0]

def parse_in_lines(string):
    return IN_LINES.parseString(string)

def parse_app_ref(string):
    return APPLICATION_REF.parseString(string)[0]

def parse_file_pattern(string):
    return FILE_PATTERN.parseString(string)[0]

def parse_file_group(string):
    return FILE_GROUP.parseString(string)[0]

def parse_qa(string):
    """ parse a QA test item (one test case for one application)"""
    return QA.parseString(string)[0]
