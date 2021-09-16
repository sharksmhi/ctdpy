# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 08:05:22 2018

@author: a002028
"""
import os
import setuptools


requirements = []
with open('requirements.txt', 'r') as fh:
    for line in fh:
        requirements.append(line.strip())

NAME = 'ctdpy'
VERSION = '0.1.3'
README = open('READMEpypi.rst', 'r').read()

setuptools.setup(
    name=NAME,
    version=VERSION,
    author="Johannes Johansson",
    author_email="johannes.johansson@smhi.se",
    description="Package to handle CTD data",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/sharksmhi/ctdpy",
    packages=setuptools.find_packages(),
    package_data={'ctdpy': [os.path.join('core', 'etc', '*.json'),
                            os.path.join('core', 'etc', 'readers', '*.yaml'),
                            os.path.join('core', 'etc', 'writers', '*.yaml'),
                            os.path.join('core', 'etc', 'templates', '*.yaml'),
                            os.path.join('templates', '*.xlsx'),
                            os.path.join('templates', '*.txt'),
                            os.path.join('templates', 'archive_structure', '*.txt'),
                            os.path.join('templates', 'archive_structure', 'processed_data', '*.txt'),
                            os.path.join('templates', 'archive_structure', 'received_data'),
                            os.path.join('templates', '*.txt'),
                            ]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=requirements,
)
