#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.doboto_module import require, DOBOTOModule

"""
Ansible module to manage DigitalOcean snapshots
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
module: doboto_snapshot

short_description: Manage DigitalOcean snapshots
description: Manages DigitalOcean Snapshots
version_added: "0.1"
author: "SWE Data <swe-data@do.co>"
options:
    token:
        description: token to use to connect to the API (uses DO_API_TOKEN from ENV if not found)
    action:
        description: snapshot action
        choices:
            - list
            - info
            - destroy
    id:
        description: same as DO API variable (snapshot id)
    resource_type:
        description: same as DO API variable
    url:
        description: URL to use if not official (for experimenting)

'''

EXAMPLES = '''
- name: snapshot | droplet | create
  doboto_droplet:
    action: create
    name: snapshot-droplet
    region: nyc1
    size: 1gb
    image: debian-7-0-x64
    wait: true
  register: snapshot_droplet

- name: snapshot | droplet | snapshot | create
  doboto_droplet:
    action: snapshot_create
    id: "{{ snapshot_droplet.droplet.id }}"
    snapshot_name: "how-bow-dah"
    wait: true
  register: snapshot_droplet_snapshot_create

- name: snapshot | volume | create
  doboto_volume:
    action: create
    name: snapshot-volume
    region: nyc1
    size_gigabytes: 1
    description: "A nice one"
  register: snapshot_volume

- name: snapshot | volume | snapshot
  doboto_volume:
    action: snapshot_create
    id: "{{ snapshot_volume.volume.id }}"
    snapshot_name: "cash-me-ousside"
  register: snapshot_volume_snapshot_create

- name: snapshot | list
  doboto_snapshot:
    action: list
  register: snapshot_list

- name: snapshot | list | droplet
  doboto_snapshot:
    action: list
    resource_type: droplet
  register: snapshot_list_droplet

- name: snapshot | list | volume
  doboto_snapshot:
    action: list
    resource_type: volume
  register: snapshot_list_volume

- name: snapshot | info
  doboto_snapshot:
    action: info
    id: "{{ snapshot_list_droplet.snapshots[0].id }}"
  register: snapshot_info

- name: snapshot | destroy | by id
  doboto_snapshot:
    action: destroy
    id: "{{ snapshot_list_volume.snapshots[0].id }}"
  register: volume_destroy
'''


class Snapshot(DOBOTOModule):

    def input(self):

        return AnsibleModule(argument_spec=dict(
            action=dict(default=None, required=True, choices=[
                "info",
                "list",
                "destroy"
            ]),
            token=dict(default=None, no_log=True),
            id=dict(default=None),
            resource_type=dict(default=None),
            url=dict(default=self.url)
        ))

    def list(self):
        self.module.exit_json(changed=False, snapshots=self.do.snapshot.list(
            resource_type=self.module.params["resource_type"]
        ))

    @require("id")
    def info(self):
        self.module.exit_json(changed=False, snapshot=self.do.snapshot.info(
            id=self.module.params["id"]
        ))

    @require("id")
    def destroy(self):
        self.module.exit_json(changed=True, result=self.do.snapshot.destroy(
            id=self.module.params["id"]
        ))


if __name__ == '__main__':
    Snapshot()
