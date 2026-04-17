_A deep dive into how Shiny's reactive engine works — using a real-world analytics dashboard as our guide._

_The code used by this article comes from my RShiny NGINX log analyzer here_

[repo](https://github.com/julienlargetpiet/Statix/tree/main/RShinyApp)

---

## Introduction: The Program That Watches Itself

Most programs you write are imperative: you call a function, it runs, it returns a value, and the world moves on. You are in control of when things happen. R Shiny breaks this contract entirely.

In Shiny, you don't call functions — you _declare relationships_. You tell Shiny: "this output depends on that input, and that reactive depends on this other reactive." Then you step back and let Shiny figure out _when_ to run _what_ and _in what order_.

This sounds simple. It is not. Understanding Shiny deeply means understanding it as a **live dependency graph** — a directed acyclic graph (DAG) of nodes that invalidate and re-execute in cascading waves whenever something upstream changes.

This article will walk you through that mental model using a real analytics dashboard: a Nginx log viewer with bot detection, geolocation, ASN filtering, and a dark mode toggle. Every Shiny pattern in that app — `reactive()`, `reactiveVal()`, `observeEvent()`, `renderPlotly()` — maps cleanly onto graph concepts. By the end, you'll see Shiny code the way Shiny itself sees it.

---

## Part 1: The Dependency Graph Mental Model

### Nodes and Edges

Think of your entire Shiny application as a directed graph where:

- **Nodes** are reactive sources, reactive expressions, and reactive consumers (outputs and observers).
- **Edges** represent "reads": when node B reads from node A, an edge is drawn from A to B, meaning "B depends on A."
- **Invalidation** flows downstream: when A changes, every node that depends on A is marked _dirty_ and will re-execute on its next demand.

There are three fundamental node types in Shiny:



| Type | Examples | Produces value? | Triggered by? |
| --- | --- | --- | --- |
| <strong>Reactive source</strong> | <code>input$x</code>, <code>reactiveVal()</code>, <code>reactiveValues()</code> | Yes | User action / explicit set |
| <strong>Reactive expression</strong> | <code>reactive({ ... })</code> | Yes | Lazy — on demand, if dirty |
| <strong>Reactive consumer</strong> | <code>render*()</code>, <code>observe()</code>, <code>observeEvent()</code> | No | Eagerly, when dirty |




The crucial insight is that edges are **created at runtime**, not at definition time. Shiny tracks which reactive sources are _read_ during a reactive expression's execution, and builds the graph dynamically.

### Invalidation vs. Re-execution

These are two distinct events, and confusing them is the source of most Shiny bugs.

**Invalidation** is cheap and immediate. When `input$time_unit` changes, Shiny marks every node that read it as invalid (dirty). This is just flipping a flag — no code runs.

**Re-execution** is deferred and lazy (for `reactive()`) or eager (for `observe()`/ `render*()`). A `reactive()` will only re-execute when something downstream _demands_ its value. A `render*()` will re-execute as soon as it's invalidated, because it has a side effect (updating the browser).

This lazy/eager distinction is what makes Shiny efficient. If ten things change at once, a `reactive()` in the middle of the graph only re-runs once — when the first downstream consumer asks for its value.

---

## Part 2: Reading the Graph in Our App

Let's map the actual app. At the top level, here is the dependency chain for the main data pipeline:

```text


input$time_unit ──┐
input$last_n ─────┤
input$strict ─────┤
input$only_articles ┤──► filtered_data() ──► geo_enriched_data() ──► output$mytable
mmdb_bump() ──────┤                    │
raw_data() ───────┘                    └──► output$kpi_hits
                                        └──► output$kpi_ips
                                        └──► output$pie_chart
                                        └──► output$graph
                                        └──► output$map (via geo_enriched_data)


```

Every time any of those inputs changes, `filtered_data()` is invalidated. Every consumer of `filtered_data()` — and there are many — is also invalidated transitively. This is the cascade.

Now let's zoom into specific patterns.

---

## Part 3: The Synchronized Inputs Pattern — Two-Way Binding Without Loops

### The Code

```r


observeEvent(input$time_unit, ignoreInit = TRUE, {
  updateSelectInput(session, "time_unit_2", selected = input$time_unit)
})

observeEvent(input$time_unit_2, ignoreInit = TRUE, {
  updateSelectInput(session, "time_unit", selected = input$time_unit_2)
})


```

The app has two tabs, each with their own `time_unit` select input. The user should be able to change either one and have the other follow. This creates an immediately obvious question: won't this cause an infinite loop?

`input$time_unit` changes → triggers first `observeEvent` → calls `updateSelectInput("time_unit_2")` → `input$time_unit_2` changes → triggers second `observeEvent` → calls `updateSelectInput("time_unit")` → ...

### Why It Doesn't Loop

The answer lies in how `updateSelectInput` works at the Shiny protocol level. When you call `updateSelectInput(session, "time_unit", selected = "h")`, Shiny sends a message to the browser to update the UI element. The browser updates it. But — and this is key — **the new value is only sent back to the server if it actually changed**.

If `input$time_unit` is already `"h"` and you send `updateSelectInput(..., selected = "h")`, the browser sets it to `"h"` — the same value — and Shiny's change detection sees no delta. No new input event is fired. The second `observeEvent` never triggers.

In dependency graph terms: the observer wakes up, sends an update, the update causes no state change in the reactive source, and the graph reaches a stable fixed point in one pass.

The `ignoreInit = TRUE` argument also matters here. Without it, both observers would fire on startup — before the user has done anything — which could cause unnecessary UI flicker and unpredictable initialization order.

### The Same Pattern, for Numeric Inputs

```r


observeEvent(input$last_n, ignoreInit = TRUE, {
  updateNumericInput(session, "last_n_2", value = input$last_n)
})

observeEvent(input$last_n_2, ignoreInit = TRUE, {
  updateNumericInput(session, "last_n", value = input$last_n_2)
})


```

Identical pattern, identical reasoning. The graph is:

```text


input$last_n ──► [observer A] ──► updateNumericInput("last_n_2")
                                         │
                                         ▼
input$last_n_2 ◄── (browser update, only if changed)
     │
     ▼
[observer B] ──► updateNumericInput("last_n")
                        │
                        ▼
          (no-op if value unchanged → graph stabilizes)


```

---

## Part 4: reactiveVal() — A Node You Control Manually

### The Concept

`reactiveVal()` creates a reactive source node that you fully control. It's not driven by user input — you set its value programmatically. But from the dependency graph's perspective, it behaves exactly like `input$x`: any reactive expression that reads it will take a dependency on it, and be invalidated when it changes.

This is powerful because it lets you introduce _synthetic_ invalidation triggers — events that aren't directly representable as UI inputs.

### The MMDB Upload Pattern

```r


mmdb_bump <- reactiveVal(0)

observeEvent(input$upload_asn_mmdb, {
  req(input$upload_asn_mmdb)
  src <- input$upload_asn_mmdb$datapath
  dst <- asn_db_path
  ok <- file.copy(src, dst, overwrite = TRUE)
  if (!ok) {
    showNotification(paste("Failed to write:", dst), type = "error")
    return()
  }
  clear_ip_caches()
  geo_cache_reactive(NULL)
  last_ips(character())
  mmdb_bump(mmdb_bump() + 1)   # <-- manual invalidation trigger
  showNotification("ASN DB uploaded and installed.", type = "message")
})


```

And then, in `filtered_data()`:

```r


filtered_data <- reactive({
  mmdb_bump()   # <-- read the value; take a dependency
  req(input$time_unit, input$last_n)
  df <- raw_data()
  ...
})


```

### Anatomy of a Manual Invalidation Cascade

Let's trace what happens step by step when the user uploads a new ASN database file:

**Step 1** — `input$upload_asn_mmdb` changes (user uploads a file). The observer wakes up.

**Step 2** — The file is copied to its destination on disk. This is a side effect — Shiny knows nothing about it. The file system changed, but the dependency graph did not.

**Step 3** — `clear_ip_caches()` is called. This deletes the `.rds` cache files on disk. Again, Shiny is unaware.

**Step 4** — `geo_cache_reactive(NULL)` resets another `reactiveVal`. This invalidates anything reading `geo_cache_reactive`.

**Step 5** — `last_ips(character())` resets another `reactiveVal`. This is used to prevent redundant geo lookups.

**Step 6** — `mmdb_bump(mmdb_bump() + 1)`. This is the critical line. `mmdb_bump()` (called with no arguments) _reads_ the current value. Then `mmdb_bump(value)` (called with an argument) _sets_ a new value. This _invalidates_ `mmdb_bump` as a reactive source.

**Step 7** — `filtered_data()` had previously read `mmdb_bump()` during its last execution, establishing a dependency edge. Now that `mmdb_bump` is invalidated, `filtered_data()` is invalidated too.

**Step 8** — Everything downstream of `filtered_data()` is also invalidated: `geo_enriched_data()`, `output$kpi_hits`, `output$kpi_ips`, `output$pie_chart`, `output$mytable`, `output$graph`, `output$map`. All marked dirty.

**Step 9** — Shiny re-executes the dirty consumers. `filtered_data()` re-runs. This time, when it calls `lookup_asns(...)`, the on-disk cache files are gone (cleared in step 3), so the ASN lookup function goes to the new MMDB file to resolve IPs. Fresh data, correctly enriched.

The beauty here: **`mmdb_bump` is a synthetic signal**. The real event was a file copy. Shiny can't observe file copies. So we create an artificial reactive source and increment it — purely to propagate invalidation through the graph.

### The Read-to-Depend Pattern

Notice this line inside `filtered_data()`:

```r


filtered_data <- reactive({
  mmdb_bump()  # value not used, dependency is the goal
  ...
})


```

The return value of `mmdb_bump()` is never assigned to a variable. It's called purely for its side effect on the dependency graph: **reading a reactive source inside a reactive context creates a dependency edge**. This is a deliberate and idiomatic Shiny pattern.

If you forget this line, uploading a new MMDB file will copy it to disk but `filtered_data()` won't know to re-run. Your data will continue to use the old database. This is a silent bug — no error, just stale results.

### The Status Display

```r


output$mmdb_status <- renderUI({
  mmdb_bump()   # same dependency trick
  asn_ok <- file.exists(asn_db_path)
  city_ok <- file.exists(geo_db_path)
  tags$div(
    tags$small(
      HTML(paste0(
        "<b>ASN DB:</b> ", if (asn_ok) "✅ present" else "❌ missing",
        "<br><b>City DB:</b> ", if (city_ok) "✅ present" else "❌ missing"
      ))
    )
  )
})


```

`output$mmdb_status` also reads `mmdb_bump()`. So every time either MMDB file is uploaded, the status UI re-renders too — automatically, because it's a consumer in the same graph. You didn't have to wire this up manually. The graph handles it.

---

## Part 5: reactive() — Memoized, Lazy, Cached Computation

### The Contract

A `reactive()` expression is the workhorse of the Shiny dependency graph. Its contract is:

1. **Lazy**: It never runs unless something demands its value.
2. **Cached**: After it runs, it caches its return value. Subsequent reads within the same "flush" return the cache without re-running.
3. **Auto-invalidating**: If any reactive source it read during its last run has changed, it marks itself dirty. The next demand causes a fresh re-run.

This is essentially **memoization with automatic cache invalidation** driven by the dependency graph.

### raw\_data() — The Foundation

```r


raw_data <- reactive({
  fp <- file_path
  req(!is.null(fp))
  df <- read_delim(fp, delim = " ", quote = '"', ...)
  ...
  parsed %>% filter(!is.na(date), !is.na(target))
})


```

`raw_data()` reads from the file system. It takes no dependency on any reactive input. This means it runs once and caches. Every consumer — `filtered_data()`, ultimately everything — reads from this cache.

In graph terms, `raw_data()` has no reactive parents. It is a leaf node on the source side. It re-runs only if it's manually invalidated (which in this app it never is — the log file is assumed to grow, not change).

A more sophisticated version might use `reactivePoll()` or `reactiveFileReader()` to watch the file for changes and auto-invalidate. But even so, the graph structure is the same — you'd just have a reactive source polling the file that `raw_data()` depends on.

### filtered\_data() — The Heavy Lifter

`filtered_data()` is the most complex node in the graph. It reads from:

- `mmdb_bump()` — synthetic invalidation signal
- `input$time_unit` — time window unit
- `input$last_n` — time window size
- `input$show_bots` — bot filtering toggle
- `input$show_static` — static asset filter toggle
- `input$only_articles` — article-only filter
- `input$strict` — ASN bot filtering level
- `raw_data()` — the base data

Eight reactive dependencies. Any one of them changing invalidates `filtered_data()`. This is the correct design — `filtered_data()` is the single source of truth for "what data the user is looking at right now." Every output reads it.

**What does this buy you?** Consider the alternative: each output independently reading from `raw_data()` and applying filters inline. Every time `input$time_unit` changes, every output would independently re-filter the raw data. That's redundant computation — potentially expensive for large log files. With `filtered_data()` as an intermediate node:

```text


input$time_unit ──────────────────────────────────────────────────────────────┐
                                                                               ▼
raw_data() ──────────────────────────► filtered_data() ──► output$kpi_hits
                                              │          └─► output$kpi_ips
                                              │          └─► output$kpi_pages
                                              │          └─► output$pie_chart
                                              │          └─► output$graph
                                              │          └─► article_readtime_stats()
                                              └──► geo_enriched_data() ──► output$mytable
                                                                        └─► output$map


```

`filtered_data()` runs **once** when `input$time_unit` changes. All eight outputs then read from the cache. The filtering logic executes exactly once, regardless of how many outputs consume it.

### geo\_enriched\_data() — Splitting the Graph

```r


geo_enriched_data <- reactive({
  df <- filtered_data()
  geo <- geo_cache_reactive()
  if (!is.null(geo)) {
    df <- df %>% left_join(geo, by = "ip")
  }
  df
})


```

This node exists to cleanly separate the geo-lookup concern from the filtering concern. `filtered_data()` does bot detection, time windowing, and ASN enrichment. `geo_enriched_data()` joins in the full geo data (lat/lon, country, city) which is expensive to compute and stored in a reactive cache.

Only two outputs need geo data: `output$mytable` and `output$map`. Outputs that don't need it — `output$kpi_hits`, `output$pie_chart`, `output$graph` — read directly from `filtered_data()` and don't pay the cost of the geo join.

This is graph design: **push expensive operations as far downstream as possible, and only connect them to the consumers that actually need them**.

---

## Part 6: The Geo Cache — Observing to Avoid Redundant Work

```r


geo_cache_reactive <- reactiveVal(NULL)
last_ips <- reactiveVal(character())

observeEvent(filtered_data(), {
  ips <- sort(unique(filtered_data()$ip))
  if (!identical(ips, last_ips())) {
    geo_data <- lookup_ips(ips, db_path = geo_db_path)
    geo_cache_reactive(geo_data)
    last_ips(ips)
  }
}, ignoreInit = FALSE)


```

This is a subtle but important pattern. `lookup_ips()` calls `mmdblookup` — a system process — for every IP it doesn't already know about. This is slow. We don't want to call it every time `filtered_data()` changes.

The solution: an observer that watches `filtered_data()`, extracts the unique IPs, and **only runs the lookup if the set of IPs has changed** (checked with `identical()`).

In dependency graph terms:

```text


filtered_data() ──► [geo observer] ──(if IPs changed)──► lookup_ips()
                                                                │
                                                                ▼
                                                     geo_cache_reactive() (updated)
                                                                │
                                                                ▼
                                                     geo_enriched_data() (invalidated)
                                                                │
                                                                ▼
                                                     output$mytable, output$map (re-render)


```

This is a manual memoization layer on top of Shiny's automatic memoization. The `last_ips` `reactiveVal` stores the previous IP set. If the time window shifts but the same IPs appear, no lookup happens. If a new IP appears, only that IP needs to be looked up (because `lookup_ips()` internally checks its own disk cache first).

The `ignoreInit = FALSE` here means the observer runs on startup — which triggers an initial geo lookup if there is data. This is the opposite default from `observeEvent` on inputs, where you typically want `ignoreInit = TRUE` to avoid running before the user has interacted.

---

## Part 7: The Dark Mode Pattern — Theme as Reactive State

### The Commented-Out Version

```r


#observeEvent(input$dark_mode, ignoreInit = TRUE, {
#  session$setCurrentTheme(
#    if (isTRUE(input$dark_mode)) { bs_theme(...) } else { bs_theme(...) }
#  )
#})


```

This would work. But it has a subtle issue: the theme object is constructed inline, inside a consumer. If you ever wanted to read the current theme in multiple places (say, to pass it to a plot), you'd have to duplicate the theme construction logic.

### The Refactored Version

```r


theme_reactive <- reactive({
  if (isTRUE(input$dark_mode)) {
    bs_theme(version = 5, bootswatch = "darkly", ...)
  } else {
    bs_theme(version = 5, bootswatch = "litera", ...)
  }
})

observeEvent(input$dark_mode, {
  session$setCurrentTheme(theme_reactive())
}, ignoreInit = TRUE)


```

Now there are two nodes:

- `theme_reactive()` — a `reactive()` that produces a `bs_theme` object, cached, invalidated when `input$dark_mode` changes.
- An `observeEvent` that _consumes_ `theme_reactive()` and applies it to the session.

The graph is: `input$dark_mode → theme_reactive() → [observer] → session theme update`

In the plot outputs, you'll also see `input$dark_mode` read directly:

```r


output$pie_chart <- renderPlotly({
  input$dark_mode   # take a dependency, re-render when mode changes
  df <- filtered_data()
  ...
  dark <- isTRUE(input$dark_mode)
  plot_ly(...) %>% layout(template = if (dark) "plotly_dark" else "plotly_white", ...)
})


```

This is the "read to depend" pattern again. The plot needs to re-render when dark mode toggles, so it reads `input$dark_mode` explicitly. Shiny registers the dependency. When `input$dark_mode` changes, the plot is invalidated and re-renders with the correct color scheme.

---

## Part 8: observe() vs. observeEvent() — Eager Consumers

Both `observe()` and `observeEvent()` create _eager reactive consumers_: nodes that re-execute immediately when invalidated, rather than waiting to be demanded.

The difference is in how they build their dependency edges:

- `observe({ ... })` reads everything inside its block and takes dependencies on all of it. It re-runs whenever any of those things change.
- `observeEvent(x, { ... })` takes a dependency only on `x`. The body of the handler (the second argument) does _not_ create reactive dependencies — it's executed as a side effect, and its reactive reads are isolated.

In the app:

```r


observe({
  session$sendCustomMessage("getTimezone", list())
})


```

This runs once on startup (it reads nothing, so it's never invalidated after that). It fires a JavaScript message to the browser asking for the client's timezone. The browser responds by setting `input$client_tz`, which is then used to format dates in `output$mytable`.

```r


observeEvent(input$dark_mode, {
  session$setCurrentTheme(theme_reactive())
}, ignoreInit = TRUE)


```

This only re-runs when `input$dark_mode` changes. `theme_reactive()` inside the handler is read as a value, and that read does create a dependency — but it's a one-time dependency inside the handler's execution context. The observer itself only watches `input$dark_mode`.

---

## Part 9: req() — Conditional Edges and Early Exit

Throughout the app you'll see `req()`:

```r


filtered_data <- reactive({
  mmdb_bump()
  req(input$time_unit, input$last_n)
  df <- raw_data()
  req(nrow(df) > 0)
  ...
})


```

`req()` is Shiny's mechanism for graceful early termination. If any argument is falsy (NULL, NA, empty string, FALSE, or zero rows), `req()` raises a special "silent error" that halts the reactive expression without producing an error message.

In graph terms, `req()` short-circuits the computation and prevents the node from producing a value. Downstream consumers that try to read from a node stopped by `req()` also halt silently. The outputs just don't update — they stay blank or show their last valid value.

This is important for startup. On the first render, `input$time_unit` might not yet be set. Without `req()`, `filtered_data()` would crash trying to look up `mult_map[[NULL]]`. With `req()`, it simply does nothing, and the outputs are empty until the inputs are initialized.

---

## Part 10: The Full Dependency Graph

Let's draw the complete picture for our app. Nodes are color-coded:

- 🟦 Reactive sources (inputs, reactiveVal)
- 🟨 Reactive expressions (reactive())
- 🟥 Reactive consumers (render\*, observe\*, observers)

```text


🟦 input$upload_asn_mmdb ──► 🟥 [observe: copy ASN file] ──► 🟦 mmdb_bump (bump +1)
🟦 input$upload_city_mmdb ──► 🟥 [observe: copy City file] ──► 🟦 mmdb_bump (bump +1)
                                                               └──► 🟦 geo_cache_reactive (NULL)
                                                               └──► 🟦 last_ips ("")

🟦 mmdb_bump ──────────────────────────────────────────────────────┐
🟦 input$time_unit ────────────────────────────────────────────────┤
🟦 input$last_n ───────────────────────────────────────────────────┤
🟦 input$strict ───────────────────────────────────────────────────┤──► 🟨 filtered_data()
🟦 input$only_articles ────────────────────────────────────────────┤
🟦 input$show_bots ────────────────────────────────────────────────┤
🟨 raw_data() ─────────────────────────────────────────────────────┘

🟨 filtered_data() ──► 🟥 [observe: geo lookup] ──► 🟦 geo_cache_reactive
🟨 filtered_data() ──► 🟥 output$kpi_hits
🟨 filtered_data() ──► 🟥 output$kpi_ips
🟨 filtered_data() ──► 🟥 output$kpi_pages
🟨 filtered_data() ──► 🟥 output$kpi_med_readtime
🟨 filtered_data() ──► 🟨 article_readtime_stats() ──► 🟥 output$read_time
🟨 filtered_data() ──► 🟥 output$pie_chart (also reads input$dark_mode)
🟨 filtered_data() ──► 🟥 output$graph (also reads input$dark_mode, input$webpages)

🟨 filtered_data() ──┐
🟦 geo_cache_reactive ─┤──► 🟨 geo_enriched_data() ──► 🟥 output$mytable
                        └──► 🟨 geo_enriched_data() ──► 🟥 output$map

🟦 input$dark_mode ──► 🟨 theme_reactive() ──► 🟥 [observe: setCurrentTheme]
🟦 input$dark_mode ──► 🟥 output$pie_chart
🟦 input$dark_mode ──► 🟥 output$graph
🟦 input$dark_mode ──► 🟥 output$map

🟦 input$time_unit ◄──► 🟥 [observe A] ◄──► 🟦 input$time_unit_2
🟦 input$last_n ◄────► 🟥 [observe B] ◄──► 🟦 input$last_n_2

🟦 mmdb_bump ──► 🟥 output$mmdb_status


```

Look at this graph and count the paths leading into `output$mytable`: `input$time_unit`, `input$last_n`, `input$strict`, `input$only_articles`, `input$show_bots`, `mmdb_bump`, `geo_cache_reactive`, all the way through `raw_data()`, `filtered_data()`, `geo_enriched_data()`. That table is the most reactive output in the app — it responds to almost everything.

Compare that to `output$mmdb_status`, which only depends on `mmdb_bump`. It's nearly isolated from the rest of the graph. Uploads refresh it; nothing else does.

This is **graph design as application design**. Narrow dependency sets mean focused, predictable re-renders. Wide dependency sets mean responsive, always-current outputs — but also more computation.

---

## Part 11: Common Pitfalls and How the Graph Explains Them

### Pitfall 1: Reading a Reactive Outside a Reactive Context

```r


# BAD: Outside any reactive context
df <- filtered_data()  # Error: no reactive context


```

You can only read reactive values inside reactive contexts: `reactive()`, `observe()`, `observeEvent()`, `render*()`. Outside these contexts, Shiny has no active graph node to attach a dependency edge to, and the read fails.

### Pitfall 2: Forgetting the "Read to Depend" Pattern

```r


# BAD: mmdb_bump is never read — no dependency edge!
filtered_data <- reactive({
  # mmdb_bump()  ← forgot this
  req(input$time_unit, input$last_n)
  df <- raw_data()
  ...
})


```

Uploading a new MMDB file bumps the counter, but `filtered_data()` never reads it, so no edge exists, so `filtered_data()` is never invalidated. The new database is never used.

### Pitfall 3: Reactive Dependency Inside a Loop or Function

```r


# RISKY: Shiny may not track dependencies inside lapply
reactive({
  results <- lapply(input$selected_ids, function(id) {
    some_reactive_data()[[id]]  # Shiny tracks this fine, but be careful
  })
})


```

Dependencies are tracked correctly inside `lapply` and standard R control flow. But if you call a reactive inside a `future::future()` or a `callr` subprocess, the dependency is **not** tracked, because those run in separate R processes with no access to the reactive graph.

### Pitfall 4: Circular Dependencies

```r


# INFINITE LOOP:
x <- reactiveVal(0)
y <- reactiveVal(0)
observe({ y(x() + 1) })
observe({ x(y() + 1) })


```

Shiny detects circular reactive graphs and throws an error. The two-input synchronization pattern in our app avoids this because `updateSelectInput` goes through the browser — it's not a direct reactive write, and the browser only sends back a change event if the value actually changed.

### Pitfall 5: Heavy Computation in a Wide-Dependency Reactive

If `filtered_data()` had a reactive dependency on `input$map_cluster` (which only affects the map display), it would re-run the entire bot detection and filtering pipeline every time the user toggles map clustering. The fix: push display-only inputs into the consumer that uses them, not into the shared intermediate reactive.

---

## Part 12: Designing with the Graph in Mind

When building a Shiny app, I now think in terms of graph design before writing any code:

**1\. Identify your data sources.** What are the raw inputs? Files? APIs? Database queries? Each becomes a `reactive()` or `reactivePoll()` near the top of the graph.

**2\. Identify your filter/transform pipeline.** What computations are shared across multiple outputs? Each shared computation becomes a `reactive()` intermediate node. The more outputs share it, the more you gain from caching.

**3\. Identify what can be split.** Not every output needs every piece of data. `output$kpi_hits` doesn't need geo coordinates. Splitting `filtered_data()` and `geo_enriched_data()` means the KPI boxes don't wait for slow geo lookups.

**4\. Identify synthetic signals.** What events need to propagate invalidation but aren't naturally reactive? File uploads that change on-disk databases, cache resets, external API poll results — these become `reactiveVal()` bump counters.

**5\. Identify your eager consumers.** What needs to happen as a side effect when something changes? `observeEvent()` is your tool. Keep side effects out of `reactive()` — they're for computation, not for doing things.

**6\. Minimize dependency fan-in.** Every extra reactive dependency an intermediate node has is another thing that can cause unnecessary re-computation. Audit your `reactive()` calls: are they reading anything they don't strictly need?

---

## Conclusion: Shiny is a Graph Runtime

R Shiny is, at its core, a **reactive graph execution engine**. The R code you write in `server.R` is not a program — it's a graph specification. When you write `reactive({ filtered_data() %>% count(ip) })`, you're not calling `filtered_data()`. You're declaring that this node has an edge from `filtered_data()`.

**Functions wrapped inside `reactive()` mark them as a node that will react when a dependance, like `mmdb_bump()` reactive value has changed. It is why `filtered_data()` calls this reactive variable to see if its value has changed, if yes, then it re-executes**

Once you internalize this, a lot of Shiny's behavior that seems magical or confusing becomes obvious:

- Why does changing one input update five outputs? Because they're all downstream in the graph.
- Why does `reactiveVal()` propagate changes without you explicitly notifying consumers? Because any consumer that read it holds a dependency edge, and setting a new value invalidates the source, which invalidates downstream nodes.
- Why does `mmdb_bump()` called with no arguments (read) vs. with an argument (write) behave differently? Because reads create edges; writes invalidate sources.
- Why do your outputs not update after a file copy? Because file system changes are invisible to the reactive graph — you need a `reactiveVal` bump to make the change visible.

The dependency graph is not a metaphor. It is the actual data structure Shiny maintains at runtime. Every `reactive()` call creates a node. Every read inside a reactive context creates an edge. Every input change propagates invalidation down the edges. Every render function re-runs when it's dirty and its turn comes.

Build with the graph in mind, and Shiny becomes predictable, efficient, and elegant. Ignore it, and you'll spend days wondering why your app re-renders too often, not often enough, or in the wrong order.

---

_The app discussed in this article is a self-hosted Nginx analytics dashboard with bot detection, ASN filtering, geolocation, and dark mode support. All code examples are from the actual production codebase._