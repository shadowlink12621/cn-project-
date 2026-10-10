# QoS experiment results

**Status:** two confirmed matched-load baseline runs and three adaptive runs are recorded. The run saved as `baseline3.csv` was actually QoS-active and is excluded from baseline averages. Two additional no-policy baseline runs are recorded separately from the matched-load averages: run 4 missed sender end markers and has sender-count-reconciled loss; run 5 received both end markers and reported no loss, but its actual bulk load differs from the matched runs. All findings remain preliminary.

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
| 4 | Baseline stress | High | 1.0521 Mbps | 29.856%* | 159.2145 ms | 314.8757 ms | 10,986 |
| 4 | Baseline stress | Bulk | 1.2454 Mbps | 55.848%* | 228.3658 ms | 326.4109 ms | 8,815 |
| 5 | Baseline extra | High | 1.5001 Mbps | 0% | 216.0576 ms | 309.9386 ms | 10,987 |
| 5 | Baseline extra | Bulk | 2.8054 Mbps | 0% | 213.4770 ms | 299.9790 ms | 8,767 |
| 1 | Adaptive | High | 1.4997 Mbps | 0% | 49.7486 ms | 253.0573 ms | 10,984 |
| 1 | Adaptive | Bulk | 1.9136 Mbps | 0% | 353.3140 ms | 688.0855 ms | 5,980 |
| 2 | Adaptive | High | 1.4726 Mbps | 1.829% | 209.8677 ms | 1,024.1037 ms | 10,987 |
| 2 | Adaptive stress | Bulk | 2.0659 Mbps | 56.566% | 951.6863 ms | 4,283.9836 ms | 14,864 |
| 3 | Adaptive | High | 1.5001 Mbps | 0% | 144.5412 ms | 422.8083 ms | 10,987 |
| 3 | Adaptive | Bulk | 1.6090 Mbps | 0% | 578.8457 ms | 2,452.5831 ms | 5,028 |

*Run 4 loss is reconciled from sender totals minus unique packets received because the receiver missed the QEND end marker; see `results/baseline4_reconciled.csv`. The receiver's own 0% loss figure for this run is invalid. This higher bulk-load run is not part of the matched-load average.

## Load-matched preliminary comparison

Baseline average over the two confirmed baseline runs versus adaptive run 1 (adaptive run 1 sender counts were 10,984 high / 5,980 bulk, within the confirmed baseline ranges 10,714–10,986 / 5,962–6,192):

| Class | Metric | Baseline average | Adaptive run 1 | Change |
|---|---|---:|---:|---:|
| High | Throughput | 1.4814 Mbps | 1.4997 Mbps | +1.3% |
| High | Mean delay | 296.8220 ms | 49.7486 ms | -83.2% |
| High | p95 delay | 518.4929 ms | 253.0573 ms | -51.7% |
| Bulk | Throughput | 1.9446 Mbps | 1.9136 Mbps | -1.6% |
| Bulk | Mean delay | 296.6548 ms | 353.3140 ms | +19.1% |
| Bulk | p95 delay | 521.8725 ms | 688.0855 ms | +31.8% |

Both confirmed baseline runs and adaptive run 1 reported 0% packet loss. This matched-load subset is consistent with the intended latency tradeoff: the high class had lower delay while the bulk class had higher delay. There is one adaptive trial in this load range, so describe it as preliminary evidence rather than a proven general result.

## Baseline runs 4 and 5

The flow dump during baseline run 4 showed normal forwarding for both classes: UDP 5001 and UDP 5002 each had `actions=output:"s1-eth3"`, with no `enqueue` action. This verifies the no-QoS baseline mode.

Sender summaries reported 10,986 high packets and 8,815 bulk packets sent. The receiver counted 7,706 high and 3,892 bulk unique packets, but its CSV said 0% loss because it had inferred the expected total from the largest sequence number received. The receiver did not observe the sender's QEND marker; consequently, the end of each stream was not included in its expected count. Reconciled against sender totals, high loss is 3,280/10,986 (29.856%) and bulk loss is 4,923/8,815 (55.848%). Throughput and delay summarize the packets that reached the receiver. This is a separate heavier-load baseline stress point, not a replacement for the matched-load baseline average.

Baseline run 5 used the updated receiver. Both classes report `end_marker_received: true`; high received 10,987/10,987 packets and bulk received 8,767/8,767. The switch flow dump showed normal `output` actions for both UDP ports. Received throughput totaled about 4.31 Mbps, below the configured 5 Mbps link cap, and reported loss was 0%. This is a valid no-policy run, but bulk packet count is above the confirmed matched-load range, so keep it separate from the average. See `results/baseline5.csv`.

The receiver code now reports `end_marker_received` and leaves loss fields null if the sender's end marker is missing. Pull the latest code before the next run.

## Switch queue-action verification

During a traffic run, `ovs-ofctl -O OpenFlow10 dump-flows s1` showed the UDP high flow (`tp_dst=5001`) with `actions=enqueue:"s1-eth3":1` and the bulk flow (`tp_dst=5002`) with `actions=enqueue:"s1-eth3":2`. A later dump showed 6,712 high packets and 4,718 bulk packets processed by those respective queue actions. This confirms the controller installed the intended queue-selection actions on the switch during the observed traffic interval.

## Runs at different actual loads

Adaptive run 2's bulk sender sent 14,864 packets, far above the confirmed matched-load baseline range. It reported 56.566% bulk loss and 1.829% high-class loss; high p95 delay reached 1,024 ms. The controller logged multiple ACTIVE/INACTIVE transitions. Treat this as a heavier-load stress run, not a direct baseline comparison.

Adaptive run 3's bulk sender sent 5,028 packets, below the confirmed matched-load baseline range. Its POX log confirmed switch connection and policy ACTIVE at 87.5%, later INACTIVE at 17.8%. Treat it as a separate lower-load point, not a direct matched comparison.

## Limitations and next validation

1. Repeat matched-load baseline and QoS runs with sender counts near the confirmed baseline ranges (about 10.7k–11.0k high and 6.0k–6.2k bulk); confirm `end_marker_received: true` before using receiver loss fields.
2. Queue-action verification is now confirmed by `ovs-ofctl` flow dumps while traffic was running; retain the output as demo evidence.
3. POX emitted repeated ICMP parsing exceptions during adaptive traffic. The controller nevertheless logged policy state changes; report this as a limitation if it remains unresolved.
4. Actual generated packet counts differ from the nominal 8 Mbps bulk request. Compare sender counts as well as configured rates.

## Raw files and reproduction

- Confirmed matched-load baseline outputs: [baseline.csv](baseline.csv), [baseline2.csv](baseline2.csv). [baseline3.csv](baseline3.csv) is excluded because its matching flow dump showed QoS queue actions. [baseline4_reconciled.csv](baseline4_reconciled.csv) records the no-QoS run with loss reconciled from sender/receiver totals; [baseline5.csv](baseline5.csv) records the extra verified baseline with end markers received.
- Adaptive receiver outputs: [adaptive.csv](adaptive.csv), [adaptive2.csv](adaptive2.csv), [adaptive3.csv](adaptive3.csv).
- Sender totals: confirmed matched-load baseline high 10,986/10,714 and bulk 6,192/5,962; baseline stress run 4 high 10,986 and bulk 8,815; extra baseline run 5 high 10,987 and bulk 8,767; Adaptive runs high 10,984/10,987/10,987 and bulk 5,980/14,864/5,028.
- Command sequence and VM setup: [../docs/SETUP_AND_EXPERIMENT.md](../docs/SETUP_AND_EXPERIMENT.md).
