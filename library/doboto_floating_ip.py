#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.doboto_module import require, DOBOTOModule

"""
Ansible module to manage DigitalOcean floating_ips
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
module: doboto_floating_ip

short_description: Manage DigitalOcean Floating IPs
description:
    - Manages DigitalOcean Floating IPs
version_added: "0.1"
author: "SWE Data <swe-data@do.co>"
options:
    token:
        description:
            - token to use to connect to the API (uses DO_API_TOKEN from ENV if not found)
    action:
        floating_ip action
        choices:
            - list
            - create
            - info
            - destroy
            - assign
            - unassign
            - action_list
            - action_info
    ip:
        description:
            - same as DO API variable
    region:
        description:
            - same as DO API variable
    droplet_id:
        description:
            - same as DO API variable
    wait:
        description:
            - wait until tasks has completed before continuing
    poll:
        description:
            - poll value to check while waiting (default 5 seconds)
    timeout:
        description:
            - timeout value to give up after waiting (default 300 seconds)
    action_id:
        description:
            - same as DO API variable (action id)
    url:
        description:
            - URL to use if not official (for experimenting)
'''

EXAMPLES = '''
'''


class FloatingIP(DOBOTOModule):

    def input(self):

        return AnsibleModule(argument_spec=dict(
            action=dict(default=None, required=True, choices=[
                "list",
                "create",
                "info",
                "destroy",
                "assign",
                "unassign",
                "action_list",
                "action_info"
            ]),
            token=dict(default=None),
            ip=dict(default=None),
            region=dict(default=None),
            droplet_id=dict(default=None),
            wait=dict(default=False, type='bool'),
            poll=dict(default=5, type='int'),
            timeout=dict(default=300, type='int'),
            action_id=dict(default=None),
            url=dict(default=self.url)
        ))

    def list(self):
        self.module.exit_json(changed=False, floating_ips=self.do.floating_ip.list())

    @require("droplet_id", "region")
    def create(self):

        floating_ip = self.do.floating_ip.create(
            droplet_id=self.module.params["droplet_id"],
            region=self.module.params["region"]
        )

        start_time = time.time()

        while self.module.params["wait"] and \
              (self.module.params["droplet_id"] is None or floating_ip["droplet"]) is None and \
              (self.module.params["region"] is None or floating_ip["region"] is None):

            time.sleep(self.module.params["poll"])

            try:
                floating_ip = self.do.floating_ip.info(floating_ip["ip"])
            except:
                pass

            if time.time() - start_time > self.module.params["timeout"]:
                self.module.fail_json(msg="Timeout on polling", floating_ip=floating_ip)

        self.module.exit_json(changed=True, floating_ip=floating_ip)

    @require("ip")
    def info(self):
        self.module.exit_json(changed=False, floating_ip=self.do.floating_ip.info(
            self.module.params["ip"]
        ))

    @require("ip")
    def destroy(self):
        self.module.exit_json(changed=True, result=self.do.floating_ip.destroy(
            self.module.params["ip"]
        ))

    @require("ip")
    @require("droplet_id")
    def assign(self):
        self.action_result(self.do.floating_ip.assign(
            self.module.params["ip"], self.module.params["droplet_id"]
        ))

    @require("ip")
    def unassign(self):
        self.action_result(self.do.floating_ip.unassign(
            self.module.params["ip"]
        ))

    @require("ip")
    def action_list(self):
        self.module.exit_json(changed=False, actions=self.do.floating_ip.action_list(
            self.module.params["ip"]
        ))

    @require("ip")
    @require("action_id")
    def action_info(self):
        self.module.exit_json(changed=False, action=self.do.floating_ip.action_info(
            self.module.params["ip"], self.module.params["action_id"]
        ))


FloatingIP()
