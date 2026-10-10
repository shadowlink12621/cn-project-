# QoS experiment results

**Status:** three baseline runs and three adaptive runs are recorded. Adaptive run 1 is the closest load match; runs 2 and 3 represent different actual bulk loads. All findings remain preliminary.

**Topology:** Mininet h1/h2 -> OpenFlow switch s1 -> h3; receiver-facing egress configured at 5 Mbps.  
**Traffic settings:** high UDP destination port 5001, requested 1.5 Mbps with 512-byte payload; bulk UDP destination port 5002, requested 8 Mbps with 1200-byte payload; each sender ran for 30 seconds.  
**Controller evidence:** adaptive run 1 logged ACTIVE at 77.9% and later INACTIVE at 35.2%; adaptive run 2 logged ACTIVE at 83.3% and 92.1%, with INACTIVE messages between activations; adaptive run 3 logged ACTIVE at 87.5% and later INACTIVE at 17.8%.

## Results by run

| Run | Mode | Class | Throughput | Loss | Mean delay | p95 delay | Sender packets |
|---|---|---|---:|---:|---:|---:|---:|
| 1 | Baseline | High | 1.5000 Mbps | 0% | 291.2616 ms | 506.9084 ms | 10,986 |
| 1 | Baseline | Bulk | 1.9814 Mbps | 0% | 290.6660 ms | 509.3280 ms | 6,192 |
| 2 | Baseline | High | 1.4628 Mbps | 0% | 302.3824 ms | 540.2097 ms | 10,714 |
| 2 | Baseline | Bulk | 1.9078 Mbps | 0% | 302.6436 ms | 534.4170 ms | 5,962 |
| 3 | Baseline | High | 1.4785 Mbps | 0% | 287.5054 ms | 508.3606 ms | 10,829 |
| 3 | Baseline | Bulk | 2.0378 Mbps | 0% | 287.9129 ms | 497.5662 ms | 6,368 |
| 1 | Adaptive | High | 1.4997 Mbps | 0% | 49.7486 ms | 253.0573 ms | 10,984 |
| 1 | Adaptive | Bulk | 1.9136 Mbps | 0% | 353.3140 ms | 688.0855 ms | 5,980 |
| 2 | Adaptive | High | 1.4726 Mbps | 1.829% | 209.8677 ms | 1,024.1037 ms | 10,987 |
| 2 | Adaptive stress | Bulk | 2.0659 Mbps | 56.566% | 951.6863 ms | 4,283.9836 ms | 14,864 |
| 3 | Adaptive | High | 1.5001 Mbps | 0% | 144.5412 ms | 422.8083 ms | 10,987 |
| 3 | Adaptive | Bulk | 1.6090 Mbps | 0% | 578.8457 ms | 2,452.5831 ms | 5,028 |

## Load-matched preliminary comparison

Baseline average over all three runs versus adaptive run 1 (adaptive run 1 sender counts were 10,984 high / 5,980 bulk, within the baseline ranges 10,714–10,986 / 5,962–6,368):

| Class | Metric | Baseline average | Adaptive run 1 | Change |
|---|---|---:|---:|---:|
| High | Throughput | 1.4804 Mbps | 1.4997 Mbps | +1.3% |
| High | Mean delay | 293.7165 ms | 49.7486 ms | -83.1% |
| High | p95 delay | 518.4929 ms | 253.0573 ms | -51.2% |
| Bulk | Throughput | 1.9757 Mbps | 1.9136 Mbps | -3.1% |
| Bulk | Mean delay | 293.7408 ms | 353.3140 ms | +20.3% |
| Bulk | p95 delay | 513.7704 ms | 688.0855 ms | +33.9% |

All baseline runs and adaptive run 1 reported 0% packet loss. This matched-load subset is consistent with the intended latency tradeoff: the high class had lower delay while the bulk class had higher delay. There is one adaptive trial in this load range, so describe it as preliminary evidence rather than a proven general result.

## Runs at different actual loads

Adaptive run 2's bulk sender sent 14,864 packets, far above the baseline range. It reported 56.566% bulk loss and 1.829% high-class loss; high p95 delay reached 1,024 ms. The controller logged multiple ACTIVE/INACTIVE transitions. Treat this as a heavier-load stress run, not a direct baseline comparison.

Adaptive run 3's bulk sender sent 5,028 packets, below the baseline range. Its POX log confirmed switch connection and policy ACTIVE at 87.5%, later INACTIVE at 17.8%. Treat it as a separate lower-load point, not a direct matched comparison.

## Limitations and next validation

1. Repeat an adaptive run with sender counts close to baseline (about 10.7k–11.0k high and 6.0k–6.4k bulk) to confirm the load-matched result.
2. Verify Open vSwitch flow/queue selection while the policy is ACTIVE before attributing all changes to queue scheduling.
3. POX emitted repeated ICMP parsing exceptions during adaptive traffic. The controller nevertheless logged policy state changes; report this as a limitation if it remains unresolved.
4. Actual generated packet counts differ from the nominal 8 Mbps bulk request. Compare sender counts as well as configured rates.

## Raw files and reproduction

- Baseline receiver outputs: [baseline.csv](baseline.csv), [baseline2.csv](baseline2.csv), [baseline3.csv](baseline3.csv).
- Adaptive receiver outputs: [adaptive.csv](adaptive.csv), [adaptive2.csv](adaptive2.csv), [adaptive3.csv](adaptive3.csv).
- Sender totals: baseline high 10,986/10,714/10,829 and bulk 6,192/5,962/6,368; Adaptive runs high 10,984/10,987/10,987 and bulk 5,980/14,864/5,028.
- Command sequence and VM setup: [../docs/SETUP_AND_EXPERIMENT.md](../docs/SETUP_AND_EXPERIMENT.md).
