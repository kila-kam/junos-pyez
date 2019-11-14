#!/usr/bin/env python
from jnpr.junos import Device
from jnpr.junos.exception import *
from lxml import etree
from sys import argv
import getpass
import argparse
import keyring


parser = argparse.ArgumentParser(
prog='packet_tracer.py',
usage='%(prog)s [-h] firewall src.ip dst.ip dst.port [--udp UDP] [--icmp ICMP]',
description='Show security match policies'
)

parser.add_argument('firewall', help= 'ip address or hostname of junos firewall')
parser.add_argument('src.ip', help= 'source ip address')
parser.add_argument('dst.ip' ,help= 'destination ip address')
parser.add_argument('dst.port' ,help= 'destination port ')
parser.add_argument('--udp' ,help= 'specify udp protocol (default: tcp) ',action='store_const', const=4)
parser.add_argument('--icmp' ,help= 'specify icmp protocol  ',action='store_const', const=4)
args = parser.parse_args()


print argv
username = "admin"
password = None

#print keyring.get_keyring()
#keyring.set_keyring("keyring.backends.fail.Keyring")

#if keyring.get_credential('mgmt','admin') != None:
#               username ='admin '
#               password = keyring.get_password('mgmt', 'admin')


if username == None:
                username = raw_input('Username: ')

if password == None:
                password = getpass.getpass()


dev = Device(host= argv[1],user=username,passwd=password,port=22)
try:
                dev.open()

                src_intf  = dev.rpc.get_route_information(destination=argv[2],active_path=True).find('.//via').text
                dst_intf  = dev.rpc.get_route_information(destination=argv[3],active_path=True).find('.//via').text
                print (src_intf,dst_intf)

                if dev.facts['version'].startswith('12.1X46'):
                        src = dev.rpc.get_interface_information(interface_name=src_intf,normalize=True).find('.//logical-interface-zone-name').text
                        dst =  dev.rpc.get_interface_information(interface_name=dst_intf,normalize=True).find('.//logical-interface-zone-name').text
                else:
                        src = dev.rpc.get_interface_information(interface_name=src_intf,terse=True,zone=True,normalize=True).find('.//zonename').text
                        dst = dev.rpc.get_interface_information(interface_name=dst_intf,terse=True,zone=True,normalize=True).find('.//zonename').text

                print (src,dst)
                if len(argv) == 5:
                 pkt_trace = 'show security match-policies global' +  ' source-ip ' + argv[2] + ' destination-ip ' + argv[3] + ' source-port 12345 ' + 'destination-port '  + argv[4] + ' protocol tcp '
                 pkt_trace2 = 'show security match-policies ' + ' from-zone ' + src +' to-zone ' + dst + ' source-ip ' + argv[2] + ' destination-ip ' + argv[3] + ' source-port 12345 ' + 'destination-port '  + argv[4] + ' protocol tcp '

                elif argv[5] == "--udp":
                 pkt_trace = 'show security match-policies global' +  ' source-ip ' + argv[2] + ' destination-ip ' + argv[3] + ' source-port 12345 ' + 'destination-port '  + argv[4] + ' protocol udp '
                 pkt_trace2 = 'show security match-policies ' + ' from-zone ' + src +' to-zone ' + dst + ' source-ip ' + argv[2] + ' destination-ip ' + argv[3] + ' source-port 12345 ' + 'destination-port '  + argv[4] + ' protocol udp '

                elif argv[5] == "--icmp":
                 pkt_trace = 'show security match-policies global' +  ' source-ip ' + argv[2] + ' destination-ip ' + argv[3] + ' source-port 12345 ' + 'destination-port '  + argv[4] + ' protocol udp '
                 pkt_trace2 = 'show security match-policies ' + ' from-zone ' + src +' to-zone ' + dst + ' source-ip ' + argv[2] + ' destination-ip ' + argv[3] + ' source-port 12345 ' + 'destination-port '  + argv[4] + ' protocol icmp '


                print dev.cli(pkt_trace2,warning=False)
                print dev.cli(pkt_trace,warning=False)

                dev.close()

except ConnectUnknownHostError:
                print(argv[1] + " is not a valid host! \n\n")
except ConnectAuthError:
                print("invalid username or password for host " + argv[1] +"\n\n")
except ConnectTimeoutError:
                print("failed to connect to " + argv[1] + ". could be: a bad ip addr, ip addr is not reachable due to a routing issue or a firewall filtering, ...\n\n")
except KeyboardInterrupt:
                dev.close()
                print '\n\nCancelling...\n\n'
                quit()

