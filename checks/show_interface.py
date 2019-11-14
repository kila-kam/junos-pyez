#!/usr/bin/env python

import getpass
from jnpr.junos import Device
from lxml import etree
from tabulate import tabulate

username = None
password = None

if username == None:
  username = raw_input('Username: ')

if password == None:
  password = getpass.getpass()

# netdevice ip address in string 

def junos_interface(netdevice):
        dev = Device(host=netdevice,user=username,passwd=password)
        dev.open()
        result  = dev.rpc.get_interface_information(interface_name='[gxa]e*',extensive=True)
        dev.close()

#print etree.dump(result)

        headers= ['name','description','interface-flapped']
        data =[]

        error_count = 1
        t = float(error_count)

        for i in result.findall('physical-interface'):

           yo = i.find('name').text
           intf = yo.strip()

           description = i.find('description')
           if description == None:
                  description = "No Description"
           else:
                  description = i.find('description').text

           if  float(i.find('interface-flapped').attrib['seconds']) < 259200:
                   flap ='flapped recently'
           else:
                   flap = i.find('interface-flapped').text

           intf_list = [intf,description,flap]

           for j in i.find('output-error-list'):
                   if float(j.text) >= t and  j.tag not in headers:
                          headers.append(j.tag)
                          x= j.text
                          intf_list.extend([x.strip()])
                          continue
                   if float(j.text) >= t and  j.tag  in headers:
                          y = j.text
                          intf_list.extend([y.strip()])

           for j in i.find('input-error-list'):
                   if float(j.text) >= t and  j.tag not in headers:
                          headers.append(j.tag)
                          x= j.text
                          intf_list.extend([x.strip()])
                          continue
                   if float(j.text) >= t and  j.tag  in headers:
                          y = j.text
                          intf_list.extend([y.strip()])

           data.extend([intf_list])
        print(tabulate(data,headers=headers,tablefmt="grid" ))
