import unittest
from pyacd.qaparser import parse_cl_line, parse_cl_lines, parse_app_ref, \
    parse_file_group, parse_qa, parse_file_pattern, parse_in_line, parse_in_lines
from pyacd.parser import parse_acd


class TestParser(unittest.TestCase):

    def test_parse_cl_line(self):
        res = parse_cl_line('CL -sequence test.fasta')
        self.assertEqual(res.command_line, ' -sequence test.fasta')

    def test_parse_cl_lines(self):
        res = parse_cl_lines('CL -sequence test.fasta\nCL -sequence2 '
                            'test2.fasta')
        self.assertEqual(res.cl_lines[0].command_line, ' -sequence test.fasta')
        self.assertEqual(res.cl_lines[1].command_line, ' -sequence2 '
                                                       'test2.fasta')

    def test_parse_in_line(self):
        res = parse_in_line('IN toto.txt')
        self.assertEqual(res.input_line, ' toto.txt')

    def test_parse_in_lines(self):
        res = parse_in_lines('IN toto.txt\nIN tutu.dat')
        self.assertEqual(res.in_lines[0].input_line, ' toto.txt')
        self.assertEqual(res.in_lines[1].input_line, ' tutu.dat')

    def test_parse_apref_lines(self):
        res = parse_app_ref('AP name')
        self.assertEqual(res.name, 'name')
        res = parse_app_ref('AA name\nAB package')
        self.assertEqual(res.name, 'name')
        self.assertEqual(res.embassy_package, 'package')

    def test_parse_file_pattern_count(self):
        res = parse_file_pattern('''
        FP 0 /ERROR/
        ''')
        self.assertEqual(res.pattern, '/ERROR/')
        self.assertEqual(res.count, 0)
        self.assertTrue(hasattr(res, 'count'))

    def test_parse_file_pattern_nocount(self):
        res = parse_file_pattern('''
        FP /MUSTHAVE/
        ''')
        self.assertEqual(res.pattern, '/MUSTHAVE/')
        self.assertFalse(hasattr(res,'count'))

    def test_parse_file_group(self):
        res = parse_file_group('''
        FI toto.txt
        FC = 2
        FZ > 45
        FP 0 /ERROR/
        FP 0 /CRITICAL/
        ''')
        self.assertEqual(res.file,'toto.txt')
        self.assertEqual(res.line_count_test, {'operator':'=', 'value':2})
        self.assertEqual(res.size_test, {'operator': '>', 'value': 45})

    def test_parse_qa_simple(self):
        res = parse_qa('''
        ID test-1
        AP test
        CL -u test -v test2
        CL -w -x
        IN toto.txt
        IN tutu.dat
        ''')
        self.assertEqual(res.id, 'test-1')
        self.assertEqual(res.application_ref.name, 'test')
        self.assertEqual(res.command_lines[0].command_line, ' -u test -v test2')
        self.assertEqual(res.command_lines[1].command_line, ' -w -x')
        self.assertEqual(res.input_lines[0].input_line, ' toto.txt')
        self.assertEqual(res.input_lines[1].input_line, ' tutu.dat')

    def test_parse_qa_cai(self):
        qatest_text = '''
        ID cai-ex
        AP cai
        CL AB009602
        IN
        IN
        FI stderr
        FC = 2
        FP 0 /Warning: /
        FP 0 /Error: /
        FP 0 /Died: /
        FI ab009602.cai
        FP /0\.188/
        //
        '''
        acd_text = '''
        application: cai [
          documentation: "Calculate codon adaptation index"
          groups: "Nucleic:Codon usage"
          relations: "EDAM_topic:0107 Codon usage analysis"
          relations: "EDAM_operation:0286 Codon usage analysis"
        ]

        section: input [
          information: "Input section"
          type: "page"
        ]

          seqall: seqall [
            parameter: "Y"
            type: "DNA"
            relations: "EDAM_data:2887 Sequence record (nucleic acid)"
          ]

          codon: cfile [
            standard: "Y"
            default: "Eyeast_cai.cut"
            relations: "EDAM_data:1597 Codon usage table"
          ]

        endsection: input

        section: output [
          information: "Output section"
          type: "page"
        ]

          outfile: outfile [
            parameter: "Y"
            knowntype: "cai output"
            relations: "EDAM_data:2865 Codon usage bias"
          ]

        endsection: output
        '''
        acd_def = parse_acd(acd_text)
        qa_item = parse_qa(qatest_text)
        qa_item.parse_command_lines(acd_def)

    def test_parse_abiview(self):
        res = parse_qa('''
        ID abiview-ex
        AP abiview
        CL -graph cps
        IN ../../data/abiview.abi
        IN
        FI stderr
        FC = 2
        FP 0 /Warning: /
        FP 0 /Error: /
        FP 0 /Died: /
        FI stdout
        FZ = 19
        FP /^Created abiview\.ps\n/
        FI abiview.fasta
        FP /^>abiview\n/
        FP /^GNNNNNNNNNG/
        FZ = 861
        FI abiview.ps
        FP /^%%Title: PLplot Graph\n/
        ''')

    def test_parse_backtranseq(self):
        res = parse_qa('''
        ID backtranseq-ex
        UC Note that this is a human protein and so the default human codon frequency file is used ie. is not specified
        AP backtranseq
        IN tsw:opsd_human
        IN
        FI opsd_human.fasta
        FP /^>OPSD_HUMAN/
        FP /CGCCACCGGCGTGGTG\n/
        FZ = 1101
        FI stderr
        FC = 2
        FP 0 /Warning: /
        FP 0 /Error: /
        FP 0 /Died: /
        ''')

    def test_parse_wsdbfetch(self):
        res = parse_qa('''
        ID wsdbfetch-uniprotxml
        RQ soapws
        CC requires (axis2C) SOAP webservices library enabled
        AP xmlget
        CL uniprotxml::twsdbfetch:uniprotkb:p12345 stdout -auto
        FI stdout
        FC > 160
        FP 1 /<uniprot xmlns="http://uniprot.org/uniprot"/
        FP 1 /<accession>P12345</accession>/
        ''')

    def test_parse_qacc_not_srswww(self):
        res = parse_qa('''
        ID qacc-not-srswww
        AP seqret
        CL "srs:uniprot-acc{p00274 ! p0aa28}" stdout -auto
        FI stdout
        FP 5 /^>/
        FP 0 /^>THIO_SALTY/
        FP 1 /^>THIO_SHIFL/
        FP 1 /^>THIO_ECOLI/
        //''')
