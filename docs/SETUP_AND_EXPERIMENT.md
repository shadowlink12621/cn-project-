# VM setup and experiment runbook

This runbook uses relative project paths, so it does not depend on a Linux username or a nested checkout name. The current topology uses a 2 Mbps receiver-facing port, with queue 1 configured for UDP port 5001 and queue 2 for UDP port 5002. Queue minimums are settings, not proof of a guaranteed bandwidth.

## 1. Install prerequisites on a fresh Ubuntu VM

If Mininet, Open vSwitch, Python 3, or Git is missing:

```bash
sudo apt update
sudo apt install -y git python3 mininet openvswitch-switch
sudo systemctl enable --now openvswitch-switch
```

If `apt` reports a 404, refresh package indexes with `sudo apt update` and retry the install.

Clone POX once if it is not already at `$HOME/pox`:

```bash
if [ ! -f "$HOME/pox/pox.py" ]; then
  git clone https://github.com/noxrepo/pox.git "$HOME/pox"
fi
```

The tested VM used Mininet 2.3.0, Open vSwitch 3.3.9, and POX 0.7.0. POX may warn that Python 3.12 is outside its documented range; do not change system Python just to hide the warning.

## 2. Clone the project

For a fresh clone, use this same folder on every VM:

```bash
git clone https://github.com/shadowlink12621/cn-project-.git "$HOME/cn-project-qos"
cd "$HOME/cn-project-qos"
git pull --ff-only origin main
```

For a repository already cloned to a different place, first change into that repository's top-level folder. Use that folder as the working directory in each terminal. All project and traffic script paths below are relative to it.

## 3. Start the custom POX controller

Open terminal 1. Start from the project root:

```bash
cd "$HOME/cn-project-qos"
PYTHONPATH="$PWD/src" python3 "$HOME/pox/pox.py" qos_controller
```

Keep the terminal open. Look for `QoS controller ready`, then `Switch 1 connected` after Mininet starts. During traffic, the controller may log `Congestion policy ACTIVE`.

If port 6633 is already in use, check the listener with:

```bash
sudo ss -ltnp 'sport = :6633'
```

Stop the correct old POX process with Ctrl+C in its terminal before starting another controller. Do not run two controllers on port 6633.

## 4. Start Mininet

Open terminal 2 in the same project root:

```bash
cd "$HOME/cn-project-qos"
sudo mn -c
sudo python3 "$PWD/src/mininet_topology.py"
```

The topology script sets the working folder of h1, h2, and h3 to the project root it finds from its own file location. This makes commands such as `python3 src/traffic.py` work even if the clone is not under a particular username or folder name.

At the `mininet>` prompt, check basic connectivity:

```text
pingall
```

All six host-to-host pings should succeed.

## 5. Run one traffic demonstration

Enter each line separately at `mininet>`. Start the receiver before the senders. The receiver runs for 90 seconds so it can collect the sender end markers after the 30-second senders finish.

```text
py h3.cmd("python3 src/traffic.py receive --seconds 90 --measure-seconds 30 --csv results/demo.csv > results/demo-receiver.log 2>&1 &")
py __import__('time').sleep(2)
py h1.cmd("python3 src/traffic.py send --traffic-class high --seconds 30 --rate-mbps 1.5 > results/demo-high.log 2>&1 &")
py h2.cmd("python3 src/traffic.py send --traffic-class bulk --seconds 30 --rate-mbps 8 > results/demo-bulk.log 2>&1 &")
py __import__('time').sleep(5)
sh ovs-ofctl -O OpenFlow10 dump-flows s1
```

While traffic is flowing, look for UDP `tp_dst=5001` with `enqueue` queue 1 and UDP `tp_dst=5002` with `enqueue` queue 2. The controller should also log `ACTIVE`. If the flow output remains `output:3`, queue selection was not verified in that run; report that accurately.

After the receiver's 90-second window has elapsed, read the results from the same Mininet prompt:

```text
py print(h3.cmd("cat results/demo-receiver.log; cat results/demo.csv"))
py print(h1.cmd("cat results/demo-high.log"))
py print(h2.cmd("cat results/demo-bulk.log"))
```

Only report receiver loss if that class has `end_marker_received: true`. The sender logs show the actual packet totals; an offered rate is only a request.

Exit Mininet with `exit`. Stop POX with Ctrl+C in terminal 1.

## 6. Baseline run

For a baseline, stop `qos_controller` with Ctrl+C and start POX's standard learning switch in terminal 1:

```bash
cd "$HOME/pox"
./pox.py forwarding.l2_learning
```

In terminal 2, restart Mininet using the steps above and run the same traffic commands with new result names such as `results/demo-baseline.csv`. During the baseline, the two UDP flows should use ordinary output actions rather than the queue 1/2 actions. Stop the learning switch before restarting `qos_controller`.

## 7. Troubleshooting

- **`mininet: command not found`:** install Mininet and Open vSwitch using section 1, then reopen the terminal.
- **Switch cannot connect:** confirm the controller is running first on port 6633, and that the topology uses OpenFlow 1.0.
- **File not found for `src/traffic.py`:** start the topology from the repository root and pull the latest `main`; the current topology sets Mininet hosts' working folders automatically.
- **A prompt says `Unknown command`:** enter one line at a time after `mininet>`; do not paste the prompt itself.
- **A CSV reports `end_marker_received: false`:** loss for that stream is unknown. Do not quote the receiver's loss percentage; repeat with a longer receiver window.

Older experiments in `results/` used a 5 Mbps cap. Keep them separate from the current 2 Mbps measurements.
