#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import copy
from ansible.module_utils.basic import AnsibleModule
from doboto.DO import DO

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
            - create
            - list
            - info
            - destroy
            - assign
            - unassign
            - actions
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


class FloatingIP(object):

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
                "create",
                "list",
                "info",
                "destroy",
                "assign",
                "unassign",
                "actions",
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

    def act(self):

        getattr(self, self.module.params["action"])()

    def create(self):

        result = None

        if self.module.params["droplet_id"] is not None:

            result = self.do.floating_ip.create(droplet_id=self.module.params["droplet_id"])

            if "floating_ip" not in result:
                self.module.fail_json(msg="DO API error", result=result)

            start_time = time.time()

            while self.module.params["wait"] and result["floating_ip"]["droplet"] is None:

                time.sleep(self.module.params["poll"])
                latest = self.do.floating_ip.info(result["floating_ip"]["ip"])
                if "floating_ip" in latest:
                    result = latest

                if time.time() - start_time > self.module.params["timeout"]:
                    self.module.fail_json(msg="Timeout on polling", result=result)

            self.module.exit_json(changed=True, floating_ip=result['floating_ip'])

        elif self.module.params["region"] is not None:

            result = self.do.floating_ip.create(region=self.module.params["region"])

            if "floating_ip" not in result:
                self.module.fail_json(msg="DO API error", result=result)

            start_time = time.time()

            while self.module.params["wait"] and result["floating_ip"]["region"] is None:

                time.sleep(self.module.params["poll"])
                latest = self.do.floating_ip.info(result["floating_ip"]["ip"])
                if "action" in latest:
                    result = latest

                if time.time() - start_time > self.module.params["timeout"]:
                    self.module.fail_json(msg="Timeout on polling", action=result['action'])

            self.module.exit_json(changed=True, floating_ip=result['floating_ip'])

        else:
            self.module.fail_json(msg="the dropelt_id or region parameter is required")

    def list(self):

        result = None

        result = self.do.floating_ip.list()

        if "floating_ips" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, floating_ips=result["floating_ips"])

    def info(self):

        if self.module.params["ip"] is None:
            self.module.fail_json(msg="the ip parameter is required")

        result = self.do.floating_ip.info(self.module.params["ip"])

        if "floating_ip" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, floating_ip=result["floating_ip"])

    def destroy(self):

        if self.module.params["ip"] is None:
            self.module.fail_json(msg="the ip parameter is required")

        result = self.do.floating_ip.destroy(self.module.params["ip"])

        if "status" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=True, result=result)

    def action_result(self, result):

        if "action" in result:

            action = result["action"]

            start_time = time.time()

            while self.module.params["wait"] and result["action"]["status"] == "in-progress":

                time.sleep(self.module.params["poll"])
                latest = self.do.action.info(action["id"])
                if "action" in latest:
                    result = latest

                if time.time() - start_time > self.module.params["timeout"]:
                    self.module.fail_json(msg="Timeout on polling", action=result['action'])

            self.module.exit_json(changed=True, action=result["action"])

        else:

            self.module.fail_json(msg="DO API error", result=result)

    def assign(self):

        if self.module.params["ip"] is None:
            self.module.fail_json(msg="the ip parameter is required")

        if self.module.params["droplet_id"] is None:
            self.module.fail_json(msg="the droplet_id parameter is required")

        result = self.do.floating_ip.assign(
            self.module.params["ip"], self.module.params["droplet_id"]
        )

        self.action_result(result)

    def unassign(self):

        if self.module.params["ip"] is None:
            self.module.fail_json(msg="the ip parameter is required")

        result = self.do.floating_ip.unassign(
            self.module.params["ip"]
        )

        self.action_result(result)

    def actions(self):

        if self.module.params["ip"] is None:
            self.module.fail_json(msg="the id parameter is required")

        result = self.do.floating_ip.actions(self.module.params["ip"])

        if "actions" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, actions=result["actions"])

    def action_info(self):

        result = None

        if self.module.params["ip"] is None:
            self.module.fail_json(msg="the id parameter is required")

        if self.module.params["action_id"] is None:
            self.module.fail_json(msg="the action_id parameter is required")

        result = self.do.floating_ip.action_info(
            self.module.params["ip"], self.module.params["action_id"]
        )

        if "action" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, action=result["action"])


FloatingIP()
