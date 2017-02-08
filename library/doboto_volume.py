#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.doboto_module import require, DOBOTOModule

"""
Ansible module to manage DigitalOcean volumes
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
module: doboto_volume

short_description: Manage DigitalOcean volumes
description:
    - Manages DigitalOcean Block Storage
version_added: "0.1"
author: "SWE Data <swe-data@do.co>"
options:
    token:
        description:
            - token to use to connect to the API (uses DO_API_TOKEN from ENV if not found)
    action:
        volume action
        choices:
            - list
            - create
            - info
            - destroy
            - snapshot_list
            - snapshot_create
            - attach
            - detach
            - resize
            - action_list
            - action_info
    id:
        description:
            - same as DO API variable (volume id)
    name:
        description:
            - same as DO API variable
    description:
        description:
            - same as DO API variable
    region:
        description:
            - same as DO API variable
    size_gigabytes:
        description:
            - same as DO API variable
    snapshot_id:
        description:
            - same as DO API variable
    snapshot_name:
        description:
            - name to give a snapshot
    droplet_id:
        description:
            - same as DO API variable
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


class Volume(DOBOTOModule):

    def input(self):

        return AnsibleModule(argument_spec=dict(
            action=dict(default=None, required=True, choices=[
                "list",
                "create",
                "info",
                "destroy",
                "snapshot_list",
                "snapshot_create",
                "attach",
                "detach",
                "resize",
                "action_list",
                "action_info"
            ]),
            token=dict(default=None),
            id=dict(default=None),
            name=dict(default=None),
            description=dict(default=None),
            region=dict(default=None),
            size_gigabytes=dict(default=None),
            snapshot_id=dict(default=None),
            snapshot_name=dict(default=None),
            droplet_id=dict(default=None),
            wait=dict(default=False, type='bool'),
            poll=dict(default=5, type='int'),
            timeout=dict(default=300, type='int'),
            action_id=dict(default=None),
            url=dict(default=self.url)
        ))

    def list(self):
        self.module.exit_json(changed=False, volumes=self.do.volume.list(
            region=self.module.params["region"]
        ))

    @require("name")
    @require("size_gigabytes")
    @require("region", "snapshot_id")
    def create(self):

        attribs = {
            "size_gigabytes": self.module.params["size_gigabytes"],
            "name": self.module.params["name"]
        }

        for param in ["region", "snapshot_id", "description"]:
            if self.module.params[param] is not None:
                attribs[param] = self.module.params[param]

        volume = self.do.volume.create(attribs)
        start_time = time.time()

        while self.module.params["wait"]:

            time.sleep(self.module.params["poll"])

            try:
                volume = self.do.volume.info(volume["id"])
                break
            except:
                pass

            if time.time() - start_time > self.module.params["timeout"]:
                self.module.fail_json(
                    msg="Timeout on polling", volume=volume
                )

        self.module.exit_json(changed=True, volume=volume)

    def info(self):

        result = None

        if self.module.params["id"] is not None:

            self.module.exit_json(changed=False, volume=self.do.volume.info(
                id=self.module.params["id"]
            ))

        elif self.module.params["name"] is not None and self.module.params["region"] is not None:

            self.module.exit_json(changed=False, volume=self.do.volume.info(
                name=self.module.params["name"], region=self.module.params["region"]
            ))

        else:
            self.module.fail_json(msg="the id or name and region parameters are required")

    def destroy(self):

        result = None

        if self.module.params["id"] is not None:

            result = self.do.volume.destroy(id=self.module.params["id"])

        elif self.module.params["name"] is not None and self.module.params["region"] is not None:

            result = self.do.volume.destroy(
                name=self.module.params["name"], region=self.module.params["region"]
            )

        else:
            self.module.fail_json(msg="the id or name and region parameters are required")

        self.module.exit_json(changed=True, result=result)

    @require("id")
    def snapshot_list(self):
        self.module.exit_json(changed=False, snapshots=self.do.volume.snapshot_list(
            id=self.module.params["id"]
        ))

    @require("id")
    @require("snapshot_name")
    def snapshot_create(self):
        self.module.exit_json(changed=True, snapshot=self.do.volume.snapshot_create(
            id=self.module.params["id"], snapshot_name=self.module.params["snapshot_name"]
        ))

    @require("id", "name")
    @require("droplet_id")
    def attach(self):
        self.action_result(self.do.volume.attach(
            id=self.module.params["id"],
            name=self.module.params["name"],
            droplet_id=self.module.params["droplet_id"],
            region=self.module.params["region"]
        ))

    @require("id", "name")
    @require("droplet_id")
    def detach(self):
        self.action_result(self.do.volume.detach(
            id=self.module.params["id"],
            name=self.module.params["name"],
            droplet_id=self.module.params["droplet_id"],
            region=self.module.params["region"]
        ))

    @require("id", "name")
    @require("size_gigabytes")
    def resize(self):
        self.action_result(self.do.volume.resize(
            self.module.params["id"],
            self.module.params["size_gigabytes"],
            region=self.module.params["region"]
        ))

    @require("id")
    def action_list(self):
        self.module.exit_json(changed=False, actions=self.do.volume.action_list(
            self.module.params["id"]
        ))

    @require("id")
    @require("action_id")
    def action_info(self):
        self.module.exit_json(changed=False, action=self.do.volume.action_info(
            self.module.params["id"], self.module.params["action_id"]
        ))


Volume()
