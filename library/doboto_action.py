#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.doboto_module import require, DOBOTOModule

"""
Ansible module to manage DigitalOcean actions
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


class Action(DOBOTOModule):

    def input(self):
        return AnsibleModule(argument_spec=dict(
            action=dict(default=None, required=True, choices=[
                "list", "info"
            ]),
            token=dict(default=None),
            id=dict(default=None),
            url=dict(default=self.url),
        ))

    def list(self):
        self.module.exit_json(changed=False, actions=self.do.action.list())

    @require("id")
    def info(self):
        self.module.exit_json(changed=False, action=self.do.action.info(
            self.module.params["id"]
        ))


Action()
