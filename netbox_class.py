import requests
import json

class Netbox_Device():
    def __init__(self):
    
        self.apiBaseUrl = "http://172.16.99.20:8000/api"
        self.headers = {  
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Token 374c7f7675c9dcc1ed847bd524799c6418b4358d'
        }

    def get_netbox_device_list(self):  
        resp = requests.get(self.apiBaseUrl + '/dcim/devices/',
                        headers=self.headers).json()
    
        #print (resp)
        return resp['results']

    def get_netbox_ipaddress_list(self):  
        resp = requests.get(self.apiBaseUrl + '/ipam/ip-addresses/',
                        headers=self.headers).json()
    
        #print (resp)
        return resp['results']

    def get_netbox_interface_list(self):  
        resp = requests.get(self.apiBaseUrl + '/dcim/interfaces/',
                        headers=self.headers).json()
    
        #print (resp)
        return resp['results']

    def check_ssh_device_exists(self, device_facts, netbox_device_list):
        for nb_device in netbox_device_list:
            if device_facts['hostname'] == nb_device['name']:
                self.nb_device = nb_device
                return True

    def check_mgmt_interface_exists(self, interface_list):
        for i in interface_list:
            if i['device']['id'] == self.nb_device['id']:
                if self.nb_device['device_type']['manufacturer']['name'] == 'Arista' and i['name'] == 'Management1':
                    return True
                elif self.nb_device['device_type']['manufacturer']['name'] == 'Cisco Systems, Inc.' and i['name'] == 'mgmt0':
                    return True
                else:
                    return False
            
        return False

    def update_netbox_device(self, ssh_device_facts):
        update_fields = {}

        if ssh_device_facts['manufacturer'] != self.nb_device['device_type']['manufacturer']['name']:
            manufacturer = {
                'device_type':{
                    'manufacturer': {
                        'name': ssh_device_facts['manufacturer']
                    }
                }
            }
            update_fields.update(manufacturer)

        if ssh_device_facts['platform'] != self.nb_device['platform']['name']:
            platform = {
                'platform':{
                    'name': ssh_device_facts['platform']
                }
            }
            update_fields.update(platform)

        if ssh_device_facts['type'] != self.nb_device['device_type']['model']:
            model = {
                'device_type':{
                    'model': ssh_device_facts['type']
                }
            }
            update_fields.update(model)

        if ssh_device_facts['serial'] != self.nb_device['serial']:
            serial = {
                'serial': ssh_device_facts['serial']
            }
            update_fields.update(serial)

        # if ssh_device_facts['primary_ip'] != self.nb_device['primary_ip']['address']:
        #     address = {
        #         'primary_ip':{
        #             'address': ssh_device_facts['primary_ip']
        #         }
        #     }
        #     update_fields.update(address)

        r = requests.patch(self.apiBaseUrl + '/dcim/devices/' + str(self.nb_device['id']) + '/',
                        data=json.dumps(update_fields), headers=self.headers)

        print(r)

    def update_netbox_device_mgmt_ip(self, ssh_device_facts, interface_list, ipaddress_list):
        update_fields = {}
        if self.check_mgmt_interface_exists(interface_list):
            pass
        else:
            pass #create mgmt interface
        

    def create_netbox_device(self):
        pass
