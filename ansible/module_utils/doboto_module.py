#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
from ansible.module_utils.basic import AnsibleModule
from doboto.DO import DO
from doboto.DOBOTOException import DOBOTOException

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

    def __init__(self):

        self.module = self.input()

        token = self.module.params["token"]

        if token is None:
            token = os.environ.get('DO_API_TOKEN', None)

        if token is None:
            self.module.fail_json(msg="the token parameter is required")

        self.do = DO(url=self.module.params["url"], token=token)

        self.act()

    def act(self):
        try:
            getattr(self, self.module.params["action"])()
        except DOBOTOException as exception:
            self.module.fail_json(msg=exception.message, result=exception.result)

    def action_result(self, action):

        start_time = time.time()

        while self.module.params["wait"] and action["status"] == "in-progress":

            time.sleep(self.module.params["poll"])
            try:
                action = self.do.action.info(action["id"])
            except:
                pass

            if time.time() - start_time > self.module.params["timeout"]:
                self.module.fail_json(msg="Timeout on polling", action=action)

        self.module.exit_json(changed=True, action=action)

    def actions_result(self, actions):

        start_time = time.time()

        while self.module.params["wait"] and \
                len([1 for action in actions if action["status"] == "in-progress"]) > 0:

            time.sleep(self.module.params["poll"])

            for index, action in enumerate(actions):
                if action["status"] == "in-progress":
                    try:
                        actions[index] = self.do.action.info(action["id"])
                    except:
                        pass

            if time.time() - start_time > self.module.params["timeout"]:
                self.module.fail_json(msg="Timeout on polling", actions=actions)

        self.module.exit_json(changed=True, actions=actions)
