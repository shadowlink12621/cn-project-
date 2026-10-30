# QoS experiment results


## Current 2 Mbps follow-up — 30 Oct 2026

The current checked-in topology configures the receiver-facing port and both queue maximum rates to 2 Mbps. Earlier 5 Mbps runs remain historical data and must not be combined with these rows.

Three cap2 baseline CSVs and three cap2 QoS CSVs have valid end markers. The averages below are calculated from those CSV rows:

| Condition | Class | Mean throughput | Mean delay | Mean p95 delay | Mean CSV loss |
|---|---|---:|---:|---:|---:|
| Baseline | High | 0.810 Mbps | 530.9 ms | 660.4 ms | 0% |
| Baseline | Bulk | 1.062 Mbps | 551.0 ms | 693.9 ms | 0% |
| QoS | High | 1.298 Mbps | 486.9 ms | 1,319.5 ms | 0.28% |
| QoS | Bulk | 0.577 Mbps | 1,911.7 ms | 5,589.6 ms | 0% |

These averages are descriptive only. Actual sender packet counts differ substantially between baseline and QoS trials, so this is not a tightly load-matched comparison. The measurements suggest higher received high-class throughput and lower bulk throughput under the QoS-labeled runs; high-class delay varies, and the high p95 average is higher. Do not claim a consistent latency improvement or a guaranteed bandwidth from these numbers. The configured queue minimum rates are 1.5 Mbps (high) and 0.5 Mbps (bulk), but configuration alone does not prove a guarantee.

A separate stress observation, **cap2-qos-check.csv**, recorded 1.4107 Mbps high throughput and 0.6538 Mbps bulk throughput, with 0% high loss and 71.562% bulk loss. Treat it as its own stress result, not as a matched comparison to cap2 baseline.

### 2 Mbps OpenFlow evidence status

The saved **cap2-qos2-flows.txt** and **cap2-qos3-flows.txt** snapshots show ordinary **output:3** actions for the UDP flows. Those particular snapshots do not demonstrate queue assignment during active congestion. Capture the flow table after the controller logs **ACTIVE** and after the senders have been running for several seconds. Queue selection is demonstrated for a trial only when the live output shows UDP destination 5001 with enqueue queue 1 and UDP destination 5002 with enqueue queue 2. The earlier 5 Mbps adaptive6 run is separately documented as having captured both actions in the same run.

### Current demo/review checklist

1. Pull the latest source and confirm the port capacity and controller utilization reference are both 2,000,000 bit/s.
2. Start one custom POX **qos_controller** and a fresh Mininet topology.
3. Start the receiver before the senders. During the send window, confirm a controller **ACTIVE** message and save a live flow dump.
4. Require both receiver end markers to be true before quoting receiver-computed loss.
5. Present the results as preliminary and separate 2 Mbps results from the earlier 5 Mbps results.
6. If the policy does not activate or both queue actions are not visible, report that accurately and use the earlier verified adaptive6 evidence for the queue-action explanation.


**Status:** two confirmed matched-load baseline runs, three earlier adaptive runs, the baseline6/adaptive5 pair, and an adaptive6 run with both queue actions captured are recorded. The new pair has valid end markers but a 16.8% high-flow sender-count mismatch, so it is a useful near-load comparison, not a tightly matched trial. The run saved as `baseline3.csv` was actually QoS-active and is excluded from baseline averages. Two additional no-policy baseline runs are recorded separately from the matched-load averages: run 4 missed sender end markers and has sender-count-reconciled loss; run 5 received both end markers and reported no loss, but its actual bulk load differs from the matched runs. All findings remain preliminary.

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

1. Repeat the baseline6/adaptive5 pair if a stronger comparison is required: actual high sender counts differed by about 16.8%; keep both receiver end-marker flags valid.
2. Queue-action verification is now confirmed by `ovs-ofctl` flow dumps while traffic was running; retain the output as demo evidence.
3. POX emitted repeated ICMP parsing exceptions during adaptive traffic. The controller nevertheless logged policy state changes; report this as a limitation if it remains unresolved.
4. Actual generated packet counts differ from the nominal 8 Mbps bulk request. Compare sender counts as well as configured rates.

## Raw files and reproduction

- Confirmed matched-load baseline outputs: [baseline.csv](baseline.csv), [baseline2.csv](baseline2.csv). [baseline3.csv](baseline3.csv) is excluded because its matching flow dump showed QoS queue actions. [baseline4_reconciled.csv](baseline4_reconciled.csv) records the no-QoS run with loss reconciled from sender/receiver totals; [baseline5.csv](baseline5.csv) records the extra verified baseline with end markers received.
- Adaptive receiver outputs: [adaptive.csv](adaptive.csv), [adaptive2.csv](adaptive2.csv), [adaptive3.csv](adaptive3.csv), [adaptive4.csv](adaptive4.csv), [adaptive5.csv](adaptive5.csv), [adaptive6.csv](adaptive6.csv).
- Sender totals: confirmed matched-load baseline high 10,986/10,714 and bulk 6,192/5,962; baseline stress run 4 high 10,986 and bulk 8,815; extra baseline run 5 high 10,987 and bulk 8,767; baseline6 high 9,408 and bulk 7,287; earlier adaptive runs high 10,984/10,987/10,987 and bulk 5,980/14,864/5,028; adaptive4 high 10,986 and bulk 23,737; adaptive5 high 10,987 and bulk 7,703.
- Command sequence and VM setup: [../docs/SETUP_AND_EXPERIMENT.md](../docs/SETUP_AND_EXPERIMENT.md).


## Adaptive run 4 — queue behavior verified, measurement incomplete

The controller log for this run showed policy activation at 86.4% utilization and deactivation at 31.5%. The live OpenFlow dump showed UDP destination port 5001 using `enqueue:"s1-eth3":1` and port 5002 using `enqueue:"s1-eth3":2`. This confirms dynamic policy activation and intended queue selection during traffic.

The receiver ran for 35 seconds while senders ran for 30 seconds, but neither flow's QEND marker arrived. Receiver counts were high 7,494 and bulk 2,972; the sender summaries reported high 10,986 and bulk 23,737. Therefore expected receiver counts and packet loss are unknown; do not compute loss from these values as if all sent packets were accounted for. The received throughput and delays are preserved in [adaptive4.csv](adaptive4.csv), but this run is a high-load stress/incomplete measurement, not a matched-load comparison. The requested bulk rate was 8 Mbps and actual sender packet count was about 2.7 times baseline5's 8,767 packets.

The attached POX traceback is an ICMP Destination Unreachable parser exception in POX's `icmp.py` (`ipv4.ipv4` attribute lookup). It is a POX compatibility/packet-parsing issue. The controller continued processing port statistics and emitted ACTIVE/INACTIVE transitions, and the observed UDP flow entries still used the correct queues. Record it as a known controller log error; it does not invalidate the direct flow-table evidence.

## Next validation

Repeat a controlled baseline/adaptive pair using identical traffic settings. To target baseline5's actual bulk load more closely, use high 1.5 Mbps and bulk 3.0 Mbps for both conditions (rather than requesting 8 Mbps). Run the receiver for 90 seconds so the end markers have time to arrive after the 30-second sender period; keep `--measure-seconds 30`. Check that both markers are true and save both sender summaries. Capture the QoS flow dump while traffic is active and keep the controller ACTIVE lines. Compare actual sender counts; if they still differ substantially, label results as separate load points. Conclusions remain preliminary until there are repeated adaptive trials at comparable loads.


## Baseline6 and adaptive5 — 19 October 2026

Both runs used 1.5 Mbps high and 3 Mbps bulk senders for 30 seconds, with the receiver left open for 90 seconds. Both classes in both runs received their QEND end marker, so receiver loss fields are valid.

| Run | Class | Sender packets | Received | Loss | Throughput | Mean delay | p95 delay |
|---|---|---:|---:|---:|---:|---:|---:|
| Baseline6 | High | 9,408 | 9,408 | 0% | 1.2845 Mbps | 248.1234 ms | 649.7309 ms |
| Baseline6 | Bulk | 7,287 | 7,287 | 0% | 2.3318 Mbps | 241.2009 ms | 584.3539 ms |
| Adaptive5 | High | 10,987 | 10,987 | 0% | 1.5001 Mbps | 117.7214 ms | 633.0678 ms |
| Adaptive5 | Bulk | 7,703 | 7,362 | 4.427% | 2.3558 Mbps | 638.9985 ms | 2,885.4477 ms |

The bulk sender totals are close (5.7% difference), while the high sender totals differ by 16.8%; therefore the pair is not tightly load matched. The observed numbers are consistent with the intended latency tradeoff, but this is one run per condition and load differs. Present as a demonstration, not a causal or statistical claim.

The adaptive5 controller logged ACTIVE at 79.5% and 96.8% utilization, with INACTIVE at 33.1% and 0.0%. Its pasted live flow dump captured high UDP port 5001 using queue 1, but did not show the bulk flow entry; adaptive4 previously showed both queue actions. Capture another flow dump after a few seconds of active traffic in any repeat to verify both queues in that run. The receiver and sender CSVs are preserved as [baseline6.csv](baseline6.csv) and [adaptive5.csv](adaptive5.csv).


## Adaptive6 — both queues confirmed in one run — 19 October 2026

The controller connected to the switch and logged ACTIVE at 79.6% utilization, followed by INACTIVE at 31.5%. `pingall` passed. The first live flow dump showed high UDP port 5001 using queue 1 and bulk UDP port 5002 using queue 2; a later dump showed both rules with increasing packet counters. This completes the same-run queue-selection verification.

The 90-second receiver got both end markers. High sent/received 10,983/10,983, loss 0%, throughput 1.4995 Mbps, mean delay 5.8537 ms, p95 31.9962 ms. Bulk sent 8,267, received 8,267, loss 0%, throughput 2.6454 Mbps, mean delay 235.7977 ms, p95 505.4946 ms. Raw receiver results are in [adaptive6.csv](adaptive6.csv).

Compared with baseline6, adaptive6's high sender count is 16.8% higher and bulk sender count is 13.4% higher. Its observed high delay is much lower, while bulk delay is similar; the differing loads and one trial per condition prevent attributing those changes solely to QoS. Present this as a successful functional demonstration with preliminary performance evidence. Another baseline trial at these same rates would strengthen the numerical comparison, but the controller, both queue actions, and valid receiver measurements have now all been demonstrated.
