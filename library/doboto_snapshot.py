#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import copy
from ansible.module_utils.basic import AnsibleModule
from doboto.DO import DO

"""

Ansible module to manage DigitalOcean snapshots
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
module: doboto_snapshot

short_description: Manage DigitalOcean snapshots
description:
    - Manages DigitalOcean Snapshots
version_added: "0.1"
author: "SWE Data <swe-data@do.co>"
options:
    token:
        description:
            - token to use to connect to the API (uses DO_API_TOKEN from ENV if not found)
    action:
        snapshot action
        choices:
            - info
            - list
            - destroy
    id:
        description:
            - same as DO API variable (snapshot id)
    resource_type:
        description:
            - same as DO API variable
    url:
        description:
            - URL to use if not official (for experimenting)

'''

EXAMPLES = '''
'''


class Snapshot(object):

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
                "info",
                "list",
                "destroy"
            ]),
            token=dict(default=None),
            id=dict(default=None),
            resource_type=dict(default=None),
            url=dict(default=self.url),
            extra=dict(default=None, type='dict'),
        ))

    def act(self):

        getattr(self, self.module.params["action"])()

    def list(self):

        result = None

        result = self.do.snapshot.list(resource_type=self.module.params["resource_type"])

        if "snapshots" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, snapshots=result["snapshots"])

    def info(self):

        if self.module.params["id"] is None:
            self.module.fail_json(msg="the id parameter is required")

        result = self.do.snapshot.info(id=self.module.params["id"])

        if "snapshot" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, snapshot=result["snapshot"])

    def destroy(self):

        if self.module.params["id"] is None:
            self.module.fail_json(msg="the id parameter is required")

        result = self.do.snapshot.destroy(id=self.module.params["id"])

        if "status" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=True, result=result)


Snapshot()
