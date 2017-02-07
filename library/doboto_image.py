#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import copy
from ansible.module_utils.basic import AnsibleModule
from doboto.DO import DO
from doboto.DOBOTOException import DOBOTOException

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


def require(*required):
    def requirer(function):
        def wrapper(*args, **kwargs):
            params = required
            if not isinstance(params, tuple):
                params = (params,)
            met = False
            for param in params:
                if args[0].module.params[param] is not None:
                    met = True
            if not met:
                args[0].module.fail_json(msg="the %s parameter is required" % " or ".join(params))
            function(*args, **kwargs)
        return wrapper
    return requirer


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

    def act(self):
        try:
            getattr(self, self.module.params["action"])()
        except DOBOTOException as exception:
            self.module.fail_json(msg=exception.message, result=exception.result)

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

    def action_result(self, action):

        start_time = time.time()

        while self.module.params["wait"] and action["status"] == "in-progress":

            time.sleep(self.module.params["poll"])
            try:
                action = self.do.action.info(action["id"])
            except:
                pass

            if time.time() - start_time > self.module.params["timeout"]:
                self.module.fail_json(msg="Timeout on polling", action=result['action'])

        self.module.exit_json(changed=True, action=action)

    @require("id")
    def convert(self):
        self.action_result(self.do.image.convert(self.module.params["id"]))

    @require("id")
    @require("region")
    def transfer(self):
        self.action_result(self.do.image.transfer(
            self.module.params["id"], self.module.params["region"]
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
