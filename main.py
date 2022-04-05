#!/usr/bin/python
from scrapli import Scrapli
from scrapli import exceptions
from netbox_class import *
from lab_device_class import *

def ssh_scrape_netbox(device):

    print(f'Starting scrape on {device}...')
    ssh_device = Lab_Device(device)
    
    try:
        if ssh_device.pingOk(device):
            conn_data = ssh_device.create_connection()
                
            print(ssh_device.get_device_facts(conn_data))
            ssh_device_facts = ssh_device.get_device_facts(conn_data)

            netbox = Netbox_Device()
            #print(netbox.get_netbox_device_list())
            nb_device_list = netbox.get_netbox_device_list()
            nb_interface_list = netbox.get_netbox_interface_list()
            nb_ipaddress_list = netbox.get_netbox_ipaddress_list()

            if netbox.netbox_device_instance_data(ssh_device_facts, nb_device_list):
                print('Device exists. Checking if updates are needed...')
                netbox.update_netbox_device(ssh_device_facts)
                netbox.update_netbox_device_mgmt_ip(ssh_device_facts, nb_interface_list, nb_ipaddress_list)
            else:
                print('Device does not exist. Building new device.')
                netbox.create_netbox_device(ssh_device_facts)

                nb_device_list = netbox.get_netbox_device_list()
                nb_interface_list = netbox.get_netbox_interface_list()
                nb_ipaddress_list = netbox.get_netbox_ipaddress_list()

                netbox.netbox_device_instance_data(ssh_device_facts, nb_device_list)

                netbox.update_netbox_device_mgmt_ip(ssh_device_facts, nb_interface_list, nb_ipaddress_list)
        else:
            print(f'Device {device} not responding to pings. Skipping...')
    except:
        print(f'Could not connect to device {device}. Unsupported device type or auth issue. Skipping...')








