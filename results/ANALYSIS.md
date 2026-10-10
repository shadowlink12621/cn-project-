# Initial QoS experiment comparison

**Status:** two baseline runs and one adaptive run. Repeat adaptive runs before making strong claims.  
**Topology:** Mininet h1/h2 -> OpenFlow switch s1 -> h3; receiver-facing egress configured at 5 Mbps.  
**Traffic:** high UDP port 5001, offered 1.5 Mbps with 512-byte payload; bulk UDP port 5002, offered 8 Mbps with 1200-byte payload; each sender ran for 30 seconds.  
**Adaptive controller evidence:** POX logged policy ACTIVE at 77.9% utilization and later INACTIVE at 35.2%.

## Results by run

| Run | Mode | Class | Throughput | Loss | Mean delay | p95 delay | Sender packets |
|---|---|---|---:|---:|---:|---:|---:|
| 1 | Baseline | High | 1.5000 Mbps | 0% | 291.2616 ms | 506.9084 ms | 10,986 |
| 1 | Baseline | Bulk | 1.9814 Mbps | 0% | 290.6660 ms | 509.3280 ms | 6,192 |
| 2 | Baseline | High | 1.4628 Mbps | 0% | 302.3824 ms | 540.2097 ms | 10,714 |
| 2 | Baseline | Bulk | 1.9078 Mbps | 0% | 302.6436 ms | 534.4170 ms | 5,962 |
| 1 | Adaptive | High | 1.4997 Mbps | 0% | 49.7486 ms | 253.0573 ms | 10,984 |
| 1 | Adaptive | Bulk | 1.9136 Mbps | 0% | 353.3140 ms | 688.0855 ms | 5,980 |

## Preliminary comparison

Baseline averages (two runs) versus the single adaptive run:

| Class | Metric | Baseline average | Adaptive | Change |
|---|---|---:|---:|---:|
| High | Throughput | 1.4814 Mbps | 1.4997 Mbps | +1.2% |
| High | Mean delay | 296.8220 ms | 49.7486 ms | -83.2% |
| High | p95 delay | 523.5591 ms | 253.0573 ms | -51.7% |
| Bulk | Throughput | 1.9446 Mbps | 1.9136 Mbps | -1.6% |
| Bulk | Mean delay | 296.6548 ms | 353.3140 ms | +19.1% |
| Bulk | p95 delay | 521.8725 ms | 688.0855 ms | +31.8% |

Both conditions reported 0% packet loss. The current measurements are consistent with a latency tradeoff favoring the high-priority class. The comparison remains preliminary because it uses two baseline runs but only one adaptive run. Run at least two more adaptive trials under identical settings before making a strong statistical claim. The actual bulk sender counts were roughly 5,962–6,192 packets even though the configured offered rate was 8 Mbps; preserve the sender output and avoid describing the result as sustained 8 Mbps delivered traffic.

POX emitted ICMP parsing exceptions during adaptive traffic. The controller still logged activation and deactivation, but the error should be understood and reported as a limitation if it recurs. Verify queue-selection actions on OVS if time permits before claiming the queue action alone caused the measured difference.

## Raw files and reproduction

- [baseline.csv](baseline.csv) and [baseline2.csv](baseline2.csv): receiver outputs for two baseline runs.
- [adaptive.csv](adaptive.csv): receiver output for the first adaptive run.
- Sender outputs: baseline run 1 high 10,986 / bulk 6,192; baseline run 2 high 10,714 / bulk 5,962; adaptive run 1 high 10,984 / bulk 5,980.
- Command sequence and VM setup: [../docs/SETUP_AND_EXPERIMENT.md](../docs/SETUP_AND_EXPERIMENT.md).
