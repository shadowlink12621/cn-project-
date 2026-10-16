# VM setup and experiment runbook

This guide assumes the team's Ubuntu VM has Mininet 2.3.0, Open vSwitch 3.3.9, and POX checked out at the home-directory path ~/pox. The topology constrains the receiver-facing Open vSwitch port to 5 Mbps and creates two HTB queues. The controller measures that port and selects queues for the two UDP destination ports after utilization crosses the configured threshold.

## 1. Pull the project files

In the VM terminal:

    cd ~/cn-project-/cn-project-
    git pull origin main

The current checkout is nested because the empty repository was cloned from inside a folder with the same name. Keep using this inner repository directory.

## 2. Start the controller

Stop the earlier POX learning-switch process with Ctrl+C. In its terminal, start the project controller:

    cd ~/cn-project-/cn-project-
    PYTHONPATH="$PWD/src" python3 ~/pox/pox.py qos_controller

Leave it running. The controller listens on port 6633 and reports switch connections, utilization, and policy state changes.

POX warned that Python 3.12 is newer than its documented Python range. The simple learning-switch smoke test worked in this VM. If the custom application fails to start, send the full traceback before changing Python packages.

## 3. Start the topology

In a second VM terminal:

    cd ~/cn-project-/cn-project-
    sudo mn -c
    sudo python3 src/mininet_topology.py

The command opens the Mininet CLI. It connects the switch to the controller and configures these queues on s1-eth3:

| Queue | UDP destination port | Meaning | Minimum rate | Maximum rate |
|---|---:|---|---:|---:|
| 1 | 5001 | High-priority real-time-like flow | 1.5 Mbps | 5 Mbps |
| 2 | 5002 | Low-priority bulk flow | 0.5 Mbps | 5 Mbps |

The port capacity is 5 Mbps. Queue minimum rates are lower than the port capacity so both classes have room; these settings are experiment controls, not proof of a bandwidth guarantee.

## 4. Run the baseline

For the baseline, the controller should be the standard POX learning switch rather than qos_controller. Stop the project controller with Ctrl+C, start the standard learning switch again, and restart the Mininet topology.

At the Mininet prompt, launch the receiver first, then both senders:

    py h3.cmd("python3 /home/link/cn-project-/cn-project-/src/traffic.py receive --seconds 35 --measure-seconds 30 --csv /tmp/baseline.csv > /tmp/baseline-receiver.log 2>&1 &")
    py __import__('time').sleep(2)
    py h1.cmd("python3 /home/link/cn-project-/cn-project-/src/traffic.py send --traffic-class high --seconds 30 --rate-mbps 1.5 >/tmp/high-baseline.log 2>&1 &")
    py h2.cmd("python3 /home/link/cn-project-/cn-project-/src/traffic.py send --traffic-class bulk --seconds 30 --rate-mbps 8 >/tmp/bulk-baseline.log 2>&1 &")

Wait about 36 seconds, then inspect the measurements:

    py print(h3.cmd('cat /tmp/baseline-receiver.log; cat /tmp/baseline.csv'))
    py print(h1.cmd('cat /tmp/high-baseline.log'))
    py print(h2.cmd('cat /tmp/bulk-baseline.log'))

The first CSV row is the high-priority flow; the second is the bulk flow. Save the output before the next run. Also save both sender summaries. Check that the receiver reports `end_marker_received: true`; if it is false or the sender total exceeds receiver expected count, mark loss as unknown and do not quote the receiver's loss percentage.

## 5. Run with adaptive QoS

Exit Mininet with exit. Stop the baseline controller with Ctrl+C, then start the project controller again:

    cd ~/cn-project-/cn-project-
    PYTHONPATH="$PWD/src" python3 ~/pox/pox.py qos_controller

In another terminal, start the topology again:

    cd ~/cn-project-/cn-project-
    sudo mn -c
    sudo python3 src/mininet_topology.py

At the Mininet prompt, repeat the same receiver and sender commands, changing the result paths from baseline to adaptive:

    py h3.cmd("python3 /home/link/cn-project-/cn-project-/src/traffic.py receive --seconds 35 --measure-seconds 30 --csv /tmp/adaptive.csv > /tmp/adaptive-receiver.log 2>&1 &")
    py __import__('time').sleep(2)
    py h1.cmd("python3 /home/link/cn-project-/cn-project-/src/traffic.py send --traffic-class high --seconds 30 --rate-mbps 1.5 >/tmp/high-adaptive.log 2>&1 &")
    py h2.cmd("python3 /home/link/cn-project-/cn-project-/src/traffic.py send --traffic-class bulk --seconds 30 --rate-mbps 8 >/tmp/bulk-adaptive.log 2>&1 &")

Check that the controller reports congestion and the policy changing to ACTIVE:

    py print(h3.cmd('cat /tmp/adaptive-receiver.log; cat /tmp/adaptive.csv'))
    py print(h1.cmd('cat /tmp/high-adaptive.log'))
    py print(h2.cmd('cat /tmp/bulk-adaptive.log'))

After the run, exit Mininet. Copy the CSV files into the repository's results directory only after confirming the rows contain real output. Record the controller log and experiment settings alongside them.

## 6. Metrics and interpretation

The receiver reports:
- **Throughput:** unique UDP traffic bytes received, divided by the configured 30-second send window.
- **Packet loss:** sent sequence count from the sender's end marker minus unique sequence numbers received.
- **End-marker status:** `end_marker_received` must be `true` for receiver-computed loss to be valid. If false, expected/lost/loss percentage are blank/null because the receiver cannot infer packets that may have been lost at the end of the stream. Compare sender totals with unique received counts or repeat the run.
- **Delay:** average and 95th-percentile one-way time difference between the sender and receiver clocks. Both processes run inside the same VM, so they share the system clock.

Use the same offered rates, packet sizes, link capacity, and run duration for both runs. Do not claim an improvement until the actual CSV results support it. The adaptive policy should direct UDP port 5001 to queue 1 and port 5002 to queue 2 only while the measured egress utilization is at least 70%; it returns to baseline below 50%.

## Troubleshooting

- **Controller does not start:** keep the complete POX traceback. Python 3.12 produced a compatibility warning during the smoke test.
- **Switch does not connect:** confirm the controller is still running on port 6633 and that Mininet uses OpenFlow 1.0.
- **Queue setup fails:** capture the complete error from the topology terminal and run sudo ovs-vsctl show after exiting Mininet.
- **A port is already in use:** exit Mininet, stop the controller with Ctrl+C, then run sudo mn -c before starting again.


## 7. Team handoff for the next run

Suggested task split for Team 14:

- **Sridatta:** coordinate the integration, keep track of valid baseline/QoS evidence, and update the results analysis after the next run.
- **Samarth:** operate the VM for the next adaptive QoS trial; capture sender counts, receiver CSV, controller ACTIVE messages, and the OpenFlow flow dump.
- **Neha:** review the project explanation and docs against the submitted proposal, add the final demo checklist/limitations, and help each teammate rehearse the packet path and results.
- **All three:** review actual numbers together and agree who runs the live demo. These are proposed roles; coordinate with each other before the review.

Do not create or revise the slide deck until the project is complete and Sridatta confirms.

For the next adaptive trial, use unique `adaptive4` paths and keep the same traffic parameters as the latest baseline. Start the QoS controller in one VM terminal, start a fresh topology in a second terminal, and run the commands in Section 5 after substituting `adaptive4` for `adaptive`. While packets are flowing, run this at the Mininet prompt:

    sh ovs-ofctl -O OpenFlow10 dump-flows s1

Retain evidence that the policy became ACTIVE, port 5001 used enqueue queue 1, and port 5002 used enqueue queue 2. Retrieve receiver and sender logs with the `py print(hN.cmd(...))` pattern. A usable result requires both receiver end markers to be true and the sender totals to be saved.


## 8. Retest after adaptive4 missed both end markers

The previous adaptive4 trial verified the controller and queue mapping, but the receiver stopped before it got either sender's QEND marker. Its loss is unknown. The bulk sender produced 23,737 packets, far more than baseline5's 8,767, so do not compare adaptive4 directly with baseline5.

For a load-matched pair, repeat **both baseline and adaptive** with identical rates: high 1.5 Mbps and bulk 3.0 Mbps. Set receiver `--seconds 90 --measure-seconds 30`; keep senders at 30 seconds. The extra receiver time allows queued packets and repeated end markers to drain. Use unique files such as `baseline6.csv`, `high-baseline6.log`, `bulk-baseline6.log`, then `adaptive5.csv`, `high-adaptive5.log`, and `bulk-adaptive5.log`.

For the baseline, run only `forwarding.l2_learning`; verify the active UDP flows have normal `output:"s1-eth3"` actions. For the adaptive condition, run `qos_controller`; save its ACTIVE line and verify UDP 5001 uses queue 1 and UDP 5002 uses queue 2 while senders are active. In each condition, record sender totals and require both receiver rows to show `end_marker_received: true`. Compare actual packet counts before describing the pair as load matched. If a QEND marker is still missing, keep loss unknown and extend receiver time or repeat; do not infer loss from receiver counts alone.
