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
# Manually set this to enable debug mode. If set to True, the script will run without the requirement of Ansible.
debug_mode=True

if not debug_mode:
    from ansible.module_utils.basic import *
try:
    from netmiko import ConnectHandler
    from netmiko.avaya import AvayaVspSSH
    has_netmiko = True
except:
    has_netmiko = False
from time import sleep

def save_config(handler,module=0):

    save_command = 'copy run start'
    save_reply = 'Save config to file /intflash/config.cfg successful.'
    try:
        handler.enable()
        output = handler.send_command_expect(save_command)
        if not save_reply in output:
            if not debug_mode:
                module.fail_json(msg="Got this save output: %s. Likely unable to save." % output)
            else:
                print "**** Likely unable to save!"
                print output
        elif debug_mode:
            print '**** Save Config Successful'
            print output
    except Exception, err:
        if not debug_mode:
            module.fail_json(msg=str(err))
        else:
            print str(err)

    return {'changed':True}

def get_software_versions(handler, module=0):
    # Get the output of 'show sofware', formats it into a clean list, seperates out the primary and backup 
    # releases into a dictionary, and returns a list of all the releases as well as a dictionary containing 
    # the primary and backup release (if there is a backup release)

    show_software_command = 'show software'
    show_software_header = '================================================================================'
    show_software_footer = '--------------------------------------------------------------------------------'
    backup_release = '(Backup Release)'
    primary_release = '(Primary Release)'
    next_boot_release = '(Next Boot Release)'

    try:
        handler.enable()
        output = handler.send_command_expect(show_software_command)
    except Exception, err:
        if not debug_mode:
            module.fail_json(msg=str(err))
        else:
            print str(err)
    try:
        # Time to clean up this output
        # Remove the header
        versions = output.split(show_software_header)[-1]
        # Remove the footer
        versions = versions.split(show_software_footer)[0]
        # Split the remaining output
        versions = versions.split('\n')
        # Dump the empties
        versions = filter(None,versions)
        # Cleanup the versions and move the primary and backup release into their own dictionary
        primary_backup_release = {'primary':None, 'backup':None, 'next boot': None}
        for index,ver in enumerate(versions):
            # If we find the primary release then we should strip out the human readable part of it and put it into the dictioary that will get returned
            if primary_release in ver:
                versions[index] = ver.split(' ')[0]
                primary_backup_release['primary']=versions[index]
            # If we find the backup release then we should strip out the human readable part of it and put it into the dictioary that will get returned
            elif backup_release in ver:
                versions[index] = ver.split(' ')[0]
                primary_backup_release['backup']=versions[index]
            # If we find the next boot release then we should strip out the human readable part of it and put it into the dictionary that will get returned
            elif next_boot_release in ver:
                versions[index] = ver.split(' ')[0]
                primary_backup_release['next boot']=versions[index]
        if debug_mode:
            print output

    except Exception, err:
        if not debug_mode:
            module.fail_json(msg=str('There was a problem parsing the output of \'show sofware\'. This must have changed since this the module was written.'))
        else:
            print '**** There was a problem parsing the output of \'show sofware\'. This must have changed since this the module was written.'

    return versions, primary_backup_release

def activate_software_version(handler, activate_version, versions, pri_back, module=0):
    # Function takes the Netmiko SSH handler (handler), the version that we want to activate (activate_version),
    # the current software version list (versions), the current primary backup dictionary (pri_back), and the 
    # Ansible handler (module). It first confirms that the version to activate isn't already primary. It then 
    # check if the version even exitst. If both of those cases are passed, it logs into the switch and activates 
    # the software version passed. It returns an updated version of the primary_backup_release dictionary and 
    # returns whether the funtion actually changed anything.

    # Set some constants that hopefully will not change with different versions of code.
    software_activate_command = 'software activate '
    software_does_not_exist = 'does not exist in /intflash/release/.'
    software_already_primary = 'is already set as the primary version.'
    software_already_next_boot = 'is already set as the next boot release.'
    software_activate_success = 'Changes will take effect on next reboot.'
    software_version_consistent = 'IMAGE SYNC: Primary image is consistent'

    # Prepare a couple of variable that might be useful later.
    active_software_has_changed = False
    activate_command = software_activate_command + activate_version

    # Check to make sure that the version that is trying to be activated is already in flash.
    # If not let's tell Ansbile that we need to bail.
    if not activate_version in versions:
        module.fail_json(msg=str('The software that is trying to be activated doesn\'t seem to be in the switches software list.'))
        return pri_back, active_software_has_changed

    if debug_mode:
        print ('**** Version to be activated: ' + str(activate_version))
        print ('**** Current Primary Boot: ' + str(pri_back['primary']))
        print ('**** Current Backup Boot: ' + str(pri_back['backup']))
        print ('**** Current Next Boot: ' + str(pri_back['next boot']))

    # Check to make sure that the version that is trying to be activated isn't already the primary version or the next boot version. 
    # If it is our work is done.
    if  (pri_back['next boot'] == None) and (pri_back['primary'] == activate_version):
        if debug_mode:
            print ('**** Next boot release doesn\'t seem to be in place and the primary version is the version to be activated.')
        return pri_back, active_software_has_changed
    elif pri_back['next boot'] == activate_version:
        if debug_mode:
            print ('**** Version to be activated found as next boot release')
        return pri_back, active_software_has_changed

    # At this point we can try to execute the sofware activate. 
    # For now we are just going to catch success and dump all other cases into failure.
    try:
        handler.enable()
        output = handler.send_command_expect(activate_command)
    except Exception, err:
        if not debug_mode:
            module.fail_json(msg=str(err))
        else:
            print str(err)
    
    # Debug mode printing
    if debug_mode:
        print output

    # If we find the text that is associated with a successful activation then check to make sure the changes were successful
    if (software_activate_success in output) or (software_version_consistent in output):
        # Double check to make sure the changes were successful
        ver, new_pri_back = get_software_versions(handler, module)
        active_software_has_changed = True
        # If the version we activated is the current version we are running then use this section.
        if  (new_pri_back['next boot'] == None) and (new_pri_back['primary'] == activate_version):
            if debug_mode:
                print ('**** After changing the active version, next boot release doesn\'t seem to be in place and the primary version is the version we wanted to activate.')
            return new_pri_back, active_software_has_changed
        # If the version we activated is the next boot then use this section. This should be the common case.
        elif new_pri_back['next boot'] == activate_version:
            if debug_mode:
                print ('**** After changing the active version, the next boot release is the version we wanted to activate.')
            return new_pri_back, active_software_has_changed
        else:
            # It doesn't seem like any changes were made. This is strange. If the user passed us the right information we shouldn't get here.
            if not debug_mode:
                module.fail_json(msg=str('The command seemed to be successful but when running the confrimation command, the versions didn\'t seem to match up.'))
            else:
                print '**** The command seemed to be successful but when running the confrimation command, the versions didn\'t seem to match up.'
            return new_pri_back, active_software_has_changed

    # Also a place we probably should never get to. Strange.
    else:
        if not debug_mode:
            module.fail_json(msg=str('When activating the new software we got a response we did not expect. It\'s possible the function used to do this was called incorrectly.'))
        else:
            print '**** When activating the new software we got a response we did not expect. It\'s possible the function used to do this was called incorrectly.'
        return pri_back, active_software_has_changed

def reboot_switch(handler, device, wait_for_reboot, module=0):
    # Function takes the Netmiko SSH handler (handler), a bool that determines if we are going to wait for successful reboot,
    # and the Ansible module (module).

    reboot_command = 'reset -y'
    login_retrys = 10
    login_wait_sec = 30

    # Reboot the switch and be done.
    if not wait_for_reboot:
        if debug_mode:
            print ('**** Rebooting Switch')
        try:
            handler.enable()
            output = handler.send_command(reboot_command)
            return None
        except Exception, err:
            if not debug_mode:
                module.fail_json(msg=str(err))
            else:
                print ('**** ' + str(err))
            return None
    # Reboot the switch and patiently wait for the reboot to occur
    else:
        if debug_mode:
            print ('**** Rebooting Switch and waiting')
        try:
            handler.enable()
            output = handler.send_command(reboot_command)
        except Exception, err:
            if not debug_mode:
                module.fail_json(msg=str(err))
            else:
                print ('**** ' + str(err))

        while login_retrys > 0:
            sleep(login_wait_sec)
            print ('**** Trying to login again...')
            login_retrys -= 1
            try:
                new_handler = ConnectHandler(**device)
                return new_handler
            except Exception, err:
                if not debug_mode:
                    module.fail_json(msg=str(err))
                else:
                    print ('**** ' + str(err))
        return None



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
    overall_has_changed = False

    if not debug_mode:
        return_status = save_config(ssh_handler,module)
    else:
        # Manual set varibale for debug_mode
        act_version = '3.1.0.2.GA'

        # Down here should be what the real script would look like.
        act_has_changed = False

        # return_status = save_config(ssh_handler)
        release_list,pri_back = get_software_versions(ssh_handler)
        pri_back,act_has_changed = activate_software_version(ssh_handler, act_version, release_list, pri_back)

        ssh_handler = reboot_switch(ssh_handler, vsp_device, False)
        save_config (ssh_handler)

    # Send Ansible a hopefully good report of successful save.
    if not debug_mode:
        module.exit_json(**return_status)

main()
