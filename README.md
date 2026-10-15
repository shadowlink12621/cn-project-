<div align="center">

# 🚦 QoS Traffic Management System

### Dynamic UDP flow prioritization with SDN

[![Course](https://img.shields.io/badge/Course-Computer%20Networks-17365D?style=for-the-badge)](#)
[![Section](https://img.shields.io/badge/Section-K-007C83?style=for-the-badge)](#)
[![Team](https://img.shields.io/badge/Team-14-E07A35?style=for-the-badge)](#)
[![Protocol](https://img.shields.io/badge/Traffic-UDP-6A4C93?style=for-the-badge)](#)

**Project 5 · SDN Socket Programming**

[🚀 Start here](#-quick-start) · [🧠 How it works](#-how-it-works) · [📈 Results](#-experiment-results) · [🛠 Troubleshooting](#-troubleshooting)

</div>

---

## 👥 Team 14

| Member | Student ID |
|---|---|
| Neha Maravalli | PES2UG25CS721 |
| Sridatta Bharadhwaj M | PES2UG25CS700 |
| Samarth Shivashimpar | PES2UG26CS818 |

## 🎯 What are we building?

A small virtual network sends two kinds of UDP traffic through a bandwidth-limited switch:

- 🟢 **High priority** — VoIP-like packets where delay matters
- 🟠 **Bulk traffic** — background transfer that can tolerate slower service

A **POX SDN controller** watches switch-port counters. When utilization crosses a threshold, it directs the two UDP classes into separate Open vSwitch queues. The switch applies the queue scheduling.

> [!NOTE]
> The controller chooses the queue; Open vSwitch schedules packets. A queue assignment by itself is not proof of a guaranteed bandwidth. We report measured behavior and configured queue limits separately.

## 📚 Contents

- [How it works](#-how-it-works)
- [Network layout](#-network-layout)
- [Quick start](#-quick-start)
- [Run experiments](#-run-experiments)
- [Experiment results](#-experiment-results)
- [Repository map](#-repository-map)
- [Troubleshooting](#-troubleshooting)
- [Team workflow](#-team-workflow)

## 🧠 How it works

1. **Generate:** Python UDP senders create high and bulk traffic.
2. **Measure:** The receiver records sequence numbers and send timestamps. It reports loss only when it receives the sender's end marker; otherwise loss is unknown.
3. **Monitor:** POX polls the receiver-facing OVS port every 2 seconds.
4. **React:** At **≥70% utilization**, the controller activates queue actions. It clears the policy below **50%**.
5. **Compare:** CSV output reports throughput, packet loss, mean delay, and p95 delay.

The gap between the 70% and 50% thresholds is hysteresis; it helps avoid rapid switching near one threshold.

## 🗺 Network layout

```mermaid
flowchart LR
    H1["🟢 h1 · high UDP · port 5001"] -->|s1-eth1| S["Open vSwitch s1"]
    H2["🟠 h2 · bulk UDP · port 5002"] -->|s1-eth2| S
    S -->|"s1-eth3 · 5 Mbps · queue 1 / 2"| H3["📥 h3 · receiver"]
    P["POX controller"] <-->|"OpenFlow 1.0 · port 6633"| S
```

## 🚀 Quick start

> Run these commands **inside the Ubuntu VM**. Open separate terminal windows for the controller and Mininet.

<details open>
<summary><strong>1 · Start the SDN controller</strong></summary>

```bash
cd ~/cn-project-/cn-project-
# Ensure port 6633 is free before launching the controller.
PYTHONPATH="$PWD/src" python3 ~/pox/pox.py qos_controller
```

Leave this terminal open. A successful start logs **“QoS controller ready”**; when Mininet connects, it logs **“Switch 1 connected”**.

</details>

<details>
<summary><strong>2 · Start the Mininet topology</strong></summary>

In a second VM terminal:

```bash
cd ~/cn-project-/cn-project-
sudo mn -c
sudo python3 src/mininet_topology.py
```

At the `mininet>` prompt, check reachability:

```text
pingall
```

</details>

## 📈 Run experiments

At the `mininet>` prompt, run one command at a time. The Python prompt `py` lets you run a command on a selected Mininet host; shell commands entered directly at the prompt can be misread as Mininet commands.

<details>
<summary><strong>Collect a run (receiver, then senders)</strong></summary>

Start the receiver and wait two seconds:

```text
py h3.cmd("python3 /home/link/cn-project-/cn-project-/src/traffic.py receive --seconds 35 --measure-seconds 30 --csv /tmp/qos-run.csv > /tmp/qos-receiver.log 2>&1 &")
py __import__('time').sleep(2)
```

Start both senders:

```text
py h1.cmd("python3 /home/link/cn-project-/cn-project-/src/traffic.py send --traffic-class high --seconds 30 --rate-mbps 1.5 >/tmp/high-run.log 2>&1 &")
py h2.cmd("python3 /home/link/cn-project-/cn-project-/src/traffic.py send --traffic-class bulk --seconds 30 --rate-mbps 8 >/tmp/bulk-run.log 2>&1 &")
```

After the run finishes, read the receiver results:

```text
py print(h3.cmd('cat /tmp/qos-run.log; cat /tmp/qos-run.csv'))
```

To verify queue selection while traffic is flowing:

```text
sh ovs-ofctl -O OpenFlow10 dump-flows s1
```

Look for UDP destination port **5001** with `enqueue:"s1-eth3":1`, and port **5002** with `enqueue:"s1-eth3":2`.

</details>

<details>
<summary><strong>Baseline vs QoS: important run labeling</strong></summary>

- **Baseline:** start the POX learning-switch component `forwarding.l2_learning`, not `qos_controller`; run the same topology and traffic rates.
- **QoS:** start `qos_controller`; the flow dump should show queue 1 / queue 2 actions during the run.
- Do not run two POX controllers on port **6633** at the same time.
- Use fresh CSV names for each trial. Record controller logs and actual sender packet counts. Check `end_marker_received`; when it is `false`, the receiver cannot know the missing tail, so use sender totals or repeat the run.
- Repeat at least three comparable trials per condition when possible.

> [!WARNING]
> The run saved as `baseline3.csv` showed QoS queue actions and is excluded from baseline averages. Baseline stress run 4 showed normal `output` actions, but the receiver missed end markers; its receiver-reported 0% loss is invalid. See `results/ANALYSIS.md` and `results/baseline4_reconciled.csv`.

</details>

## 📊 Experiment results

The detailed measurements and caveats are in **[`results/ANALYSIS.md`](results/ANALYSIS.md)**. CSV files are in the same folder.

A preliminary load-matched comparison showed lower high-priority delay and higher bulk delay under QoS. The sample is small and VM traffic rates varied, so treat it as a demonstration—not a final statistical claim. Stress runs showed higher bulk packet loss when demand exceeded available capacity.

> [!TIP]
> For a fair result, hold offered load and run duration constant, verify which controller is active, then compare repeated baseline and QoS trials.

## 🗂 Repository map

| Path | Purpose |
|---|---|
| `src/traffic.py` | UDP sender/receiver and CSV measurements |
| `src/mininet_topology.py` | Three-host Mininet and shaped OVS bottleneck |
| `src/qos_controller.py` | POX learning switch, port-stat polling, adaptive queue policy |
| `docs/SETUP_AND_EXPERIMENT.md` | Full setup, commands, and experiment procedure |
| `results/ANALYSIS.md` | Recorded results, interpretation, and limitations |
| `results/*.csv` | Per-run measurements |
| `TEAM_WORKLOG.md` | Shared progress, errors, tasks, and next steps |

## 🛠 Troubleshooting

<details>
<summary><strong>“Address already in use” on port 6633</strong></summary>

Find the process holding the controller port:

```bash
sudo ss -ltnp 'sport = :6633'
ps -p ACTUAL_PID -o pid,ppid,cmd
```

Replace `ACTUAL_PID` with the number shown by `ss`. If it is a stale POX process, stop only that process:

```bash
sudo kill -TERM ACTUAL_PID
```

Check that the port is clear, then start exactly one controller. Do not type angle-bracket placeholders such as `<PID>` into Bash; the shell interprets them as redirection syntax.

</details>

<details>
<summary><strong>Mininet says it cannot contact the controller</strong></summary>

1. Check that the controller terminal is still running and port 6633 is listening.
2. Start the topology only after the controller is ready.
3. Check the switch connection log.
4. Confirm both use OpenFlow 1.0 and the same address and port.

</details>

<details>
<summary><strong>Mininet prompt command errors</strong></summary>

- Use `py h1.cmd("...")` for commands on a Mininet host.
- Use `sh ...` for a shell command on the VM.
- Enter one Mininet command at a time. Avoid pasting prompt text such as `mininet>` with the command.

</details>

<details>
<summary><strong>POX Python version warning</strong></summary>

POX 0.7 may warn that Python 3.12 is outside its documented support range. The project has run in the current VM despite this warning. Do not change the system Python just to suppress the warning; record any observed controller errors and verify policy behavior from logs and the OpenFlow flow table.

</details>

## 🤝 Team workflow

- Commit each completed milestone with a clear message.
- Use issues or the worklog to claim tasks and record blockers.
- Pull the latest `main` before starting VM work.
- Keep raw CSV files and the exact command used for each run.
- Update **[`TEAM_WORKLOG.md`](TEAM_WORKLOG.md)** whenever setup, code, measurements, or errors change.

### ✅ Current milestone checklist

- [x] Mininet and Open vSwitch installed; base connectivity checked
- [x] UDP senders and receiver implemented
- [x] SDN congestion controller and queue actions observed
- [x] OVS flow table verified queue 1 / queue 2 mapping
- [x] Re-run baseline with end-marker validation and verify normal output actions
- [ ] Repeat the run with qos_controller; compare after checking actual packet counts
- [ ] Update final analysis from only correctly labeled runs
- [ ] Present and demonstrate the final results

---

<div align="center">

**Built by Team 14 · Section K · Computer Networks**

> [!IMPORTANT]
> **Current closeout step (15 Oct 2026):** run one final adaptive trial with `qos_controller`, save controller/flow/receiver/sender evidence, review the analysis as a team, and rehearse the demo. Implementation and queue behavior have already been observed; the final comparison remains preliminary until another correctly captured adaptive run is added. PPT work is on hold pending Sridatta's end-of-project confirmation.

</div>
