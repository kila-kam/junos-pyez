from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from pprint import pprint

username = 'admin'
password = 'admin'

# generates and loads configuration file on juniper devices

def config_devices(netdevice):
        dev = Device(host=netdevice, user=username,passwd=password,port=22,ssh_config='~/.ssh/config')
        dev.open()
        print('Connecting to device: {}'.format(netdevice))
        dev.timeout = 300
        print('Connected to device: {}'.format(dev.facts['hostname']))
        with Config(dev) as cu:
                cu.load(template_path=TEMPLATE_FILE, template_vars=TEMPLATE_VARS,merge=True,format=set)
                cu.commit(timeout=360)
                print('Committing the configuration on device: {}'.format(netdevice))
                dev.close()
