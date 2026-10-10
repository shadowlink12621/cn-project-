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

## Objective

Generate high-priority and bulk UDP flows, detect congestion using SDN switch port statistics, dynamically direct the flows to different Open vSwitch queues, and compare measured throughput, delay, and packet loss before and after the policy.

The controller detects congestion and selects queues; Open vSwitch performs queue scheduling. Claims about bandwidth guarantees or fairness must be supported by the actual queue settings and experiment results.

## Project files

- **src/traffic.py** — UDP sender and receiver with sequence numbers, timestamps, and CSV summaries.
- **src/mininet_topology.py** — two senders, one receiver, one OpenFlow switch, and a 5 Mbps HTB bottleneck with two queues.
- **src/qos_controller.py** — POX learning switch that monitors the receiver-facing switch port and activates queue selection above 70% utilization, returning to normal forwarding below 50%.
- **docs/SETUP_AND_EXPERIMENT.md** — step-by-step VM setup and baseline/adaptive experiment instructions.
- **TEAM_WORKLOG.md** — team context, responsibilities, Git commit workflow, VM state, troubleshooting log, next steps, and review checklist.
- **.gitignore** — ignores Python caches, local virtual environments, and logs.

## Current status

- [x] Mininet 2.3.0 and Open vSwitch 3.3.9 installed in the Ubuntu VM.
- [x] Basic Mininet topology and POX learning-switch connectivity verified.
- [x] Starter implementation and team runbook committed to the repository.
- [ ] Run the custom controller and queue topology in the VM.
- [ ] Capture genuine baseline and adaptive CSV results.
- [ ] Update the work log with verified outcomes and prepare the final presentation.

Start with **TEAM_WORKLOG.md** for the exact next action. Do not report performance results until both experiment runs have been collected from the VM.
