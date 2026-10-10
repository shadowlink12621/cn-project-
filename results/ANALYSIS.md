# Initial QoS experiment comparison

**Status:** one baseline and one adaptive run; repeat before making strong claims.  
**Topology:** Mininet h1/h2 -> OpenFlow switch s1 -> h3; receiver-facing egress configured at 5 Mbps.  
**Traffic:** high UDP port 5001, offered 1.5 Mbps with 512-byte payload; bulk UDP port 5002, offered 8 Mbps with 1200-byte payload; each sender ran for 30 seconds.  
**Adaptive controller evidence:** POX logged policy ACTIVE at 77.9% utilization and later INACTIVE at 35.2%.

## Results

| Mode | Class | Receiver throughput | Loss | Mean delay | p95 delay | Sender packets |
|---|---|---:|---:|---:|---:|---:|
| Baseline | High | 1.5000 Mbps | 0% | 291.2616 ms | 506.9084 ms | 10,986 |
| Adaptive | High | 1.4997 Mbps | 0% | 49.7486 ms | 253.0573 ms | 10,984 |
| Baseline | Bulk | 1.9814 Mbps | 0% | 290.6660 ms | 509.3280 ms | 6,192 |
| Adaptive | Bulk | 1.9136 Mbps | 0% | 353.3140 ms | 688.0855 ms | 5,980 |

## Initial interpretation

In these runs, high-class mean delay fell by 82.9% and p95 delay fell by 50.1% under the adaptive controller. Bulk mean delay increased by 21.6%, p95 by 35.1%, and throughput fell by 3.4%. Both runs reported 0% packet loss.

This is consistent with a latency tradeoff favoring the high-priority class. It does not establish a statistically reliable improvement: there is only one run per mode, sender packet counts differ slightly, and the adaptive controller logged ICMP parsing exceptions. Repeat at least two more runs in each mode under the same settings. Verify the queue-selection actions on OVS before claiming that queueing caused the delay change.

## Raw files and reproduction

- [baseline.csv](baseline.csv) and [adaptive.csv](adaptive.csv) contain the receiver output.
- Sender output: baseline high 10,986 packets and bulk 6,192; adaptive high 10,984 and bulk 5,980.
- Command sequence and VM setup: [../docs/SETUP_AND_EXPERIMENT.md](../docs/SETUP_AND_EXPERIMENT.md).
