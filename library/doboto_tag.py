#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Ansible module to manage DigitalOcean tags
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
module: doboto_tag

short_description: Manage DigitalOcean Tags
description:
    - Manages DigitalOcean tags
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
            - present
            - info
            - list
            - update
            - attach
            - detach
            - destroy
    name:
        description:
            - same as DO API variable
    new_name:
        description:
            - same as DO API variable, new name for updating
    resources:
        description:
            - same as DO API variable
    resource_type:
        description:
            - same as DO API variable, use if doing a single resource type
    resource_id:
        description:
            - same as DO API variable, use if doing a single resource id
    resource_ids:
        description:
            - paired with a single resource_type to build a resources list
    url:
        description:
            - URL to use if not official (for experimenting)
'''

EXAMPLES = '''
'''

import os
import copy
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

    result = do.tag.create(module.params["name"])

    if "tag" not in result:
        module.fail_json(msg="DO API error", result=result)

    module.exit_json(changed=True, tag=result['tag'])


def present(do, module):

    if module.params["name"] is None:
        module.fail_json(msg="the name parameter is required")

    result = do.tag.list()

    if "tags" not in result:
        module.fail_json(msg="DO API error", result=result)

    tags = result["tags"]

    existing = None
    for tag in tags:
        if module.params["name"] == tag["name"]:
            existing = tag
            break

    if existing is not None:
        module.exit_json(changed=False, tag=existing)
    else:
        create(do, module)


def info(do, module):

    result = None

    if module.params["name"] is None:
        module.fail_json(msg="the name parameter is required")

    result = do.tag.info(module.params["name"])

    if "tag" not in result:
        module.fail_json(msg="DO API error", result=result)

    module.exit_json(changed=False, tag=result['tag'])


def list(do, module):

    result = do.tag.list()

    if "tags" not in result:
        module.fail_json(msg="DO API error", result=result)

    module.exit_json(changed=False, tags=result["tags"])


def names(do, module):

    result = do.tag.names()

    if "tags" not in result:
        module.fail_json(msg="DO API error", result=result)

    module.exit_json(changed=False, tags=result["tags"])


def update(do, module):

    result = None

    if module.params["name"] is None:
        module.fail_json(msg="the name parameter is required")

    if module.params["new_name"] is None:
        module.fail_json(msg="the new_name parameter is required")

    result = do.tag.update(module.params["name"], module.params["new_name"])

    if "tag" not in result:
        module.fail_json(msg="DO API error", result=result)

    module.exit_json(changed=True, tag=result['tag'])


def build(do, module):

    resources = []

    if module.params["resource_type"] is not None and module.params["resource_id"] is not None:
        resources.append({
            "resource_type": module.params["resource_type"],
            "resource_id": module.params["resource_id"]
        })

    if module.params["resource_type"] is not None and module.params["resource_ids"] is not None:
        for resource_id in module.params["resource_ids"]:
            resources.append({
                "resource_type": module.params["resource_type"],
                "resource_id": resource_id
            })

    if module.params["resources"] is not None:
        resources.extend(copy.deepcopy(module.params["resources"]))

    return resources


def attach(do, module):

    result = None

    if module.params["name"] is None:
        module.fail_json(msg="the name parameter is required")

    resources = build(do, module)

    if not resources:
        module.fail_json(
            msg="the resources or resource_type and resource_id(s) parameters are required"
        )

    result = do.tag.attach(module.params["name"], resources)

    if "status" not in result:
        module.fail_json(msg="DO API error", result=result)

    module.exit_json(changed=True, result=result)


def detach(do, module):

    result = None

    if module.params["name"] is None:
        module.fail_json(msg="the name parameter is required")

    resources = build(do, module)

    if not resources:
        module.fail_json(
            msg="the resources or resource_type and resource_id(s) parameters are required"
        )

    result = do.tag.detach(module.params["name"], resources)

    if "status" not in result:
        module.fail_json(msg="DO API error", result=result)

    module.exit_json(changed=True, result=result)


def destroy(do, module):

    result = None

    if module.params["name"] is None:
        module.fail_json(msg="the name parameter is required")

    result = do.tag.destroy(module.params["name"])

    if "status" not in result:
        module.fail_json(msg="DO API error", result=result)

    module.exit_json(changed=True, result=result)


def main():

    module = AnsibleModule(
        argument_spec = dict(
            action=dict(default=None, required=True, choices=[
                "create",
                "present",
                "info",
                "list",
                "update",
                "attach",
                "detach",
                "destroy"
            ]),
            token=dict(default=None),
            name=dict(default=None),
            new_name=dict(default=None),
            resources=dict(default=None, type='list'),
            resource_type=dict(default=None),
            resource_id=dict(default=None),
            resource_ids=dict(default=None, type='list'),
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
    elif module.params["action"] == "present":
        present(do, module)
    elif module.params["action"] == "info":
        info(do, module)
    elif module.params["action"] == "list":
        list(do, module)
    elif module.params["action"] == "update":
        update(do, module)
    elif module.params["action"] == "attach":
        attach(do, module)
    elif module.params["action"] == "detach":
        detach(do, module)
    elif module.params["action"] == "destroy":
        destroy(do, module)

main()
