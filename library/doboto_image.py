#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import copy
from ansible.module_utils.basic import AnsibleModule
from doboto.DO import DO

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
            - info
            - list
            - update
            - destroy
            - actions
            - convert
            - transfer
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


class Image(object):

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
                "update",
                "destroy",
                "actions",
                "convert",
                "transfer",
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
            url=dict(default=self.url),
            extra=dict(default=None, type='dict'),
        ))

    def act(self):

        getattr(self, self.module.params["action"])()

    def info(self):

        result = None

        if self.module.params["id"] is not None:
            result = self.do.image.info(self.module.params["id"])
        elif self.module.params["slug"] is not None:
            result = self.do.image.info(self.module.params["slug"])
        else:
            self.module.fail_json(msg="the id or slug parameter is required")

        if "image" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, image=result["image"])

    def list(self):

        result = None

        if self.module.params["type"] is not None:
            result = self.do.image.list(type=self.module.params["type"])
        elif self.module.params["private"] is not None and self.module.params["private"]:
            result = self.do.image.list(private="true")
        else:
            result = self.do.image.list()

        if "images" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, images=result["images"])

    def update(self):

        if self.module.params["id"] is None:
            self.module.fail_json(msg="the id parameter is required")

        if self.module.params["name"] is None:
            self.module.fail_json(msg="the name parameter is required")

        result = self.do.image.update(self.module.params["id"], self.module.params["name"])

        if "image" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=True, image=result["image"])

    def destroy(self):

        if self.module.params["id"] is None:
            self.module.fail_json(msg="the id parameter is required")

        result = self.do.image.destroy(self.module.params["id"])

        if "status" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=True, result=result)

    def actions(self):

        if self.module.params["id"] is None:
            self.module.fail_json(msg="the id parameter is required")

        result = self.do.image.actions(self.module.params["id"])

        if "actions" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, actions=result["actions"])

    def action_result(self, result):

        if "action" in result:

            action = result["action"]

            start_time = time.time()

            while self.module.params["wait"] and result["action"]["status"] == "in-progress":

                time.sleep(self.module.params["poll"])
                latest = self.do.droplet.action_info(action["resource_id"], action["id"])
                if "action" in latest:
                    result = latest

                if time.time() - start_time > self.module.params["timeout"]:
                    self.module.fail_json(msg="Timeout on polling", action=result['action'])

            self.module.exit_json(changed=True, action=result["action"])

        else:

            self.module.fail_json(msg="DO API error", result=result)

    def convert(self):

        if self.module.params["id"] is None:
            self.module.fail_json(msg="the id parameter is required")

        result = self.do.image.convert(self.module.params["id"])
        self.action_result(result)

    def transfer(self):

        if self.module.params["id"] is None:
            self.module.fail_json(msg="the id parameter is required")

        if self.module.params["region"] is None:
            self.module.fail_json(msg="the region parameter is required")

        result = self.do.image.transfer(self.module.params["id"], self.module.params["region"])
        self.action_result(result)

    def action_info(self):

        result = None

        if self.module.params["id"] is None:
            self.module.fail_json(msg="the id parameter is required")

        if self.module.params["action_id"] is None:
            self.module.fail_json(msg="the action_id parameter is required")

        result = self.do.image.action_info(
            self.module.params["id"], self.module.params["action_id"]
        )

        if "action" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, action=result["action"])


Image()
