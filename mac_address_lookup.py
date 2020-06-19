#!/usr/bin/env python
from jnpr.junos import Device
from lxml import etree
import getpass
from pprint import pprint
import requests
import time

username = raw_input('Username: ')
password = getpass.getpass()

def mac_vendor(switch,vlan):
	dev = Device(host=switch , user=username, passwd=password, port=22)
	dev.open()
	if dev['model'].startswith='XX'
		result = dev.rpc.get_vlan_ethernet_switching_table(vlan_name=vlan)
			for mac in result.findall('.//mac-address'):
			mac_address=str(mac.text)
			URL='https://api.macvendors.com/' +mac_address
			response=requests.get(url=URL)
			print(mac_address,response.text)
			time.sleep(3)
	Else:
        	result = dev.rpc.get_ethernet_switching_table_information(vlan_name=vlan)
			for mac in result.findall('.//l2ng-l2-mac-address'):
                	mac_address=str(mac.text)
                	URL='https://api.macvendors.com/' +mac_address
                	response=requests.get(url=URL)
                	print(mac_address,response.text)
                	time.sleep(3)
