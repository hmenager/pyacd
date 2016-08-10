from acd import BooleanParameter, ToggleParameter

class ApplicationRef(object):
    """
    A reference to an application
    EMBOSS App, EMBASSY App, of build binary
    """
    def __init__(self, name, embassy_package=None, is_build=False):
        self.name = name
        if embassy_package:
            self.embassy_package = embassy_package
        self.is_build = is_build

class FilePattern(object):
    """
    A pattern to find in a result file and optionally
    the count of times it should match
    """
    def __init__(self, pattern, count=None):
        self.pattern = pattern
        if count is not None:
            self.count = count

class FileGroup(object):
    """
    A "file group", i.e. the name of the file
    and the tests that must be run on this file
    e.g.: line count, patterns
    """
    def __init__(self, file, line_count_test=None, patterns=None,
                 size_test=None):
        self.file = file
        """output file name"""
        self.line_count_test = line_count_test
        """test on the number of lines expected in the file"""
        self.patterns = patterns or []
        """patterns which should be found in the file"""
        self.size_test = size_test
        """test on the expected size of the file"""

class CommandLine(object):
    """
    A raw part of command line defined in the QA test
    """
    def __init__(self, command_line=None):
        self.command_line = command_line

class InputLine(object):
    """
    A input provided in response to a prompt
    """
    def __init__(self, input_line=None):
        self.input_line = input_line

class AmbiguousOptionParseException(Exception):
    """
    Exception thrown when an option can belong to multiple parameters
    """
    def __init__(self, option_name, parameters):
        super(AmbiguousOptionParseException, self).__init__()
        self.option_name = option_name
        self.parameters = parameters

    def __str__(self):
        template = 'cannot map option {0} to a parameter, since it belongs ' \
                   'to multiple parameters: {1}'
        return template.format(self.option_name, [p.name for p in
                                               self.parameters])

class UnknownOptionParseException(Exception):
    """
    Exception thrown when an option doesn't belong to any parameter
    """
    def __init__(self, option_name):
        super(UnknownOptionParseException, self).__init__()
        self.option_name = option_name

    def __str__(self):
        template = 'cannot find a parameter for option {0}'
        return template.format(self.option_name)

class Qa(object):
    """
    QA test
    """
    def __init__(self, id, uc, application_ref, command_lines=None,
                 input_lines=None, file_groups=None, time_limit=None):
        self.id = id
        """test id"""
        self.uc = uc
        """text description for the test"""
        self.application_ref = application_ref
        """application ref"""
        self.command_lines = command_lines or []
        """list of command lines"""
        self.input_lines = input_lines or []
        """list of prompt input values"""
        self.file_groups = file_groups or []
        """list of file groups defined for output files"""
        self.time_limit = time_limit
        """time limit for test"""

    def parse_command_lines(self, acd_def):
        """
        parse the command line to generate an abstract job order dictionary,
        based on the parameters defined in the ACD
        structure of job order is that for each defined parameter, there is
        a dictionary entry containing its value and the value of its various
        qualifiers
        """
        command_line_string = ' '.join([cl.command_line for cl in
                                        self.command_lines])
        command_line_string = command_line_string.replace('=',' ')
        command_line_array = [param_value for
                              param_value in command_line_string.split(' ')
                              if param_value != '']
        job_order = {}
        for parameter in acd_def.desc_parameters():
            job_order[parameter.name]={'value':None}
        """dictionary describing the parameter values passed to the job"""
        cl_chunks = iter(command_line_array)
        parameters_count = 0
        for chunk in cl_chunks:
            if chunk.replace('-','') in ['auto', 'stdout', 'debug', 'filter',
                                         'help', 'options']:
                # ignore all global qualifiers?
                #ignore auto qualifier, which should be automatically set by
                #wrappers
                continue
            if chunk.startswith('-'):
                # parameter values that start with the -name
                name = chunk[1:]
                parameter = acd_def.parameter_by_name(name)
                if parameter is not None:
                    if isinstance(parameter, BooleanParameter) or isinstance(
                            parameter, ToggleParameter):
                        parameter_value = True
                    else:
                        parameter_value = cl_chunks.next()
                    if parameter.qualifiers.get('parameter') == True:
                        parameters_count += 1
                    job_order[parameter.name]['value'] = parameter_value
                else:
                    if name.startswith('no') and acd_def.parameter_by_name(
                            name[2:]) is not None:
                        parameter = acd_def.parameter_by_name(
                            name[2:])
                        job_order[parameter.name]['value'] = False
                    else:
                        index = None
                        if name[-1].isdigit():
                            #if digits are used for explicit ordering of
                            # qualifiers
                            index = int(name[-1])-1
                            name = name[:-1]
                        parameters = acd_def.parameter_by_qualifier_name(
                            name)
                        if len(parameters)==1:
                            parameter = parameters[0][0]
                            qualifier_name = parameters[0][1]
                            if isinstance(parameters[0][2], bool):
                                parameter_value = True
                            else:
                                parameter_value = cl_chunks.next()
                            job_order[parameter.name][qualifier_name] = parameter_value
                        elif len(parameters)>1:
                            # ambiguous qualifier name
                            if index is not None:
                                parameter = parameters[index][0]
                                qualifier_name = parameters[index][1]
                                if isinstance(parameters[index][2], bool):
                                    parameter_value = True
                                else:
                                    parameter_value = cl_chunks.next()
                                job_order[parameter.name][qualifier_name] = parameter_value
                            else:
                                # in case multiple parameters match for the
                                # qualifier, we set it for all the
                                # parameters, assuming these are
                                # 'toggle-controlled'
                                for match in parameters:
                                    parameter = match[0]
                                    qualifier_name = match[1]
                                    if isinstance(match[2], bool):
                                        parameter_value = True
                                    else:
                                        parameter_value = cl_chunks.next()
                                    job_order[parameter.name][
                                        qualifier_name] = parameter_value
                        else: #len(parameters)==0
                            # testing for a no-prefixed qualifier
                            parameters = acd_def.parameter_by_qualifier_name(
                                name[2:])
                            if len(parameters) == 1:
                                parameter = parameters[0][0]
                                qualifier_name = parameters[0][1]
                                job_order[parameter.name][
                                    qualifier_name] = False
                            elif len(parameters) > 1:
                                # ambiguous qualifier name
                                if index is not None:
                                    parameter = parameters[index][0]
                                    qualifier_name = parameters[index][1]
                                    job_order[parameter.name][
                                        qualifier_name] = False
                                else:
                                    #in case multiple parameters match for the
                                    # qualifier, we set it for all the
                                    # parameters, assuming these are
                                    # 'toggle-controlled'
                                    for match in parameters:
                                        parameter = match[0]
                                        qualifier_name = match[1]
                                        job_order[parameter.name][
                                            qualifier_name] = False
                            else:  # len(parameters)==0
                                #if absolutely no matching parameter found,
                                # it may be an abbreviation for a global
                                # qualifier
                                if [gq for gq in ['auto', 'stdout',
                                                         'debug', 'filter',
                                                         'help', 'options']
                                    if gq.startswith(name)]:
                                        continue
                                #if not, raise an error
                                raise UnknownOptionParseException(name)
            else:
                # parameter values by position on the command line
                parameter = acd_def.parameter_by_index(parameters_count)
                job_order[parameter.name]['value'] = chunk
                if parameter.qualifiers.get('parameter')==True:
                    parameters_count += 1
        input_lines_array = [line.input_line for line in self.input_lines]
        for parameter in acd_def.desc_parameters():
            if len(input_lines_array)==0:
                break
            if job_order[parameter.name]['value'] is None:
                job_order[parameter.name]['value']=input_lines_array.pop(0)
        for key in job_order.keys():
            if job_order[key]=={'value':None}:
                del job_order[key]
        return job_order