#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import copy
from ansible.module_utils.basic import AnsibleModule
from doboto.DO import DO

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


class Volume(object):

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
                "create",
                "info",
                "list",
                "snapshots",
                "snapshot",
                "destroy",
                "attach",
                "detach",
                "resize",
                "actions",
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

    def act(self):

        getattr(self, self.module.params["action"])()

    def list(self):

        result = None

        if self.module.params["region"] is not None:
            result = self.do.volume.list(region=self.module.params["region"])
        else:
            result = self.do.volume.list()

        if "volumes" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, volumes=result["volumes"])

    def create(self):

        attribs = {}

        if self.module.params["size_gigabytes"] is None:
            self.module.fail_json(msg="the size_gigabytes parameter is required")

        if self.module.params["name"] is None:
            self.module.fail_json(msg="the name parameter is required")

        attribs = {
            "size_gigabytes": self.module.params["size_gigabytes"],
            "name": self.module.params["name"]
        }

        if self.module.params["region"] is not None:
            attribs["region"] = self.module.params["region"]
        elif self.module.params["snapshot_id"] is not None:
            attribs["snapshot_id"] = self.module.params["snapshot_id"]
        else:
            self.module.fail_json(msg="the region or snapshot_id parameters is required")

        if self.module.params["description"] is not None:
            attribs["description"] = self.module.params["description"]

        result = self.do.volume.create(attribs)

        if "volume" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        start_time = time.time()

        while self.module.params["wait"]:

            time.sleep(self.module.params["poll"])

            latest = self.do.volume.info(result['volume']["id"])
            if "volume" in latest:
                break

            if time.time() - start_time > self.module.params["timeout"]:
                self.module.fail_json(
                    msg="Timeout on polling", volume=result['volume'], latest=latest
                )

        self.module.exit_json(changed=True, volume=result['volume'])

    def info(self):

        result = None

        if self.module.params["id"] is not None:

            result = self.do.volume.info(id=self.module.params["id"])

            if "volume" not in result:
                self.module.fail_json(msg="DO API error", result=result)

            self.module.exit_json(changed=False, volume=result["volume"])

        elif self.module.params["name"] is not None and self.module.params["region"] is not None:

            result = self.do.volume.info(
                name=self.module.params["name"], region=self.module.params["region"]
            )

            if "volumes" not in result:
                self.module.fail_json(msg="DO API error", result=result)

            self.module.exit_json(changed=False, volume=result["volumes"][0])

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

        if "status" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=True, result=result)

    def snapshot_list(self):

        if self.module.params["id"] is None:
            self.module.fail_json(msg="the id parameter is required")

        result = self.do.volume.snapshot_list(id=self.module.params["id"])

        if "snapshots" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, snapshots=result["snapshots"])

    def snapshot_create(self):

        if self.module.params["id"] is None:
            self.module.fail_json(msg="the id parameter is required")

        if self.module.params["snapshot_name"] is None:
            self.module.fail_json(msg="the snapshot_name parameter is required")

        result = self.do.volume.snapshot_create(
            id=self.module.params["id"], snapshot_name=self.module.params["snapshot_name"]
        )

        if "snapshot" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=True, snapshot=result["snapshot"])

    def action_result(self, result):

        if "action" in result:

            action = result["action"]

            start_time = time.time()

            while self.module.params["wait"] and result["action"]["status"] == "in-progress":

                time.sleep(self.module.params["poll"])
                latest = self.do.action.info(action["id"])
                if "action" in latest:
                    result = latest

                if time.time() - start_time > self.module.params["timeout"]:
                    self.module.fail_json(msg="Timeout on polling", action=result['action'])

            self.module.exit_json(changed=True, action=result["action"])

        else:

            self.module.fail_json(msg="DO API error", result=result)

    def attach(self):

        result = None

        if self.module.params["droplet_id"] is None:
            self.module.fail_json(msg="the droplet_id parameter is required")

        if self.module.params["id"] is not None:

            result = self.do.volume.attach(
                id=self.module.params["id"],
                droplet_id=self.module.params["droplet_id"],
                region=self.module.params["region"]
            )

        elif self.module.params["name"] is not None and self.module.params["region"] is not None:

            result = self.do.volume.attach(
                name=self.module.params["name"],
                droplet_id=self.module.params["droplet_id"],
                region=self.module.params["region"]
            )

        else:

            self.module.fail_json(msg="the id or name and region parameters are required")

        self.action_result(result)

    def detach(self):

        result = None

        if self.module.params["droplet_id"] is None:
            self.module.fail_json(msg="the droplet_id parameter is required")

        if self.module.params["id"] is not None:

            result = self.do.volume.detach(
                id=self.module.params["id"],
                droplet_id=self.module.params["droplet_id"],
                region=self.module.params["region"]
            )

        elif self.module.params["name"] is not None:

            result = self.do.volume.detach(
                name=self.module.params["name"],
                droplet_id=self.module.params["droplet_id"],
                region=self.module.params["region"]
            )

        else:

            self.module.fail_json(msg="the id or name and region parameters are required")

        self.action_result(result)

    def resize(self):

        result = None

        if self.module.params["id"] is None:
            self.module.fail_json(msg="the id parameter is required")

        if self.module.params["size_gigabytes"] is None:
            self.module.fail_json(msg="the size_gigabytes parameter is required")

        result = self.do.volume.resize(
            self.module.params["id"],
            self.module.params["size_gigabytes"],
            region=self.module.params["region"]
        )

        self.action_result(result)

    def action_list(self):

        if self.module.params["id"] is None:
            self.module.fail_json(msg="the id parameter is required")

        result = self.do.volume.action_list(self.module.params["id"])

        if "actions" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, actions=result["actions"])

    def action_info(self):

        result = None

        if self.module.params["id"] is None:
            self.module.fail_json(msg="the id parameter is required")

        if self.module.params["action_id"] is None:
            self.module.fail_json(msg="the action_id parameter is required")

        result = self.do.volume.action_info(
            self.module.params["id"], self.module.params["action_id"]
        )

        if "action" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, action=result["action"])


Volume()
