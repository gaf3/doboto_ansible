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
            - token to use to connect to the API (uses DO_API_TOKEN from ENV if not found)
    action:
        droplet action
        choices:
            - create
            - present
            - list
            - info
            - destroy
    id:
        description:
            - same as DO API variable (droplet id)
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
    tag_name:
        description:
            - same as DO API variable (for tag ID)
    wait:
        description:
            - wait until tasks has completed before continuing
    poll:
        description:
            - poll value to check while waiting (default 5 seconds)
    timeout:
        description:
            - timeout value to give up after waiting (default 120 seconds)
    url:
        description:
            - URL to use if not official (for experimenting)
    extra:
        description:
            - key / value of extra values to send (for experimenting)

'''

EXAMPLES = '''
'''

import os
import time
import copy
from ansible.module_utils.basic import *

try:
    from doboto.DO import DO
except ImportError:
    doboto_found = False
else:
    doboto_found = True


def ready(droplet, module, existing):

    for exist in existing:
        if droplet["id"] == exist["id"]:
            return True

    if droplet["status"] == "new":
        return False

    if module.params["private_networking"]:
        found = False
        for v4 in droplet["networks"]["v4"]:
            if v4["type"] == "private":
                found = True
        if not found:
            return False

    if module.params["ipv6"] and not droplet["networks"]["v6"]:
        return False

    if module.params["tags"] and len(module.params["tags"]) != len(droplet["tags"]):
        return False

    return True


def create(do, module, existing=None):

    if existing is None:
        existing = []

    existing_names = {droplet["name"]: True for droplet in existing}

    attribs = {}

    if module.params["name"] is not None:
        attribs["name"] = module.params["name"]
    elif module.params["names"] is not None:
        attribs["names"] = []
        for name in module.params["names"]:
            if name not in existing_names:
                attribs["names"].append(name)
    else:
        module.fail_json(msg="the name or names parameter is required")

    for required in ['region', 'size', 'image']:
        if module.params[required] is None:
            module.fail_json(msg="the %s parameter is required" % required)
        attribs[required] = module.params[required]

    for optional in [
        'ssh_keys', 'volume', 'tags', 'backups', 'ipv6',
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

        start_time = time.time()

        while module.params["wait"] and not ready(result["droplet"], module, existing):

            time.sleep(module.params["poll"])
            latest = do.droplet.info(droplet["id"])
            if "droplet" in latest:
                result = latest

            if time.time() - start_time > module.params["timeout"]:
                module.fail_json(msg="Timeout on polling", droplet=result['droplet'])

        module.exit_json(changed=True, droplet=result['droplet'])

    elif "droplets" in result:

        droplets = copy.deepcopy(existing)
        droplets.extend(result["droplets"])

        start_time = time.time()

        while module.params["wait"] and \
          len([1 for droplet in droplets if not ready(droplet, module, existing)]) > 0:

            time.sleep(module.params["poll"])

            for index, droplet in enumerate(droplets):
                if not ready(droplet, module, existing):
                    latest = do.droplet.info(droplet["id"])
                    if "droplet" in latest:
                        droplets[index] = latest["droplet"]

            if time.time() - start_time > module.params["timeout"]:
                module.fail_json(msg="Timeout on polling", droplets=droplets)

        if not existing:
            module.exit_json(changed=True, droplets=droplets)
        else:
            created = [droplet for droplet in droplets if droplet["name"] not in existing_names]
            module.exit_json(changed=True, droplets=droplets, created=created)

    else:

        module.fail_json(msg="DO API error", result=result)


def present(do, module):

    if module.params["name"] is None and module.params["names"] is None:
        module.fail_json(msg="the name or names parameter is required")

    result = do.droplet.list()

    if "droplets" not in result:
        module.fail_json(msg="DO API error", result=result)

    droplets = result["droplets"]

    if module.params["name"] is not None:

        existing = None
        for droplet in droplets:
            if module.params["name"] == droplet["name"]:
                existing = droplet
                break

        if existing is not None:
            module.exit_json(changed=False, droplet=existing)
        else:
            create(do, module)

    else:

        existing = []

        for name in module.params["names"]:
            for droplet in droplets:
                if name == droplet["name"]:
                    existing.append(droplet)
                    break

        if len(existing) == len(module.params["names"]):
            module.exit_json(changed=False, droplets=existing)
        else:
            create(do, module, existing)


def list(do, module):

    result = None

    if module.params["tag_name"] is None:
        result = do.droplet.list()
    else:
        result = do.droplet.list(tag_name=module.params["tag_name"])

    if "droplets" not in result:
        module.fail_json(msg="DO API error", result=result)

    module.exit_json(changed=False, droplets=result["droplets"])


def info(do, module):

    result = None

    if module.params["id"] is None:
        module.fail_json(msg="the id parameter is required")

    result = do.droplet.info(module.params["id"])

    if "droplet" not in result:
        module.fail_json(msg="DO API error", result=result)

    module.exit_json(changed=False, droplet=result["droplet"])


def destroy(do, module):

    result = None

    if module.params["id"] is not None:
        result = do.droplet.destroy(id=module.params["id"])
    elif module.params["tag_name"] is not None:
        result = do.droplet.destroy(tag_name=module.params["tag_name"])
    else:
        module.fail_json(msg="the id or tag_name parameter is required")

    if "status" not in result:
        module.fail_json(msg="DO API error", result=result)

    module.exit_json(changed=True, result=result)

def main():

    module = AnsibleModule(
        argument_spec = dict(
            action=dict(default=None, required=True, choices=[
                "create", "present", "list", "info", "destroy"
            ]),
            token=dict(default=None),
            id=dict(default=None),
            name=dict(default=None),
            names=dict(default=None, type='list'),
            region=dict(default=None),
            size=dict(default=None),
            image=dict(default=None),
            ssh_keys=dict(default=None, type='list'),
            backups=dict(default=False, type='bool'),
            ipv6=dict(default=False, type='bool'),
            private_networking=dict(type='bool'),
            user_data=dict(default=False),
            monitoring=dict(type='bool'),
            volume=dict(default=None, type='list'),
            tags=dict(type='list'),
            tag_name=dict(default=None),
            wait=dict(default=False, type='bool'),
            poll=dict(default=5, type='int'),
            timeout=dict(default=120, type='int'),
            url=dict(default="https://api.digitalocean.com/v2"),
            extra=dict(default=None, type='dict'),
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
    elif module.params["action"] == "present":
        present(do, module)
    elif module.params["action"] == "list":
        list(do, module)
    elif module.params["action"] == "info":
        info(do, module)
    elif module.params["action"] == "destroy":
        destroy(do, module)

main()
