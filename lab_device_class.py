from scrapli import Scrapli
from scrapli import exceptions
import json

class Lab_Device():
    # def __init__(self, primary_ip, driver):
    #     self.primary_ip = primary_ip
    #     self.driver = driver
    #     self.username = 'admin'
    #     self.password = 'admin'

    def __init__(self, primary_ip):
        self.primary_ip = primary_ip
        self.driver_list = ['cisco_nxos', 'arista_eos']
        self.auth_pair = [
                ('admin', 'admin')
            ]
        self.username = 'admin'
        self.password = 'admin'

    def create_connection(self):
        device = {
            "host": self.primary_ip,
            # "auth_username": self.username,
            # "auth_password": self.password,
            "auth_strict_key": False,
        }
        try:
            for driver in self.driver_list:
                d = {'platform': driver}
                device.update(d)
                for auth_pair in self.auth_pair:
                    pair = {
                        'auth_username': auth_pair[0],
                        'auth_password': auth_pair[1],
                    }
                    device.update(pair)

                    conn = Scrapli(**device)
                    conn.open()
                    if conn.isalive():
                        return device
        except:
            return None

    def get_device_facts(self, device):    
    
        conn = Scrapli(**device, timeout_socket=30)
        
        conn.open()
        response = conn.send_command('show version | json')
        basic_device_facts = json.loads(response.result)
        

        try:
            if 'nxos_ver_str' in basic_device_facts.keys():
                self.device_type = 'nxos'
                commands = ["show version | json", "show ip int mgmt 0 | json"]
                responses = conn.send_commands(commands=commands)
                expanded_device_facts = []
                for response in responses:
                    expanded_device_facts.append(json.loads(response.result))
            
            elif 'EOS'.casefold() in str(basic_device_facts['modelName']).casefold() or 'Arista'.casefold() in str(basic_device_facts['mfgName']).casefold() :
                self.device_type = 'arista'
                commands = ["show version | json", "show hostname | json", "show ip int brief | json"]
                responses = conn.send_commands(commands=commands)
                expanded_device_facts = []
                for response in responses:
                    expanded_device_facts.append(json.loads(response.result))
            
            return self.set_facts_for_netbox(expanded_device_facts, self.device_type)
        
        except:
            return 'Error: Cannot gather facts on device.'

    def set_facts_for_netbox(self, facts, device_type):
        try:
            if device_type == 'nxos':
                prefix = facts[1]['TABLE_intf']['ROW_intf']['prefix']
                mask = facts[1]['TABLE_intf']['ROW_intf']['masklen']
                
                device_nb_dict = {
                    'hostname':facts[0]['host_name'],
                    'manufacturer':facts[0]['manufacturer'],
                    'platform':facts[0]['nxos_ver_str'],
                    'type':facts[0]['chassis_id'],
                    'serial':facts[0]['proc_board_id'],
                    'management_int': 'mgmt0',
                    'primary_ip': prefix + '/' + str(mask),
                    'device_type': device_type,
                }
                return device_nb_dict

            elif device_type == 'arista':
                prefix = facts[2]['interfaces']['Management1']['interfaceAddress']['ipAddr']['address']
                mask = facts[2]['interfaces']['Management1']['interfaceAddress']['ipAddr']['maskLen']
                device_nb_dict = {
                    'hostname':facts[1]['hostname'],
                    'manufacturer':'Arista',
                    'platform':facts[0]['version'],
                    'type':facts[0]['modelName'],
                    'serial':facts[0]['serialNumber'],
                    'management_int': 'Management1',
                    'primary_ip': prefix + '/' + str(mask),
                    'device_type': device_type,
                }
                return device_nb_dict
        except:
            return 'Error: Cannot set device facts.'
