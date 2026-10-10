# QoS Traffic Management System

**Course:** Computer Networks — SDN Socket Programming  
**Section:** K  
**Team:** 14  
**Project:** 5 — QoS Traffic Management System  
**Protocol:** UDP

## Team

- Neha Maravalli — PES2UG25CS721
- Sridatta Bharadhwaj M — PES2UG25CS700
- Samarth Shivashimpar — PES2UG26CS818

## Project objective

Build a UDP application that generates multiple traffic classes and uses an SDN controller to change how selected flows are treated when a Mininet link becomes congested. Compare the two classes before and after the policy is applied using measured throughput, delay, and packet loss.

This repository is the implementation workspace for the approach submitted to the professor. The implementation and measurements will be added as they are built and run. Results must come from actual VM runs; no performance numbers are assumed here.

## Planned demo

1. Create a Mininet topology with two traffic senders, one receiver, and one OpenFlow switch.
2. Constrain the receiver-facing link to create repeatable congestion.
3. Generate two UDP flows identified by distinct destination ports:
   - High-priority: smaller, periodic real-time-like packets.
   - Low-priority: sustained bulk traffic.
4. Have the SDN controller monitor switch traffic and detect when utilization crosses a configured threshold.
5. Apply queue-aware flow rules during congestion, then restore the normal policy when congestion clears.
6. Run the same traffic scenario with the policy disabled and enabled; compare throughput, receiver-side delay, and packet loss.

The switch queues perform the traffic scheduling/rate treatment. The controller detects the condition and installs or changes the flow rules that select the queues. Any bandwidth guarantee or fairness conclusion must be supported by the configured queue parameters and measured results.

## Planned repository layout

```text
.
├── README.md
├── .gitignore
├── src/
│   ├── traffic_sender.py
│   ├── traffic_receiver.py
│   ├── mininet_topology.py
│   └── qos_controller.py
├── scripts/
│   ├── setup_ovs_queues.sh
│   └── run_experiment.sh
├── results/
│   └── README.md
└── docs/
    ├── setup.md
    ├── experiment-method.md
    └── presentation-outline.md
```

Files will be added as the design is implemented and verified in the team VM. Planned names may change to match the final code.

## Implementation checklist

- [ ] Confirm Mininet and Open vSwitch work in the Ubuntu VM.
- [ ] Agree on topology, UDP ports, packet sizes, send rates, link capacity, and congestion threshold.
- [ ] Implement UDP sender and receiver with sequence numbers and timestamps.
- [ ] Implement a repeatable Mininet topology and controlled bottleneck.
- [ ] Configure Open vSwitch queues and confirm traffic can be directed to them.
- [ ] Implement controller statistics polling and congestion-triggered policy changes.
- [ ] Capture baseline and policy-enabled runs under the same conditions.
- [ ] Calculate and document throughput, delay, packet loss, and fairness observations.
- [ ] Write exact setup/run/troubleshooting steps and capture genuine screenshots or terminal output.
- [ ] Build the final presentation from the verified implementation and results.

## Measurement plan

For each traffic class and each run, retain the experiment settings and report:

- Throughput at the receiver (bits/s).
- Packet loss, calculated from transmitted and received sequence numbers.
- Receiver-side delay from packet timestamps (use a clear, consistent clock method).
- Whether the controller detected congestion and when the policy changed.

Compare baseline and policy-enabled runs with identical offered traffic and link capacity. Repeat runs where time permits and report the actual results and limitations.

## Current status

Project workspace initialized. The implementation, VM verification, experiment outputs, and final presentation are not yet added.
