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

module: avaya_vsp_ssh_software
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
    new_image_filename:
        description:
            - The filename of the new image residing on the SCP server. The filename should end in a .tgz. For example 'VOSS4K.0.0.0.0int647.tgz'.
        required: false
        reliance: Needed if upload_image_confirm is set to true.
    new_image_version:
        description:
            - The version of the new image to be uploaded, activated, or rebooted to. If you are utilizing the upload functionality of this module, the version name can be detected automatically. Otherwise be cautious when using this variable as it doesn't always align well with the filename of the new image. An example is '3.1.0.2.GA'.
        required: false
        reliance: If not using the upload functionality this will be required as it will not automatically be detected and is needed in order to activate and safely reboot.    
    scp_server_host:
        description: The IP address or hostname of the SCP server that will contain the new image to upload.
        required: false
        reliance: This will be required if uploading a new image.
    scp_server_port:
        description: 
            - The port on which the SCP server is running.
        required: false
        reliance: This will be required if uploading a new image and the server is running on a non-standard port (not port 22).
    scp_server_directory:
        description:
            - The directory on the SCP server where the new image resides.
        required: false
        relaince: This will be required if uploading a new image and image resides in something other than the default directory of the SCP server.
    del_image_version:
        description:
            - The version of the image to be deleted if there is no additional room for images is availible on the switch. This is not needed if the user is OK with allowing the script to automatically select the oldest image version residing on the switch and remove that one.
        required: false
        reliance: This will only be carried out if we are uploading a new image.    
    del_image_oldest_confirm:
        description:
            - This is a user confrimation to confirm that the user is OK with deletion of the oldest image on the switch if no additional room is availible.
        required: false
        default: false
        reliance: This will only come into play if a user is uploading a new image and there is no additional space availible.
    upload_image_confirm:
        description:
            - This is a user confrimation to confirm that the user wants to upload a new image to the switch.
        required: false
        default: false
    activate_image_confirm:
        description:
            - This is a user confrimation to confirm that the user wants to activate the new image that was either just uploaded or was specified in the new_image_version variable.
        required: false
        default: false
    reboot_image_confirm:
        description:
            - This is a user confrimation to confirm that the user wants to reboot the switch to enable the new image that was either just uploaded or just activated (or both).
        required: false
        default: false    
    wait_for_success_confirm:
        description:
            - This is a user confrimation to confirm that the user wants to wait for the switch to reboot fully and check the running version of the switch to ensure success before exiting the script.
        required: false
        default: false
        reliance: This only comes into play if reboot_image_confirm is set to true, as otherwise we would not be rebooting the switch.
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
# Manually set this to enable debug mode. In this case the script will run without the requirement of Ansible.
debug_mode=True

if not debug_mode:
    from ansible.module_utils.basic import *
try:
    from netmiko import ConnectHandler
    from netmiko.avaya import AvayaVspSSH
    has_netmiko = True
except:
    has_netmiko = False

def save_config(handler,module=0):

    # Manually set this to enable debug mode. Debug mode will run the script standalone without the need for interaction with Ansible

    save_command = 'copy run start'
    save_reply = 'Save config to file /intflash/config.cfg successful.'
    try:
        handler.enable()
        output = handler.send_command_expect(save_command)
        if not save_reply in output:
            if not debug_mode:
                module.fail_json(msg="Got this save output: %s. Likely unable to save." % output)
            else:
                print "Got this save output: %s. Likely unable to save." % output
        elif debug_mode:
            print 'Save Config Successful: %s' % output
    except Exception, err:
        if not debug_mode:
            module.fail_json(msg=str(err))
        else:
            print str(err)

    return {'changed':True}

def main():

    # Set our needed parameters for integration into Ansible
    if not debug_mode:
        module = AnsibleModule(
            argument_spec=dict(
                host=dict(required=True),
                port=dict(required=False,default=22),
                username=dict(required=True),
                password=dict(required=True),))
        ansible_arguments = module.params

    # Check to make sure that netmiko is there. If not then bail out.
    if not has_netmiko:
        if not debug_mode:
            module.fail_json(msg='Missing required Netmiko module')
        else:
            print 'Missing required Netmiko module'

    # Port the Ansible arguemnts into a Netmiko variable
    if not debug_mode:
        vsp_device = {
            'device_type':'avaya_vsp',
            'ip':ansible_arguments['host'],
            'port':ansible_arguments['port'],
            'username':ansible_arguments['username'],
            'password':ansible_arguments['password'],
        }
    else:
        vsp_device = {
            'device_type':'avaya_vsp',
            'ip':'10.177.213.76',
            'port':22,
            'username':'admin',
            'password':'avaya123',
        }

    # Setup the Netmiko SSH Handler with the parameters pulled from Ansible. 
    # Catch any exceptions that might come from Netmiko and throw it to Ansible.
    try:
        ssh_handler = ConnectHandler(**vsp_device)
    except Exception, err:
        if not debug_mode:
            module.fail_json(msg=str(err))
        else:
            print str(err)

    # Meat and Potatos. In this case, save the config.
    if not debug_mode:
        return_status = save_config(ssh_handler,module)
    else:
        return_status = save_config(ssh_handler)

    # Send Ansible a hopefully good report of successful save.
    if not debug_mode:
        module.exit_json(**return_status)

main()
