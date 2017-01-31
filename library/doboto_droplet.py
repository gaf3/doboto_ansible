#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import copy
from ansible.module_utils.basic import AnsibleModule
from doboto.DO import DO

"""

Ansible module to manage DigitalOcean droplets
(c) 2017, Gaffer Fitch <gfitch@digitalocean.com>

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
module: doboto_droplet

short_description: Manage DigitalOcean droplets
description:
    - Manages DigitalOcean droplets
version_added: "0.1"
author: "SWE Data <swe-data@do.co>"
options:
    token:
        description:
            - token to use to connect to the API (uses DO_API_TOKEN from ENV if not found)
    action:
        droplet action
        choices:
            - create
            - present
            - info
            - list
            - kernels
            - snapshots
            - backups
            - actions
            - destroy
            - neighbors
            - droplet_neighbors
            - enable_backups
            - disable_backups
            - reboot
            - shutdown
            - power_cycle
            - power_on
            - power_off
            - restore
            - password_reset
            - resize
            - rebuild
            - rename
            - change_kernel
            - enable_private_networking
            - enable_ipv6
            - snapshot
            - action_info

    id:
        description:
            - same as DO API variable (droplet id)
    name:
        description:
            - same as DO API variable (for single create)
    names:
        description:
            - same as DO API variable (for mass create)
    region:
        description:
            - same as DO API variable
    size:
        description:
            - same as DO API variable
    disk:
        description:
            - same as DO API variable
    image:
        description:
            - same as DO API variable
    kernel:
        description:
            - same as DO API variable
    ssh_keys:
        description:
            - same as DO API variable (if single value, converted to array)
    backups:
        description:
            - same as DO API variable
    ipv6:
        description:
            - same as DO API variable
    private_networking:
        description:
            - same as DO API variable
    user_data:
        description:
            - same as DO API variable
    monitoring:
        description:
            - same as DO API variable
    volume:
        description:
            - same as DO API variable (if single value, converted to array)
    tags:
        description:
            - same as DO API variable (if single value, converted to array)
    tag_name:
        description:
            - same as DO API variable (for tag ID)
    snapshot_name:
        description:
            - name of the snapshot
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
    extra:
        description:
            - key / value of extra values to send (for experimenting)

'''

EXAMPLES = '''
'''


class Droplet(object):

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
                "present",
                "info",
                "list",
                "kernels",
                "snapshots",
                "backups",
                "actions",
                "destroy",
                "neighbors",
                "droplet_neighbors",
                "enable_backups",
                "reboot",
                "disable_backups",
                "shutdown",
                "power_cycle",
                "power_on",
                "power_off",
                "restore",
                "password_reset",
                "resize",
                "rebuild",
                "rename",
                "change_kernel",
                "enable_private_networking",
                "enable_ipv6",
                "snapshot",
                "action_info"
            ]),
            token=dict(default=None),
            id=dict(default=None),
            name=dict(default=None),
            names=dict(default=None, type='list'),
            region=dict(default=None),
            size=dict(default=None),
            disk=dict(default=None, type='bool'),
            image=dict(default=None),
            kernel=dict(default=None),
            ssh_keys=dict(default=None, type='list'),
            backups=dict(default=False, type='bool'),
            ipv6=dict(default=False, type='bool'),
            private_networking=dict(type='bool'),
            user_data=dict(default=False),
            monitoring=dict(type='bool'),
            volume=dict(default=None, type='list'),
            tags=dict(type='list'),
            tag_name=dict(default=None),
            wait=dict(default=False, type='bool'),
            poll=dict(default=5, type='int'),
            timeout=dict(default=300, type='int'),
            action_id=dict(default=None),
            url=dict(default=self.url),
            extra=dict(default=None, type='dict'),
        ))

    def act(self):

        if self.module.params["action"] in [
            "kernels",
            "snapshots",
            "backups",
            "actions"
        ]:
            self.list_action()
        elif self.module.params["action"] in [
            "enable_backups",
            "disable_backups",
            "shutdown",
            "power_cycle",
            "power_on",
            "power_off",
            "enable_private_networking",
            "enable_ipv6"
        ]:
            self.action()
        elif self.module.params["action"] in [
            "reboot",
            "password_reset"
        ]:
            self.action(tagless=True)
        elif self.module.params["action"] == "neighbors":
            self.list_action("droplets")
        else:
            getattr(self, self.module.params["action"])()

    def ready(self, droplet, existing):

        for exist in existing:
            if droplet["id"] == exist["id"]:
                return True

        if droplet["status"] == "new":
            return False

        if self.module.params["private_networking"]:
            found = False
            for v4 in droplet["networks"]["v4"]:
                if v4["type"] == "private":
                    found = True
            if not found:
                return False

        if self.module.params["ipv6"] and not droplet["networks"]["v6"]:
            return False

        if self.module.params["tags"] and len(self.module.params["tags"]) != len(droplet["tags"]):
            return False

        return True

    def create(self, existing=None):

        if existing is None:
            existing = []

        existing_names = {droplet["name"]: True for droplet in existing}

        attribs = {}

        if self.module.params["name"] is not None:
            attribs["name"] = self.module.params["name"]
        elif self.module.params["names"] is not None:
            attribs["names"] = []
            for name in self.module.params["names"]:
                if name not in existing_names:
                    attribs["names"].append(name)
        else:
            self.module.fail_json(msg="the name or names parameter is required")

        for required in ['region', 'size', 'image']:
            if self.module.params[required] is None:
                self.module.fail_json(msg="the %s parameter is required" % required)
            attribs[required] = self.module.params[required]

        for optional in [
            'ssh_keys', 'volume', 'tags', 'backups', 'ipv6',
            'private_networking', 'user_data', 'monitoring'
        ]:
            attribs[optional] = self.module.params[optional]

        if self.module.params['extra'] is not None:
            attribs.update(self.module.params['extra'])

        result = self.do.droplet.create(attribs)

        if "droplet" not in result and "droplets" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        if "droplet" in result:

            droplet = result["droplet"]

            start_time = time.time()

            while self.module.params["wait"] and not self.ready(result["droplet"], existing):

                time.sleep(self.module.params["poll"])
                latest = self.do.droplet.info(droplet["id"])
                if "droplet" in latest:
                    result = latest

                if time.time() - start_time > self.module.params["timeout"]:
                    self.module.fail_json(msg="Timeout on polling", droplet=result['droplet'])

            self.module.exit_json(changed=True, droplet=result['droplet'])

        elif "droplets" in result:

            droplets = copy.deepcopy(existing)
            droplets.extend(result["droplets"])

            start_time = time.time()

            while self.module.params["wait"] and \
                    len([1 for droplet in droplets if not self.ready(droplet, existing)]) > 0:

                time.sleep(self.module.params["poll"])

                for index, droplet in enumerate(droplets):
                    if not self.ready(droplet, existing):
                        latest = self.do.droplet.info(droplet["id"])
                        if "droplet" in latest:
                            droplets[index] = latest["droplet"]

                if time.time() - start_time > self.module.params["timeout"]:
                    self.module.fail_json(msg="Timeout on polling", droplets=droplets)

            if not existing:
                self.module.exit_json(changed=True, droplets=droplets)
            else:
                created = [droplet for droplet in droplets if droplet["name"] not in existing_names]
                self.module.exit_json(changed=True, droplets=droplets, created=created)

        else:

            self.module.fail_json(msg="DO API error", result=result)

    def present(self):

        if self.module.params["name"] is None and self.module.params["names"] is None:
            self.module.fail_json(msg="the name or names parameter is required")

        result = self.do.droplet.list()

        if "droplets" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        droplets = result["droplets"]

        if self.module.params["name"] is not None:

            existing = None
            for droplet in droplets:
                if self.module.params["name"] == droplet["name"]:
                    existing = droplet
                    break

            if existing is not None:
                self.module.exit_json(changed=False, droplet=existing)
            else:
                self.create()

        else:

            existing = []

            for name in self.module.params["names"]:
                for droplet in droplets:
                    if name == droplet["name"]:
                        existing.append(droplet)
                        break

            if len(existing) == len(self.module.params["names"]):
                self.module.exit_json(changed=False, droplets=existing)
            else:
                self.create(existing)

    def info(self):

        result = None

        if self.module.params["id"] is None:
            self.module.fail_json(msg="the id parameter is required")

        result = self.do.droplet.info(self.module.params["id"])

        if "droplet" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, droplet=result["droplet"])

    def list(self):

        result = None

        if self.module.params["tag_name"] is None:
            result = self.do.droplet.list()
        else:
            result = self.do.droplet.list(tag_name=self.module.params["tag_name"])

        if "droplets" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, droplets=result["droplets"])

    def list_action(self, key=None):

        if key is None:
            key = self.module.params["action"]

        result = None

        if self.module.params["id"] is None:
            self.module.fail_json(msg="the id parameter is required")

        result = getattr(self.do.droplet, self.module.params["action"])(self.module.params["id"])

        if key not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, **{key: result[key]})

    def droplet_neighbors(self):

        result = self.do.droplet.droplet_neighbors()

        if "neighbors" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=True, neighbors=result["neighbors"])

    def destroy(self):

        result = None

        if self.module.params["id"] is not None:
            result = self.do.droplet.destroy(id=self.module.params["id"])
        elif self.module.params["tag_name"] is not None:
            result = self.do.droplet.destroy(tag_name=self.module.params["tag_name"])
        else:
            self.module.fail_json(msg="the id or tag_name parameter is required")

        if "status" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=True, result=result)

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

    def actions_result(self, result):

        if "actions" in result:

            actions = result["actions"]

            start_time = time.time()

            while self.module.params["wait"] and \
                    len([1 for action in actions if action["status"] == "in-progress"]) > 0:

                time.sleep(self.module.params["poll"])

                for index, action in enumerate(actions):
                    if action["status"] == "in-progress":
                        latest = self.do.droplet.action_info(action["resource_id"], action["id"])
                        if "action" in latest:
                            actions[index] = latest["action"]

                if time.time() - start_time > self.module.params["timeout"]:
                    self.module.fail_json(msg="Timeout on polling", droplets=droplets)

            self.module.exit_json(changed=True, actions=actions)

        else:

            self.module.fail_json(msg="DO API error", result=result)

    def action(self, tagless=False):

        if self.module.params["id"] is not None:

            result = getattr(
                self.do.droplet,
                self.module.params["action"]
            )(id=self.module.params["id"])

            self.action_result(result)

        elif not tagless and self.module.params["tag_name"] is not None:

            result = getattr(
                self.do.droplet,
                self.module.params["action"]
            )(tag_name=self.module.params["tag_name"])

            self.actions_result(result)

        else:

            self.module.fail_json(msg="the id or tag_name parameter is required")

    def restore(self):

        result = None

        if self.module.params["id"] is None:
            self.module.fail_json(msg="the id parameter is required")

        if self.module.params["image"] is None:
            self.module.fail_json(msg="the image parameter is required")

        result = self.do.droplet.restore(self.module.params["id"], self.module.params["image"])

        self.action_result(result)

    def resize(self):

        result = None

        if self.module.params["id"] is None:
            self.module.fail_json(msg="the id parameter is required")

        if self.module.params["size"] is None:
            self.module.fail_json(msg="the size parameter is required")

        result = None

        if self.module.params["disk"] is None:
            result = self.do.droplet.resize(self.module.params["id"], self.module.params["size"])
        else:
            result = self.do.droplet.resize(
                self.module.params["id"], self.module.params["size"], self.module.params["disk"]
            )

        self.action_result(result)

    def rebuild(self):

        result = None

        if self.module.params["id"] is None:
            self.module.fail_json(msg="the id parameter is required")

        if self.module.params["image"] is None:
            self.module.fail_json(msg="the image parameter is required")

        result = self.do.droplet.rebuild(self.module.params["id"], self.module.params["image"])

        self.action_result(result)

    def rename(self):

        result = None

        if self.module.params["id"] is None:
            self.module.fail_json(msg="the id parameter is required")

        if self.module.params["name"] is None:
            self.module.fail_json(msg="the name parameter is required")

        result = self.do.droplet.rename(self.module.params["id"], self.module.params["name"])

        self.action_result(result)

    def change_kernel(self):

        result = None

        if self.module.params["id"] is None:
            self.module.fail_json(msg="the id parameter is required")

        if self.module.params["kernel"] is None:
            self.module.fail_json(msg="the kernel parameter is required")

        result = self.do.droplet.change_kernel(
            self.module.params["id"], self.module.params["kernel"]
        )

        self.action_result(result)

    def snapshot(self):

        if self.module.params["name"] is None:
            self.module.fail_json(msg="the name parameter is required")

        if self.module.params["id"] is not None:

            result = self.do.droplet.snapshot(
                id=self.module.params["id"], name=self.module.params["name"]
            )

            self.action_result(result)

        elif self.module.params["tag_name"] is not None:

            result = self.do.droplet.snapshot(
                tag_name=self.module.params["tag_name"], name=self.module.params["name"]
            )

            self.action_result(result)

        else:

            self.module.fail_json(msg="the id or tag_name parameter is required")

    def action_info(self):

        result = None

        if self.module.params["id"] is None:
            self.module.fail_json(msg="the id parameter is required")

        if self.module.params["action_id"] is None:
            self.module.fail_json(msg="the action_id parameter is required")

        result = self.do.droplet.action_info(
            self.module.params["id"], self.module.params["action_id"]
        )

        if "action" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, action=result["action"])


Droplet()
