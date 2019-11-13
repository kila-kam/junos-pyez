#!/usr/bin/env python
from jnpr.junos import Device
from lxml import etree
from tabulate import tabulate
from sys import argv
import getpass

username = None
password = None

if username == None:
    username = raw_input('Username: ')

if password == None:
    password = getpass.getpass()

dev = Device(host=argv[1], user=username, passwd=password, port=22)
dev.open()
bgp = dev.rpc.get_bgp_summary_information()

data = []
intf_dic={}
headers = ['peer ip', 'peer state', 'description', 'elaspsed time', 'flap count', 'status', 'last-error']
for i in bgp.findall('bgp-peer'):
    elapsed_time = int(i.find('elapsed-time').attrib['seconds'])
    flap_count = int(i.find('flap-count').text)

    if elapsed_time < 259200 and flap_count > 0:
        peer = i.find('peer-address').text
        peer_state = i.find('peer-state').text
        description = i.find('description')
        if description == None:
            description = "No Description"
        else:
            description = i.find('description').text
        bgp_sum = [peer, peer_state, description, i.find('elapsed-time').text, i.find('flap-count').text]
        if peer_state != 'Established':
            bgp_neighbour_etree = dev.rpc.get_bgp_neighbor_information(neighbor_address=peer)
            bgp_sum.append('DOWN and FLAPPED RECENTLY')
            bgp_sum.append(bgp_neighbour_etree.find('.//last-error').text)
            data.extend([bgp_sum])
        else:
            bgp_neighbour_etree = dev.rpc.get_bgp_neighbor_information(neighbor_address=peer)
            bgp_intf= dev.rpc.get_route_information(destination=peer,active_path=True).find('.//via').text
            result  = dev.rpc.get_interface_information(interface_name=bgp_intf,normalize=True)
            bgp_sum.append('FLAPPED RECENTLY')
            bgp_sum.append(bgp_neighbour_etree.find('.//last-error').text)
            data.extend([bgp_sum])
            intf_desc = result.find('.//description').text
            intf_dic[description]=intf_desc
dev.close()

print(intf_dic)
#print(data)
if len(data) > 0:
    print
    argv[1]
    print
    '************'
    print(tabulate((data), headers=headers, tablefmt="grid"))

