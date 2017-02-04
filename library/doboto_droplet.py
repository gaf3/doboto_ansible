#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import copy
from ansible.module_utils.basic import AnsibleModule
from doboto.DO import DO
from doboto.DOBOTOException import DOBOTOException

"""

Ansible module to manage DigitalOcean droplets
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
            - list
            - neighbor_list
            - droplet_neighbor_list
            - create
            - present
            - info
            - destroy
            - backup_list
            - backup_enable
            - backup_disable
            - reboot
            - shutdown
            - power_on
            - power_off
            - power_cycle
            - restore
            - password_reset
            - resize
            - rebuild
            - rename
            - kernel_list
            - kernel_update
            - ipv6_enable
            - private_networking_enable
            - snapshot_list
            - snapshot_create
            - action_list
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
                "list",
                "neighbor_list",
                "droplet_neighbor_list",
                "create",
                "present",
                "info",
                "destroy",
                "backup_list",
                "backup_enable",
                "backup_disable",
                "reboot",
                "shutdown",
                "power_on",
                "power_off",
                "power_cycle",
                "restore",
                "password_reset",
                "resize",
                "rebuild",
                "rename",
                "kernel_list",
                "kernel_update",
                "ipv6_enable",
                "private_networking_enable",
                "snapshot_list",
                "snapshot_create",
                "action_list",
                "action_info",
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
            snapshot_name=dict(default=None),
            wait=dict(default=False, type='bool'),
            poll=dict(default=5, type='int'),
            timeout=dict(default=300, type='int'),
            action_id=dict(default=None),
            url=dict(default=self.url),
            extra=dict(default=None, type='dict'),
        ))

    def act(self):

        try:

            if self.module.params["action"] in [
                "kernel_list",
                "snapshot_list",
                "backup_list",
                "action_list"
            ]:
                self.list_action(self.module.params["action"].replace('_list', 's'))
            elif self.module.params["action"] in [
                "backup_enable",
                "backup_disable",
                "shutdown",
                "power_cycle",
                "power_on",
                "power_off",
                "private_networking_enable",
                "ipv6_enable"
            ]:
                self.action()
            elif self.module.params["action"] in [
                "reboot",
                "password_reset"
            ]:
                self.action(tagless=True)
            elif self.module.params["action"] == "neighbor_list":
                self.list_action("droplets")
            else:
                getattr(self, self.module.params["action"])()

        except DOBOTOException as exception:
            self.module.fail_json(msg=exception.message, result=exception.result)

    def list(self):
        self.module.exit_json(changed=False, droplets=self.do.droplet.list(
            tag_name=self.module.params["tag_name"])
        )

    def droplet_neighbor_list(self):
        self.module.exit_json(changed=False, neighbors=self.do.droplet.droplet_neighbor_list())

    @require("id")
    def list_action(self, key=None):

        if key is None:
            key = self.module.params["action"]

        self.module.exit_json(changed=False,
            **{key: getattr(self.do.droplet, self.module.params["action"])(
               self.module.params["id"]
            )}
        )

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

    @require("name", "names")
    @require("region")
    @require("size")
    @require("image")
    def create(self, existing=None):

        if existing is None:
            existing = []

        existing_names = {droplet["name"]: True for droplet in existing}

        attribs = {
            "region": self.module.params["region"],
            "size": self.module.params["size"],
            "image": self.module.params["image"],
        }

        for optional in [
            'ssh_keys', 'volume', 'tags', 'backups', 'ipv6',
            'private_networking', 'user_data', 'monitoring'
        ]:
            attribs[optional] = self.module.params[optional]

        if self.module.params['extra'] is not None:
            attribs.update(self.module.params['extra'])

        if self.module.params["name"] is not None:

            attribs["name"] = self.module.params["name"]

            droplet = self.do.droplet.create(attribs)

            start_time = time.time()

            while self.module.params["wait"] and not self.ready(droplet, existing):

                time.sleep(self.module.params["poll"])
                try:
                    droplet = self.do.droplet.info(droplet["id"])
                except:
                    pass

                if time.time() - start_time > self.module.params["timeout"]:
                    self.module.fail_json(msg="Timeout on polling", droplet=droplet)

            self.module.exit_json(changed=True, droplet=droplet)

        elif self.module.params["names"] is not None:

            attribs["names"] = []
            for name in self.module.params["names"]:
                if name not in existing_names:
                    attribs["names"].append(name)

            droplets = copy.deepcopy(existing)
            droplets.extend(self.do.droplet.create(attribs))

            start_time = time.time()

            while self.module.params["wait"] and \
                    len([1 for droplet in droplets if not self.ready(droplet, existing)]) > 0:

                time.sleep(self.module.params["poll"])

                for index, droplet in enumerate(droplets):
                    if not self.ready(droplet, existing):
                        try:
                            droplets[index] = self.do.droplet.info(droplet["id"])
                        except:
                            pass

                if time.time() - start_time > self.module.params["timeout"]:
                    self.module.fail_json(msg="Timeout on polling", droplets=droplets)

            if not existing:
                self.module.exit_json(changed=True, droplets=droplets)
            else:
                created = [droplet for droplet in droplets if droplet["name"] not in existing_names]
                self.module.exit_json(changed=True, droplets=droplets, created=created)

    @require("name", "names")
    def present(self):

        droplets = self.do.droplet.list()

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

    @require("id")
    def info(self):
        self.module.exit_json(changed=False, droplet=self.do.droplet.info(
            self.module.params["id"]
        ))

    @require("id", "tag_name")
    def destroy(self):
        self.module.exit_json(changed=True, result=self.do.droplet.destroy(
            id=self.module.params["id"], tag_name=self.module.params["tag_name"]
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
                self.module.fail_json(msg="Timeout on polling", action=action)

        self.module.exit_json(changed=True, action=action)

    def actions_result(self, actions):

        start_time = time.time()

        while self.module.params["wait"] and \
                len([1 for action in actions if action["status"] == "in-progress"]) > 0:

            time.sleep(self.module.params["poll"])

            for index, action in enumerate(actions):
                if action["status"] == "in-progress":
                    try:
                        actions[index] = self.do.droplet.action_info(
                            action["resource_id"], action["id"]
                        )
                    except:
                        pass

            if time.time() - start_time > self.module.params["timeout"]:
                self.module.fail_json(msg="Timeout on polling", actions=actions)

        self.module.exit_json(changed=True, actions=actions)

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

    @require("id")
    @require("image")
    def restore(self):
        self.action_result(self.do.droplet.restore(
            self.module.params["id"], self.module.params["image"]
        ))

    @require("id")
    @require("size")
    def resize(self):
        self.action_result(self.do.droplet.resize(
            self.module.params["id"], self.module.params["size"], self.module.params["disk"]
        ))

    @require("id")
    @require("image")
    def rebuild(self):
        self.action_result(self.do.droplet.rebuild(
            self.module.params["id"], self.module.params["image"]
        ))

    @require("id")
    @require("name")
    def rename(self):
        self.action_result(self.do.droplet.rename(
            self.module.params["id"], self.module.params["name"]
        ))

    @require("id")
    @require("kernel")
    def kernel_update(self):
        self.action_result(self.do.droplet.kernel_update(
            self.module.params["id"], self.module.params["kernel"]
        ))

    @require("id", "tag_name")
    @require("snapshot_name")
    def snapshot_create(self):
        self.action_result(self.do.droplet.snapshot_create(
            id=self.module.params["id"],
            tag_name=self.module.params["tag_name"],
            snapshot_name=self.module.params["snapshot_name"]
        ))

    @require("id")
    @require("action_id")
    def action_info(self):
        self.module.exit_json(changed=False, action=self.do.droplet.action_info(
            self.module.params["id"], self.module.params["action_id"]
        ))


Droplet()
