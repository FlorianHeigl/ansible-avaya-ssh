#!/usr/bin/python

# Copyright 2015 Miles Davis <mileswdavis@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

DOCUMENTATION = '''
---

module: avaya_vsp_ssh_save_config
author: Miles Davis (mileswdavis@gmail.com)
short_description: Saves the configuration.
description:
    - Saves running configuration to startup configuration.
requirements:
    - netmiko
options:
    host:
        description:
            - Typically set to {{ inventory_hostname }}
        required: true
    port:
        description:
            - Port on which SSH is running
        required: false
    username:
        description:
            - Username for SSH login
        required: true
    password:
        description:
            - Password for SSH login
        required: true
'''

EXAMPLES = '''
# Save configuration with standard port 22
- avaya_vsp_ssh_save_config: host={{ inventory_hostname }} username=admin password=avaya123

# Save configuration with custom port
- avaya_vsp_ssh_save_config:
    host={{ inventory_hostname }}
    port=1022
    username=admin
    password=avaya123
'''

from ansible.module_utils.basic import *
try:
    from netmiko import ConnectHandler
    from netmiko.avaya import AvayaVspSSH
    has_netmiko = True
except:
    has_netmiko = False

def save_config(handler,module):
    save_command = 'copy run start'
    save_reply = 'Save config to file /intflash/config.cfg successful.'
    try:
        handler.enable()
        output = handler.send_command_expect(save_command)
        if not save_reply in output:
            module.fail_json(msg="Got this save output: %s. Likely unable to save." % output)
    except Exception, err:
        module.fail_json(msg=str(err))

    return {'changed':True}

def main():
    # Set our needed parameters for integration into Ansible
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(required=True),
            port=dict(required=False,default=22),
            username=dict(required=True),
            password=dict(required=True),))

    ansible_arguments = module.params

    # Check to make sure that netmiko is there. If not then bail out.
    if not has_netmiko:
        module.fail_json(msg='Missing required Netmiko module')

    # Port the Ansible arguemnts into a Netmiko variable
    vsp_device = {
        'device_type':'avaya_vsp',
        'ip':ansible_arguments['host'],
        'port':ansible_arguments['port'],
        'username':ansible_arguments['username'],
        'password':ansible_arguments['password'],
    }

    # Setup the Netmiko SSH Handler with the parameters pulled from Ansible. 
    # Catch any exceptions that might come from Netmiko and throw it to Ansible.
    try:
        ssh_handler = ConnectHandler(**vsp_device)
    except Exception, err:
        module.fail_json(msg=str(err))

    # Meat and Potatos. In this case, save the config.
    return_status = save_config(ssh_handler,module)

    # Send Ansible a hopefully good report of successful save.
    module.exit_json(**return_status)

main()
