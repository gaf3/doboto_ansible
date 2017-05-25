#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
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

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: doboto_action

short_description: Manage DigitalOcean Actions
description: Manages DigitalOcean actions
version_added: "2.4"
author:
  - "Gaffer Fitch (@gaf3)"
  - "Ben Mildren (@bmildren)"
  - "Cole Tuininga (@egon1024)"
  - "Josh Bradley (@aww-yiss)"
options:
    token:
        description: token to use to connect to the API (uses DO_API_TOKEN from ENV if not found)
    action:
        description: action action
        choices:
            - list
            - info
    id:
        description: (Action ID) same as DO API variable
    url:
        description: URL to use if not official (for experimenting)
'''

EXAMPLES = '''
- name: action | list
  doboto_action:
    action: list
  register: action_list

- name: action | info
  doboto_action:
    action: info
    id: "{{ action_list.actions[0].id }}"
  register: action_info
'''

RETURNS = '''

'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.digitalocean_doboto import DOBOTOModule

class Action(DOBOTOModule):

    def input(self):

        argument_spec = self.argument_spec()

        argument_spec.update(
            dict(
                action=dict(required=True, default="list", choices=[
                    "list",
                    "info"]),
                id=dict(default=None)
            )
        )

        return AnsibleModule(
            argument_spec=argument_spec,
            supports_check_mode=True,
            required_if=[
                ["action", "info", ["id"]]
            ]
        )

    def list(self):

        self.module.exit_json(
            changed=False,
            actions=self.do.action.list()
        )

    def info(self):

        self.module.exit_json(
            changed=False,
            action=self.do.action.info(self.module.params["id"])
        )

if __name__ == '__main__':
    Action()
