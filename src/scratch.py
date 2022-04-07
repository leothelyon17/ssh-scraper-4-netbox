import requests
from scrapli import Scrapli
import json

class Lab_Device():
    def __init__(self, primary_ip, manufacturer):
        self.primary_ip = primary_ip
        self.manufacturer = manufacturer
        self.username = 'admin'
        self.password = 'admin'

    def get_arista_facts(self):
        device = {
            "host": self.primary_ip,
            "auth_username": self.username,
            "auth_password": self.password,
            "auth_strict_key": False,
            "platform": self.manufacturer
        }
        conn = Scrapli(**device)
        conn.open()
        commands = ["show version | json", "show hostname | json", "show ip int brief | json"]
        responses = conn.send_commands(commands=commands)
        self.arista_device_facts = []
        for response in responses:
           self.arista_device_facts.append(json.loads(response.result))
        
        return self.arista_device_facts

    def get_nxos_facts(self):
        device = {
            "host": self.primary_ip,
            "auth_username": self.username,
            "auth_password": self.password,
            "auth_strict_key": False,
            "platform": self.manufacturer
        }
        conn = Scrapli(**device)
        conn.open()
        commands = ["show version | json", "show ip int mgmt 0 | json"]
        responses = conn.send_commands(commands=commands)
        self.nxos_device_facts = []
        for response in responses:
           self.nxos_device_facts.append(json.loads(response.result))
        
        return self.nxos_device_facts