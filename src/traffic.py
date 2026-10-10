#!/usr/bin/env python3
"""UDP traffic generator and receiver for the Team 14 QoS experiment."""

import argparse
import csv
import json
import select
import socket
import struct
import time

DATA = struct.Struct("!4sQQ")
END = struct.Struct("!4sQ")
CLASSES = {
    "high": {"port": 5001, "id": 1, "default_rate": 1.5, "default_size": 512},
    "bulk": {"port": 5002, "id": 2, "default_rate": 8.0, "default_size": 1200},
}


def send_traffic(args):
    flow = CLASSES[args.traffic_class]
    packet_size = args.packet_size or flow["default_size"]
    rate_mbps = args.rate_mbps or flow["default_rate"]
    if packet_size < DATA.size or rate_mbps <= 0:
        raise SystemExit("packet size must be at least 20 bytes and rate must be positive")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    interval = packet_size * 8 / (rate_mbps * 1_000_000)
    deadline = time.monotonic() + args.seconds
    next_send = time.monotonic()
    sequence = 0
    padding = b"x" * (packet_size - DATA.size)

    while time.monotonic() < deadline:
        payload = DATA.pack(b"QOS1", sequence, time.time_ns()) + padding
        sock.sendto(payload, (args.host, flow["port"]))
        sequence += 1
        next_send += interval
        delay = next_send - time.monotonic()
        if delay > 0:
            time.sleep(delay)

    end_packet = END.pack(b"QEND", sequence)
    for _ in range(5):
        sock.sendto(end_packet, (args.host, flow["port"]))
        time.sleep(0.02)
    sock.close()
    print(json.dumps({
        "class": args.traffic_class,
        "destination": f"{args.host}:{flow['port']}",
        "sent_packets": sequence,
        "offered_rate_mbps": rate_mbps,
        "packet_size_bytes": packet_size,
        "duration_seconds": args.seconds,
    }, sort_keys=True))


def receive_traffic(args):
    sockets = {}
    for name, flow in CLASSES.items():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((args.bind, flow["port"]))
        sock.setblocking(False)
        sockets[sock] = name

    stats = {
        name: {"sequences": set(), "expected": None, "bytes": 0, "delays_ms": []}
        for name in CLASSES
    }
    deadline = time.monotonic() + args.seconds
    while time.monotonic() < deadline:
        readable, _, _ = select.select(list(sockets), [], [], 0.5)
        for sock in readable:
            data, _ = sock.recvfrom(65535)
            name = sockets[sock]
            row = stats[name]
            if len(data) >= END.size and data[:4] == b"QEND":
                _, expected = END.unpack(data[:END.size])
                row["expected"] = max(expected, row["expected"] or 0)
                continue
            if len(data) < DATA.size:
                continue
            magic, sequence, sent_ns = DATA.unpack(data[:DATA.size])
            if magic != b"QOS1":
                continue
            row["sequences"].add(sequence)
            row["bytes"] += len(data)
            row["delays_ms"].append(max(0.0, (time.time_ns() - sent_ns) / 1_000_000))

    rows = []
    for name in CLASSES:
        row = stats[name]
        received = len(row["sequences"])
        expected = row["expected"]
        if expected is None:
            expected = (max(row["sequences"]) + 1) if row["sequences"] else 0
        lost = max(0, expected - received)
        delays = sorted(row["delays_ms"])
        mean_delay = sum(delays) / len(delays) if delays else 0.0
        p95_delay = delays[min(len(delays) - 1, int(0.95 * len(delays)))] if delays else 0.0
        rows.append({
            "class": name,
            "expected_packets": expected,
            "received_packets": received,
            "lost_packets": lost,
            "loss_percent": round(100.0 * lost / expected, 3) if expected else 0.0,
            "throughput_mbps": round(row["bytes"] * 8 / (args.measure_seconds * 1_000_000), 4),
            "mean_delay_ms": round(mean_delay, 4),
            "p95_delay_ms": round(p95_delay, 4),
        })

    for sock in sockets:
        sock.close()

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as output:
            writer = csv.DictWriter(output, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    print(json.dumps(rows, indent=2, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    sender = subparsers.add_parser("send", help="send one UDP traffic class")
    sender.add_argument("--traffic-class", choices=CLASSES, required=True)
    sender.add_argument("--host", default="10.0.0.3", help="receiver IP address")
    sender.add_argument("--seconds", type=float, default=30.0)
    sender.add_argument("--rate-mbps", type=float, help="offered bit rate")
    sender.add_argument("--packet-size", type=int, help="UDP payload size in bytes")
    sender.set_defaults(func=send_traffic)

    receiver = subparsers.add_parser("receive", help="receive both UDP traffic classes")
    receiver.add_argument("--bind", default="0.0.0.0")
    receiver.add_argument("--seconds", type=float, default=35.0, help="receiver run time")
    receiver.add_argument("--measure-seconds", type=float, default=30.0,
                          help="sender run time used for throughput calculation")
    receiver.add_argument("--csv", help="optional path for the result CSV")
    receiver.set_defaults(func=receive_traffic)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
