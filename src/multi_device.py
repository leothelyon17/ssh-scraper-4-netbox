from scrapli import Scrapli
from scrapli import exceptions
from netbox_class import *
from lab_device_class import *
from main import ssh_scrape_netbox


device_list = ['172.16.99.53','172.16.99.54','172.16.99.55','172.16.99.56',]

for device in device_list:
    ssh_scrape_netbox(device)