# Team 14 project guide and work log

**Project:** QoS Traffic Management System (Project 5)  
**Course / section:** Computer Networks, Section K  
**Repository:** https://github.com/shadowlink12621/cn-project-  
**Working branch:** main  
**Last updated:** 2026-10-10

This is the team's shared reference for the project goal, what each person needs to do, how to work in GitHub, what has been tried, and the next action. Add a dated note here after each meaningful setup, implementation, experiment, or presentation milestone. Keep errors and the fix that worked so the next teammate does not repeat the same debugging.

## 1. What we are building

The project follows the understanding-and-approach email sent to the professor:

1. Generate two UDP traffic classes from separate Mininet hosts.
2. Identify the classes by UDP destination port:
   - High-priority, real-time-like packets: destination port 5001.
   - Low-priority bulk packets: destination port 5002.
3. Send both flows through one OpenFlow switch to a receiver host.
4. Limit the receiver-facing switch port to 5 Mbps to create repeatable congestion.
5. Have an SDN controller poll switch port statistics. When utilization reaches 70%, it directs the two UDP classes to separate Open vSwitch queues. When utilization falls below 50%, it returns to normal forwarding.
6. Compare baseline and adaptive runs using received throughput, sequence-based packet loss, average delay, and 95th-percentile delay.

The controller detects congestion and changes the forwarding action. Open vSwitch queues do the scheduling. Queue settings alone do not prove a bandwidth guarantee; state claims according to the measurements.

## 2. Team responsibilities

Agree together on the final assignment. A useful initial split is:

- **Topology and VM lead:** keep Mininet/Open vSwitch working, run the topology, record switch and queue configuration, and capture screenshots.
- **Traffic and measurement lead:** run sender/receiver programs, save CSV outputs, check that the offered load and run duration match across conditions, and summarize metrics.
- **Controller and integration lead:** run/debug the POX controller, verify policy activation and queue selection, and merge each working component into the shared repository.
- **Everyone:** understand the overall packet path and be ready to explain the controller threshold, queue IDs, measurements, and limitations in the review.

The initial code is in the repository; these roles are suggestions, not assignments already made to named members.

## 3. Current project files

- **src/traffic.py** — sends high or bulk UDP traffic and receives both classes with sequence numbers and timestamps; can write a CSV summary.
- **src/mininet_topology.py** — creates h1 and h2 senders, h3 receiver, switch s1, and 5 Mbps HTB queues on s1-eth3.
- **src/qos_controller.py** — POX learning switch; samples port 3 counters and selects queue 1 or 2 while the congestion policy is active.
- **docs/SETUP_AND_EXPERIMENT.md** — detailed VM commands for baseline and adaptive experiments.
- **README.md** — project overview and current status.
- **.gitignore** — ignores Python cache, virtual environment, and log files.

Code has been added to GitHub but the custom topology/controller/traffic flow still needs to be run in the VM. Do not present it as validated until that run succeeds.

## 4. Environment and repository

### VM status confirmed on 2026-10-10

- Ubuntu VM is named VirtualBox in the terminal.
- Open vSwitch: 3.3.9; service enabled and active.
- Mininet: 2.3.0. The command is **mn**, not mininet.
- POX: version 0.7.0 (gar), cloned at ~/pox.
- POX printed a warning that it documents Python 3.6–3.9, while the VM runs Python 3.12.
- Despite that warning, POX started, the Mininet switch connected, and the basic two-host ping test reported 0% dropped.
- This confirms the basic controller connection only. The custom QoS application and queues have not yet been validated.

### Repository facts

- The GitHub repository is public and currently uses branch main.
- The VM checkout is nested at ~/cn-project-/cn-project- because the empty repo was cloned from inside a folder of the same name.
- The public repository can be cloned or pulled without authentication.
- A local commit can be created without signing in. Pushing from the VM to GitHub requires GitHub authentication. Do not put a password or token in this file, the repository, or this chat.
- The connected GitHub integration can make repository commits without VM shell access. It cannot operate the VirtualBox terminal; a teammate must run and report VM commands.

## 5. Git workflow: one commit per completed step

Before starting a step, update the VM checkout:

    cd ~/cn-project-/cn-project-
    git pull origin main
    git status

After one coherent task is done, save it as a small commit:

    git add <files-for-this-step>
    git commit -m "feat: describe the completed step"
    git status

Use clear commit messages, for example:

- docs: add VM setup guide
- feat: add UDP traffic measurement
- feat: add congestion-triggered QoS rules
- fix: correct controller queue selection
- results: record baseline and adaptive measurements
- docs: add verified demo steps

A commit records the change locally. To publish a VM-made commit:

    git push origin main

If push asks you to log in, use GitHub CLI browser login or an SSH key. Never use your GitHub account password as the Git password. If you are not ready to set up VM authentication, share the error and we can use the connected GitHub integration for repository changes.

Before each teammate begins editing, pull the latest main branch. For independent work, use a short-lived branch and open a pull request rather than overwriting another person's changes. Do not commit secrets, VM passwords, access tokens, or large VM images.

## 6. Exact next step

The custom controller has now started, the switch connected, queue setup completed, and pingall passed. The next milestone is to run the adaptive UDP traffic and confirm policy activation and receiver measurements.

1. Keep the existing POX process only if it is still needed for reference. Stop it with Ctrl+C before starting another controller on port 6633.
2. In controller terminal 1:

       cd ~/cn-project-/cn-project-
       git pull origin main
       PYTHONPATH="$PWD/src" python3 ~/pox/pox.py qos_controller

   Leave it running. A Python 3.12 warning is known; if the application throws a traceback, save the full error rather than installing packages at random.
3. In topology terminal 2:

       cd ~/cn-project-/cn-project-
       sudo mn -c
       sudo python3 src/mininet_topology.py

   The topology script creates the queues and opens the Mininet CLI. Run pingall first. It should show 0% dropped.
4. If pingall succeeds, run one adaptive measurement from the Mininet prompt:

       h3 python3 /home/link/cn-project-/cn-project-/src/traffic.py receive --seconds 35 --measure-seconds 30 --csv /tmp/adaptive.csv > /tmp/adaptive-receiver.log 2>&1 &
       h1 python3 /home/link/cn-project-/cn-project-/src/traffic.py send --traffic-class high --seconds 30 --rate-mbps 1.5 &
       h2 python3 /home/link/cn-project-/cn-project-/src/traffic.py send --traffic-class bulk --seconds 30 --rate-mbps 8 &

   Wait about 36 seconds, then inspect:

       h3 cat /tmp/adaptive-receiver.log
       h3 cat /tmp/adaptive.csv

   In controller terminal 1, look for congestion detection and the policy becoming ACTIVE. If anything fails, stop at that step and report the exact terminal output.

5. Record the outcome in the work log below. Only after the adaptive run works, do a baseline run with the standard POX learning switch and identical traffic settings. Save both genuine CSV files and compare them.

The full procedure and measurement definitions are in **docs/SETUP_AND_EXPERIMENT.md**. Commands above use the VM username and repository path currently shown in the team's terminal; revise them if that path changes.

## 7. Error and recovery log

Add new entries at the top with date, exact symptom, cause if known, action taken, result, and next step. Keep the original error text concise but specific.

### 2026-10-10 — POX reports a Python-version warning

- **Symptom:** POX 0.7.0 says it requires Python 3.6, 3.7, 3.8, or 3.9; the VM runs Python 3.12.
- **Action/result:** POX still started, the switch connected, and Mininet pingall passed in the basic smoke test.
- **Status:** Warning remains. Custom controller not verified. If it fails, keep the full traceback and switch to a supported controller/runtime plan before changing VM packages.

### 2026-10-10 — Mininet command name looked missing

- **Symptom:** mininet --version returned command not found.
- **Cause/fix:** the command-line executable is mn. mn --version returned 2.3.0, and sudo mn --test pingall created a topology successfully.
- **Status:** Resolved.

### 2026-10-10 — Mininet did not find a default OpenFlow controller

- **Symptom:** Mininet printed “No default OpenFlow controller found” and “Falling back to OVS Bridge.”
- **Meaning/fix:** the first ping test did not prove a controller was active. Starting POX with forwarding.l2_learning and specifying the remote controller let the switch connect; pingall then reported 0% dropped.
- **Status:** Basic controller connection verified; dynamic QoS remains to be verified.

### 2026-10-10 — GitHub clone asked for an account password

- **Symptom:** GitHub rejected the password with “Password authentication is not supported for Git operations.”
- **Meaning/fix:** public clone/pull does not need credentials; GitHub password cannot be used as a Git password. Push requires a token, SSH key, or GitHub CLI authentication.
- **Status:** Public repository cloned and README pulled successfully. VM push authentication is not configured.

### 2026-10-10 — APT reported a 404 for libunbound8

- **Symptom:** apt install mininet hit a 404 for an Ubuntu noble-updates package; attempting to install package vswitch returned “Unable to locate package.”
- **Fix/clarification:** refresh package indexes with sudo apt update; Open vSwitch package name is openvswitch-switch. The later VM checks confirmed Open vSwitch and Mininet are installed.
- **Status:** Resolved.

### 2026-10-10 — Initial clone was nested

- **Symptom:** the repo was cloned while already inside a directory named cn-project-.
- **Result:** the actual Git checkout is in ~/cn-project-/cn-project-.
- **Status:** Working. Continue using that inner path; do not clone again.

## 8. Experiment record

Do not fill in results from estimates. Copy each actual CSV and fill out settings.

| Run | Controller | Policy | Capacity | High offered rate | Bulk offered rate | Result file | Notes |
|---|---|---|---:|---:|---:|---|---|
| Baseline | Standard POX learning switch | No adaptive queue selection | 5 Mbps | 1.5 Mbps | 8 Mbps | Pending | Not run |
| Adaptive | Team QoS controller | Threshold-triggered queues | 5 Mbps | 1.5 Mbps | 8 Mbps | Pending | Not run |

## 9. Presentation and review checklist

When the implementation and measurements are real, prepare slides covering:

1. Problem statement and team/project identification.
2. Topology and packet path.
3. How UDP ports identify the two traffic classes.
4. How the controller calculates port utilization and applies/removes the policy.
5. What the OVS queue IDs and rates mean.
6. Baseline versus adaptive throughput, packet loss, and delay results.
7. Fairness interpretation, limitations, and what the team learned.
8. Live demonstration commands and a backup screenshot/video capture.

Every team member should be able to explain why UDP needs application-level sequence numbers for measuring loss, why congestion must be controlled/repeatable, and why the controller chooses queues while the switch enforces them.


### 2026-10-10 — Custom controller and topology integration passed

- **Action:** Pulled the project files, launched the custom qos_controller component, started the three-host topology, configured the 5 Mbps receiver-facing queue, and ran pingall.
- **Observed:** Controller loaded and reported switch 1 connected. The topology script reported queue 1 as high and queue 2 as bulk. Pingall reported 0% dropped (6/6 received).
- **Status:** Controller startup, switch connection, topology creation, queue setup command, and basic reachability are verified. UDP traffic, congestion detection, queue action, and measurements remain unverified.
- **Next:** Run the adaptive traffic commands at the Mininet prompt, then record controller policy logs and receiver CSV output.


### 2026-10-10 — First UDP run completed, but adaptive QoS was not demonstrated

- **Observed receiver CSV:** high class: 8,572 expected/received, 0% reported loss, 1.1704 Mbps, 93.0208 ms mean delay, 385.7701 ms p95 delay. Bulk: 7,354 expected, 4,180 received, 43.16% reported loss, 1.3376 Mbps, 1,027.9569 ms mean delay, 4,975.6929 ms p95 delay.
- **Sender summaries:** high sent 10,987 packets at 1.5 Mbps for 30 seconds; bulk sent 9,567 packets at 8 Mbps for 30 seconds. These sender counts do not agree with the receiver's expected-packet fields, so do not treat the loss percentages as final yet.
- **Controller evidence:** the supplied controller log ends with “Congestion policy INACTIVE at 21.3% utilization” and contains no captured ACTIVE line. The controller did not demonstrate activation in the supplied log. Also, receipt of traffic in separate queues is not confirmed. Do not claim these are before/after or QoS-caused results.
- **POX error:** repeated PacketIn exceptions end in `AttributeError: type object 'ipv4' has no attribute 'ipv4'` while POX parses an ICMP Destination Unreachable packet. This appears separate from UDP data parsing; its trigger still needs confirmation. The first command attempt produced concatenated-shell errors, so stray traffic or a sender racing ahead of receiver startup may have triggered an unreachable response.
- **Command-line correction:** inside Mininet, the plain `h3 cat ...` commands were interpreted incorrectly in this pasted session. The `py h3.cmd(...)` form worked. Start receiver first, wait a couple of seconds, then start senders; retrieve logs with `py print(h3.cmd(...))`.
- **Next:** repeat one clean adaptive run after `sudo mn -c`, confirm no old traffic processes, start the controller and topology, start the receiver, wait 2 seconds, then start both senders. Capture the complete controller output from startup through the end of the run, receiver CSV, and sender summaries. If no ACTIVE message appears and utilization stays below threshold, check actual interface counters and queue configuration before changing thresholds. Then perform an identical no-policy baseline run. Keep this first result labeled “diagnostic / inconclusive.”
