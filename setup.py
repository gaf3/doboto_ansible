#!/usr/bin/env python

from distutils.core import setup
import os

setup(
    name='doboto-ansible',
    version="0.4.0",
    description="DOBOTO Ansible Modules",
    packages=['ansible.module_utils'],
    long_description="BOTO-like Ansible modules for interacting with the Digital Ocean API",
    author="Digital Ocean Data Team",
    author_email="swe-data@do.co",
    install_requires=[
        "doboto>=0.4.0"
    ],
    classifiers=[
        'Programming Language :: Python :: 2'
        'Programming Language :: Python :: 2.7'
    ],
    data_files=[("/usr/share/ansible/doboto/", [
        "library/doboto_account.py",
        "library/doboto_action.py",
        "library/doboto_domain.py",
        "library/doboto_droplet.py",
        "library/doboto_floating_ip.py",
        "library/doboto_image.py",
        "library/doboto_region.py",
        "library/doboto_size.py",
        "library/doboto_snapshot.py",
        "library/doboto_ssh_key.py",
        "library/doboto_tag.py",
        "library/doboto_volume.py"
    ])]
)
