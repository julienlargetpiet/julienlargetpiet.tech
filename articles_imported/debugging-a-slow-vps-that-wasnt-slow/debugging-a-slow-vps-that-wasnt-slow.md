My VPS suddenly felt _extremely slow_:

- pages taking 3–5 seconds
- TLS handshake hanging
- random spikes in latency

First instinct: server issue.

Reality: network path instability.

This is how I debugged it step by step.

---

## 1\. Measure Real User Experience with `curl`

Instead of guessing, start with actual HTTP timing.

```bash


curl -o /dev/null -s -w "\
DNS: %{time_namelookup}s\n\
Connect: %{time_connect}s\n\
TLS: %{time_appconnect}s\n\
TTFB: %{time_starttransfer}s\n\
Total: %{time_total}s\n" \
https://your-domain.com


```

### What each metric means

- **DNS ( `time_namelookup`)**
  → time to resolve domain → IP

- **Connect ( `time_connect`)**
  → TCP handshake (network latency baseline)

- **TLS ( `time_appconnect`)**
  → SSL/TLS negotiation (very sensitive to packet loss)

- **TTFB ( `time_starttransfer`)**
  → time until first byte from server

- **Total ( `time_total`)**
  → full request time


### Example (bad case)

```text


DNS: 0.05s
Connect: 0.30s
TLS: 2.29s
TTFB: 3.10s
Total: 5.01s


```

This is NOT normal.

---

## 2\. Isolate Network vs Server

Force IPv4 (avoid dual-stack ambiguity):

```bash


curl -4 -o /dev/null -s -w "Connect:%{time_connect}s TLS:%{time_appconnect}s TTFB:%{time_starttransfer}s Total:%{time_total}s\n" https://your-domain.com


```

If this is stable, the issue is not your backend.

---

## 3\. Check Your Server Internally

From inside the VPS:

```bash


curl -o /dev/null -s -w "TTFB: %{time_starttransfer}s\nTotal: %{time_total}s\n" http://localhost


```

If this is ~1ms:

→ your app is NOT the problem.

---

## 4\. Measure Raw Network Latency with `ping`

```bash


ping -c 100 your-server-ip


```

Look for:

- packet loss %
- average latency
- jitter (min/max spread)

### Example (bad)

```text


13% packet loss


```

Even 1–2% can hurt.

10%+ will destroy performance.

---

## 5\. Understand the Path with `traceroute`

Before using MTR, a quick traceroute gives you a snapshot of the route.

```bash


traceroute -n your-server-ip


```

### Why `-n` matters

- Skips DNS resolution
- Faster
- Cleaner output
- Avoids misleading delays caused by reverse DNS

---

### What traceroute shows

Each line = one hop (router)

Example:

```text


1  192.168.1.1
2  80.10.x.x
3  orange.net
4  cogentco.com
5  ...


```

---

### Important notes

- `---` = router not replying (NOT necessarily packet loss)
- Latency jumps = geographic distance or congestion
- Paths can be asymmetric (forward ≠ return path)

---

### Example insight

In my case:

```text


Paris → Cogent → Washington → Atlanta → Texas → Phoenix


```

→ My VPS was in the US, not Europe.

## 6\. Trace the Network Path with `mtr`

```bash


mtr -4 -rw your-server-ip


```

### Important flags

- `-4` → force IPv4
- `-r` → report mode (no interactive UI)
- `-w` → wide output (no truncation)
- `-c 100` → number of packets (recommended for accuracy)

Example:

```bash


mtr -4 -rw -c 100 your-server-ip


```

---

### How to read MTR

Each row = one hop (router)

Columns:

- **Loss%** → packet loss at that hop
- **Avg** → average latency
- **Best/Wrst** → jitter range

---

### Critical rule

> Intermediate hop loss often lies.

Routers may:

- rate-limit ICMP
- ignore probes

#### What matters:

- **Final hop loss**
- **End-to-end ping results**

---

### Example (real issue)

```text


Final hop: 4% loss
Avg: 204ms
Best: 146ms
Worst: 236ms


```

This means:

- real packet loss
- high jitter
- unstable path

---

## 7\. Understand the Root Cause

In my case:

- VPS was in the US
- I was in Europe
- traffic path:

```text


France → Cogent → US backbone → Phoenix → VPS


```

Issues observed:

- packet loss spikes (0% → 20% → 0%)
- unstable routing
- TLS delays (because retransmissions)

---

## 8\. Why TLS Explodes Under Packet Loss

TLS requires multiple round trips.

With packet loss:

- packets are retransmitted
- handshake stalls
- latency multiplies

That’s why:

```text


Ping: 250ms
→ feels like seconds in real requests


```

---

## 9\. Final Outcome

After some time:

- packet loss dropped to 0%
- curl stabilized:

```text


Connect: 0.15s
TLS: 0.30s
TTFB: 0.45s
Total: 0.60s


```

Conclusion:

→ transient network congestion / routing issue

---

## 10\. Key Takeaways

- Always measure before guessing
- Separate:
  - server performance
  - network latency
  - packet loss
- Use:
  - `curl` → user experience
  - `ping` → packet loss
  - `mtr` → path analysis
- Packet loss hurts more than latency
- Geography still matters

---

## 11\. One-Liner Summary

> My VPS wasn’t slow. The Internet path to it was.