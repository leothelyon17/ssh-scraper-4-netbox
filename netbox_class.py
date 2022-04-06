import requests
import json
import re

class Netbox_Device():
    def __init__(self):
    
        self.apiBaseUrl = "http://172.16.99.20:8000/api"
        self.headers = {  
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Token 374c7f7675c9dcc1ed847bd524799c6418b4358d'
        }

    def create_netbox_slug(self,string):
        special_characters = ".!@#$%^&*()+?=,<>\/\""
        slug = ''

        for c in string:
            if c in special_characters:
                slug += '-'
            else:
                slug += c

        return slug.replace(' ','').lower()

    
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

    def get_netbox_device_types(self):  
        resp = requests.get(self.apiBaseUrl + '/dcim/device-types/',
                        headers=self.headers).json()
    
        #print (resp)
        return resp['results']

    def get_netbox_device_roles(self):  
        resp = requests.get(self.apiBaseUrl + '/dcim/device-roles/',
                        headers=self.headers).json()
    
        #print (resp)
        return resp['results']

    def get_netbox_device_platforms(self):  
        resp = requests.get(self.apiBaseUrl + '/dcim/platforms/',
                        headers=self.headers).json()
    
        #print (resp)
        return resp['results']

    def get_netbox_device_sites(self):  
        resp = requests.get(self.apiBaseUrl + '/dcim/sites/',
                        headers=self.headers).json()
    
        #print (resp)
        return resp['results']

    def get_netbox_device_manufacturers(self):  
        resp = requests.get(self.apiBaseUrl + '/dcim/manufacturers/',
                        headers=self.headers).json()
    
        #print (resp)
        return resp['results']


    def find_and_set_device_instance_data(self, ssh_device_facts, netbox_device_list):
        """Attempts to find and set the existing netbox device instance data to be used with the Netbox class.
            Uses the gathered facts from ssh device and netbox device list API data."""
        
        for nb_device in netbox_device_list:
            if ssh_device_facts['hostname'] == nb_device['name']:
                self.nb_device = nb_device
                return True

    
    def check_mgmt_interface_exists(self, interface_list):
        print('Checking if MGMT interface exists in Netbox...')
        for i in interface_list:
            if i['device']['id'] == self.nb_device['id']:
                if self.nb_device['device_type']['manufacturer']['name'] == 'Arista' and i['name'] == 'Management1':
                    self.nb_interface_data = i
                    print('Found existing Arista MGMT device in Netbox.')
                    return True
                elif self.nb_device['device_type']['manufacturer']['name'] == 'Cisco Systems, Inc.' and i['name'] == 'mgmt0':
                    self.nb_interface_data = i
                    print('Found existing Cisco NXOS MGMT device in Netbox.')
                    return True
                else:
                    print('Interface Error.')
                    return False
            
        return False

    def check_ipaddress_exists(self, ipaddress_list, ssh_device_facts):
        print(f'Checking if ip address {ssh_device_facts["primary_ip"]} exists in Netbox...')
        for i in ipaddress_list:
            if i['address'] == ssh_device_facts['primary_ip']:
                print(f'{ssh_device_facts["primary_ip"]} found.')
                self.nb_ipaddress_data = i
                return True
        print(f'{ssh_device_facts["primary_ip"]} NOT found.')
        return False

    def check_mgmt_int_ip_binding(self, int_info, ip_info):
        print(f'Checking if ip address is bound to management interface...')
        if ip_info['assigned_object_id'] == int_info['id']:
            print('IP address is bound to correct interface.')
            return True
        
        return False

    def set_netbox_device_primary_ip(self, ip_info):
        required_fields = {
            'primary_ip4': ip_info['id'],
        }
        
        r = requests.patch(self.apiBaseUrl + '/dcim/devices/' + str(self.nb_device['id']) + '/',
                        data=json.dumps(required_fields), headers=self.headers)     

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

        r = requests.patch(self.apiBaseUrl + '/dcim/devices/' + str(self.nb_device['id']) + '/',
                        data=json.dumps(update_fields), headers=self.headers)

    def update_netbox_device_mgmt_ip(self, ssh_device_facts, interface_list, ipaddress_list):
        
        correct_binding = False
        
        while not correct_binding:
            if self.check_mgmt_interface_exists(interface_list):
                if self.check_ipaddress_exists(ipaddress_list, ssh_device_facts):
                    if self.check_mgmt_int_ip_binding(self.nb_interface_data, self.nb_ipaddress_data):
                        print('No updates to Management interface required.')
                        correct_binding = True
                    else:
                        self.create_netbox_ip_int_binding(self.nb_interface_data, self.nb_ipaddress_data, ssh_device_facts)
                        self.set_netbox_device_primary_ip(self.nb_ipaddress_data)
                        ipaddress_list = self.get_netbox_ipaddress_list()
                else:
                    self.create_netbox_mgmt_ipaddress(ssh_device_facts)
                    ipaddress_list = self.get_netbox_ipaddress_list()
            else:
                self.create_netbox_mgmt_interface(ssh_device_facts)
                interface_list = self.get_netbox_interface_list()
        

    def create_netbox_device(self, ssh_device_facts):
        found_device_type = self.match_ssh_device_netbox_device_type(ssh_device_facts)
        found_device_role = self.match_ssh_device_netbox_device_role()
        found_device_platform = self.match_ssh_device_netbox_device_platform(ssh_device_facts)
        found_device_site = self.match_ssh_device_netbox_device_site()
        
        device_info = {
            'name': ssh_device_facts['hostname'],
            'device_role': found_device_role,
            'device_type': found_device_type,
            'site': found_device_site,
            'status': 'active',
            'platform': found_device_platform,
            'serial': ssh_device_facts['serial'],
        }
        
        r = requests.post(self.apiBaseUrl + '/dcim/devices/',
                        data=json.dumps(device_info), headers=self.headers)

        r= r.json()

        self.nb_device = {
            'id':r['id']
        }


    def create_netbox_mgmt_interface(self, ssh_device_facts):
        print('Creating new MGMT interface in Netbox for current device...')
        required_fields = {
            'device': self.nb_device['id'],
            'type':'1000base-t',
            'enabled': True,
            'mgmt_only': True
        }

        if ssh_device_facts['device_type'] == 'nxos':
            name = {
                'name': 'mgmt0'
            }
            required_fields.update(name)
        elif ssh_device_facts['device_type'] == 'arista':
            name = {
                'name': 'Management1'
            }
            required_fields.update(name)
        
        r = requests.post(self.apiBaseUrl + '/dcim/interfaces/',
                        data=json.dumps(required_fields), headers=self.headers)

    def create_netbox_mgmt_ipaddress(self, ssh_device_facts):

        required_fields = {
            'address': ssh_device_facts['primary_ip']
        }
        
        r = requests.post(self.apiBaseUrl + '/ipam/ip-addresses/',
                        data=json.dumps(required_fields), headers=self.headers)
        
        # print(r)

    def create_netbox_ip_int_binding(self, int_data, ip_data, ssh_device_facts):

        required_fields = {
            'address': ssh_device_facts['primary_ip'],
            'assigned_object_type': 'dcim.interface',
            'assigned_object_id': int_data['id']
        }
        
        r = requests.patch(self.apiBaseUrl + '/ipam/ip-addresses/' + str(ip_data['id']) + '/',
                        data=json.dumps(required_fields), headers=self.headers)
        
        # print(r)

    def create_netbox_platform(self, ssh_device_facts):

        required_fields = {
            'name': ssh_device_facts['platform'],
            'slug': self.create_netbox_slug(ssh_device_facts['platform']),
            'manufacturer': self.match_ssh_device_netbox_device_manufacturer(ssh_device_facts)
        }
        
        r = requests.post(self.apiBaseUrl + '/dcim/platforms/',
                        data=json.dumps(required_fields), headers=self.headers)
        
        #print(r, r.content)

    def create_netbox_manufacturer(self, ssh_device_facts):

        required_fields = {
            'name': ssh_device_facts['manufacturer'],
            'slug': self.create_netbox_slug(ssh_device_facts['manufacturer']),
        }
        
        r = requests.post(self.apiBaseUrl + '/dcim/manufacturers/',
                        data=json.dumps(required_fields), headers=self.headers)
        
        print(r, r.content)

    def match_ssh_device_netbox_device_type(self, ssh_device_facts):
        nb_device_type_list = self.get_netbox_device_types()

        for dtype in nb_device_type_list:
            if dtype['model'] == ssh_device_facts['type']:
                return dtype['id']
            else:
                pass # Create new device type

    def match_ssh_device_netbox_device_role(self):
        nb_device_role_list = self.get_netbox_device_roles()

        for drole in nb_device_role_list:
            if drole['name'] == 'Leaf Switch':
                return drole['id']
            else:
                pass # Create new device type

    def match_ssh_device_netbox_device_platform(self, ssh_device_facts):
        nb_device_platform_list = self.get_netbox_device_platforms()

        for dplatform in nb_device_platform_list:
            if dplatform['name'] == ssh_device_facts['platform']:
                return dplatform['id']
            
        self.create_netbox_platform(ssh_device_facts)
        self.match_ssh_device_netbox_device_platform(ssh_device_facts)

    def match_ssh_device_netbox_device_site(self):
        nb_device_site_list = self.get_netbox_device_sites()

        for dsite in nb_device_site_list:
            if dsite['name'] == 'Lab':
                return dsite['id']
            else:
                pass # Create new device type

    def match_ssh_device_netbox_device_manufacturer(self, ssh_device_facts):
        nb_device_manufacturers_list = self.get_netbox_device_manufacturers()

        for dmanufacturer in nb_device_manufacturers_list:
            if dmanufacturer['name'] == ssh_device_facts['manufacturer']:
                return dmanufacturer['id']
        
        self.create_netbox_manufacturer(ssh_device_facts)
        self.match_ssh_device_netbox_device_manufacturer(ssh_device_facts)

