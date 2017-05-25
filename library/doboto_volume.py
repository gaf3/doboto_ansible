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
module: doboto_volume

short_description: Manage DigitalOcean volumes
description: Manages DigitalOcean Block Storage
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
        description: volume action
        choices:
            - list
            - create
            - present
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
        description: same as DO API variable (volume id)
    name:
        description: same as DO API variable
    description:
        description: same as DO API variable
    region:
        description: same as DO API variable
    size_gigabytes:
        description: same as DO API variable
    snapshot_id:
        description: same as DO API variable
    snapshot_name:
        description: name to give a snapshot
    droplet_id:
        description: same as DO API variable
    wait:
        description: wait until tasks has completed before continuing
    poll:
        description: poll value to check while waiting (default 5 seconds)
    timeout:
        description: timeout value to give up after waiting (default 300 seconds)
    action_id:
        description: same as DO API variable (action id)
    url:
        description: URL to use if not official (for experimenting)

'''

EXAMPLES = '''
- name: volume | create
  doboto_volume:
    token: "{{ lookup('env','DO_API_TOKEN') }}"
    action: create
    name: volume-create
    region: nyc1
    size_gigabytes: 1
    description: "A nice one"
  register: volume_create

- name: volume | list
  doboto_volume:
    action: list
  register: volume_list

- name: volume | info | by id
  doboto_volume:
    action: info
    id: "{{ volume_create.volume.id }}"
  register: volume_info_id

- name: volume | info | by name region
  doboto_volume:
    action: info
    name: volume-create
    region: nyc1
  register: volume_info_name_region

- name: volume | snapshot | create
  doboto_volume:
    action: snapshot_create
    id: "{{ volume_create.volume.id }}"
    snapshot_name: bulletproof
  register: volume_snapshot_create

- name: volume | snapshot | list
  doboto_volume:
    action: snapshot_list
    id: "{{ volume_create.volume.id }}"
  register: volume_snapshot_list

- name: volume | droplet | create
  doboto_droplet:
    action: create
    name: volume-droplet
    region: nyc1
    size: 1gb
    image: debian-7-0-x64
    wait: true
  register: volume_droplet

- name: volume | create | by snapshot
  doboto_volume:
    action: create
    name: volume-create-snapshot
    snapshot_id: "{{ volume_snapshot_create.snapshot.id }}"
    size_gigabytes: 2
    description: "A bad one"
    wait: true
  register: volume_create_snapshot

- name: volume | attach | by id
  doboto_volume:
    action: attach
    id: "{{ volume_create.volume.id }}"
    droplet_id: "{{ volume_droplet.droplet.id }}"
    wait: true
  register: volume_attach_id

- name: volume | attach | by name
  doboto_volume:
    action: attach
    name: volume-create-snapshot
    region: nyc1
    droplet_id: "{{ volume_droplet.droplet.id }}"
    wait: true
  register: volume_attach_name

- name: volume | detach | by id
  doboto_volume:
    action: detach
    id: "{{ volume_create.volume.id }}"
    droplet_id: "{{ volume_droplet.droplet.id }}"
    wait: true
  register: volume_detach_id

- name: volume | resize
  doboto_volume:
    action: resize
    id: "{{ volume_create.volume.id }}"
    size_gigabytes: 3
  register: volume_resize

- name: volume | action | list
  doboto_volume:
    action: action_list
    id: "{{ volume_create.volume.id }}"
  register: volume_action_list

- name: volume | action | info
  doboto_volume:
    action: action_info
    id: "{{ volume_create.volume.id }}"
    action_id: "{{ volume_attach_id.action.id }}"
  register: volume_action_info

- name: volume | destroy | by id
  doboto_volume:
    action: destroy
    id: "{{ volume_create.volume.id }}"
  register: volume_destroy_id

- name: volume | destroy | by name region
  doboto_volume:
    action: destroy
    name: volume-create-snapshot
    region: nyc1
  register: volume_destroy_name_region
'''

RETURNS = '''

'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.digitalocean_doboto import DOBOTOModule

class Volume(DOBOTOModule):

    def input(self):

        argument_spec = self.argument_spec()

        argument_spec.update(
            dict(
                action=dict(required=True, default="list", choices=[
                    "list",
                    "create",
                    "present",
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
                action_id=dict(default=None)
            )
        )

        return AnsibleModule(
            argument_spec=argument_spec,
            required_if=[
                ["action", "create", ["name", "size_gigabytes"]],
                ["action", "create", ["region", "snapshot_id"], True],
                ["action", "present", ["name", "size_gigabytes"]],
                ["action", "present", ["region", "snapshot_id"], True],
                ["action", "info", ["id", "name"], True],
                ["action", "destroy", ["id", "name"], True],
                ["action", "snapshot_list", ["id"]],
                ["action", "snapshot_create", ["id", "snapshot_name"]],
                ["action", "attach", ["id", "name"], True],
                ["action", "attach", ["droplet_id"]],
                ["action", "detach", ["id", "name"], True],
                ["action", "detach", ["droplet_id"]],
                ["action", "resize", ["id", "name"], True],
                ["action", "resize", ["size_gigabytes"]]
                ["action", "action_list", ["id"]],
                ["action", "action_info", ["id", "action_id"]]
            ]
        )

    def list(self):

        self.module.exit_json(
            changed=False,
            volumes=self.do.volume.list(
                region=self.module.params["region"]
            )
        )

    def attribs(self):

        attribs = {
            "size_gigabytes": self.module.params["size_gigabytes"],
            "name": self.module.params["name"]
        }

        for param in ["region", "snapshot_id", "description"]:
            if self.module.params[param] is not None:
                attribs[param] = self.module.params[param]

        return attribs

    def create(self):

        attribs = self.attribs()

        self.module.exit_json(
            changed=True,
            volume=self.do.volume.create(
                attribs,
                wait=self.module.params["wait"],
                poll=self.module.params["poll"],
                timeout=self.module.params["timeout"]
            )
        )

    def present(self):

        attribs = self.attribs()

        (volume, created) = self.do.volume.present(
            attribs,
            wait=self.module.params["wait"],
            poll=self.module.params["poll"],
            timeout=self.module.params["timeout"]
        )

        self.module.exit_json(
            changed=(created is not None),
            volume=volume,
            created=created
        )

    def info(self):

        result = None

        if self.module.params["id"] is not None:

            self.module.exit_json(
                changed=False,
                volume=self.do.volume.info(
                    id=self.module.params["id"]
                )
            )

        elif self.module.params["name"] is not None and self.module.params["region"] is not None:

            self.module.exit_json(
                changed=False,
                volume=self.do.volume.info(
                    name=self.module.params["name"],
                    region=self.module.params["region"]
                )
            )

        else:
            self.module.fail_json(
                msg="the id or name and region parameters are required"
            )

    def destroy(self):

        result = None

        if self.module.params["id"] is not None:

            result = self.do.volume.destroy(
                id=self.module.params["id"]
            )

        elif self.module.params["name"] is not None and self.module.params["region"] is not None:

            result = self.do.volume.destroy(
                name=self.module.params["name"],
                region=self.module.params["region"]
            )

        else:
            self.module.fail_json(
                msg="the id or name and region parameters are required"
            )

        self.module.exit_json(
            changed=True,
            result=result
        )

    def snapshot_list(self):

        self.module.exit_json(
            changed=False,
            snapshots=self.do.volume.snapshot_list(
                id=self.module.params["id"]
            )
        )

    def snapshot_create(self):

        self.module.exit_json(
            changed=True,
            snapshot=self.do.volume.snapshot_create(
                id=self.module.params["id"],
                snapshot_name=self.module.params["snapshot_name"]
            )
        )

    def attach(self):

        self.module.exit_json(
            changed=True,
            action=self.do.volume.attach(
                id=self.module.params["id"],
                name=self.module.params["name"],
                droplet_id=self.module.params["droplet_id"],
                region=self.module.params["region"],
                wait=self.module.params["wait"],
                poll=self.module.params["poll"],
                timeout=self.module.params["timeout"]
            )
        )

    def detach(self):

        self.module.exit_json(
            changed=True,
            action=self.do.volume.detach(
                id=self.module.params["id"],
                name=self.module.params["name"],
                droplet_id=self.module.params["droplet_id"],
                region=self.module.params["region"],
                wait=self.module.params["wait"],
                poll=self.module.params["poll"],
                timeout=self.module.params["timeout"]
            )
        )

    def resize(self):

        self.module.exit_json(
            changed=True,
            action=self.do.volume.resize(
                self.module.params["id"],
                self.module.params["size_gigabytes"],
                region=self.module.params["region"],
                wait=self.module.params["wait"],
                poll=self.module.params["poll"],
                timeout=self.module.params["timeout"]
            )
        )

    def action_list(self):

        self.module.exit_json(
            changed=False,
            actions=self.do.volume.action_list(
                self.module.params["id"]
            )
        )

    def action_info(self):

        self.module.exit_json(
            changed=False,
            action=self.do.volume.action_info(
                self.module.params["id"],
                self.module.params["action_id"]
            )
        )

if __name__ == '__main__':
    Volume()
