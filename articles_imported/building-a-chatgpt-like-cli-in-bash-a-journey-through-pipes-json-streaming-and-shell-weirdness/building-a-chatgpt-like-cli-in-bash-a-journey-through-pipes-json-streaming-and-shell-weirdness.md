There is something deeply satisfying about building a serious tool with primitive Unix bricks.

The mentioned in this article comes from:

- [repo](https://github.com/julienlargetpiet/CLIChatGPT)

A shell. A `while true`. A `read`. A `curl`. A `jq`. A pipe.

At first, the goal looks almost absurdly simple: "I want ChatGPT, but in my terminal, with Bash."

Then the real questions begin.

How do we keep a conversation alive if the API is stateless? How do we build valid JSON safely from user input? How do we stream tokens as they arrive? Why does `curl | while read ...` break variable updates? What exactly is this cursed construct: `done < <(curl ...)`? And what is Bash really doing when we write `IFS= read -r line`?

This article is the story of building a small but real OpenAI CLI chat client in Bash, and in the process, discovering a lot about shell I/O, process substitution, streaming, JSON transformation, and the difference between "works" and "feels right".

The final tool is this:

```bash


#!/usr/bin/env bash

set -Eeuo pipefail

MODEL="${MODEL:-gpt-4.1}"
API_URL="https://api.openai.com/v1/responses"
LOG_FILE="${LOG_FILE:-chat.log}"

########################################
# Utils
########################################

log() {
  printf "[%s] %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$1" >> "$LOG_FILE"
}

fatal() {
  echo "Fatal: $1" >&2
  log "FATAL: $1"
  exit 1
}

check_dependencies() {
  command -v curl >/dev/null || fatal "curl not installed"
  command -v jq >/dev/null || fatal "jq not installed"
}

cleanup() {
  echo
  echo "Exiting."
  log "Session ended."
  exit 0
}

trap cleanup SIGINT SIGTERM

########################################
# Init checks
########################################

check_dependencies

: "${OPENAI_API_KEY:?OPENAI_API_KEY not set}"

touch "$LOG_FILE" || fatal "Cannot write log file"

log "Session started with model=$MODEL"

HISTORY="[]"

echo "Production CLI Chat (type 'exit' to quit)"
echo "-----------------------------------------"

########################################
# Main loop
########################################

# Each API call is stateless, it means the LLM has no memory from what happened during the session
# so we have to build a session history and the payload will contain it for each call

while true; do
  echo -n "> "
  read -r USER_INPUT || cleanup

  [[ "$USER_INPUT" == "exit" ]] && cleanup
  [[ -z "$USER_INPUT" ]] && continue

  log "USER: $USER_INPUT"

  ########################################
  # Update history
  ########################################

  HISTORY=$(jq \
    --arg msg "$USER_INPUT" \
    '. + [{"role":"user","content":[{"type":"input_text","text":$msg}]}]' \
    <<< "$HISTORY"
  )

  ########################################
  # Build payload
  ########################################

  PAYLOAD=$(jq -n \
    --arg model "$MODEL" \
    --argjson input "$HISTORY" \
    '{model:$model,input:$input,stream:true}'
  )

  ########################################
  # Streaming call
  ########################################

  ASSISTANT_REPLY=""
  BUFFER=""

  # IFS is a SHELL variable in fact, read will get its value of line separator from it
  while IFS= read -r line; do
    [[ "$line" != data:* ]] && continue

    DATA="${line#data: }" # trim left line -> removes starting "data: "
    [[ "$DATA" == "[DONE]" ]] && break

    DELTA=$(jq -r '
      select(.type=="response.output_text.delta")
      | .delta // empty
    ' <<< "$DATA") # stdin from "$DATA"

    [[ -z "$DELTA" ]] && continue # if string is empty

    ASSISTANT_REPLY+="$DELTA"
    BUFFER+="$DELTA"

    # length of BUFFER >= 40 OR DELTA contains a breakline
    if [[ ${#BUFFER} -ge 40 || "$DELTA" == *$'\n'* ]]; then
      printf "%s" "$BUFFER"
      BUFFER=""
    fi

  done < <(
      curl -sS -N "$API_URL" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $OPENAI_API_KEY" \
      -d "$PAYLOAD"
  )

  # flush final if string is not empty
  if [[ -n "$BUFFER" ]]; then
    printf "%s" "$BUFFER"
  fi

  echo

  ########################################
  # Safety check
  ########################################

  if [[ -z "$ASSISTANT_REPLY" ]]; then
    log "Empty assistant response"
    echo "No response."
    continue
  fi

  log "ASSISTANT: $ASSISTANT_REPLY"

  ########################################
  # Append assistant to history
  ########################################

  HISTORY=$(jq \
    --arg msg "$ASSISTANT_REPLY" \
    '. + [{"role":"assistant","content":[{"type":"output_text","text":$msg}]}]' \
    <<< "$HISTORY"
  )

done


```

What follows is not just an explanation of the code, but the reasoning behind it.

---

## 1\. The architecture we want

Before writing code, we need a mental model.

We want a terminal application that behaves like a conversational assistant. That means:

- it prompts the user repeatedly
- it sends each message to the OpenAI API
- it displays the answer
- it keeps the previous conversation context
- it streams the answer progressively instead of waiting for the full response
- it exits cleanly
- it logs what happened

So the global loop looks like this:

```text


read user input
→ append it to history
→ build JSON payload
→ send request to API
→ stream answer as it arrives
→ append assistant reply to history
→ repeat


```

That sounds almost trivial, but each arrow hides interesting technical choices.

The hardest part conceptually is this: **the API is stateless.**

This is the key thing many people miss at first. The model does not "remember" the previous turn unless you send the previous turn again. Every API call is independent. The illusion of memory comes from the client continuously resending the conversation history.

That is why we keep a `HISTORY` variable.

---

## 2\. Starting strict: `set -Eeuo pipefail`

At the top of the script:

```bash


set -Eeuo pipefail


```

This is a classic "take Bash seriously" line. It changes the shell behavior to be more strict and fail earlier.

- `-e` means: exit on command failure.
- `-u` means: treat unset variables as errors.
- `-o pipefail` means: if a pipeline fails anywhere, the whole pipeline fails.
- `-E` makes trap/error behavior more consistent with functions and subshells.

This matters because shell scripts are otherwise very permissive. A typo in a variable name or a silent failure in a pipeline can produce nonsense behavior.

It is the difference between "quick hack" and "something you trust".

---

## 3\. Configuration variables

```bash


MODEL="${MODEL:-gpt-4.1}"
API_URL="https://api.openai.com/v1/responses"
LOG_FILE="${LOG_FILE:-chat.log}"


```

This is simple but elegant.

`MODEL="${MODEL:-gpt-4.1}"` means:

- if `MODEL` is already defined in the environment, use it
- otherwise default to `gpt-4.1`

Same idea for `LOG_FILE`.

This pattern is extremely useful in shell scripting because it lets you override behavior without editing the script.

Example:

```bash


MODEL="gpt-4.1-mini" bash chat.sh


```

or:

```bash


LOG_FILE="session1.log" bash chat.sh


```

---

## 4\. Utilities: logging, errors, cleanup

The utility functions define the "operating environment" of the CLI.

### Logging

```bash


log() {
  printf "[%s] %s\n" "$(date '+%Y-%m-%d %H:%M:%S')" "$1" >> "$LOG_FILE"
}


```

This function appends a timestamped line to the log file. A call like:

```bash


log "USER: hello"


```

writes something like:

```text


[2026-03-21 14:35:10] USER: hello


```

A few interesting things are happening here:

- `$1` is the first argument passed to the function.
- `$(date '+%Y-%m-%d %H:%M:%S')` is command substitution. Bash runs the `date` command and inserts its output into the `printf`.
- `>> "$LOG_FILE"` appends instead of overwriting.

This is one of those small pieces of code that look simple, but already show three different shell mechanisms at once: functions, command substitution, and redirection.

### Fatal errors

```bash


fatal() {
  echo "Fatal: $1" >&2
  log "FATAL: $1"
  exit 1
}


```

This prints to stderr, logs the event, and exits. `>&2` means "send to file descriptor 2", which is standard error.

### Dependency checks

```bash


check_dependencies() {
  command -v curl >/dev/null || fatal "curl not installed"
  command -v jq >/dev/null || fatal "jq not installed"
}


```

This checks whether `curl` and `jq` are available in the current environment.

### Cleanup and signal handling

```bash


cleanup() {
  echo
  echo "Exiting."
  log "Session ended."
  exit 0
}

trap cleanup SIGINT SIGTERM


```

This is how the script exits gracefully on Ctrl+C or termination. Without this, abrupt interruption would feel rough. With it, the session closes cleanly and gets logged.

---

## 5\. Initialization and environment validation

```bash


check_dependencies

: "${OPENAI_API_KEY:?OPENAI_API_KEY not set}"

touch "$LOG_FILE" || fatal "Cannot write log file"

log "Session started with model=$MODEL"

HISTORY="[]"


```

The line:

```bash


: "${OPENAI_API_KEY:?OPENAI_API_KEY not set}"


```

is a neat Bash idiom. It says: evaluate this variable, and if it is unset or empty, abort with this message. The `:` command itself does nothing; it is just a placeholder command that lets us exploit Bash parameter expansion.

Then we initialize:

```bash


HISTORY="[]"


```

This is the initial conversation state: an empty JSON array. That line is more important than it looks. It establishes that the conversation history is not a Bash array or some ad-hoc string format. It is explicitly a JSON array, because that is what we will feed into the API.

---

## 6\. The REPL: `while true; do ... read -r ...`

Now the real engine begins.

```bash


while true; do
  echo -n "> "
  read -r USER_INPUT || cleanup


```

This is a classic REPL structure: Read-Eval-Print Loop.

- `while true` means the loop never ends unless we explicitly break or exit.
- `echo -n "> "` prints a prompt without a trailing newline.
- `read -r USER_INPUT` reads one line from stdin into the variable `USER_INPUT`.

**Why `-r`?** Because without `-r`, `read` interprets backslashes as escape characters. In shell scripts that process raw text, that is usually not what you want. `-r` preserves backslashes literally.

Then:

```bash


[[ "$USER_INPUT" == "exit" ]] && cleanup
[[ -z "$USER_INPUT" ]] && continue


```

If the user types `exit`, we leave. If the input is empty, we skip this loop iteration. `-z` means "string length is zero".

---

## 7\. Why we keep `HISTORY`

This part is the conceptual heart of the script.

> Each API call is stateless, it means the LLM has no memory from what happened during the session, so we have to build a session history and the payload will contain it for each call.

If we only sent the latest user input every time, the model would answer each question as if it were a fresh standalone prompt. Conversation continuity only exists because we rebuild and resend the full history on each request.

---

## 8\. Updating JSON safely with `jq`

```bash


HISTORY=$(jq \
  --arg msg "$USER_INPUT" \
  '. + [{"role":"user","content":[{"type":"input_text","text":$msg}]}]' \
  <<< "$HISTORY"
)


```

**`jq` is a JSON transformer.** The right mental model is:

```text


input JSON → jq program → output JSON


```

We feed the current `HISTORY` into `jq`. Inside `jq`, `.` refers to that input JSON. So `. + [ ... ]` means: take the existing array and append a new element.

**Why `<<< "$HISTORY"`?** This is a here-string. It means: take the string stored in `HISTORY` and feed it as stdin to `jq`.

**Why `--arg msg "$USER_INPUT"`?** This creates a jq variable called `$msg`. It safely injects Bash data into JSON — if the user types quotes, newlines, or weird characters, `jq` handles escaping properly. Without `--arg`, you would eventually produce invalid JSON.

**Example:** if `HISTORY` is `[]` and `USER_INPUT` is `hello`, then after this `jq`, `HISTORY` becomes:

```json


[
  {
    "role": "user",
    "content": [
      {
        "type": "input_text",
        "text": "hello"
      }
    ]
  }
]


```

---

## 9\. Building the payload

```bash


PAYLOAD=$(jq -n \
  --arg model "$MODEL" \
  --argjson input "$HISTORY" \
  '{model:$model,input:$input,stream:true}'
)


```

**Why `-n`?** `jq -n` means: do not read input JSON from stdin; start from nothing and build JSON explicitly. That makes sense here, because we are not transforming an existing object — we are constructing a new request payload.

**Why `--argjson input "$HISTORY"`?** Because `HISTORY` is already JSON, not a plain string. If we used `--arg`, it would become a string containing JSON text, which would be wrong. `--argjson` tells `jq`: treat this as actual JSON.

The final payload looks roughly like this:

```json


{
  "model": "gpt-4.1",
  "input": [
    {
      "role": "user",
      "content": [
        {
          "type": "input_text",
          "text": "hello"
        }
      ]
    }
  ],
  "stream": true
}


```

---

## 10\. Why we switched to streaming

At first, it is tempting to use a normal blocking API call: send request, wait, print full answer. That works, but it feels bad.

A terminal chat tool should feel alive. It should start talking as soon as the first tokens arrive. Streaming improves three things:

- perceived responsiveness
- terminal UX
- realism of interaction

Instead of waiting two or three seconds and dumping the whole answer, we see it unfold progressively. That is why the payload contains `"stream": true` and why the `curl` call is built to consume a stream.

---

## 11\. The streaming loop

```bash


ASSISTANT_REPLY=""
BUFFER=""

while IFS= read -r line; do
  [[ "$line" != data:* ]] && continue

  DATA="${line#data: }"
  [[ "$DATA" == "[DONE]" ]] && break

  DELTA=$(jq -r '
    select(.type=="response.output_text.delta")
    | .delta // empty
  ' <<< "$DATA")

  [[ -z "$DELTA" ]] && continue

  ASSISTANT_REPLY+="$DELTA"
  BUFFER+="$DELTA"

  if [[ ${#BUFFER} -ge 40 || "$DELTA" == *$'\n'* ]]; then
    printf "%s" "$BUFFER"
    BUFFER=""
  fi

done < <(
  curl -sS -N "$API_URL" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -d "$PAYLOAD"
)


```

This block is where Bash goes from "small script language" to "interesting systems tool".

---

## 12\. `curl -sS -N`

```bash


curl -sS -N ...


```

- **`-s`** — Silent mode. Removes the progress meter and other noise.
- **`-S`** — Show errors even in silent mode. This is why `-sS` is a common combination: suppress progress noise, but still report actual failures.
- **`-N`** — No buffering. Critical for streaming. Without `-N`, `curl` may buffer output before flushing it to stdout, which ruins the feeling of real-time token streaming.

This flag is one of those tiny details that dramatically changes UX.

---

## 13\. The famous `done < <(curl ...)`

This syntax confuses almost everybody the first time they see it:

```bash


done < <(
  curl ...
)


```

It is **process substitution**.

Conceptually, it means: run `curl`, and connect its stdout to the stdin of the `while` loop.

**Why not just write `curl ... | while read ...`?**

Because that would usually run the loop in a subshell. Then variables modified inside the loop, like `ASSISTANT_REPLY`, would be lost outside the loop. That is one of the most classic Bash traps.

With process substitution, the loop runs in the current shell, so variables remain available after the loop ends.

**Under the hood**, Bash roughly:

- creates a pipe
- runs `curl` with its stdout connected to the write end
- exposes the read end as something like `/dev/fd/63`
- redirects the `while` loop stdin from that fd

That `/dev/fd/N` path is not a real disk file. It is just a reference to an open file descriptor. Nothing is written to disk. The data flows through a kernel pipe buffer.

This is a great example of Unix I/O unification: files, pipes, sockets, and terminals all end up being accessed through file descriptors.

---

## 14\. Is the pipe a file? Is it a buffer?

The best answer is:

- a pipe is not a file
- a pipe uses a kernel buffer
- the read side and write side are accessed via file descriptors

So yes, there is buffering, but not "a temporary file in memory". It is a kernel pipe buffer, typically FIFO, with synchronization behavior:

- if the pipe is empty, the reader blocks
- if the pipe is full, the writer blocks

That is why this streaming design is efficient and natural.

---

## 15\. `while IFS= read -r line`

```bash


while IFS= read -r line; do


```

**What is `IFS`?** It is the Internal Field Separator, a shell variable that controls how Bash splits input fields. By default, it contains space, tab, and newline.

**Why set `IFS=` here?** Because we want to read each incoming line exactly as it is, without trimming leading spaces or doing weird field-splitting.

**Why `-r`?** Because we do not want backslashes to be interpreted as escapes.

**What does `read` do in this context?** It blocks until a full line is available on stdin. There is no polling loop and no "read every 10 ms" timer. The loop wakes up when a line arrives from the `curl` stream. So this is event-driven in the Unix I/O sense.

---

## 16\. Ignoring non-data SSE lines

The API sends SSE-style lines, which look like:

```text


data: {"type":"response.output_text.delta","delta":"Hello"}


```

That is why the first filter is:

```bash


[[ "$line" != data:* ]] && continue


```

It ignores anything that is not an SSE `data:` line.

---

## 17\. `DATA="${line\#data: }"`

This is pure Bash parameter expansion. It removes the prefix `data: ` from the beginning of the line.

If `line` is `data: {"foo":"bar"}`, then `DATA` becomes `{"foo":"bar"}`.

The syntax `${var#pattern}` means: remove the shortest match of `pattern` from the left. This is a very efficient way to strip a known prefix without spawning `sed` or `cut`.

---

## 18\. Detecting the end of the stream

```bash


[[ "$DATA" == "[DONE]" ]] && break


```

SSE streams often signal the end with a special sentinel. Here, `[DONE]` tells us the response is complete.

---

## 19\. Extracting only text deltas with `jq`

```bash


DELTA=$(jq -r '
  select(.type=="response.output_text.delta")
  | .delta // empty
' <<< "$DATA")


```

This small but elegant filter says:

- keep only events whose `.type` is `response.output_text.delta`
- extract `.delta`
- if missing, use empty string

If the incoming JSON is

```text


{"type":"response.output_text.delta","delta":"Hello"}`,


```

then `DELTA` becomes `Hello`. If the JSON is some other event type, `DELTA` becomes empty, and:

```bash


[[ -z "$DELTA" ]] && continue


```

skips irrelevant events.

---

## 20\. Why `ASSISTANT_REPLY` and `BUFFER` are separate

```bash


ASSISTANT_REPLY+="$DELTA"
BUFFER+="$DELTA"


```

They serve different purposes.

- **`ASSISTANT_REPLY`** stores the full raw assistant response so we can append it back into `HISTORY` later.
- **`BUFFER`** is only for display smoothing. If we printed every tiny delta immediately, the terminal might feel jittery or noisy. By buffering small chunks and flushing them every ~40 characters, we get a smoother stream.

---

## 21\. The buffering heuristic

```bash


if [[ ${#BUFFER} -ge 40 || "$DELTA" == *$'\n'* ]]; then
  printf "%s" "$BUFFER"
  BUFFER=""
fi


```

This is deliberately simple. `${#BUFFER}` is the length of the string. This condition says:

- if buffer length reaches 40
- or if the latest delta contains a newline
- print the buffer, then clear it

This is not semantic formatting. It does not understand markdown structure or sentence boundaries. It is just a pragmatic UX heuristic.

We experimented with more "intelligent" formatting — inserting line breaks after punctuation or markdown markers like `---` and `**` — but that turned out to be fragile. Streaming chunks do not necessarily correspond to meaningful textual boundaries. Punctuation and formatting markers can be split across arbitrary deltas.

That is one of the most instructive lessons in this project:

> **Raw token streams do not align nicely with human formatting structures.**

So the best compromise was to keep the rendering logic simple and robust.

---

## 22\. Final flush

```bash


if [[ -n "$BUFFER" ]]; then
  printf "%s" "$BUFFER"
fi

echo


```

If anything remains in the buffer, print it. Then emit a final newline so the prompt does not appear on the same line as the response. `-n` means "string is not empty".

---

## 23\. Safety check: empty responses

```bash


if [[ -z "$ASSISTANT_REPLY" ]]; then
  log "Empty assistant response"
  echo "No response."
  continue
fi


```

This is basic hygiene. If something went wrong in the stream parsing and no text was accumulated, we avoid polluting history with an empty assistant message.

---

## 24\. Appending the assistant reply back into history

```bash


HISTORY=$(jq \
  --arg msg "$ASSISTANT_REPLY" \
  '. + [{"role":"assistant","content":[{"type":"output_text","text":$msg}]}]' \
  <<< "$HISTORY"
)


```

This mirrors the earlier user append. Now the next user turn will be sent with the complete conversation so far. That is how the script synthesizes memory from a stateless API.

---

## 25\. What we learned along the way

This little Bash project looks modest, but it teaches a surprising amount.

**APIs are often stateless.** The "memory" of a conversation is not magic. The client rebuilds and resends context.

**Streaming UX matters.** Even a tiny CLI feels dramatically better when output streams progressively.

**`jq` is not just a query tool.** It is an incredibly useful JSON transformation language for shell scripts.

**Bash I/O is weird, but powerful.** `<<<`, `< <(...)`, `IFS= read -r`, file descriptors, pipes, redirections — once you understand them, a lot of shell code suddenly becomes readable.

**Process substitution solves a real problem.** `cmd | while read ...` is tempting, but often wrong if you need variables updated after the loop.

**Formatting streamed output is harder than expected.** Trying to be too clever with punctuation or markdown during token streaming quickly becomes unreliable. The simplest robust renderer usually wins.

---

## 26\. Small command experiments that make everything clearer

If you want to really internalize the mechanisms used in the script, these are worth trying directly in a shell.

**Here-string:**

```bash


jq '.' <<< '{"a":1}'


```

Feeds a string into `jq` via stdin.

**Prefix removal:**

```bash


line='data: {"x":1}'
echo "${line#data: }"


```

Outputs: `{"x":1}`

**`IFS= read -r`:**

```bash


printf '  hello \\ world\n' | while IFS= read -r line; do
  printf '[%s]\n' "$line"
done


```

Preserves the line exactly.

**Process substitution:**

```bash


while IFS= read -r line; do
  echo "Got: $line"
done < <(printf 'a\nb\nc\n')


```

The loop reads from another command without using a pipeline subshell.

**Why not a pipeline:**

```bash


x=""
printf 'a\n' | while read -r line; do
  x="changed"
done
echo "x=$x"


```

Often prints `x=` because the loop runs in a subshell.

**Buffer length:**

```bash


BUFFER="hello world"
echo "${#BUFFER}"


```

Prints `11`.

---

## 27\. Why Bash was actually a good choice

This is not the kind of project for which Bash is the "best engineering language" in an abstract sense. If you wanted maximum extensibility, structured error handling, tool calling, TUI rendering, or cross-platform maintainability, you would probably choose Python, Go, or Rust.

But that is missing the point.

Bash was a good choice here because the project is fundamentally about:

- stdin/stdout
- process composition
- pipes
- JSON marshalling
- shell ergonomics
- terminal interaction

This project is almost a celebration of Unix primitives. And Bash is the natural language of those primitives.

---

## 28\. The final shape of the tool

The result is a compact CLI that:

- validates dependencies
- validates the API key
- logs session activity
- keeps conversation context
- constructs JSON safely with `jq`
- streams answers with `curl`
- parses SSE lines incrementally
- preserves assistant replies for future turns
- exits cleanly

That is already a real tool, not just a toy snippet. And more importantly, it becomes a great excuse to learn Bash properly.

---

## 29\. Closing thought

The most interesting part of this project was not "calling OpenAI from Bash". That part is actually easy.

The interesting part was everything around it:

- the realization that the API is stateless
- the need to rebuild memory explicitly
- the switch from blocking responses to streaming
- the discovery that `curl -N` changes the whole feel of the tool
- the fight with subshells
- the weird elegance of `done < <(curl ...)`
- and the moment when pipes, file descriptors, and `read` stop feeling like shell black magic and start feeling like a coherent model

That is what made this little CLI fun to build.

It is not just a wrapper around an API.

It is a small lesson in how Unix thinks.