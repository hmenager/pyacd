#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
from setuptools import setup

readme = open('README.md').read()

setup(
    name='pyacd',
    version='0.1.2',
    description='python API to EMBOSS ACD files',
    long_description=readme,
    author='Hervé Ménager',
    author_email='hmenager@pasteur.fr',
    url='https://github.com/hmenager/pyacd.git',
    download_url='https://github.com/hmenager/pyacd/tarball/0.1',
    packages=['pyacd'],
    install_requires=[
          'pyparsing',
          'ruamel.yaml'
    ],
    license="BSD",
    entry_points={
          'console_scripts': ['pyacd=pyacd:main'],
        },
    tests_require=['nose','nose_parameterized'],
    test_suite='nose.collector',
    include_package_data=True,
    zip_safe=False 
)
