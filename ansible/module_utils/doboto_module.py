#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
from ansible.module_utils.basic import AnsibleModule

"""
Ansible util for DigitalOcean DOBOTO modules
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

try:
    from doboto.DO import DO
    from doboto.exception import DOBOTOException, DOBOTONotFoundException, DOBOTOPollingException
    HAS_DOBOTO = True
except:
    HAS_DOBOTO = False


def require(*required):
    def requirer(function):
        def wrapper(*args, **kwargs):
            params = required
            if not isinstance(params, tuple):
                params = (params,)
            met = False
            for param in params:
                if args[0].module.params[param] is not None:
                    met = True
            if not met:
                args[0].module.fail_json(msg="the %s parameter is required" % " or ".join(params))
            function(*args, **kwargs)
        return wrapper
    return requirer


class DOBOTOModule(object):

    url = "https://api.digitalocean.com/v2"
    agent = "DOBOTO Ansible"

    def __init__(self):

        self.module = self.input()

        if not HAS_DOBOTO:
            self.module.fail_json(msg="the doboto package is required")

        token = self.module.params["token"]

        if token is None:
            token = os.environ.get('DO_API_TOKEN', None)

        if token is None:
            self.module.fail_json(msg="the token parameter is required")

        self.do = DO(token=token, url=self.module.params["url"], agent=self.agent)

        try:
            self.act()
        except DOBOTONotFoundException as exception:
            self.module.fail_json(msg=exception.message)
        except DOBOTOPollingException as exception:
            self.module.fail_json(
                msg=exception.message,
                polling=exception.result,
                error=exception.result
            )
        except DOBOTOException as exception:
            self.module.fail_json(msg=exception.message, result=exception.result)

    def act(self):
        getattr(self, self.module.params["action"])()
