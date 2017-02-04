#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from ansible.module_utils.basic import AnsibleModule
from doboto.DO import DO
from doboto.DOBOTOException import DOBOTOException

"""

Ansible module to manage DigitalOcean sizes
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
module: doboto_size

short_description: Manage DigitalOcean Sizes
description:
    - Manages DigitalOcean sizes
version_added: "0.1"
author: "SWE Data <swe-data@do.co>"
options:
    token:
        description:
            - token to use to connect to the API (uses DO_API_TOKEN from ENV if not found)
    action:
        size action
        choices:
            - list
    url:
        description:
            - URL to use if not official (for experimenting)
'''

EXAMPLES = '''
'''


class Size(object):

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
                "list"
            ]),
            token=dict(default=None),
            url=dict(default=self.url)
        ))

    def act(self):
        try:
            getattr(self, self.module.params["action"])()
        except DOBOTOException as exception:
            self.module.fail_json(msg=exception.message, result=exception.result)

    def list(self):
        self.module.exit_json(changed=False, sizes=self.do.size.list())


Size()
