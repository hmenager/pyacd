Python API to parse and access EMBOSS ACD files
===============================================

pyacd is a parsing library for:
- EMBOSS ACD files.
- EMBOSS QA files (functional tests for EMBOSS)

Install
-------

Installing the official package from PyPi:

`pip install pyacd`

Or from source:
`
git clone https://github.com/hmenager/pyacd.git
cd pyacd && python setup.py install
`

Usage
-----

pyacd is a Python API. Here is a small example that shows how to use it to parse an ACD file and
retrieve basic information from it.

`
from pyacd.parser import parse_acd
abiview_acd = parse_acd(open('/usr/share/EMBOSS/acd/abiview.acd','r').read())
print abiview_acd.application.name
for section in abiview_acd.sections:
    print [p.name for p in section.parameters]
`
