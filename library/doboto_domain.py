#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.doboto_module import require, DOBOTOModule

"""
Ansible module to manage DigitalOcean domains
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
module: doboto_domain

short_description: Manage DigitalOcean domains
description: Manages DigitalOcean Domains
version_added: "0.1"
author: "SWE Data <swe-data@do.co>"
options:
    token:
        description: token to use to connect to the API (uses DO_API_TOKEN from ENV if not found)
    action:
        description: domain action
        choices:
            - list
            - create
            - present
            - info
            - destroy
            - record_list
            - record_create
            - record_info
            - record_update
            - record_destroy
    name:
        description: same as DO API variable
    ip_address:
        description: same as DO API variable
    record_id:
        description: same as DO API variable id for records
    record_type:
        description: same as DO API variable type for records
    record_name:
        description: same as DO API variable name for records
    record_data:
        description: same as DO API variable data for records
    record_priority:
        description: same as DO API variable priority for records
    record_port:
        description: same as DO API variable port for records
    record_weight:
        description: same as DO API variable weight for records
    url:
        description: URL to use if not official (for experimenting)
'''

EXAMPLES = '''
- name: domain | create
  doboto_domain:
    action: create
    name: domain.create.com
    ip_address: "1.2.3.4"
  register: domain_create

- name: domain | list
  doboto_domain:
    action: list
  register: domain_list

- name: domain | present | new
  doboto_domain:
    action: present
    name: domain.present.com
    ip_address: "2.3.4.5"
  register: domain_present_new

- name: domain | info
  doboto_domain:
    action: info
    name: domain.create.com
  register: domain_info

- name: domain | record | list
  doboto_domain:
    action: record_list
    name: domain.create.com
  register: domain_record_list

- name: domain | record | create
  doboto_domain:
    action: record_create
    name: domain.create.com
    record_type: CNAME
    record_name: www.domain.create.com
    record_data: domain.create.com.
  register: domain_record_create

- name: domain | record | info
  doboto_domain:
    action: record_info
    name: domain.create.com
    record_id: "{{ domain_record_create.domain_record.id }}"
  register: domain_record_info

- name: domain | record | update
  doboto_domain:
    action: record_update
    name: domain.create.com
    record_id: "{{ domain_record_create.domain_record.id }}"
    record_name: w2.domain.create.com
    record_data: domain.create.com.
  register: domain_record_update

- name: domain | record | destroy
  doboto_domain:
    action: record_destroy
    name: domain.create.com
    record_id: "{{ domain_record_create.domain_record.id }}"
  register: domain_record_destroy

- name: domain | destroy
  doboto_domain:
    action: destroy
    name: domain.create.com
  register: domain_destroy

'''


class Domain(DOBOTOModule):

    def input(self):
        return AnsibleModule(argument_spec=dict(
            action=dict(default=None, required=True, choices=[
                "list",
                "create",
                "present",
                "info",
                "update",
                "destroy",
                "record_list",
                "record_create",
                "record_info",
                "record_update",
                "record_destroy"
            ]),
            token=dict(default=None, no_log=True),
            name=dict(default=None),
            ip_address=dict(default=None),
            record_id=dict(default=None),
            record_type=dict(default=None),
            record_name=dict(default=None),
            record_data=dict(default=None),
            record_priority=dict(default=None),
            record_port=dict(default=None),
            record_weight=dict(default=None),
            url=dict(default=self.url)
        ))

    def list(self):
        self.module.exit_json(changed=False, domains=self.do.domain.list())

    @require("name")
    @require("ip_address")
    def create(self):
        self.module.exit_json(changed=True, domain=self.do.domain.create(
            self.module.params["name"], self.module.params["ip_address"]
        ))

    @require("name")
    @require("ip_address")
    def present(self):
        (domain, created) = self.do.domain.present(
            self.module.params["name"], self.module.params["ip_address"]
        )
        self.module.exit_json(changed=(created is not None), domain=domain, created=created)

    @require("name")
    def info(self):
        self.module.exit_json(changed=False, domain=self.do.domain.info(
            self.module.params["name"])
        )

    @require("name")
    def destroy(self):
        self.module.exit_json(changed=True, result=self.do.domain.destroy(
            self.module.params["name"])
        )

    @require("name")
    def record_list(self):
        self.module.exit_json(changed=False, domain_records=self.do.domain.record_list(
            self.module.params["name"]
        ))

    @require("name")
    def record_create(self):

        attribs = {}

        for field in [
            "type",
            "name",
            "data",
            "priority",
            "port",
            "weight"
        ]:
            if self.module.params["record_%s" % field] is not None:
                attribs[field] = self.module.params["record_%s" % field]

        self.module.exit_json(changed=True, domain_record=self.do.domain.record_create(
            self.module.params["name"], attribs
        ))

    @require("name")
    @require("record_id")
    def record_info(self):
        self.module.exit_json(changed=False, domain_record=self.do.domain.record_info(
            self.module.params["name"], self.module.params["record_id"]
        ))

    @require("name")
    @require("record_id")
    def record_update(self):

        attribs = {}

        for field in [
            "type",
            "name",
            "data",
            "priority",
            "port",
            "weight"
        ]:
            if self.module.params["record_%s" % field] is not None:
                attribs[field] = self.module.params["record_%s" % field]

        self.module.exit_json(changed=True, domain_record=self.do.domain.record_update(
            self.module.params["name"], self.module.params["record_id"], attribs
        ))

    @require("name")
    @require("record_id")
    def record_destroy(self):
        self.module.exit_json(changed=True, result=self.do.domain.record_destroy(
            self.module.params["name"], self.module.params["record_id"]
        ))


if __name__ == '__main__':
    Domain()
