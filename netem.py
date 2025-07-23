import os
import sys
import json
from typing import List

class Host:
    def __init__(self, ip_address, interface, latency, jitter, bandwidth):
        self.ip_address = ip_address
        self.interface = interface
        self.latency = latency
        self.jitter = jitter
        self.bandwidth = bandwidth

def unset(host: Host):
    os.system(f'sudo tc qdisc del dev {host.interface} root')
    print(f'reset config for {host.ip_address}')
    
def static_delay(host: Host):
    os.system(f"sudo tc qdisc add dev {host.interface} root handle 1: prio")
    os.system(f"sudo tc qdisc add dev {host.interface} parent 1:1 handle 10: netem delay {host.latency}ms")
    os.system(f"sudo tc filter add dev {host.interface} protocol ip parent 1:0 prio 1 u32 match ip dst {host.ip_address}/32 flowid 1:1")
    print(f'Latency to {host.ip_address} set to {host.latency}ms')

def jitter_delay(host: Host):
    os.system(f"sudo tc qdisc add dev {host.interface} root handle 1: prio")
    os.system(f"sudo tc qdisc add dev {host.interface} parent 1:1 handle 10: netem delay {host.latency}ms {host.jitter}ms")
    os.system(f"sudo tc filter add dev {host.interface} protocol ip parent 1:0 prio 1 u32 match ip dst {host.ip_address}/32 flowid 1:1")
    print(f'Latency to {host.ip_address} set to {host.latency}ms with jitter {host.jitter}ms')

def advance(host: Host):
    os.system(f"sudo tc qdisc add dev {host.interface} root handle 1: htb")
    os.system(f"sudo tc class add dev {host.interface} parent 1: classid 1:1 htb rate {host.bandwidth}mbit")
    os.system(f"sudo tc qdisc add dev {host.interface} parent 1:1 handle 10: netem delay {host.latency}ms {host.jitter}ms")
    os.system(f"sudo tc filter add dev {host.interface} protocol ip parent 1:0 prio 1 u32 match ip dst {host.ip_address}/32 flowid 1:1")
    print(f'Latency to {host.ip_address} set to {host.latency}ms with jitter {host.jitter}ms and bandwidth {host.bandwidth}mbit')

    
if __name__ == "__main__":
    with open('cfg.json', 'r') as cfg_file:
        cfg = json.load(cfg_file)
    
    args = sys.argv
    
    hosts: List[Host] = []
    
    for host_cfg in cfg['hosts']:
        host = Host(
            ip_address=host_cfg['ip_address'], 
            interface=host_cfg['interface'], 
            latency=host_cfg['latency'], 
            jitter=host_cfg['jitter'], 
            bandwidth=host_cfg['bandwidth'])
        hosts.append(host)
        
    if len(args) >= 2:
        if args[1] == 'reset':
            for host in hosts:
                unset(host)
            sys.exit(0)
            
    for host in hosts:
        unset(host)
                
    for host in hosts:
        if host.bandwidth == -1 and host.jitter == -1 and host.latency == -1:
            continue
        elif host.bandwidth == -1 and host.jitter == -1:
            print(f'{host.ip_address}, {host.latency}')
            static_delay(host)
        elif host.bandwidth == -1:
            jitter_delay(host)
        else:
            advance(host)
        
        
        
            
    