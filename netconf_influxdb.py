from jnpr.junos import Device
from jnpr.junos.op.ethport import EthPortTable
from time import sleep
from influxdb_client import InfluxDBClient, Point

device = Device(host="127.0.0.1", port=22, user="admin", passwd="admin")
device.open()
switch_name = device.facts['fqdn']
print ('Connected to', switch_name,  device.facts['model'],  device.facts['version'] )
ports_table = EthPortTable(device)

print(ports_table.get())

database = 'network'
retention_policy = 'autogen'

bucket = f'{database}/{retention_policy}'

client = InfluxDBClient(url='http://localhost:8086', token='my-token', org='-')

print('*** Write Points ***')

while True:
        ports=ports_table.get()
        for port in ports:
                point=  Point.measurement("interface_statistics").tag('vsrx',port['name']).field("tx_packets",int(port['tx_packets'])).field("rx_packets",int(port['rx_packets']))
                print(point.to_line_protocol())
                write_api = client.write_api()
                write_api.write(bucket=bucket, record=point)
                sleep(1)
