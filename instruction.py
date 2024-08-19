import os
import sys

interface = "enp1s0"

# The chosen answer is incorrect/incomplete. I faced a similar issue, 
# the chosen answer gave some help, but not enough.

# First, the following command is not really needed.
os.system(f"tc qdisc del dev {interface} root")

# It will 'delete' the root qdisc, but inmediately gets substituted by a pfifo_fast one 
# (so you don't lose connectivity).

# The second command:
os.system(f"tc qdisc add dev {interface} root handle 1: prio")

# Will substitute the pfifo_fast qdisc with the prio one. 
# By default, the prio queue has 3 bands (0, 1, 2) each managed by one class (1:1, 1:2 and 1:3).

# The packets will be sent to one of those bands using the TOS field of the IP package. 
# This configuration is shown when you execute:
os.system(f"tc qdisc ls")

# looking at the 'priomap' values.

# Then, you add a netem qdisc:
os.system(f"tc qdisc add dev {interface} parent 1:1 handle 2: netem delay 500ms")

# With this command you delay all traffic going to the 1:1 band (until the filter is in place).

# BREAKDOWN:
# 1. What is "band" in traffic control:
#       - Each "band" represents a different priority level
#           + Band 0: Highest priority.
#           + Band 1: Medium priority.
#           + Band 2: Lowest priority.
# 2. What is "handle" in qdisc
#       - A handle typically consists of two parts, separated by a colon (:):
#           + The part before the colon (:) associated with a root qdisc or a parent qdisc.  
#           + The part after the colon (:) used for classes or nested qdiscs.

# But there are two caveats:

# Your traffic can have a different TOS value and then being sent to another band.
# The prio qdisc can be configured so the traffic goes to another band.
# The following solved my issue to not be affected by the netem while the filter is not applied. 
# Instead of the above steps, I did:
os.system(f"sudo tc qdisc add dev {interface} root handle 1: prio priomap 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2 2")

# BREAKDOWN:
# 1. Prio priomap:
#       - This configuration assigns all 16 possible ToS values to Band 2, which is the lowest priority
#       - All traffic, regardless of its ToS or DSCP value, will be placed in the lowest priority band.
#       - This setup might be useful if you want to deprioritize all traffic on the eth0 interface compared to other interfaces or network activities

# This will send all traffic by default to the band 1:3.
# Then, I added the rule to delay traffic:
os.system(f"tc qdisc add dev {interface} parent 1:1 handle 10: netem delay 100ms 10ms")

# This creates the qdisc in the band 0, but since all traffic goes to band 3, it didn't affect me.

# Afterwards, I added the filter:

os.system(f"tc filter add dev eth0 protocol ip parent 1:0 prio 1 u32 match ip dst 10.0.0.1/32 match ip dport 80 0xffff flowid 1:1")

# BREAKDOWN:
#       + "parent 1:0": Indicates the parent qdisc or class to which this filter is attached. 
#         Here, 1: is the handle of the root qdisc, and 0 specifies the root of this qdisc.
#       + "prio 1": Sets the priority of the filter. 
#         Filters with lower priority numbers are evaluated before those with higher numbers. 
#         Here, prio 1 indicates that this is a high-priority filter.
#       + "u32": Specifies that the filter uses the u32 classifier, 
#         which allows for matching specific fields within the packet header (such as IP addresses, ports, etc.).
#       + "match ip dst 10.0.0.1/32": This matches packets where the destination IP address is "10.0.0.1". 
#         The "/32" indicates that the match should be exact (all 32 bits of the IP address).
#       + "match ip dport 80 0xffff": This matches packets with a destination port (dport) of 80, 
#         which is typically used for HTTP traffic. 
#         The 0xffff is a mask that specifies an exact match on the port number (all 16 bits).
#       + "flowid 1:1": Specifies that packets matching this filter should be directed to the class with the ID 1:1. 
#         This class is part of the queuing discipline with the root handle 1:.

# Now with the filter, only the chosen IP/port will be affected, since we redirect the chosen traffic to the band 0.
# All the other traffic continues unaffected since it continues to flow to band 3.