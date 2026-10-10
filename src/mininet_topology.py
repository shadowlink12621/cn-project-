#!/usr/bin/env python3
"""Start the Team 14 three-host Mininet topology and configure egress queues."""

import subprocess

from mininet.cli import CLI
from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.topo import Topo


class QoSTopology(Topo):
    def build(self):
        switch = self.addSwitch(
            "s1",
            dpid="0000000000000001",
            protocols="OpenFlow10",
            failMode="secure",
        )
        high_sender = self.addHost("h1", ip="10.0.0.1/24")
        bulk_sender = self.addHost("h2", ip="10.0.0.2/24")
        receiver = self.addHost("h3", ip="10.0.0.3/24")
        self.addLink(high_sender, switch)
        self.addLink(bulk_sender, switch)
        self.addLink(receiver, switch)


def configure_receiver_queues():
    """Shape s1's receiver-facing port and create the two traffic queues."""
    subprocess.run(
        ["ovs-vsctl", "--", "clear", "Port", "s1-eth3", "qos"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.run(
        [
            "ovs-vsctl",
            "--",
            "set",
            "Port",
            "s1-eth3",
            "qos=@newqos",
            "--",
            "--id=@newqos",
            "create",
            "QoS",
            "type=linux-htb",
            "other-config:max-rate=5000000",
            "queues:1=@high",
            "queues:2=@bulk",
            "--",
            "--id=@high",
            "create",
            "Queue",
            "other-config:min-rate=1500000",
            "other-config:max-rate=5000000",
            "--",
            "--id=@bulk",
            "create",
            "Queue",
            "other-config:min-rate=500000",
            "other-config:max-rate=5000000",
        ],
        check=True,
    )
    print("Configured s1-eth3 at 5 Mbps: queue 1 = high, queue 2 = bulk.")


def main():
    network = Mininet(
        topo=QoSTopology(),
        switch=OVSSwitch,
        controller=None,
        autoSetMacs=True,
        autoStaticArp=False,
    )
    network.addController(
        "c0",
        controller=RemoteController,
        ip="127.0.0.1",
        port=6633,
    )
    try:
        network.start()
        configure_receiver_queues()
        print("Hosts: h1=10.0.0.1 (high), h2=10.0.0.2 (bulk), h3=10.0.0.3 (receiver)")
        print("The OpenFlow controller must already be running on 127.0.0.1:6633.")
        CLI(network)
    finally:
        network.stop()


if __name__ == "__main__":
    main()
