## About

This repo contains [Ansible](https://github.com/ansible/ansible) modules which use SSH to change configuration on Avaya devices. It is currently in the proof of concept stage and is intended to demonstrate how devices without modern APIs can be automated and integrated into a DevOps/NetOps model.

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

TASK: [Ensure VLAN 10 is present and has the name INTERNAL] *******************
changed: [10.177.213.76]

TASK: [Ensure VLAN 12 is present and has the name GUESTS] *********************
changed: [10.177.213.77]

TASK: [Ensure that VLAN 40 is created] ****************************************
changed: [10.177.213.78]

TASK: [Remove VLAN 80 if it is present] ***************************************
changed: [10.177.213.79]

TASK: [Create vlan 100 with SNMPv3] *******************************************
ok: [172.29.50.5]

TASK: [Create vlan from variable] *********************************************
changed: [172.29.50.5] => (item={'vlan_id': 30, 'vlan_name': 'red'})
ok: [172.29.50.5] => (item={'vlan_id': 31, 'vlan_name': 'green'})
changed: [172.29.50.5] => (item={'vlan_id': 32, 'vlan_name': 'blue'})

NOTIFIED: [save config] *******************************************************
changed: [172.29.50.5]

PLAY RECAP ********************************************************************
172.29.50.5                : ok=7    changed=3    unreachable=0    failed=0
```

Running the playbook a second time:

```
$ ansible-playbook -i hosts example-playbooks/how-to/examples-vlan.yml

PLAY [all] ********************************************************************

TASK: [Ensure VLAN 10 is present and has the name INTERNAL] *******************
ok: [172.29.50.5]

TASK: [Ensure VLAN 12 is present and has the name GUESTS] *********************
ok: [172.29.50.5]

TASK: [Ensure that VLAN 40 is created] ****************************************
ok: [172.29.50.5]

TASK: [Remove VLAN 80 if it is present] ***************************************
ok: [172.29.50.5]

TASK: [Create vlan 100 with SNMPv3] *******************************************
ok: [172.29.50.5]

TASK: [Create vlan from variable] *********************************************
ok: [172.29.50.5] => (item={'vlan_id': 30, 'vlan_name': 'red'})
ok: [172.29.50.5] => (item={'vlan_id': 31, 'vlan_name': 'green'})
ok: [172.29.50.5] => (item={'vlan_id': 32, 'vlan_name': 'blue'})

PLAY RECAP ********************************************************************
172.29.50.5                : ok=6    changed=0    unreachable=0    failed=0
```

## Todo

* Error handling (the module assumes that the SNMPv3 user/SNMPv2 community has write access to the device)
* Ability to save running configuration to startup configuration
* cisco_snmp_switchport module - Add ability to set allowed VLANs on a trunk

## Known issues

* Naming conflicts: If you try to add a vlan using a name which already exists the module won't pick this up. The vlan will keep it's old name or be created without a name
* No checking if the provided vlan_id is a valid number. I.e. the module won't complain if you try to create a vlan with id 37812942

## Potential roadmap

* Change interfaces i.e. access/trunk port, vlan assignments, description, admin up/down
* Handle configuraion backups
* All other things which might be possible through SNMP

## Feedback

If you have any questions or feedback. Please send me a note over [at my blog](http://networklore.com/contact/) or submit an issue here at Github.
