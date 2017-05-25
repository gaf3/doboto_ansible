#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
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

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: doboto_tag

short_description: Manage DigitalOcean Tags
description: Manages DigitalOcean tags
version_added: "2.4"
author:
  - "Gaffer Fitch (@gaf3)"
  - "Ben Mildren (@bmildren)"
  - "Cole Tuininga (@egon1024)"
  - "Josh Bradley (@aww-yiss)"
options:
    token:
        description: token to use to connect to the API (uses DO_API_TOKEN from ENV if not found)
    action:
        description: tag action
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
        description: same as DO API variable
    new_name:
        description: same as DO API variable, new name for updating
    resources:
        description: same as DO API variable
    resource_type:
        description: same as DO API variable, use if doing a single resource type
    resource_id:
        description: same as DO API variable, use if doing a single resource id
    resource_ids:
        description: paired with a single resource_type to build a resources list
    url:
        description: URL to use if not official (for experimenting)
'''

EXAMPLES = '''
- name: tag | create
  doboto_tag:
    token: "{{ lookup('env','DO_API_TOKEN') }}"
    action: create
    name: tag-create
  register: tag_create

- name: tag | present | new
  doboto_tag:
    action: present
    name: tag-present
  register: tag_present_new

- name: tag | info
  doboto_tag:
    action: info
    name: tag-create
  register: tag_info

- name: tag | list
  doboto_tag:
    action: list
  register: tag_list

- name: tag | name_list
  doboto_tag:
    action: name_list
  register: tag_name_list

- name: tag | update
  doboto_tag:
    action: update
    name: tag-create
    new_name: tag-update
  register: tag_update

- name: tag | update | reload
  doboto_tag:
    action: info
    name: tag-update
  register: tag_update_reload

- name: tag | update | reload | verify
  assert:
    that:
      - "{{ tag_update_reload.tag.name == 'tag-update' }}"
    msg: "{{ tag_update_reload }}"

- name: tag | attach | create
  doboto_droplet:
    action: create
    names:
      - tag-droplet-01
      - tag-droplet-02
      - tag-droplet-03
    region: nyc3
    size: 1gb
    image: ubuntu-14-04-x64
    wait: true
  register: tag_droplet

- name: tag | attach | droplet
  doboto_tag:
    action: attach
    name: tag-update
    resource_type: "droplet"
    resource_id: "{{ tag_droplet.droplets[0].id }}"
  register: tag_attach

- name: tag | attach | new | droplet
  doboto_tag:
    action: "{{item}}"
    name: tag-new
    resources:
      -
        resource_type: "droplet"
        resource_id: "{{ tag_droplet.droplets[0].id }}"
  with_items:
    - present
    - attach

- name: tag | attach | multiple | droplet
  doboto_tag:
    action: "{{item}}"
    name: tag-multi
    resource_type: "droplet"
    resource_ids: "{{tag_droplet|json_query(tag_droplet_ids_query)}}"
  with_items:
    - present
    - attach
  vars:
    tag_droplet_ids_query: "droplets[].id"

- name: tag | detach | droplet
  doboto_tag:
    action: detach
    name: tag-update
    resource_type: "droplet"
    resource_id: "{{ tag_droplet.droplets[0].id }}"
  register: tag_droplet_detach

- name: tag | destroy
  doboto_tag:
    action: destroy
    name: tag-update
  register: tag_destroy
'''

RETURNS = '''

'''

from copy import deepcopy
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.digitalocean_doboto import DOBOTOModule

class Tag(DOBOTOModule):

    def input(self):

        argument_spec = self.argument_spec()

        argument_spec.update(
            dict(
                action=dict(required=True, default="list", choices=[
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
                name=dict(default=None),
                new_name=dict(default=None),
                resources=dict(default=None, type='list'),
                resource_type=dict(default=None),
                resource_id=dict(default=None),
                resource_ids=dict(default=None, type='list')
            )
        )

        return AnsibleModule(
            argument_spec=argument_spec,
            required_if=[
                ["action", "create", ["name"]],
                ["action", "present", ["name"]],
                ["action", "info", ["name"]],
                ["action", "update", ["name", "new_name"]],
                ["action", "attach", ["name"]],
                ["action", "detach", ["name"]],
                ["action", "destroy", ["name"]]
            ]
        )

    def list(self):

        self.module.exit_json(
            changed=False,
            tags=self.do.tag.list()
        )

    def name_list(self):

        self.module.exit_json(
            changed=False,
            names=self.do.tag.name_list()
        )

    def create(self):

        self.module.exit_json(
            changed=True,
            tag=self.do.tag.create(
                self.module.params["name"]
            )
        )

    def present(self):

        (tag, created) = self.do.tag.present(self.module.params["name"])

        self.module.exit_json(
            changed=(created is not None),
            tag=tag,
            created=created
        )

    def info(self):

        self.module.exit_json(
            changed=False,
            tag=self.do.tag.info(
                self.module.params["name"]
            )
        )

    def update(self):

        self.module.exit_json(
            changed=True,
            tag=self.do.tag.update(
                self.module.params["name"],
                self.module.params["new_name"]
            )
        )

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
            resources.extend(deepcopy(self.module.params["resources"]))

        return resources

    def attach(self):

        resources = self.build()

        if not resources:
            self.module.fail_json(
                msg="the resources or resource_type and resource_id(s) parameters are required"
            )

        self.module.exit_json(
            changed=True,
            result=self.do.tag.attach(
                self.module.params["name"],
                resources
            )
        )

    def detach(self):

        resources = self.build()

        if not resources:
            self.module.fail_json(
                msg="the resources or resource_type and resource_id(s) parameters are required"
            )

        self.module.exit_json(
            changed=True,
            result=self.do.tag.detach(
                self.module.params["name"],
                resources
            )
        )

    def destroy(self):

        self.module.exit_json(
            changed=True,
            result=self.do.tag.destroy(
                self.module.params["name"]
            )
        )

if __name__ == '__main__':
    Tag()
