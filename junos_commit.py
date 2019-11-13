from devices import *
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, wait
from pprint import pprint
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import *



network_devices = lab
username= 'admin'
password = getpass.getpass()
conf_file = 'file.txt'
ssh_proxy_file='~/.ssh/config'
annotation = 'changed by me '
timeout_var=360


def junos_config(device,username,password,ssh_proxy_file,annotation,timeout_var,conf_file):
    output ={}
    # open a connection with the device and start a NETCONF session
    try:
        dev = Device(host=device,user=username,passwd=password,port=22,ssh_config=ssh_proxy_file)
        dev.open()
        output['hostname']=dev.facts['hostname']
    except ConnectError as err:
         output['error']= ("Cannot connect to device: {0}".format(err))
         return(output)
    except TimeoutExpiredError as err:
         output['error']= ("RPC timeout  to device: {0}".format(err))
         return(output)
          #
    dev.bind(cu=Config)
    #
    print ("Loading configuration changes on {}".format(dev.facts['hostname']))
    try:
        dev.cu.load(path=conf_file,format='set', merge=True)
        print(dev.cu.pdiff())
        if type(dev.cu.diff()) == str :
             output['changed'] ='yes'
        else:
            output['changed'] = None 
    except (ConfigLoadError, Exception) as err:
        output['error']= ("Unable to load configuration changes: {0}".format(err))
        return(output)

        print ("Unlocking the configuration")
        try:
            dev.cu.unlock()
        except UnlockError:
            output['error']=("Unable to unlock configuration: {0}".format(err))
            return(output)
        dev.close()

       #

    print ("Committing the configuration")
    try:
        dev.cu.commit(comment=annotation,timeout=timeout_var)
    except CommitError as err:
        output['error']=("Unable to commit configuration: {0}".format(err))
        return(output)
    except TimeoutExpiredError as err:
        output['error']=("Unable to commit configuration -TimeoutExpiredError: {0}".format(err))
        return(output)

        print ("Unlocking the configuration")
        try:
            dev.cu.unlock()
        except UnlockError as err:
            output['error']= ("Unable to unlock configuration: {0}".format(err))
            return(output)
        dev.close()
#    print ("Unlocking the configuration")
#    try:
#        dev.cu.unlock()
 #   except UnlockError as err:
 #       print ("Unable to unlock configuration: {0}".format(err))
       #
    # End the NETCONF session and close the connection
    dev.close()
    return(output)

def main():

    start_time = datetime.now()
    max_threads = 5 

    # Create the thread pool
    pool = ThreadPoolExecutor(max_threads)

    # Create list to append threads to
    futures = []
    for device in network_devices:
        futures.append(pool.submit(junos_config,device,username,password,ssh_proxy_file,annotation,timeout_var,conf_file))

    # Wait for all threads to complete.
    wait(futures)

    for future in futures:
        print("-" * 40)
        pprint(future.result())


    end_time = datetime.now()
    print("Finished in {}" .format(end_time - start_time))
    print("\n\n")

if __name__ == "__main__":
    main()
