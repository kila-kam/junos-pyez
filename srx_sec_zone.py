#!/usr/bin/env python

import getpass
from jnpr.junos import Device
from lxml import etree
import yaml
import subprocess 

username=None
password= None
netdevice= None
if username == None:
  username = raw_input('Username: ')

if password == None:
  password = getpass.getpass()

dev = Device(host=netdevice,user=username,passwd=password,port=22)
dev.open()
result  = dev.rpc.get_zones_information()

sec_zone ={}
for zone in result.findall(".//zones-security"):
    x= zone.find(".//zones-security-zonename").text
    if x != "junos-host":
        for zone_intf in zone.iter("zones-security-interface-name"):
            y=zone_intf.text
            if x in sec_zone:
                sec_zone[x].append(y)
            else:
                sec_zone[x]=[y]

filehandle = './<dir>/' + dev.facts['hostname'] +'.yml'
dev.close()

subprocess.call(['rm',filehandle])
with open(filehandle, 'w') as outfile:
    yaml.dump(sec_zone,outfile,default_flow_style=False)
