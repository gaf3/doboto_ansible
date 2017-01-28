#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

Ansible module to manage DigitalOcean account
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
module: doboto_account

short_description: Manage DigitalOcean Account
description:
    - Manages DigitalOcean account
version_added: "0.1"
author: "Gaffer Fitch <gfitch@digitalocean.com>"
options:
    token:
        description:
            - token to use to connect to the API (uses DO_API_TOKEN from ENV if not found)
    url:
        description:
            - URL to use if not official (for experimenting)
'''

EXAMPLES = '''
'''

import os
from ansible.module_utils.basic import *

try:
    from doboto.DO import DO
except ImportError:
    doboto_found = False
else:
    doboto_found = True


def main():

    module = AnsibleModule(
        argument_spec = dict(
            token=dict(default=None),
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

    result = do.account.info()

    if "account" not in result:
        module.fail_json(msg="DO API error", result=result)

    module.exit_json(changed=False, account=result['account'])

main()
