from jinja2 import Template
from jinja2 import FileSystemLoader, StrictUndefined
from jinja2.environment import Environment
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from pprint import pprint


data_switchports = []

for i in range(0,4):
        for j in range(24):
                data_switchports.append('ge-' + str(i) + '/0/' + str(j))
                
video_switchports = []
for i in range(0,4):
        for j in range(24,48):
                video_switchports.append('ge-' + str(i) + '/0/' + str(j))
                
                
                
username = 'admin'
password = 'admin'
TEMPLATE_FILE = 'templates/data_layer2.j2'
TEMPLATE_VARS  = {
"data_ports": data_switchports ,
"video_ports": video_switchports ,
}

env = Environment(undefined=StrictUndefined)
env.loader = FileSystemLoader(".")

#genrates  config file locally from Jinja template

def config_file():
        template = env.get_template(TEMPLATE_FILE)
        output = template.render(**TEMPLATE_VARS)
        with open('configs/output.txt', 'w') as f:
                f.write(output)
                f.close()

# generates and loads configuration file on juniper devices

def config_devices(devices='lab.txt'):
        with open(devices, 'r') as f:
                netdevices = f.readlines()
                netdevices = [x.strip() for x in netdevices]
                for netdevice in netdevices:
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

if __name__ == '__main__':
        config_devices()
        config_file()
