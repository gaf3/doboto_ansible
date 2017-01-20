#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Ansible module to manage DigitalOcean droplets
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
module: doboto_droplet

short_description: Manage DigitalOcean droplets
description:
    - Manages DigitalOcean droplets
version_added: "0.1"
author: "Gaffer Fitch <gfitch@digitalocean.com>"
options:
    token:
        description:
            - token to use to connect to the API
    action:
        droplet action
        choices:
            - create
    name:
        description:
            - same as DO API variable (for single create)
    names:
        description:
            - same as DO API variable (for mass create)
    region:
        description:
            - same as DO API variable
    size:
        description:
            - same as DO API variable
    image:
        description:
            - same as DO API variable
    ssh_keys:
        description:
            - same as DO API variable (if single value, converted to array)
    backups:
        description:
            - same as DO API variable
    ipv6:
        description:
            - same as DO API variable
    private_networking:
        description:
            - same as DO API variable
    user_data:
        description:
            - same as DO API variable
    monitoring:
        description:
            - same as DO API variable
    volume:
        description:
            - same as DO API variable (if single value, converted to array)
    tags:
        description:
            - same as DO API variable (if single value, converted to array)
    wait:
        description:
            - wait until tasks has completed before continuing
    poll:
        description:
            - poll value to check while waiting (default 5 seconds)
    url:
        description:
            - URL to use if not official (for experimenting)
    extra:
        description:
            - key / value of extra values to send (for experimenting)

'''

EXAMPLES = '''
# Create a droplet
- doboto_droplet: action=create

'''

import time
from ansible.module_utils.basic import *

try:
    from doboto.DO import DO
except ImportError:
    doboto_found = False
else:
    doboto_found = True


def create(do, module):

    attribs = {}

    if module.params["name"] is not None:
        attribs["name"] = module.params["name"]
    elif module.params["names"] is not None:
        attribs["names"] = module.params["names"]
    else:
        module.fail_json(msg="the name or names parameter is required")

    for required in ['region', 'size', 'image']:
        if module.params[required] is None:
            module.fail_json(msg="the %s parameter is required" % required)
        attribs[required] = module.params[required]

    for optional in [
        'ssh_keys', 'volume', 'tags','backups', 'ipv6',
        'private_networking', 'user_data', 'monitoring'
    ]:
        attribs[optional] = module.params[optional]

    if module.params['extra'] is not None:
        attribs.update(module.params['extra'])

    result = do.droplet.create(attribs)

    if "droplet" not in result and "droplets" not in result:
        module.fail_json(msg="DO API error", result=result)

    if "droplet" in result:

        droplet = result["droplet"]

        while module.params["wait"] and result["droplet"]["status"] == "new":

            time.sleep(module.params["poll"])
            latest = do.droplet.info(droplet["id"])
            if "droplet" in latest:
                result = latest

        module.exit_json(changed=True, droplet=result['droplet'])

    elif "droplets" in result:

        droplets = result["droplets"]

        while module.params["wait"] and \
            len([1 for droplet in result["droplets"] if droplet["status"] == "new"]) > 0:

            time.sleep(module.params["poll"])

            for index, droplet in enumerate(result["droplets"]):
                if droplet["status"] == "new":
                    latest = do.droplet.info(droplet["id"])
                    if "droplet" in latest:
                        result["droplets"][index] = latest["droplet"]

        module.exit_json(changed=True, droplets=result['droplets'])

    else:

        module.fail_json(msg="DO API error", result=result)

def main():

    module = AnsibleModule(
        argument_spec = dict(
            action=dict(default=None, required=True, choices=["create"]),
            token=dict(default=None, required=True),
            name=dict(default=None),
            names=dict(default=None, type='list'),
            region=dict(default=None),
            size=dict(default=None),
            image=dict(default=None),
            ssh_keys=dict(default=None, type='list'),
            backups=dict(default=False, type='bool'),
            ipv6=dict(default=False, type='bool'),
            private_networking=dict(type='bool'),
            user_data=dict(default=False, type='bool'),
            monitoring=dict(type='bool'),
            volume=dict(default=None, type='list'),
            tags=dict(default=None, type='list'),
            wait=dict(default=False, type='bool'),
            poll=dict(default=5, type='int'),
            url=dict(default="https://api.digitalocean.com/v2"),
            extra=dict(default=None, type='dict'),
        )
    )

    if not doboto_found:
        module.fail_json(msg="the python doboto module is required")

    do = DO(url=module.params["url"], token=module.params["token"])

    if module.params["action"] == "create":
        create(do, module)

main()
