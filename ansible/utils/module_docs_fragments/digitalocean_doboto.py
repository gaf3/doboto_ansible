# (c) 2017, SWE Data <swe-data@do.co>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.


class ModuleDocFragment(object):

    # DigitalOcean documentation fragment
    DOCUMENTATION = """
options:
    token:
        description:
          - token used to connect to the API (uses DO_API_TOKEN from ENV if not found).
        required: True
        default: null
    url:
        description:
          - URL of digitalocean api.
        required: True
        default: https://api.digitalocean.com/v2

requirements:
  - doboto
    """
