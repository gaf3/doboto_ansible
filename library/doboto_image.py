#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.doboto_module import require, DOBOTOModule

"""
Ansible module to manage DigitalOcean images
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
module: doboto_image

short_description: Manage DigitalOcean images
description:
    - Manages DigitalOcean Images
version_added: "0.1"
author: "SWE Data <swe-data@do.co>"
options:
    token:
        description:
            - token to use to connect to the API (uses DO_API_TOKEN from ENV if not found)
    action:
        image action
        choices:
            - list
            - info
            - update
            - destroy
            - convert
            - transfer
            - action_list
            - action_info
    id:
        description:
            - same as DO API variable (image id)
    slug:
        description:
            - same as DO API variable (for info)
    name:
        description:
            - same as DO API variable (for update)
    type:
        description:
            - same as DO API variable (distribution or application)
    private:
        description:
            - same as DO API variable (true for user images)
    region:
        description:
            - same as DO API variable (for transferring images)
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


class Image(DOBOTOModule):

    def input(self):

        return AnsibleModule(argument_spec=dict(
            action=dict(default=None, required=True, choices=[
                "list",
                "info",
                "update",
                "destroy",
                "convert",
                "transfer",
                "action_list",
                "action_info"
            ]),
            token=dict(default=None),
            id=dict(default=None),
            slug=dict(default=None),
            name=dict(default=None),
            type=dict(default=None),
            private=dict(default=None, type='bool'),
            region=dict(default=None),
            wait=dict(default=False, type='bool'),
            poll=dict(default=5, type='int'),
            timeout=dict(default=300, type='int'),
            action_id=dict(default=None),
            url=dict(default=self.url)
        ))

    def list(self):
        self.module.exit_json(changed=False, images=self.do.image.list(
            type=self.module.params["type"],
            private=('true' if self.module.params["private"] else 'false')
        ))

    @require("id", "slug")
    def info(self):
        self.module.exit_json(changed=False, image=self.do.image.info(
            self.module.params["id"] or self.module.params["slug"]
        ))

    @require("id")
    @require("name")
    def update(self):
        self.module.exit_json(changed=True, image=self.do.image.update(
            self.module.params["id"], self.module.params["name"]
        ))

    @require("id")
    def destroy(self):
        self.module.exit_json(changed=True, result=self.do.image.destroy(
            self.module.params["id"]
        ))

    @require("id")
    def convert(self):
        self.module.exit_json(changed=True, action=self.do.image.convert(
            self.module.params["id"],
            wait=self.module.params["wait"],
            poll=self.module.params["poll"],
            timeout=self.module.params["timeout"]
        ))

    @require("id")
    @require("region")
    def transfer(self):
        self.module.exit_json(changed=True, action=self.do.image.transfer(
            self.module.params["id"], self.module.params["region"],
            wait=self.module.params["wait"],
            poll=self.module.params["poll"],
            timeout=self.module.params["timeout"]
        ))

    @require("id")
    def action_list(self):
        self.module.exit_json(changed=False, actions=self.do.image.action_list(
            self.module.params["id"]
        ))

    @require("id")
    @require("action_id")
    def action_info(self):
        self.module.exit_json(changed=False, action=self.do.image.action_info(
            self.module.params["id"], self.module.params["action_id"]
        ))


Image()
