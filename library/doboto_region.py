#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.doboto_module import DOBOTOModule

"""
Ansible module to manage DigitalOcean regions
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
module: doboto_region

short_description: Manage DigitalOcean Regions
description: Manages DigitalOcean regions
version_added: "0.1"
author: "SWE Data <swe-data@do.co>"
options:
    token:
        description: token to use to connect to the API (uses DO_API_TOKEN from ENV if not found)
    action:
        description: region action
        choices:
            - list
    url:
        description: URL to use if not official (for experimenting)
'''

EXAMPLES = '''
- name: region | list
  doboto_region:
    action: list
  register: region_list
'''


class Region(DOBOTOModule):

    def input(self):

        return AnsibleModule(argument_spec=dict(
            action=dict(default=None, required=True, choices=[
                "list"
            ]),
            token=dict(default=None, no_log=True),
            url=dict(default=self.url)
        ))

    def list(self):
        self.module.exit_json(changed=False, regions=self.do.region.list())


if __name__ == '__main__':
    Region()
