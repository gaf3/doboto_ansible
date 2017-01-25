#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Ansible module to manage DigitalOcean ssh keys
(c) 2017, Gaffer Fitch <gfitch@digitalocean.com>

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
module: doboto_ssh_key

short_description: Manage DigitalOcean SSH Keys
description:
    - Manages DigitalOcean ssh keys
version_added: "0.1"
author: "Gaffer Fitch <gfitch@digitalocean.com>"
options:
    token:
        description:
            - token to use to connect to the API (uses DO_API_TOKEN from ENV if not found)
    action:
        ssh key action
        choices:
            - create
            - list
            - info
            - update
            - destroy
    id:
        description:
            - (SSH Key ID) same as DO API variable
    name:
        description:
            - same as DO API variable (for single create)
    public_key:
        description:
            - same as DO API variable (for mass create)
    fingerprint:
        description:
            - same as DO API variable
    url:
        description:
            - URL to use if not official (for experimenting)
'''

EXAMPLES = '''
# Create a droplet
- doboto_droplet: action=create

'''

import os
from ansible.module_utils.basic import *

try:
    from doboto.DO import DO
except ImportError:
    doboto_found = False
else:
    doboto_found = True


def create(do, module):

    if module.params["name"] is None:
        module.fail_json(msg="the name parameter is required")

    if module.params["public_key"] is None:
        module.fail_json(msg="the public_key parameter is required")

    result = do.ssh_key.create(module.params["name"], module.params["public_key"])

    if "ssh_key" not in result:
        module.fail_json(msg="DO API error", result=result)

    module.exit_json(changed=True, ssh_key=result['ssh_key'])


def list(do, module):

    result = do.ssh_key.list()

    if "ssh_keys" not in result:
        module.fail_json(msg="DO API error", result=result)

    module.exit_json(changed=True, ssh_keys=result["ssh_keys"])


def info(do, module):

    result = None

    if module.params["id"] is not None:
        result = do.ssh_key.info(module.params["id"])
    elif module.params["fingerprint"] is not None:
        result = do.ssh_key.info(module.params["fingerprint"])
    else:
        module.fail_json(msg="the id or fingerprint parameter is required")

    if "ssh_key" not in result:
        module.fail_json(msg="DO API error", result=result)

    module.exit_json(changed=True, ssh_key=result["ssh_key"])


def update(do, module):

    result = None

    if module.params["name"] is None:
        module.fail_json(msg="the name parameter is required")

    if module.params["id"] is not None:
        result = do.ssh_key.update(module.params["id"], module.params["name"])
    elif module.params["fingerprint"] is not None:
        result = do.ssh_key.update(module.params["fingerprint"], module.params["name"])
    else:
        module.fail_json(msg="the id or fingerprint parameter is required")

    if "ssh_key" not in result:
        module.fail_json(msg="DO API error", result=result)

    module.exit_json(changed=True, ssh_key=result["ssh_key"])


def destroy(do, module):

    result = None

    if module.params["id"] is not None:
        result = do.ssh_key.destroy(module.params["id"])
    elif module.params["fingerprint"] is not None:
        result = do.ssh_key.destroy(module.params["fingerprint"])
    else:
        module.fail_json(msg="the id or fingerprint parameter is required")

    if "status" not in result:
        module.fail_json(msg="DO API error", result=result)

    module.exit_json(changed=True, result=result)


def main():

    module = AnsibleModule(
        argument_spec = dict(
            action=dict(default=None, required=True, choices=[
                "create", "list", "info", "update", "destroy"
            ]),
            token=dict(default=None),
            id=dict(default=None),
            fingerprint=dict(default=None),
            public_key=dict(default=None),
            name=dict(default=None),
            url=dict(default="https://api.digitalocean.com/v2"),
        )
    )

    if not doboto_found:
        module.fail_json(msg="the python doboto module is required")

    token = module.params["token"]

    if token is None:
        token = os.environ.get('DO_API_TOKEN', None)

    if token is None:
        module.fail_json(msg="the token parameter is required")

    do = DO(url=module.params["url"], token=token)

    if module.params["action"] == "create":
        create(do, module)
    elif module.params["action"] == "list":
        list(do, module)
    elif module.params["action"] == "info":
        info(do, module)
    elif module.params["action"] == "update":
        update(do, module)
    elif module.params["action"] == "destroy":
        destroy(do, module)

main()
