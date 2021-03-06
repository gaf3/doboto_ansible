#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.doboto_module import require, DOBOTOModule

"""
Ansible module to manage DigitalOcean
(c) 2017, SWE Data <swe-data@do.co>

This file is part of Ansible

Ansible is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Ansible is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
"""

DOCUMENTATION = '''
---
module: doboto_certificate

short_description: Manage DigitalOcean certificates
description: Manages DigitalOcean certificates
version_added: "0.5.0"
author: "SWE Data <swe-data@do.co>"
options:
    token:
        description: token to use to connect to the API (uses DO_API_TOKEN from ENV if not found)
    action:
        description: certificate action
        choices:
            - list
            - create
            - present
            - info
            - destroy

    id:
        description: same as DO API variable (certificate id)
    name:
        description: same as DO API variable
    private_key:
        description: same as DO API variable
    leaf_certificate:
        description: same as DO API variable
    certificate_chain:
        description: same as DO API variable
    url:
        description: URL to use if not official (for experimenting)
'''

EXAMPLES = '''
- name: certificate | create
  doboto_certificate:
    action: create
    name: certificate-create
    private_key: "{{ lookup('file', 'private.pem') }}"
    leaf_certificate: "{{ lookup('file', 'public.pem') }}"
    certificate_chain: "{{ lookup('file', 'public.pem') }}"
  register: certificate_create

- name: certificate | present | exists
  doboto_certificate:
    action: present
    name: certificate-create
    private_key: "{{ lookup('file', 'private.pem') }}"
    leaf_certificate: "{{ lookup('file', 'public.pem') }}"
    certificate_chain: "{{ lookup('file', 'public.pem') }}"
  register: certificate_present_exists

- name: certificate | present | new
  doboto_certificate:
    action: present
    name: certificate-present
    private_key: "{{ lookup('file', 'private.pem') }}"
    leaf_certificate: "{{ lookup('file', 'public.pem') }}"
    certificate_chain: "{{ lookup('file', 'public.pem') }}"
  register: certificate_present_new

- name: certificate | info
  doboto_certificate:
    action: info
    id: "{{ certificate_create.certificate.id }}"
  register: certificate_info

- name: certificate | list
  doboto_certificate:
    action: list
  register: certificates_list

- name: certificate | destroy
  doboto_certificate:
    action: destroy
    id: "{{ certificate_create.certificate.id }}"
  register: certificate_destroy
'''


class Certificate(DOBOTOModule):

    def input(self):

        return AnsibleModule(argument_spec=dict(
            action=dict(default=None, required=True, choices=[
                "list",
                "create",
                "present",
                "info",
                "destroy",
            ]),
            token=dict(default=None),
            id=dict(default=None),
            name=dict(default=None),
            private_key=dict(default=None),
            leaf_certificate=dict(default=None),
            certificate_chain=dict(default=None),
            url=dict(default=self.url),
        ))

    def list(self):
        self.module.exit_json(changed=False, certificates=self.do.certificate.list())

    @require("name")
    @require("private_key")
    @require("leaf_certificate")
    @require("certificate_chain")
    def create(self):

        certificate = self.do.certificate.create(
            self.module.params["name"],
            self.module.params["private_key"],
            self.module.params["leaf_certificate"],
            self.module.params["certificate_chain"]
        )
        self.module.exit_json(changed=True, certificate=certificate)

    @require("name")
    @require("private_key")
    @require("leaf_certificate")
    @require("certificate_chain")
    def present(self):

        (certificate, created) = self.do.certificate.present(
            self.module.params["name"],
            self.module.params["private_key"],
            self.module.params["leaf_certificate"],
            self.module.params["certificate_chain"]
        )
        self.module.exit_json(
            changed=(created is not None),
            certificate=certificate, created=created
        )

    @require("id")
    def info(self):
        self.module.exit_json(changed=False, certificate=self.do.certificate.info(
            self.module.params["id"]
        ))

    @require("id")
    def destroy(self):
        self.module.exit_json(changed=True, result=self.do.certificate.destroy(
            id=self.module.params["id"]
        ))


if __name__ == '__main__':
    Certificate()
