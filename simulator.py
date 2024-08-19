import os
import sys

# Change these information before using
interface = "enp1s0"
des_ipaddress = "192.168.122.160"

def undelay():
    os.system(f"sudo tc qdisc del dev {interface} root")

# interface, host_password, des_ipaddress, delay, jitter, bandwidth

def delay(des_ipaddress, delay, jitter, bandwidth):
    os.system(f"sudo tc qdisc add dev {interface} root handle 1: htb")
    os.system(f"sudo tc class add dev {interface} parent 1: classid 1:1 htb rate {bandwidth}mbit")
    os.system(f"sudo tc qdisc add dev {interface} parent 1:1 handle 10: netem delay {delay}ms {jitter}ms")
    os.system(f"sudo tc filter add dev {interface} protocol ip parent 1:0 prio 1 u32 match ip dst {des_ipaddress}/32 flowid 1:1")
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


if __name__ == "__main__":
    args = sys.argv
    globals()[args[1]](*args[2:])
