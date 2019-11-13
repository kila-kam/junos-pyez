from interface_table import *
import yaml

#for multiple devices , simply update yaml file

with open('netdevices.yaml', 'r') as file:
   netdevice_dict = yaml.load(file)
   
   for i,j in netdevice_dict['netdevices'].iteritems():
      print (i)
      print ('------------------------------')
      junos_interface(j)
      print ('\n \n \n')
