from scrapli import Scrapli
from scrapli import exceptions
from netbox_class import *
from lab_device_class import *
from main import ssh_scrape_netbox


device = input('Please enter (valid) IP address of device to check into Netbox: ')

ssh_scrape_netbox(device)


