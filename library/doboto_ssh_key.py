#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from ansible.module_utils.basic import AnsibleModule
from doboto.DO import DO

"""

Ansible module to manage DigitalOcean ssh keys
(c) 2017, Gaffer Fitch <gfitch@digitalocean.com>

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
author: "Gaffer Fitch <gfitch@digitalocean.com>"
options:
    token:
        description:
            - token to use to connect to the API (uses DO_API_TOKEN from ENV if not found)
    action:
        ssh key action
        choices:
            - create
            - present
            - list
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


class SSHKey(object):

    url = "https://api.digitalocean.com/v2"

    def __init__(self):

        self.module = self.input()

        token = self.module.params["token"]

        if token is None:
            token = os.environ.get('DO_API_TOKEN', None)

        if token is None:
            self.module.fail_json(msg="the token parameter is required")

        self.do = DO(url=self.module.params["url"], token=token)

        self.act()

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

    def act(self):

        getattr(self, self.module.params["action"])()

    def create(self):

        if self.module.params["name"] is None:
            self.module.fail_json(msg="the name parameter is required")

        if self.module.params["public_key"] is None:
            self.module.fail_json(msg="the public_key parameter is required")

        result = self.do.ssh_key.create(
            self.module.params["name"], self.module.params["public_key"]
        )

        if "ssh_key" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=True, ssh_key=result['ssh_key'])

    def present(self):

        if self.module.params["name"] is None:
            self.module.fail_json(msg="the name parameter is required")

        result = self.do.ssh_key.list()

        if "ssh_keys" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        ssh_keys = result["ssh_keys"]

        existing = None
        for ssh_key in ssh_keys:
            if self.module.params["name"] == ssh_key["name"]:
                existing = ssh_key
                break

        if existing is not None:
            self.module.exit_json(changed=False, ssh_key=existing)
        else:
            self.create()

    def list(self):

        result = self.do.ssh_key.list()

        if "ssh_keys" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, ssh_keys=result["ssh_keys"])

    def info(self):

        result = None

        if self.module.params["id"] is not None:
            result = self.do.ssh_key.info(self.module.params["id"])
        elif self.module.params["fingerprint"] is not None:
            result = self.do.ssh_key.info(self.module.params["fingerprint"])
        else:
            self.module.fail_json(msg="the id or fingerprint parameter is required")

        if "ssh_key" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, ssh_key=result["ssh_key"])

    def update(self):

        result = None

        if self.module.params["name"] is None:
            self.module.fail_json(msg="the name parameter is required")

        if self.module.params["id"] is not None:
            result = self.do.ssh_key.update(self.module.params["id"], self.module.params["name"])
        elif self.module.params["fingerprint"] is not None:
            result = self.do.ssh_key.update(
                self.module.params["fingerprint"], self.module.params["name"]
            )
        else:
            self.module.fail_json(msg="the id or fingerprint parameter is required")

        if "ssh_key" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=True, ssh_key=result["ssh_key"])

    def destroy(self):

        result = None

        if self.module.params["id"] is not None:
            result = self.do.ssh_key.destroy(self.module.params["id"])
        elif self.module.params["fingerprint"] is not None:
            result = self.do.ssh_key.destroy(self.module.params["fingerprint"])
        else:
            self.module.fail_json(msg="the id or fingerprint parameter is required")

        if "status" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=True, result=result)


SSHKey()
