## About

This repo contains [Ansible](https://github.com/ansible/ansible) modules which utilize the SSH protocol to change configuration on Avaya devices. It is currently in the proof of concept stage and is intended to demonstrate how devices without modern APIs can be automated and integrated into a DevOps/NetOps model.

## Goal

The goal of this project is to provide an automation tool set for Avaya products using Ansible as a framework.

## Alpha code

This code is still very fresh and will likely go through many iterations.

## Dependencies

These modules requires:

* [netmiko](https://github.com/ktbyers/netmiko)
* Avaya VSP devices

## Installation of Ansible module
```
pip install netmiko
```
If you are running Ansible through a Python virtualenv you might need to change the ansible_python_interpreter variable. Check the hosts file in this repo for an example. You can clone this repo and copy the modules to your Ansible library path.

## Configuration of Avaya VSP device

Testing: SSH via Local Auth
```
boot config flags sshd
ssh
username admin leve rwa
Enter the old password : ******** 
Enter the New password : ******** 
Re-enter the New password : ********
```
Production: SSH via Radius
```
boot config flags sshd
ssh
```


## Demo

Running the playbook the first time:

```
$ ansible-playbook -i hosts example-playbooks/how-to/examples-save-config.yml

PLAY [all] ********************************************************************

TASK: [save config] ***********************************************************
changed: [10.177.213.76]

TASK: [save config] ***********************************************************
changed: [10.177.213.77]

TASK: [save config] ***********************************************************
changed: [10.177.213.78]

TASK: [save config] ***********************************************************
changed: [10.177.213.79]

PLAY RECAP ********************************************************************
10.177.213.10              : ok=0    changed=4    unreachable=0    failed=0
```

## Todo

## Known issues

## Prioritized roadmap

1. Confirm/Add software image, enable specific software image, and reboot to update OS.
2. Backup configuration to file server
3. Modify VLANs
4. Modify ISID to VLAN mapping
5. Interface configuration

## Feedback

Feel free to reach out to me at mileswdavis@gmail.com or submit an issue on GitHub.
