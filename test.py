import os
import sys
import time
import csv

# Change these information before using
interface = "enp1s0"
# host_username = "thai"
# host_ipaddress = "192.168.122.159"
des_ipaddress_1 = "192.168.122.160"
des_ipaddress_2 = "192.168.122.161"
sleep_time = 1
local_csv_file = "B_2018.01.19_07.31.48.csv"

def ssh(command):
    # Executes the command remotely via SSH
    os.system(f"ssh {HOST_USER}@{HOST_IP_ADDRESS} '{command}'")

def unset():
    ssh(f"sudo tc qdisc del dev {interface} root")

def static(delay):
    ssh(f"sudo tc qdisc add dev {interface} root handle 1: prio")
    ssh(f"sudo tc qdisc add dev {interface} parent 1:1 handle 10: netem delay {delay}ms")
    ssh(f"sudo tc filter add dev {interface} protocol ip parent 1:0 prio 1 u32 match ip dst {des_ipaddress_1}/32 flowid 1:1")
    ssh(f"sudo tc filter add dev {interface} protocol ip parent 1:0 prio 1 u32 match ip dst {des_ipaddress_2}/32 flowid 1:1")

def var(delay, jitter):
    ssh(f"sudo tc qdisc add dev {interface} root handle 1: prio")
    ssh(f"sudo tc qdisc add dev {interface} parent 1:1 handle 10: netem delay {delay}ms {jitter}ms")
    ssh(f"sudo tc filter add dev {interface} protocol ip parent 1:0 prio 1 u32 match ip dst {des_ipaddress_1}/32 flowid 1:1")
    ssh(f"sudo tc filter add dev {interface} protocol ip parent 1:0 prio 1 u32 match ip dst {des_ipaddress_2}/32 flowid 1:1")

def advance(delay, jitter, bandwidth):
    ssh(f"sudo tc qdisc add dev {interface} root handle 1: htb")
    ssh(f"sudo tc class add dev {interface} parent 1: classid 1:1 htb rate {bandwidth}mbit")
    ssh(f"sudo tc qdisc add dev {interface} parent 1:1 handle 10: netem delay {delay}ms {jitter}ms")
    ssh(f"sudo tc filter add dev {interface} protocol ip parent 1:0 prio 1 u32 match ip dst {des_ipaddress_1}/32 flowid 1:1")
    ssh(f"sudo tc filter add dev {interface} protocol ip parent 1:0 prio 1 u32 match ip dst {des_ipaddress_2}/32 flowid 1:1")
    # BREAKDOWN:
    #       - "parent 1:0": Indicates the parent qdisc or class to which this filter is attached. 
    #         Here, 1: is the handle of the root qdisc, and 0 specifies the root of this qdisc.
    #       - "prio 1": Sets the priority of the filter. 
    #         Filters with lower priority numbers are evaluated before those with higher numbers. 
    #         Here, prio 1 indicates that this is a high-priority filter.
    #       - "u32": Specifies that the filter uses the u32 classifier, 
    #         which allows for matching specific fields within the packet header (such as IP addresses, ports, etc.).
    #       - "match ip dst 10.0.0.1/32": This matches packets where the destination IP address is "10.0.0.1". 
    #         The "/32" indicates that the match should be exact (all 32 bits of the IP address).
    #         The 0xffff is a mask that specifies an exact match on the port number (all 16 bits).
    #       - "flowid 1:1": Specifies that packets matching this filter should be directed to the class with the ID 1:1. 
    #         This class is part of the queuing discipline with the root handle 1:.

def datatrace(delay, jitter):
    ssh(f"sudo tc qdisc add dev {interface} root handle 1: htb")
    ssh(f"sudo tc class add dev {interface} parent 1: classid 1:1 htb rate 100mbit")
    ssh(f"sudo tc qdisc add dev {interface} parent 1:1 handle 10: netem delay {delay}ms {jitter}ms")
    ssh(f"sudo tc filter add dev {interface} protocol ip parent 1:0 prio 1 u32 match ip dst {des_ipaddress_1}/32 flowid 1:1")
    ssh(f"sudo tc filter add dev {interface} protocol ip parent 1:0 prio 1 u32 match ip dst {des_ipaddress_2}/32 flowid 1:1")
    
    while True:
        with open(local_csv_file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            
            for row in csv_reader:
                if line_count == 0:
                    line_count +=1
                    time.sleep(sleep_time)
                    continue
                bandwidth = int(float(row[12]) / 1000)
                
                print(f"konnichiwa {line_count} {bandwidth}mbit")
                
                ssh(f"sudo tc class change dev {interface} parent 1: classid 1:1 htb rate {bandwidth}mbit")

                line_count += 1
                time.sleep(sleep_time)    


if __name__ == "__main__":
    args = sys.argv
    globals()[args[1]](*args[2:])
