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

with open('/netdevices.yaml', 'r') as file:
	yo = yaml.load(file)
	for netdevice in yo['bgp']:
		dev = Device(host=netdevice, user=username, passwd=password, port=22)
		try:
			dev.open()
			print(dev.facts["hostname"])
			print('----------------------------------\n')
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
						bgp_sum.append('FLAPPED RECENTLY')
						bgp_sum.append(bgp_neighbour_etree.find('.//last-error').text)
						data.extend([bgp_sum])
						bgp_intf= dev.rpc.get_route_information(destination=peer,active_path=True).find('.//via').text
						result  = dev.rpc.get_interface_information(interface_name=bgp_intf,normalize=True)
						intf_desc = result.find('.//description')
						print(bgp_intf)
						print(intf_desc)
						if intf_desc == None:
							result2  = dev.rpc.get_interface_information(interface_name=bgp_intf.split(".")[0],normalize=True)
							intf_desc2 = result2.find('.//description') 
							if intf_desc2 == None:
								intf_desc2 = "No Description"
								intf_dic[description]=intf_desc2
							else:
								intf_desc2 = result2.find('.//description').text
								intf_dic[description]=intf_desc2
						else:
							intf_desc = result.find('.//description').text
							intf_dic[description]=intf_desc
			if len(data) > 0:
				print(tabulate((data), headers=headers, tablefmt="grid"))
				print("\n")
				print(intf_dic)
				print("\n\n")
			elif len(data) == 0:
				 print("no flaps on device " + dev.facts["hostname"] + "\n\n" )
		except ConnectUnknownHostError:
			print(netdevice + " is not a valid host! \n\n")
		except ConnectAuthError:
			print("invalid username or password for host " + netdevice +"\n\n")
		except ConnectTimeoutError:
			print("failed to connect to " + netdevice + ". could be: a bad ip addr, ip addr is not reachable due to a routing issue or a firewall filtering, ...\n\n")
		except KeyboardInterrupt:
			dev.close()
			print '\n\nCancelling...\n\n'
			quit()
#        except:
#            print("another error ...\n\n")
		else:
#            print ("the device "+ dev.facts["hostname"]+ " runs " + dev.facts["version"])
			dev.close()
