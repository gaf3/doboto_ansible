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
module: doboto_load_balancer

short_description: Manage DigitalOcean load balancers
description: Manages DigitalOcean Load Balancers
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
        description: load_balancer action
        choices:
            - list
            - create
            - present
            - info
            - update
            - destroy
            - droplet_add
            - droplet_remove
            - forwarding_rule_add
            - forwarding_rule_remove
    id:
        description: same as DO API variable
    name:
        description: same as DO API variable
    algorithm:
        description: same as DO API variable
    region:
        description: same as DO API variable
    forwarding_rules:
        description: same as DO API variable
    health_check:
        description: same as DO API variable
    sticky_sessions:
        description: same as DO API variable
    redirect_http_to_https:
        description: same as DO API variable
    droplet_ids:
        description: same as DO API variable
    tag:
        description: same as DO API variable
    wait:
        description: wait until tasks has completed before continuing
    poll:
        description: poll value to check while waiting (default 5 seconds)
    timeout:
        description: timeout value to give up after waiting (default 300 seconds)
    url:
        description: URL to use if not official (for experimenting)
'''

EXAMPLES = '''
- name: load_balancer | droplet | create
  doboto_droplet:
    action: create
    names:
      - droplet-create-01
      - droplet-create-02
      - droplet-create-03
    region: nyc3
    size: 1gb
    image: ubuntu-14-04-x64
    tags: yasss
    wait: true
  register: load_balancer_droplet_create

- name: load_balancer | create | droplets
  doboto_load_balancer:
    token: "{{ lookup('env','DO_API_TOKEN') }}"
    action: create
    name: load-balancer-create-droplets
    region: nyc3
    droplet_ids: "{{ load_balancer_droplet_create.droplets[0].id }}"
    forwarding_rules:
      -
        entry_protocol: https
        entry_port: 443
        target_protocol: https
        target_port: 443
        tls_passthrough: true
    wait: true
  register: load_balancer_create_droplets

- name: load_balancer | present | droplets | exists
  doboto_load_balancer:
    action: present
    name: load-balancer-create-droplets
    region: nyc3
    droplet_ids: "{{ load_balancer_droplet_create.droplets[0].id }}"
    forwarding_rules:
      -
        entry_protocol: http
        entry_port: 80
        target_protocol: http
        target_port: 80
    wait: true
  register: load_balancer_present_droplets

- name: load_balancer | certificate
  doboto_certificate:
    action: create
    name: load-balancer-certificate
    private_key: "{{ lookup('file', 'private.pem') }}"
    leaf_certificate: "{{ lookup('file', 'public.pem') }}"
    certificate_chain: "{{ lookup('file', 'public.pem') }}"
  register: load_balancer_certificate

- name: load_balancer | present | tag | new
  doboto_load_balancer:
    action: present
    name: load-balancer-present-tag
    region: nyc3
    tag: yasss
    forwarding_rules:
      -
        certificate_id: "{{ load_balancer_certificate.certificate.id }}"
        entry_protocol: https
        entry_port: 443
        target_protocol: https
        target_port: 443
    wait: true
  register: load_balancer_present_tag

- name: load_balancer | destroy
  doboto_load_balancer:
    action: destroy
    id: "{{ load_balancer_present_tag.load_balancer.id }}"
  register: load_balancer_destroy

- name: load_balancer | list
  doboto_load_balancer:
    action: list
  register: load_balancer_list

- name: load_balancer | info
  doboto_load_balancer:
    action: info
    id: "{{ load_balancer_create_droplets.load_balancer.id }}"
  register: load_balancer_info

- name: load_balancer | update | droplets
  doboto_load_balancer:
    action: update
    id: "{{ load_balancer_create_droplets.load_balancer.id }}"
    name: load-balancer-update-droplets
    region: nyc3
    algorithm: round_robin
    health_check:
      check_interval_seconds: 10
      healthy_threshold: 5
      path: "/"
      port: 80
      protocol: http
      response_timeout_seconds: 5
      unhealthy_threshold: 3
    droplet_ids: "{{ load_balancer_droplet_create.droplets[1].id }}"
    forwarding_rules:
      -
        entry_protocol: http
        entry_port: 8080
        target_protocol: http
        target_port: 8080
    wait: true
  register: load_balancer_update_droplets

- name: load_balancer | droplet_add
  doboto_load_balancer:
    action: droplet_add
    id: "{{ load_balancer_create_droplets.load_balancer.id }}"
    droplet_ids: "{{ load_balancer_droplet_create.droplets[2].id }}"
  register: load_balancer_droplet_add

- name: load_balancer | droplet_remove
  doboto_load_balancer:
    action: droplet_remove
    id: "{{ load_balancer_create_droplets.load_balancer.id }}"
    droplet_ids: "{{ load_balancer_droplet_create.droplets[1].id }}"
  register: load_balancer_droplet_remove

- name: load_balancer | forwarding_rule_add
  doboto_load_balancer:
    action: forwarding_rule_add
    id: "{{ load_balancer_create_droplets.load_balancer.id }}"
    forwarding_rules:
      -
        entry_protocol: http
        entry_port: 80
        target_protocol: http
        target_port: 80
  register: load_balancer_forwarding_rule_add

- name: load_balancer | forwarding_rule_remove
  doboto_load_balancer:
    action: forwarding_rule_remove
    id: "{{ load_balancer_create_droplets.load_balancer.id }}"
    forwarding_rules:
      -
        entry_protocol: http
        entry_port: 8080
        target_protocol: http
        target_port: 8080
  register: load_balancer_forwarding_rule_remove
'''

RETURNS = '''

'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.digitalocean_doboto import DOBOTOModule

class LoadBalancer(DOBOTOModule):

    def input(self):

        argument_spec = self.argument_spec()

        argument_spec.update(
            dict(
                action=dict(required=True, default="list", choices=[
                    "list",
                    "create",
                    "present",
                    "info",
                    "update",
                    "destroy",
                    "droplet_add",
                    "droplet_remove",
                    "forwarding_rule_add",
                    "forwarding_rule_remove"
                ]),
                id=dict(default=None),
                name=dict(default=None),
                algorithm=dict(default=None),
                region=dict(default=None),
                forwarding_rules=dict(default=None, type='list'),
                health_check=dict(default=None, type='dict'),
                sticky_sessions=dict(default=None, type='list'),
                redirect_http_to_https=dict(default=None, type='bool'),
                droplet_ids=dict(default=None, type='list'),
                tag=dict(default=None),
                wait=dict(default=False, type='bool'),
                poll=dict(default=5, type='int'),
                timeout=dict(default=300, type='int')
            )
        )

        return AnsibleModule(
            argument_spec=argument_spec,
            required_if=[
                ["action", "create", ["name", "region", "forwarding_rules"]],
                ["action", "present", ["name", "region", "forwarding_rules"]],
                ["action", "info", ["id"]],
                ["action", "update", ["id", "name", "region", "forwarding_rules"]],
                ["action", "destroy", ["id"]],
                ["action", "droplet_add", ["id", "droplet_ids"]],
                ["action", "droplet_remove", ["id", "droplet_ids"]],
                ["action", "forwarding_rule_add", ["id", "forwarding_rules"]],
                ["action", "forwarding_rule_remove", ["id", "forwarding_rules"]]
            ]
        )

    def list(self):

        self.module.exit_json(
            changed=False,
            load_balancers=self.do.load_balancer.list()
        )

    def attribs(self):

        attribs = {
            "name": self.module.params["name"],
            "region": self.module.params["region"],
            "forwarding_rules": self.module.params["forwarding_rules"]
        }

        for optional in [
                'algorithm', 'health_check', 'sticky_sessions',
                'redirect_http_to_https', 'droplet_ids', 'tag'
        ]:
            if self.module.params[optional] is not None:
                attribs[optional] = self.module.params[optional]

        return attribs

    def create(self):

        attribs = self.attribs()

        self.module.exit_json(
            changed=True,
            load_balancer=self.do.load_balancer.create(
                attribs,
                self.module.params["wait"],
                self.module.params["poll"],
                self.module.params["timeout"]
            )
        )

    def present(self):

        attribs = self.attribs()

        (load_balancer, created) = self.do.load_balancer.present(
            attribs,
            self.module.params["wait"],
            self.module.params["poll"],
            self.module.params["timeout"]
        )

        self.module.exit_json(
            changed=(created is not None),
            load_balancer=load_balancer,
            created=created
        )

    def info(self):

        self.module.exit_json(
            changed=False,
            load_balancer=self.do.load_balancer.info(
                self.module.params["id"]
            )
        )

    def update(self):

        attribs = self.attribs()

        self.module.exit_json(
            changed=True,
            load_balancer=self.do.load_balancer.update(
                self.module.params["id"],
                attribs
            )
        )

    def destroy(self):

        self.module.exit_json(
            changed=True,
            result=self.do.load_balancer.destroy(
                self.module.params["id"]
            )
        )

    def droplet_add(self):

        self.module.exit_json(
            changed=True,
            result=self.do.load_balancer.droplet_add(
                self.module.params["id"],
                self.module.params["droplet_ids"]
            )
        )

    def droplet_remove(self):

        self.module.exit_json(
            changed=True,
            result=self.do.load_balancer.droplet_remove(
                self.module.params["id"],
                self.module.params["droplet_ids"]
            )
        )

    def forwarding_rule_add(self):

        self.module.exit_json(
            changed=True,
            result=self.do.load_balancer.forwarding_rule_add(
                self.module.params["id"],
                self.module.params["forwarding_rules"]
            )
        )

    def forwarding_rule_remove(self):

        self.module.exit_json(
            changed=True,
            result=self.do.load_balancer.forwarding_rule_remove(
                self.module.params["id"],
                self.module.params["forwarding_rules"]
            )
        )

if __name__ == '__main__':
    LoadBalancer()
