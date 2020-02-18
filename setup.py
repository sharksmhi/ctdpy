# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 08:05:22 2018

@author: a002028
"""

import setuptools
import os


def long_description():
    if os.path.exists('README.md'):
        return open('README.md').read()
    else:
        return 'No readme file'


setuptools.setup(
    name="ctdpy",
    version="0.0.32",
    author="Johannes Johansson",
    author_email="johannes.johansson@smhi.se",
    description="TEST version 0.0.32 Package to handle CTD data",
    long_description=long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    package_data={'ctdpy': [os.path.join('ctdpy_core', 'etc', '*.yaml'),
                            os.path.join('ctdpy_core', 'etc', 'readers', '*.yaml'),
                            os.path.join('ctdpy_core', 'etc', 'writers', '*.yaml'),
                            os.path.join('ctdpy_core', 'etc', 'templates', '*.yaml'),
                            os.path.join('docs', 'flows', '*.xml'),
                            os.path.join('docs', '*.docx'),
                            os.path.join('templates', '*.xlsx'),
                            os.path.join('tests', 'etc', 'data', '*.cnv')]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
