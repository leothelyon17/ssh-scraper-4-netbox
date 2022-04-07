from netbox_class import *
from lab_device_class import *


def get_netbox_data():
    global nb_device_list, nb_interface_list, nb_ipaddress_list
    
    nb_device_list = netbox.get_netbox_device_list()
    nb_interface_list = netbox.get_netbox_interface_list()
    nb_ipaddress_list = netbox.get_netbox_ipaddress_list()

with open('device_list.json', 'r') as json_file:
	json_load = json.load(json_file)

for d in json_load['device_list']:
    print(f'Starting scrape on {d["device"]}...')
    
    print(d['ssh_device_facts'])
    ssh_device_facts = d['ssh_device_facts']

    netbox = Netbox_Device()
    #print(netbox.get_netbox_device_list())
    get_netbox_data()

    if netbox.find_and_set_device_instance_data(ssh_device_facts, nb_device_list):
        print('Device exists. Checking if updates are needed...')
        netbox.update_netbox_device(ssh_device_facts)
        netbox.update_netbox_device_mgmt_ip(ssh_device_facts, nb_interface_list, nb_ipaddress_list)
    else:
        print('Device does not exist. Building new device.')
        netbox.create_netbox_device(ssh_device_facts)

        get_netbox_data()

        netbox.find_and_set_device_instance_data(ssh_device_facts, nb_device_list)

        netbox.update_netbox_device_mgmt_ip(ssh_device_facts, nb_interface_list, nb_ipaddress_list)
