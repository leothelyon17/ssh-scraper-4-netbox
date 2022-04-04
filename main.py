#!/usr/bin/python
import requests
from scrapli import Scrapli
import json
import pprint
from netbox_class import *
from lab_device_class import *


# deviceA = Lab_Device('172.16.99.54', 'arista_eos')
# print(deviceA.get_device_facts())


# ssh_device = Lab_Device('172.16.99.55', 'cisco_nxos')
# print(ssh_device.get_device_facts())
# ssh_device_facts = ssh_device.get_device_facts()

lab_device_list = [
    ('172.16.99.54', 'arista_eos'),
    ('172.16.99.55', 'cisco_nxos'),
    ('172.16.99.56', 'cisco_nxos')
]

for device in lab_device_list:

    ssh_device = Lab_Device(*device)
    print(ssh_device.get_device_facts())
    ssh_device_facts = ssh_device.get_device_facts()



    netbox = Netbox_Device()
    #print(netbox.get_netbox_device_list())
    nb_device_list = netbox.get_netbox_device_list()
    nb_interface_list = netbox.get_netbox_interface_list()
    nb_ipaddress_list = netbox.get_netbox_ipaddress_list()

    if netbox.netbox_device_instance_data(ssh_device_facts, nb_device_list):
        print('Device exists. Checking if updates are needed...')
        print(netbox.update_netbox_device(ssh_device_facts))
        print(netbox.update_netbox_device_mgmt_ip(ssh_device_facts, nb_interface_list, nb_ipaddress_list))
    else:
        print('Device does not exist. Building new device.')
        netbox.create_netbox_device(ssh_device_facts)

        nb_device_list = netbox.get_netbox_device_list()
        nb_interface_list = netbox.get_netbox_interface_list()
        nb_ipaddress_list = netbox.get_netbox_ipaddress_list()

        netbox.netbox_device_instance_data(ssh_device_facts, nb_device_list)

        netbox.update_netbox_device_mgmt_ip(ssh_device_facts, nb_interface_list, nb_ipaddress_list)





deviceA = Lab_Device('172.16.99.54', 'arista_eos')
#print(device1.get_arista_facts())
d_facts = deviceA.get_arista_facts()
print(deviceA.get_primary_ip(d_facts))

device = Lab_Device('172.16.99.55', 'cisco_nxos')
d_facts = device.get_nxos_facts()
print(device.get_primary_ip(d_facts))


netbox = Netbox_Device()
