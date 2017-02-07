#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.doboto_module import require, DOBOTOModule

"""
Ansible module to manage DigitalOcean tags
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
module: doboto_tag

short_description: Manage DigitalOcean Tags
description:
    - Manages DigitalOcean tags
version_added: "0.1"
author: "SWE Data <swe-data@do.co>"
options:
    token:
        description:
            - token to use to connect to the API (uses DO_API_TOKEN from ENV if not found)
    action:
        tag action
        choices:
            - list
            - name_list
            - create
            - present
            - info
            - update
            - destroy
            - attach
            - detach
    name:
        description:
            - same as DO API variable
    new_name:
        description:
            - same as DO API variable, new name for updating
    resources:
        description:
            - same as DO API variable
    resource_type:
        description:
            - same as DO API variable, use if doing a single resource type
    resource_id:
        description:
            - same as DO API variable, use if doing a single resource id
    resource_ids:
        description:
            - paired with a single resource_type to build a resources list
    url:
        description:
            - URL to use if not official (for experimenting)
'''

EXAMPLES = '''
'''


class Tag(DOBOTOModule):

    def input(self):

        return AnsibleModule(argument_spec=dict(
            action=dict(default=None, required=True, choices=[
                "list",
                "name_list",
                "create",
                "present",
                "info",
                "update",
                "destroy",
                "attach",
                "detach",
            ]),
            token=dict(default=None),
            name=dict(default=None),
            new_name=dict(default=None),
            resources=dict(default=None, type='list'),
            resource_type=dict(default=None),
            resource_id=dict(default=None),
            resource_ids=dict(default=None, type='list'),
            url=dict(default=self.url),
        ))

    def list(self):
        self.module.exit_json(changed=False, tags=self.do.tag.list())

    def name_list(self):
        self.module.exit_json(changed=False, names=self.do.tag.name_list())

    @require("name")
    def create(self):
        self.module.exit_json(changed=True, tag=self.do.tag.create(self.module.params["name"]))

    @require("name")
    def present(self):
        tags = self.do.tag.list()

        existing = None
        for tag in tags:
            if self.module.params["name"] == tag["name"]:
                existing = tag
                break

        if existing is not None:
            self.module.exit_json(changed=False, tag=existing)
        else:
            self.create()

    @require("name")
    def info(self):
        self.module.exit_json(changed=False, tag=self.do.tag.info(self.module.params["name"]))

    @require("name")
    @require("new_name")
    def update(self):
        self.module.exit_json(changed=True, tag=self.do.tag.update(
            self.module.params["name"], self.module.params["new_name"]
        ))

    def build(self):

        resources = []

        if self.module.params["resource_type"] is not None and \
           self.module.params["resource_id"] is not None:
            resources.append({
                "resource_type": self.module.params["resource_type"],
                "resource_id": self.module.params["resource_id"]
            })

        if self.module.params["resource_type"] is not None and \
           self.module.params["resource_ids"] is not None:
            for resource_id in self.module.params["resource_ids"]:
                resources.append({
                    "resource_type": self.module.params["resource_type"],
                    "resource_id": resource_id
                })

        if self.module.params["resources"] is not None:
            resources.extend(copy.deepcopy(self.module.params["resources"]))

        return resources

    @require("name")
    def attach(self):

        resources = self.build()

        if not resources:
            self.module.fail_json(
                msg="the resources or resource_type and resource_id(s) parameters are required"
            )

        self.module.exit_json(changed=True, result=self.do.tag.attach(
            self.module.params["name"], resources
        ))

    @require("name")
    def detach(self):

        resources = self.build()

        if not resources:
            self.module.fail_json(
                msg="the resources or resource_type and resource_id(s) parameters are required"
            )

        self.module.exit_json(changed=True, result=self.do.tag.detach(
            self.module.params["name"], resources
        ))

    @require("name")
    def destroy(self):
        self.module.exit_json(changed=True, result=self.do.tag.destroy(
            self.module.params["name"]
        ))

Tag()
