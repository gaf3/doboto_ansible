#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import copy
from ansible.module_utils.basic import AnsibleModule
from doboto.DO import DO

"""

Ansible module to manage DigitalOcean domains
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
module: doboto_domain

short_description: Manage DigitalOcean domains
description:
    - Manages DigitalOcean Domains
version_added: "0.1"
author: "SWE Data <swe-data@do.co>"
options:
    token:
        description:
            - token to use to connect to the API (uses DO_API_TOKEN from ENV if not found)
    action:
        domain action
        choices:
            - list
            - create
            - info
            - destroy
            - record_list
            - record_create
            - record_info
            - record_update
            - record_destroy
    name:
        description:
            - same as DO API variable
    ip_address:
        description:
            - same as DO API variable
    record_id:
        description:
            - same as DO API variable id for records
    record_type:
        description:
            - same as DO API variable type for records
    record_name:
        description:
            - same as DO API variable name for records
    record_data:
        description:
            - same as DO API variable data for records
    record_priority:
        description:
            - same as DO API variable priority for records
    record_port:
        description:
            - same as DO API variable port for records
    record_weight:
        description:
            - same as DO API variable weight for records
    url:
        description:
            - URL to use if not official (for experimenting)
'''

EXAMPLES = '''
'''


class Domain(object):

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
                "create",
                "info",
                "update",
                "destroy",
                "record_list",
                "record_create",
                "record_info",
                "record_update",
                "record_destroy"
            ]),
            token=dict(default=None),
            name=dict(default=None),
            ip_address=dict(default=None),
            record_id=dict(default=None),
            record_type=dict(default=None),
            record_name=dict(default=None),
            record_data=dict(default=None),
            record_priority=dict(default=None),
            record_port=dict(default=None),
            record_weight=dict(default=None),
            url=dict(default=self.url)
        ))

    def act(self):

        getattr(self, self.module.params["action"])()

    def create(self):

        if self.module.params["name"] is None:
            self.module.fail_json(msg="the name parameter is required")

        if self.module.params["ip_address"] is None:
            self.module.fail_json(msg="the ip_address parameter is required")

        result = self.do.domain.create(
            self.module.params["name"], self.module.params["ip_address"]
        )

        if "domain" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=True, domain=result['domain'])

    def list(self):

        result = None

        result = self.do.domain.list()

        if "domains" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, domains=result["domains"])

    def info(self):

        if self.module.params["name"] is None:
            self.module.fail_json(msg="the name parameter is required")

        result = self.do.domain.info(self.module.params["name"])

        if "domain" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, domain=result["domain"])

    def destroy(self):

        if self.module.params["name"] is None:
            self.module.fail_json(msg="the name parameter is required")

        result = self.do.domain.destroy(self.module.params["name"])

        if "status" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=True, result=result)

    def record_list(self):

        if self.module.params["name"] is None:
            self.module.fail_json(msg="the name parameter is required")

        result = self.do.domain.record_list(self.module.params["name"])

        if "domain_records" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, domain_records=result["domain_records"])

    def record_create(self):

        if self.module.params["name"] is None:
            self.module.fail_json(msg="the name parameter is required")

        attribs = {}

        for field in [
            "type",
            "name",
            "data",
            "priority",
            "port",
            "weight"
        ]:
            if self.module.params["record_%s" % field] is not None:
                attribs[field] = self.module.params["record_%s" % field]

        result = self.do.domain.record_create(self.module.params["name"], attribs)

        if "domain_record" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=True, domain_record=result["domain_record"])

    def record_info(self):

        if self.module.params["name"] is None:
            self.module.fail_json(msg="the name parameter is required")

        if self.module.params["record_id"] is None:
            self.module.fail_json(msg="the record_id parameter is required")

        result = self.do.domain.record_info(
            self.module.params["name"], self.module.params["record_id"]
        )

        if "domain_record" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=False, domain_record=result["domain_record"])

    def record_update(self):

        if self.module.params["name"] is None:
            self.module.fail_json(msg="the name parameter is required")

        if self.module.params["record_id"] is None:
            self.module.fail_json(msg="the record_id parameter is required")

        attribs = {}

        for field in [
            "type",
            "name",
            "data",
            "priority",
            "port",
            "weight"
        ]:
            if self.module.params["record_%s" % field] is not None:
                attribs[field] = self.module.params["record_%s" % field]

        result = self.do.domain.record_update(
            self.module.params["name"], self.module.params["record_id"], attribs
        )

        if "domain_record" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=True, domain_record=result["domain_record"])

    def record_destroy(self):

        if self.module.params["name"] is None:
            self.module.fail_json(msg="the name parameter is required")

        if self.module.params["record_id"] is None:
            self.module.fail_json(msg="the record_id parameter is required")

        result = self.do.domain.record_destroy(
            self.module.params["name"], self.module.params["record_id"]
        )

        if "status" not in result:
            self.module.fail_json(msg="DO API error", result=result)

        self.module.exit_json(changed=True, result=result)


Domain()
