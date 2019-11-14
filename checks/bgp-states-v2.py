# !/usr/bin/env python
from jnpr.junos import Device
from jnpr.junos.exception import *
from lxml import etree
from tabulate import tabulate
from sys import argv
import getpass
import yaml

username = None
password = None

def show_bgp_summary(device):
  try:
    dev = Device(**device)
    dev.open()
    print('\n\n')
    print(dev.facts['hostname'])
    print('=============\n\n')
    bgp = dev.rpc.get_bgp_summary_information()
    data = []
    headers = ['peer ip', 'peer state', 'description', 'elaspsed time', 'flap count', 'status']
    for i in bgp.findall('bgp-peer'):
      elapsed_time = int(i.find('elapsed-time').attrib['seconds'])
      flap_count = int(i.find('flap-count').text)
      peer = i.find('peer-address').text
      if elapsed_time < 259200 and peer != '1.1.1.1':
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
          data.extend([bgp_sum])
        else:
          bgp_neighbour_etree = dev.rpc.get_bgp_neighbor_information(neighbor_address=peer)
          bgp_sum.append('FLAPPED RECENTLY')
          data.extend([bgp_sum])
    dev.close()
    if len(data) != 0:
      print(tabulate((data), headers=headers, tablefmt="grid"))
    else:
      print('\n BGP is All good, No flaps in the last 72 hours !!!\n ')
  except Exception as e:
    print(e)

