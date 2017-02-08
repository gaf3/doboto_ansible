#!/usr/bin/env python

from distutils.core import setup
import os

our_dir = os.path.abspath(os.path.dirname(__file__))
__version__ = open(our_dir + "/VERSION", "r").readline().strip()

setup(
    name='DOBOTO Ansible',
    version=__version__,
    description="DOBOTO Ansible Modules",
    packages=['ansible.module_utils'],
    long_description="BOTO-like Ansible modules for interacting with the Digital Ocean API",
    author="Digital Ocean Data Team",
    author_email="swe-data@do.co",
    classifiers=[
        'Programming Language :: Python :: 2'
        'Programming Language :: Python :: 2.7'
    ],
)
