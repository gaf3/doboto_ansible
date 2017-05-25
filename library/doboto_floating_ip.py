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
module: doboto_floating_ip

short_description: Manage DigitalOcean Floating IPs
description: Manages DigitalOcean Floating IPs
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
        description: floating_ip action
        choices:
            - list
            - create
            - info
            - destroy
            - assign
            - unassign
            - action_list
            - action_info
    ip:
        description:
            - same as DO API variable
    region:
        description:
            - same as DO API variable
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
- name: floating_ip | droplet | create
  doboto_droplet:
    action: create
    name: floating-ip-droplet
    region: nyc1
    size: 1gb
    image: debian-7-0-x64
    wait: true
  register: floating_ip_droplet

- name: floating_ip | create | droplet
  doboto_floating_ip:
    action: create
    droplet_id: "{{ floating_ip_droplet.droplet.id }}"
    wait: true
  register: floating_ip_create_droplet

- name: floating_ip | create | region
  doboto_floating_ip:
    action: create
    region: nyc1
    wait: true
  register: floating_ip_create_region

- name: floating_ip | list
  doboto_floating_ip:
    action: list
  register: floating_ip_list

- name: floating_ip | info
  doboto_floating_ip:
    action: info
    ip: "{{ floating_ip_create_region.floating_ip.ip }}"
  register: floating_ip_info

- name: floating_ip | droplet | assign
  doboto_droplet:
    action: create
    name: floating-ip-assign
    region: nyc1
    size: 1gb
    image: debian-7-0-x64
    wait: true
  register: floating_ip_assign

- name: floating_ip | assign
  doboto_floating_ip:
    action: assign
    ip: "{{ floating_ip_create_region.floating_ip.ip }}"
    droplet_id: "{{ floating_ip_assign.droplet.id }}"
    wait: true
  register: floating_ip_assign

- name: floating_ip | unassign
  doboto_floating_ip:
    action: unassign
    ip: "{{ floating_ip_create_region.floating_ip.ip }}"
    wait: true
  register: floating_ip_unassign

- name: floating_ip | action | list
  doboto_floating_ip:
    action: action_list
    ip: "{{ floating_ip_create_region.floating_ip.ip }}"
  register: floating_ip_action_list

- name: floating_ip | action | info
  doboto_floating_ip:
    action: action_info
    ip: "{{ floating_ip_create_region.floating_ip.ip }}"
    action_id: "{{ floating_ip_unassign.action.id }}"
  register: floating_ip_action_info

- name: floating_ip | destroy
  doboto_floating_ip:
    action: destroy
    ip: "{{ floating_ip_create_region.floating_ip.ip }}"
  register: floating_ip_destroy

'''

RETURNS = '''

'''

from time import time, sleep
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.digitalocean_doboto import DOBOTOModule

class FloatingIP(DOBOTOModule):

    def input(self):

        argument_spec = self.argument_spec()

        argument_spec.update(
            dict(
                action=dict(required=True, default="list", choices=[
                    "list",
                    "create",
                    "info",
                    "destroy",
                    "assign",
                    "unassign",
                    "action_list",
                    "action_info"
                ]),
                ip=dict(default=None),
                region=dict(default=None),
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
                ["action", "create", ["droplet_id", "region"], True],
                ["action", "info", ["ip"]],
                ["action", "destroy", ["ip"]],
                ["action", "assign", ["ip", "droplet_id"]],
                ["action", "unassign", ["ip"]],
                ["action", "action_list", ["ip"]],
                ["action", "action_info", ["ip", "action_id"]]
            ]
        )

    def list(self):

        self.module.exit_json(
            changed=False,
            floating_ips=self.do.floating_ip.list()
        )

    def create(self):

        floating_ip = \
            self.do.floating_ip.create(
                droplet_id=self.module.params["droplet_id"],
                region=self.module.params["region"]
            )

        start_time = time()

        while self.module.params["wait"] and \
            (self.module.params["droplet_id"] is None or floating_ip["droplet"]) is None and \
                (self.module.params["region"] is None or floating_ip["region"] is None):

            sleep(self.module.params["poll"])

            try:
                floating_ip = self.do.floating_ip.info(floating_ip["ip"])
            except:
                pass

            if time() - start_time > self.module.params["timeout"]:
                self.module.fail_json(
                    msg="Timeout on polling",
                    floating_ip=floating_ip
                )

        self.module.exit_json(
            changed=True,
            floating_ip=floating_ip
        )

    def info(self):

        self.module.exit_json(
            changed=False,
            floating_ip=self.do.floating_ip.info(
                self.module.params["ip"]
            )
        )

    def destroy(self):

        self.module.exit_json(
            changed=True,
            result=self.do.floating_ip.destroy(
                self.module.params["ip"]
            )
        )

    def assign(self):

        self.module.exit_json(
            changed=True,
            action=self.do.floating_ip.assign(
                self.module.params["ip"],
                self.module.params["droplet_id"],
                wait=self.module.params["wait"],
                poll=self.module.params["poll"],
                timeout=self.module.params["timeout"]
            )
        )

    def unassign(self):

        self.module.exit_json(
            changed=True,
            action=self.do.floating_ip.unassign(
                self.module.params["ip"],
                wait=self.module.params["wait"],
                poll=self.module.params["poll"],
                timeout=self.module.params["timeout"]
            )
        )

    def action_list(self):
        self.module.exit_json(
            changed=False,
            actions=self.do.floating_ip.action_list(
                self.module.params["ip"]
            )
        )

    def action_info(self):
        self.module.exit_json(
            changed=False,
            action=self.do.floating_ip.action_info(
                self.module.params["ip"],
                self.module.params["action_id"]
            )
        )

if __name__ == '__main__':
    FloatingIP()
