#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.doboto_module import require, DOBOTOModule

"""
Ansible module to manage DigitalOcean ssh keys
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
module: doboto_ssh_key

short_description: Manage DigitalOcean SSH Keys
description:
    - Manages DigitalOcean ssh keys
version_added: "0.1"
author: "SWE Data <swe-data@do.co>"
options:
    token:
        description:
            - token to use to connect to the API (uses DO_API_TOKEN from ENV if not found)
    action:
        ssh key action
        choices:
            - list
            - create
            - present
            - info
            - update
            - destroy
    id:
        description:
            - (SSH Key ID) same as DO API variable
    name:
        description:
            - same as DO API variable
    public_key:
        description:
            - same as DO API variable
    fingerprint:
        description:
            - same as DO API variable
    url:
        description:
            - URL to use if not official (for experimenting)
'''

EXAMPLES = '''
'''


class SSHKey(DOBOTOModule):

    def input(self):

        return AnsibleModule(argument_spec=dict(
            action=dict(default=None, required=True, choices=[
                "create", "present", "list", "info", "update", "destroy"
            ]),
            token=dict(default=None),
            id=dict(default=None),
            fingerprint=dict(default=None),
            public_key=dict(default=None),
            name=dict(default=None),
            url=dict(default=self.url),
        ))

    def list(self):
        self.module.exit_json(changed=False, ssh_keys=self.do.ssh_key.list())

    @require("name")
    @require("public_key")
    def create(self):
        self.module.exit_json(changed=True, ssh_key=self.do.ssh_key.create(
            self.module.params["name"], self.module.params["public_key"]
        ))

    @require("name")
    def present(self):
        ssh_keys = self.do.ssh_key.list()

        existing = None
        for ssh_key in ssh_keys:
            if self.module.params["name"] == ssh_key["name"]:
                existing = ssh_key
                break

        if existing is not None:
            self.module.exit_json(changed=False, ssh_key=existing)
        else:
            self.create()

    @require("id", "fingerprint")
    def info(self):
        self.module.exit_json(changed=False, ssh_key=self.do.ssh_key.info(
            self.module.params["id"] or self.module.params["fingerprint"]
        ))

    @require("id", "fingerprint")
    @require("name")
    def update(self):
        self.module.exit_json(changed=True, ssh_key=self.do.ssh_key.update(
            self.module.params["id"] or self.module.params["fingerprint"],
            self.module.params["name"]
        ))

    @require("id", "fingerprint")
    def destroy(self):
        self.module.exit_json(changed=True, result=self.do.ssh_key.destroy(
            self.module.params["id"] or self.module.params["fingerprint"]
        ))


SSHKey()
