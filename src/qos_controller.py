"""POX controller for the Team 14 dynamic UDP QoS demo.

The topology uses OpenFlow 1.0. Switch port 3 is the receiver-facing bottleneck.
Queue 1 is the high-priority class and queue 2 is background/bulk traffic.
"""

import time

from pox.core import core
from pox.lib.addresses import IPAddr
from pox.lib.packet import ethernet
from pox.lib.recoco import Timer
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

SERVER_IP = "10.0.0.3"
RECEIVER_PORT = 3
LINK_CAPACITY_BPS = 5_000_000
POLL_SECONDS = 2
HIGH_UTILIZATION = 0.70
LOW_UTILIZATION = 0.50
HIGH_CLASS_PORT = 5001
BULK_CLASS_PORT = 5002
HIGH_QUEUE_ID = 1
BULK_QUEUE_ID = 2


class QoSController(object):
    """Learning switch that enables queue selection when the egress is busy."""

    def __init__(self):
        self.connections = {}
        self.mac_to_port = {}
        self.policy_active = {}
        self.last_port_sample = {}
        core.openflow.addListeners(self)
        Timer(POLL_SECONDS, self._poll_port_stats, recurring=True)
        log.info("QoS controller ready; watching switch port %s", RECEIVER_PORT)

    def _handle_ConnectionUp(self, event):
        dpid = event.dpid
        self.connections[dpid] = event.connection
        self.mac_to_port[dpid] = {}
        self.policy_active[dpid] = False
        log.info("Switch %s connected; requesting port statistics", dpid)

    def _handle_ConnectionDown(self, event):
        self.connections.pop(event.dpid, None)
        self.mac_to_port.pop(event.dpid, None)
        self.policy_active.pop(event.dpid, None)
        self.last_port_sample.pop((event.dpid, RECEIVER_PORT), None)

    def _poll_port_stats(self):
        for connection in list(self.connections.values()):
            request = of.ofp_stats_request(
                body=of.ofp_port_stats_request(port_no=RECEIVER_PORT)
            )
            connection.send(request)

    def _handle_PortStatsReceived(self, event):
        dpid = event.dpid
        now = time.monotonic()
        for stat in event.stats:
            if stat.port_no != RECEIVER_PORT:
                continue
            key = (dpid, stat.port_no)
            previous = self.last_port_sample.get(key)
            self.last_port_sample[key] = (stat.tx_bytes, now)
            if previous is None:
                continue

            old_bytes, old_time = previous
            elapsed = now - old_time
            if elapsed <= 0:
                continue
            rate_bps = max(0, stat.tx_bytes - old_bytes) * 8.0 / elapsed
            utilization = rate_bps / LINK_CAPACITY_BPS
            active = self.policy_active.get(dpid, False)

            if not active and utilization >= HIGH_UTILIZATION:
                self._set_policy(dpid, True, utilization)
            elif active and utilization < LOW_UTILIZATION:
                self._set_policy(dpid, False, utilization)

    def _class_match(self, port):
        match = of.ofp_match()
        match.dl_type = ethernet.IP_TYPE
        match.nw_proto = 17  # UDP
        match.nw_dst = IPAddr(SERVER_IP)
        match.tp_dst = port
        return match

    def _set_policy(self, dpid, enabled, utilization):
        connection = self.connections.get(dpid)
        if connection is None:
            return

        # Remove old entries for these UDP classes so the next packet-in is
        # forwarded using the new queue selection (or the baseline action).
        for port in (HIGH_CLASS_PORT, BULK_CLASS_PORT):
            delete = of.ofp_flow_mod()
            delete.command = of.OFPFC_DELETE
            delete.match = self._class_match(port)
            delete.out_port = of.OFPP_NONE
            connection.send(delete)

        self.policy_active[dpid] = enabled
        state = "ACTIVE" if enabled else "INACTIVE"
        log.info("Congestion policy %s at %.1f%% utilization", state, utilization * 100)

    def _handle_PacketIn(self, event):
        packet = event.parsed
        if packet is None or not packet.parsed:
            return

        dpid = event.dpid
        table = self.mac_to_port.setdefault(dpid, {})
        table[packet.src] = event.port

        if packet.dst.is_multicast:
            self._send_flood(event)
            return

        output_port = table.get(packet.dst)
        if output_port is None:
            self._send_flood(event)
            return
        if output_port == event.port:
            return

        flow = of.ofp_flow_mod()
        flow.match = of.ofp_match.from_packet(packet, event.port)
        flow.idle_timeout = 10
        flow.hard_timeout = 30
        flow.data = event.ofp

        action = self._queue_action(packet, output_port, self.policy_active.get(dpid, False))
        if action is None:
            flow.actions.append(of.ofp_action_output(port=output_port))
        else:
            flow.priority = 40000
            flow.actions.append(action)
        event.connection.send(flow)

    def _queue_action(self, packet, output_port, active):
        if not active or output_port != RECEIVER_PORT:
            return None
        ip_packet = packet.find("ipv4")
        if ip_packet is None or str(ip_packet.dstip) != SERVER_IP or ip_packet.protocol != 17:
            return None
        udp_packet = ip_packet.find("udp")
        if udp_packet is None:
            return None
        if udp_packet.dstport == HIGH_CLASS_PORT:
            return of.ofp_action_enqueue(port=output_port, queue_id=HIGH_QUEUE_ID)
        if udp_packet.dstport == BULK_CLASS_PORT:
            return of.ofp_action_enqueue(port=output_port, queue_id=BULK_QUEUE_ID)
        return None

    def _send_flood(self, event):
        message = of.ofp_packet_out()
        message.data = event.ofp
        message.in_port = event.port
        message.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        event.connection.send(message)


def launch():
    core.registerNew(QoSController)
