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
module: doboto_snapshot

short_description: Manage DigitalOcean snapshots
description: Manages DigitalOcean Snapshots
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

RETURNS = '''

'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.digitalocean_doboto import DOBOTOModule

class Snapshot(DOBOTOModule):

    def input(self):

        argument_spec = self.argument_spec()

        argument_spec.update(
            dict(
                action=dict(required=True, default="list", choices=[
                    "list",
                    "info",
                    "destroy"
                ]),
                id=dict(default=None),
                resource_type=dict(default=None)
            )
        )

        return AnsibleModule(
            argument_spec=argument_spec,
            required_if=[
                ["action", "info", ["id"]],
                ["action", "destroy", ["id"]]
            ]
        )

    def list(self):

        self.module.exit_json(
            changed=False,
            snapshots=self.do.snapshot.list(
                resource_type=self.module.params["resource_type"]
            )
        )

    def info(self):

        self.module.exit_json(
            changed=False,
            snapshot=self.do.snapshot.info(
                id=self.module.params["id"]
            )
        )

    def destroy(self):
        self.module.exit_json(
            changed=True,
            result=self.do.snapshot.destroy(
                id=self.module.params["id"]
            )
        )

if __name__ == '__main__':
    Snapshot()
