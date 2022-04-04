import requests
from scrapli import Scrapli
from scrapli import exceptions
import json
import pprint

import scrapli
from netbox_class import *
from lab_device_class import *


# deviceA = Lab_Device('172.16.99.54', 'arista_eos')
# print(deviceA.get_device_facts())


# ssh_device = Lab_Device('172.16.99.55', 'cisco_nxos')
# print(ssh_device.get_device_facts())
# ssh_device_facts = ssh_device.get_device_facts()

# lab_device_list = [
#     ('172.16.99.53', 'arista_eos'),
#     ('172.16.99.54', 'arista_eos'),
#     ('172.16.99.55', 'cisco_nxos'),
#     ('172.16.99.56', 'cisco_nxos')
# ]

lab_device_list = ['172.16.99.53','172.16.99.54','172.16.99.55','172.16.99.56']

for device in lab_device_list:
    try:
        ssh_device = Lab_Device(device)
        conn_data = ssh_device.create_connection()
        #print(conn_data)
        
        print(ssh_device.get_device_facts(conn_data))
        ssh_device_facts = ssh_device.get_device_facts(conn_data)
    except:
        print(f'Could not connect to device {device}. Possible issues include device is down, network driver, or auth issue.')


    # netbox = Netbox_Device()
    # #print(netbox.get_netbox_device_list())
    # nb_device_list = netbox.get_netbox_device_list()
    # nb_interface_list = netbox.get_netbox_interface_list()
    # nb_ipaddress_list = netbox.get_netbox_ipaddress_list()

    # if netbox.netbox_device_instance_data(ssh_device_facts, nb_device_list):
    #     print('Device exists. Checking if updates are needed...')
    #     print(netbox.update_netbox_device(ssh_device_facts))
    #     print(netbox.update_netbox_device_mgmt_ip(ssh_device_facts, nb_interface_list, nb_ipaddress_list))
    # else:
    #     print('Device does not exist. Building new device.')
    #     netbox.create_netbox_device(ssh_device_facts)

    #     nb_device_list = netbox.get_netbox_device_list()
    #     nb_interface_list = netbox.get_netbox_interface_list()
    #     nb_ipaddress_list = netbox.get_netbox_ipaddress_list()

    #     netbox.netbox_device_instance_data(ssh_device_facts, nb_device_list)

    #     netbox.update_netbox_device_mgmt_ip(ssh_device_facts, nb_interface_list, nb_ipaddress_list)
