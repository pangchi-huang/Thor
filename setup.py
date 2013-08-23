#!/usr/bin/env python

from contextlib import closing
from os.path import exists
from setuptools import setup, find_packages

from Thor import __version__

with closing(open('requirements.txt')) as f:
    requires = f.read().splitlines()

setup(
    name='Thor',
    version=__version__,
    # Your name & email here
    author='Yu Liang',
    author_email='yu.liang@thekono.com',
    # If you had Thor.tests, you would also include that in this list
    packages=find_packages(),
    # Any executable scripts, typically in 'bin'. E.g 'bin/do-something.py'
    scripts=[],
    # REQUIRED: Your project's URL
    url='',
    # Put your license here. See LICENSE.txt for more information
    license='',
    # Put a nice one-liner description here
    description='',
    long_description=open('README.md').read() if exists("README.md") else "",
    # Any requirements here, e.g. "Django >= 1.1.1"
    install_requires=requires,
)
