# QoS experiment results

**Status:** two baseline runs and two adaptive runs are recorded. The adaptive controller logged ACTIVE during both adaptive trials. The comparison remains preliminary because the actual sender packet counts differ substantially between trials, especially for the bulk class.

**Topology:** Mininet h1/h2 -> OpenFlow switch s1 -> h3; receiver-facing egress configured at 5 Mbps.  
**Traffic settings:** high UDP destination port 5001, requested 1.5 Mbps with 512-byte payload; bulk UDP destination port 5002, requested 8 Mbps with 1200-byte payload; each sender ran for 30 seconds.  
**Controller evidence:** first adaptive run logged ACTIVE at 77.9% and later INACTIVE at 35.2%; second adaptive run logged ACTIVE at 83.3% and 92.1%, with INACTIVE messages between activations.

## Results by run

| Run | Mode | Class | Throughput | Loss | Mean delay | p95 delay | Sender packets |
|---|---|---|---:|---:|---:|---:|---:|
| 1 | Baseline | High | 1.5000 Mbps | 0% | 291.2616 ms | 506.9084 ms | 10,986 |
| 1 | Baseline | Bulk | 1.9814 Mbps | 0% | 290.6660 ms | 509.3280 ms | 6,192 |
| 2 | Baseline | High | 1.4628 Mbps | 0% | 302.3824 ms | 540.2097 ms | 10,714 |
| 2 | Baseline | Bulk | 1.9078 Mbps | 0% | 302.6436 ms | 534.4170 ms | 5,962 |
| 1 | Adaptive | High | 1.4997 Mbps | 0% | 49.7486 ms | 253.0573 ms | 10,984 |
| 1 | Adaptive | Bulk | 1.9136 Mbps | 0% | 353.3140 ms | 688.0855 ms | 5,980 |
| 2 | Adaptive | High | 1.4726 Mbps | 1.829% | 209.8677 ms | 1,024.1037 ms | 10,987 |
| 2 | Adaptive | Bulk | 2.0659 Mbps | 56.566% | 951.6863 ms | 4,283.9836 ms | 14,864 |

## Interpretation and limits

The two adaptive runs show a differentiated outcome: bulk delay/loss was much higher in the second adaptive run, while high-class throughput stayed near 1.5 Mbps and the first adaptive run showed much lower high-class delay. However, the second adaptive run's bulk sender sent 14,864 packets, compared with 5,962–6,192 in the baseline runs and 5,980 in adaptive run 1. This is a substantial difference in actual load even though the command requested the same rate. Therefore, do not claim a controlled, causal before/after improvement from these trials.

Both baseline runs reported no loss. Adaptive run 1 reported no loss; adaptive run 2 reported 1.829% high loss and 56.566% bulk loss. This suggests the controller's active period and offered load matter; high priority was not loss-free in every trial. POX also emitted repeated ICMP parsing exceptions during adaptive runs. The controller nevertheless logged policy state changes.

## Recommended next validation

1. Capture the next baseline and adaptive trials with sender counts and controller logs.
2. Aim for comparable actual packet counts in each condition, not just the same requested rate. If the sender output differs greatly, label that run as a different load level.
3. Verify OVS flow/queue selection while the adaptive policy is active before attributing all changes to queue scheduling.
4. Keep the POX ICMP parser exception as a known limitation unless it is fixed and retested.

## Raw files and reproduction

- Baseline receiver outputs: [baseline.csv](baseline.csv), [baseline2.csv](baseline2.csv).
- Adaptive receiver outputs: [adaptive.csv](adaptive.csv), [adaptive2.csv](adaptive2.csv).
- Sender totals: baseline runs high 10,986/10,714 and bulk 6,192/5,962; adaptive runs high 10,984/10,987 and bulk 5,980/14,864.
- Commands and setup: [../docs/SETUP_AND_EXPERIMENT.md](../docs/SETUP_AND_EXPERIMENT.md).
