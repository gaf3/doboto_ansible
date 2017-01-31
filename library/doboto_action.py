#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from ansible.module_utils.basic import AnsibleModule
from doboto.DO import DO

"""

Ansible module to manage DigitalOcean actions
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
module: doboto_action

short_description: Manage DigitalOcean Actions
description:
    - Manages DigitalOcean actions
version_added: "0.1"
author: "SWE Data <swe-data@do.co>"
options:
    token:
        description:
            - token to use to connect to the API (uses DO_API_TOKEN from ENV if not found)
    action:
        action action
        choices:
            - list
            - info
    id:
        description:
            - (Action ID) same as DO API variable
    url:
        description:
            - URL to use if not official (for experimenting)
'''

EXAMPLES = '''
'''


class Action(object):

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
                "list", "info"
            ]),
            token=dict(default=None),
            id=dict(default=None),
            url=dict(default=self.url),
        ))

    def act(self):

        getattr(self, self.module.params["action"])()

    def list(self):

        result = self.do.action.list()

        if "actions" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, actions=result["actions"])

    def info(self):

        result = None

        if self.module.params["id"] is None:
            self.module.fail_json(msg="the id parameter is required")

        result = self.do.action.info(self.module.params["id"])

        if "action" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, action=result["action"])


Action()
