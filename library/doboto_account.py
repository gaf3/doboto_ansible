#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
(c) 2017, DigitalOcean, SWE Data <swe-data@do.co>

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
module: doboto_account
short_description: Manage DigitalOcean Account
description: Manages DigitalOcean account
version_added: "2.4"
author:
  - "Gaffer Fitch (@gaf3)"
  - "Ben Mildren (@bmildren)"
  - "Cole Tuininga (@egon1024)"
  - "Josh Bradley (@aww-yiss)"
options:
    action:
        description: account action
        choices:
            - info
extends_documentation_fragment: digitalocean_doboto
'''

EXAMPLES = '''
- name: account | info
  doboto_account:
    action: info
  register: account_info
'''

RETURNS = '''

'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.digitalocean_doboto import DOBOTOModule

class Account(DOBOTOModule):

    def input(self):

        argument_spec = self.argument_spec()

        argument_spec.update(
            dict(
                action=dict(required=True, default="info", choices=[
                    "info"])
            )
        )

        return AnsibleModule(
            argument_spec=argument_spec,
            supports_check_mode=True
        )

    def info(self):

        self.module.exit_json(
            changed=False,
            account=self.do.account.info()
        )

if __name__ == '__main__':
    Account()
