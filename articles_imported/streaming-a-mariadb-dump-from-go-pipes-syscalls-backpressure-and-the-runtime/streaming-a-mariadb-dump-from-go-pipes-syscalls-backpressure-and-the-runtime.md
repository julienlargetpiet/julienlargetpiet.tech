We start from a very simple handler:
spawn `mysqldump`, capture its stdout, and stream it directly to the browser.
No intermediate file. No full buffering in memory.

```go


func (s *Server) handleDumpDb(w http.ResponseWriter, r *http.Request) {
    cmd := exec.Command("mysqldump", "-u", "root", "go_blog")

    stdout, err := cmd.StdoutPipe()
    if err != nil {
        http.Error(w, "pipe error", 500)
        return
    }

    if err := cmd.Start(); err != nil {
        http.Error(w, "start error", 500)
        return
    }

    w.Header().Set("Content-Type", "application/sql")
    w.Header().Set("Content-Disposition", `attachment; filename="dump.sql"`)

    io.Copy(w, stdout)

    cmd.Wait()
}

```

What looks like “just stream stdout” is in fact a multi-layered systems pipeline involving:

- Kernel pipes
- File descriptors
- Syscalls
- Scheduler decisions
- TCP flow control
- Go runtime goroutine scheduling

Let’s dissect this deeply.

---

## 1\. What `StdoutPipe()` Actually Does (Kernel-Level)

When you call:

```go


stdout, _ := cmd.StdoutPipe()

```

Go performs something conceptually equivalent to the Unix `pipe()` syscall:

```
int pipefd[2];
pipe(pipefd);

```

This creates:

```

pipefd[1] → write end
pipefd[0] → read end

```

The kernel allocates a FIFO buffer (often ~64KB, sometimes dynamically sized).

Then Go:

- Assigns the write end to the child process’s file descriptor 1 (stdout)
- Returns the read end to your Go code as `stdout`

So after `cmd.Start()`:

```

mysqldump (fd=1) → pipe write end → [ kernel pipe buffer ] → pipe read end → Go

```

Important: this is not a memory region containing the whole dump.
It is a bounded kernel-managed streaming buffer.

---

## 2\. Syscalls and Blocking Semantics

When `mysqldump` writes:

```
write(1, buffer, n);
```

The kernel checks:

```

if (pipe has free space)
    copy data into pipe buffer
else
    block thread until space available

```

Blocking means:

- The thread transitions from **Running** to **Sleeping**
- The scheduler removes it from the run queue
- It consumes zero CPU
- It resumes when buffer space is freed

There is no special “block message”. The syscall simply does not return until the condition is satisfied.

---

## 3\. io.Copy and the Write Side

`io.Copy(w, stdout)` is conceptually:

```

loop:
    n = read(pipe)
    write(socket, n bytes)

```

The `stdout` variable implements `io.Reader`.
The `w` implements `io.Writer`.

But `w` is not just a buffer.
It ultimately writes to:

```
TCP socket → kernel send buffer → NIC → network
```

If the TCP send buffer fills, the write syscall behaves similarly:

```

if (socket buffer has space)
    copy data
else
    block or return EAGAIN (non-blocking mode)

```

---

## 4\. Backpressure Propagation Across the Entire Chain

The full pipeline:

```

mysqldump
    ↓
pipe buffer
    ↓
io.Copy
    ↓
TCP send buffer
    ↓
network
    ↓
browser

```

Suppose the browser is slow.

- TCP send buffer fills
- Go cannot write to socket
- Go stops draining pipe
- Pipe fills
- mysqldump blocks

No component knows the global throughput.
Each component only knows:

> Can I push more bytes right now?

This is emergent flow control via local blocking.

---

## 5\. Scheduler and Context Switching

When a syscall blocks:

- Thread state changes (Running → Sleeping)
- Scheduler runs
- Another runnable thread may execute

If another process or thread runs:

- CPU registers are saved
- New registers are loaded
- Instruction pointer changes

This is a context switch.

Costs include:

- Pipeline flush (due to privilege switch or interrupt)
- Possible cache eviction
- TLB effects (if switching address spaces)

However:

- Network latency dominates syscall overhead
- Blocking is far cheaper than busy-waiting

---

## 6\. CPU Pipeline and Cache Effects

When execution switches:

- CPU speculative execution state is invalidated
- Branch predictor state may adapt
- L1/L2 caches may no longer contain previous working set

If the thread resumes quickly, cache locality is often preserved.
If it resumes after heavy scheduling activity, data may need to be reloaded.

But again: in IO-bound systems, this is negligible compared to network delays.

---

## 7\. Go Runtime: Goroutines, M–P–G Model

Go does not map one goroutine to one OS thread.
It uses:

- G = goroutine
- P = logical processor
- M = OS thread

For network IO:

- Go uses non-blocking syscalls
- Registers interest in epoll/kqueue
- Parks the goroutine
- Runs another goroutine immediately

Thus:

- Often avoids OS thread blocking
- User-space goroutine switch is cheaper than kernel thread switch

For pipe reads (like `StdoutPipe`):

- May block an OS thread
- Go may spawn additional threads to compensate

The runtime ensures system liveness.

---

## 8\. Failure Modes

If client disconnects:

- Socket write fails
- `io.Copy` returns error
- Process may receive SIGPIPE

If mysqldump crashes:

- `cmd.Wait()` returns non-zero
- stderr can be captured

Streaming systems must handle partial completion gracefully.

---

## 9\. Why This Architecture Is Beautiful

This design leverages:

- Unix file descriptor abstraction
- Kernel-managed bounded buffers
- TCP congestion control
- Go’s minimal `io.Reader`/ `io.Writer` abstraction
- Cheap goroutine scheduling

No global coordinator.
No custom rate limiter.
No explicit throughput calculation.

Local blocking produces global equilibrium.

---

## Conclusion

A simple admin dump endpoint exposes:

- Kernel pipe semantics
- Syscall blocking behavior
- Scheduler mechanics
- TCP backpressure
- Go runtime concurrency model

Once you internalize that everything is just a stream of bytes flowing through bounded buffers,
you begin to see systems design not as isolated layers,
but as a continuous pressure-balanced pipeline.

And that is the real lesson behind streaming a database dump.