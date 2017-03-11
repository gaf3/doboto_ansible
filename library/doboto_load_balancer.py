#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.doboto_module import require, DOBOTOModule

"""
Ansible module to manage DigitalOcean load balancers
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
module: doboto_load_balancer

short_description: Manage DigitalOcean load balancers
description: Manages DigitalOcean Load Balancers
version_added: "0.6.0"
author: "SWE Data <swe-data@do.co>"
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
'''


class LoadBalancer(DOBOTOModule):

    def input(self):
        return AnsibleModule(argument_spec=dict(
            action=dict(default=None, required=True, choices=[
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
            token=dict(default=None, no_log=True),
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
            timeout=dict(default=300, type='int'),
            url=dict(default=self.url)
        ))

    def list(self):
        self.module.exit_json(changed=False, load_balancers=self.do.load_balancer.list())

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

    @require("name")
    @require("region")
    @require("forwarding_rules")
    def create(self):

        attribs = self.attribs()

        self.module.exit_json(changed=True, load_balancer=self.do.load_balancer.create(
            attribs,
            self.module.params["wait"],
            self.module.params["poll"],
            self.module.params["timeout"]
        ))

    @require("name")
    @require("region")
    @require("forwarding_rules")
    def present(self):

        attribs = self.attribs()

        (load_balancer, created) = self.do.load_balancer.present(
            attribs,
            self.module.params["wait"],
            self.module.params["poll"],
            self.module.params["timeout"]
        )
        self.module.exit_json(
            changed=(created is not None), load_balancer=load_balancer, created=created
        )

    @require("id")
    def info(self):
        self.module.exit_json(changed=False, load_balancer=self.do.load_balancer.info(
            self.module.params["id"]
        ))

    @require("id")
    @require("name")
    @require("region")
    @require("forwarding_rules")
    def update(self):

        attribs = self.attribs()

        self.module.exit_json(changed=True, load_balancer=self.do.load_balancer.update(
            self.module.params["id"], attribs
        ))

    @require("id")
    def destroy(self):
        self.module.exit_json(changed=True, result=self.do.load_balancer.destroy(
            self.module.params["id"]
        ))

    @require("id")
    @require("droplet_ids")
    def droplet_add(self):
        self.module.exit_json(changed=True, result=self.do.load_balancer.droplet_add(
            self.module.params["id"], self.module.params["droplet_ids"]
        ))

    @require("id")
    @require("droplet_ids")
    def droplet_remove(self):
        self.module.exit_json(changed=True, result=self.do.load_balancer.droplet_remove(
            self.module.params["id"], self.module.params["droplet_ids"]
        ))

    @require("id")
    @require("forwarding_rules")
    def forwarding_rule_add(self):
        self.module.exit_json(changed=True, result=self.do.load_balancer.forwarding_rule_add(
            self.module.params["id"], self.module.params["forwarding_rules"]
        ))

    @require("id")
    @require("forwarding_rules")
    def forwarding_rule_remove(self):
        self.module.exit_json(changed=True, result=self.do.load_balancer.forwarding_rule_remove(
            self.module.params["id"], self.module.params["forwarding_rules"]
        ))


if __name__ == '__main__':
    LoadBalancer()
