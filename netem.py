import os
import sys
import json
from typing import List


class Host:
    def __init__(self, ip_address, latency, jitter, bandwidth):
        self.ip_address = ip_address
        self.latency = latency
        self.jitter = jitter
        self.bandwidth = bandwidth


class Config:
    def __init__(self, hosts: List[Host], interface):
        self.hosts = hosts
        self.interface = interface


def unset(config: Config):
    os.system(f"sudo tc qdisc del dev {config.interface} root")
    print(f"sudo tc qdisc del dev {config.interface} root")


def add_prio_qdisc(config: Config):
    print(f"--- Add Prio qdisc ---")
    print(f"There are {len(config.hosts)} hosts")
    os.system(f"sudo tc qdisc add dev {config.interface} root handle 1: prio")
    print(f"sudo tc qdisc add dev {config.interface} root handle 1: prio")
    os.system(
        f"sudo tc qdisc replace dev {config.interface} root handle 1: prio bands {len(config.hosts) + 1}"
    )
    print(
        f"sudo tc qdisc replace dev {config.interface} root handle 1: prio bands {len(config.hosts) + 1}"
    )


def config_full(config: Config):
    unique_id = 3
    for index, host in enumerate(config.hosts):
        os.system(
            f"sudo tc qdisc add dev {config.interface} parent 1:{index+2} handle {unique_id}: htb"
        )
        print(
            f"sudo tc qdisc add dev {config.interface} parent 1:{index+2} handle {unique_id}: htb"
        )
        os.system(
            f"sudo tc class add dev {config.interface} parent {unique_id}: classid {unique_id}:1 htb rate {host.bandwidth}kbit"
        )
        print(
            f"sudo tc class add dev {config.interface} parent {unique_id}: classid {unique_id}:1 htb rate {host.bandwidth}kbit"
        )
        os.system(
            f"sudo tc qdisc add dev {config.interface} parent {unique_id}:1 handle {unique_id+len(config.hosts)}: netem delay {host.latency}ms {host.jitter}ms"
        )
        print(
            f"sudo tc qdisc add dev {config.interface} parent {unique_id}:1 handle {unique_id+len(config.hosts)}: netem delay {host.latency}ms {host.jitter}ms"
        )
        os.system(
            f"sudo tc filter add dev {config.interface} protocol ip parent 1: prio {index+2} u32 match ip dst {host.ip_address}/32 flowid 1:{index+2}"
        )
        print(
            f"sudo tc filter add dev {config.interface} protocol ip parent 1: prio {index+2} u32 match ip dst {host.ip_address}/32 flowid 1:{index+2}"
        )
        os.system(
            f"sudo tc filter add dev {config.interface} protocol ip parent {unique_id}: u32 match ip dst {host.ip_address}/32 flowid {unique_id}:1"
        )
        print(
            f"sudo tc filter add dev {config.interface} protocol ip parent {unique_id}: u32 match ip dst {host.ip_address}/32 flowid {unique_id}:1"
        )

        os.system(
            f"sudo tc filter add dev {config.interface} protocol ip parent 1: prio {index+2} u32 match ip src {host.ip_address}/32 flowid 1:{index+2}"
        )
        print(
            f"sudo tc filter add dev {config.interface} protocol ip parent 1: prio {index+2} u32 match ip src {host.ip_address}/32 flowid 1:{index+2}"
        )
        os.system(
            f"sudo tc filter add dev {config.interface} protocol ip parent {unique_id}: u32 match ip src {host.ip_address}/32 flowid {unique_id}:1"
        )
        print(
            f"sudo tc filter add dev {config.interface} protocol ip parent {unique_id}: u32 match ip src {host.ip_address}/32 flowid {unique_id}:1"
        )
        unique_id += 1


def config_Prometheus(config: Config):
    os.system(f"sudo tc qdisc add dev {config.interface} parent 1:1 handle 2: htb")
    print(f"sudo tc qdisc add dev {config.interface} parent 1:1 handle 2: htb")
    os.system(
        f"sudo tc filter add dev {config.interface} protocol ip parent 1: prio 1 u32 match ip sport 9090 0xffff flowid 1:1"
    )
    print(
        f"sudo tc filter add dev {config.interface} protocol ip parent 1: prio 1 u32 match ip sport 9090 0xffff flowid 1:1"
    )
    os.system(
        f"sudo tc filter add dev {config.interface} protocol ip parent 1: prio 1 u32 match ip sport 9100 0xffff flowid 1:1"
    )
    print(
        f"sudo tc filter add dev {config.interface} protocol ip parent 1: prio 1 u32 match ip sport 9100 0xffff flowid 1:1"
    )
    os.system(
        f"sudo tc filter add dev {config.interface} protocol ip parent 1: prio 1 u32 match ip dport 9090 0xffff flowid 1:1"
    )
    print(
        f"sudo tc filter add dev {config.interface} protocol ip parent 1: prio 1 u32 match ip dport 9090 0xffff flowid 1:1"
    )
    os.system(
        f"sudo tc filter add dev {config.interface} protocol ip parent 1: prio 1 u32 match ip dport 9100 0xffff flowid 1:1"
    )
    print(
        f"sudo tc filter add dev {config.interface} protocol ip parent 1: prio 1 u32 match ip dport 9100 0xffff flowid 1:1"
    )


if __name__ == "__main__":
    # Load config file
    with open("cfg.json", "r") as cfg_file:
        cfg = json.load(cfg_file)

    args = sys.argv

    hosts: List[Host] = []

    for host_cfg in cfg["hosts"]:
        host = Host(
            ip_address=host_cfg["ip_address"],
            latency=host_cfg["latency"],
            jitter=host_cfg["jitter"],
            bandwidth=host_cfg["bandwidth"],
        )
        hosts.append(host)

    interface = cfg["interface"]

    # NOTE: Config file loaded
    config = Config(hosts=hosts, interface=interface)

    if len(args) >= 2:
        if args[1] == "reset":
            for host in hosts:
                unset(config)
            sys.exit(0)
        else:
            sys.exit(0)

    unset(config)
    add_prio_qdisc(config)
    config_Prometheus(config)
    config_full(config)
