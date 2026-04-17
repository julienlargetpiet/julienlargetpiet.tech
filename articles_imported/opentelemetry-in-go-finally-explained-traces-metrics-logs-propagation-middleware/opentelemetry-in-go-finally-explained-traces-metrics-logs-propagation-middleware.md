I spent the day digging into OpenTelemetry in Go and, honestly, a lot of things that look magical at first finally clicked.

The code snippet of this article come from my recreational/tutorial repo:

- [TutOpenTelemetry-Go](https://github.com/julienlargetpiet/TutOpenTelemetry-Go)

This article is the version I wish I had when I started.

It covers:

- what `context.Context` is doing in Go HTTP servers
- how OpenTelemetry plugs into a Go service
- what traces, metrics, and logs actually are
- how `otelhttp` middleware changes request handling
- why you can have both a middleware-created HTTP span and your own manual span
- what propagators do and how they work across services
- why metrics flush in the background
- what the stdout trace / metric / log output really means field by field
- how to read the actual JSON output from the OpenTelemetry Go SDK

I’ll use a concrete dice service written in Go and the exact kind of stdout data the OpenTelemetry getting-started guide produces.

---

## The example service

The service has:

- an HTTP server
- a `/rolldice` endpoint
- a `/checkluck` endpoint
- OpenTelemetry tracing
- OpenTelemetry metrics
- OpenTelemetry logging
- automatic HTTP instrumentation on both server and client sides

---

## 1\. The complete code

### `main.go`

```go



package main

import (
	"context"
	"errors"
	"log"
	"net"
	"net/http"
	"os"
	"os/signal"
	"time"

	"go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
)

func main() {
	if err := run(); err != nil {
		log.Fatalln(err)
	}
}

func run() error {
	// Handle SIGINT (CTRL+C) gracefully.
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stop()

	// Set up OpenTelemetry.
	otelShutdown, err := setupOTelSDK(ctx)
	if err != nil {
		return err
	}
	// Handle shutdown properly so nothing leaks.
	defer func() {
		err = errors.Join(err, otelShutdown(context.Background()))
	}()

	// Start HTTP server.
	srv := &http.Server{
		Addr:         ":8080",
		BaseContext:  func(net.Listener) context.Context { return ctx },
		ReadTimeout:  time.Second,
		WriteTimeout: 10 * time.Second,
		Handler:      newHTTPHandler(),
	}
	srvErr := make(chan error, 1)
	go func() {
		srvErr <- srv.ListenAndServe()
	}()

	// Wait for interruption.
	select {
	case err = <-srvErr:
		// Error when starting HTTP server.
		return err
	case <-ctx.Done():
		// Wait for first CTRL+C.
		// Stop receiving signal notifications as soon as possible.
		stop()
	}

	// When Shutdown is called, ListenAndServe immediately returns ErrServerClosed.
	err = srv.Shutdown(context.Background())
	return err
}

func newHTTPHandler() http.Handler {
	mux := http.NewServeMux()

	// Register handlers.
	mux.Handle("/rolldice", http.HandlerFunc(rolldice))
	mux.Handle("/rolldice/{player}", http.HandlerFunc(rolldice))
    mux.Handle("/checkluck", http.HandlerFunc(checkluck))

	// Add HTTP instrumentation for the whole server.
	handler := otelhttp.NewHandler(mux,
    "dice-server") // fallback span name
    // otelhttp midleware automatically injects as http attrs:
    // http.request.method
    // http.response.status_code
    // server.address
    // network.peer.address
    // in other words, this automaticaly extracts trace context from header
    // it does ctx := propagator.Extract(r.Context(), propagation.HeaderCarrier(r.Header))
    // where r is *http.Request
    // extract context from headers
    // create SERVER span for HTTP request
    // store it in r.Context()

	return handler
}


```

---

### `otel.go`

```go



package main

import (
	"context"
	"errors"
	"time"

	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/exporters/stdout/stdoutlog"
	"go.opentelemetry.io/otel/exporters/stdout/stdoutmetric"
	"go.opentelemetry.io/otel/exporters/stdout/stdouttrace"
	"go.opentelemetry.io/otel/log/global"
	"go.opentelemetry.io/otel/propagation"
	semconv "go.opentelemetry.io/otel/semconv/v1.26.0"
	"go.opentelemetry.io/otel/sdk/log"
	"go.opentelemetry.io/otel/sdk/metric"
	"go.opentelemetry.io/otel/sdk/resource"
	"go.opentelemetry.io/otel/sdk/trace"
)

// setupOTelSDK bootstraps the OpenTelemetry pipeline.
// If it does not return an error, make sure to call shutdown for proper cleanup.
func setupOTelSDK(ctx context.Context) (func(context.Context) error, error) {
	var shutdownFuncs []func(context.Context) error // set of terminating logics
	var err error

	// shutdown calls cleanup functions registered via shutdownFuncs.
	// The errors from the calls are joined.
	// Each registered cleanup will be invoked once.
    // Execute each shutdown function
    //
    // Collect any error it returns
    //
    // Merge it with previously collected errors
	shutdown := func(ctx context.Context) error {
		var err error
		for _, fn := range shutdownFuncs {
			err = errors.Join(err, fn(ctx)) // union of all errors
		}
		shutdownFuncs = nil // clear the terminating logics
		return err
	}

	// handleErr calls shutdown for cleanup and makes sure that all errors are returned.
	handleErr := func(inErr error) {
		err = errors.Join(inErr, shutdown(ctx))
	}

	// Set up propagator.
	prop := newPropagator()
	otel.SetTextMapPropagator(prop) // register propagator

	// Set up trace provider.
	tracerProvider, err := newTracerProvider()
	if err != nil {
		handleErr(err)
		return shutdown, err
	}
	shutdownFuncs = append(shutdownFuncs, tracerProvider.Shutdown) // register the terminating logic for tracerProvider
	otel.SetTracerProvider(tracerProvider)                         // register traceProvider

	// Set up meter provider - metrics
	meterProvider, err := newMeterProvider()
	if err != nil {
		handleErr(err)
		return shutdown, err
	}
	shutdownFuncs = append(shutdownFuncs, meterProvider.Shutdown) // register the terminating logic for meterProvider
	otel.SetMeterProvider(meterProvider)                          // register the metrics

	// Set up logger provider.
	loggerProvider, err := newLoggerProvider()
	if err != nil {
		handleErr(err)
		return shutdown, err
	}
	shutdownFuncs = append(shutdownFuncs, loggerProvider.Shutdown) // register the terminating logic for loggerProvider
	global.SetLoggerProvider(loggerProvider)                       // register the logging

	return shutdown, nil
}

// acts for propagating context between spans
// The receiving service extracts the trace context from the request, creates a new span, and links it as a child of the previous span.
//
// 1️⃣ Service A creates a span
//
// Suppose Service A receives a request and creates a span:
//
// ctx, span := tracer.Start(ctx, "checkout")
//
// Internally the context now contains something like:
//
// trace_id = abc123
// span_id  = spanA
// 2️⃣ Service A calls Service B
//
// Before sending the HTTP request, OpenTelemetry injects the trace context into headers:
//
// otel.GetTextMapPropagator().Inject(ctx, req.Header)
//
// Headers now contain something like:
//
// traceparent: 00-abc123-spanA-01
//
// Meaning:
//
// trace_id = abc123
// parent_span_id = spanA
//
// So the request carries the trace lineage.
//
// 3️⃣ Service B receives the request
//
// Service B extracts the trace context:
//
// ctx := otel.GetTextMapPropagator().Extract(context.Background(), req.Header)
//
// Now the context contains:
//
// trace_id = abc123
// parent_span_id = spanA
//
// This reconstructs the upstream trace state

func newPropagator() propagation.TextMapPropagator {
	return propagation.NewCompositeTextMapPropagator(
		propagation.TraceContext{},
		propagation.Baggage{},
	)
}

// creating span context:
// - trace_id
// - span_id
// - parent_span_id
// - name
// - start_time
// - end_time
// - attributes
func newTracerProvider() (*trace.TracerProvider, error) {
	// traceExporter is responsible to send finished spans somewhere
	traceExporter, err := stdouttrace.New(stdouttrace.WithPrettyPrint())
	if err != nil {
		return nil, err
	}

	// metadata about the service
	res, _ := resource.Merge(
		resource.Default(), // detected attrs, hostname, process.pid, os.type, telemetry sdk name
		resource.NewWithAttributes( // custom attrs
			semconv.SchemaURL,
			semconv.ServiceName("dice-service"),
		),
	)

	// goroutine A → span.End()
	// goroutine B → span.End()
	// goroutine C → span.End()
	//
	// All push spans into the same queue.

	// tracerProvider.Shutdown(ctx)
	//
	// The SDK does:
	//
	// flush remaining spans
	// stop exporter goroutine

	tracerProvider := trace.NewTracerProvider(
		trace.WithResource(res), // register metadata
		trace.WithBatcher(traceExporter, // store it as batches and flushes every second, a background goroutine is charged to flush the batch - batch Queue
			// Default is 5s. Set to 1s for demonstrative purposes.
			trace.WithBatchTimeout(time.Second)),
	)
	return tracerProvider, nil
}

// Metrics creation
// Example:
// {
//   "name": "http.server.duration",
//   "unit": "ms",
//   "attributes": {
//     "http.method": "GET",
//     "http.route": "/rolldice"
//   },
//   "timestamp": 1710600000,
//   "value": 23
// }
// Example usage:
// meter := otel.Meter("dice-service")
//
// counter, _ := meter.Int64Counter("dice.rolls")
//
// counter.Add(ctx, 1) // recording here
func newMeterProvider() (*metric.MeterProvider, error) {
	metricExporter, err := stdoutmetric.New(stdoutmetric.WithPrettyPrint())
	if err != nil {
		return nil, err
	}

	meterProvider := metric.NewMeterProvider(
		metric.WithReader(metric.NewPeriodicReader(metricExporter,
			// Default is 1m. Set to 3s for demonstrative purposes.
			// creates a background goroutine that its only work is to flush aggregated data
			metric.WithInterval(3*time.Second))), // every 3 seconds it will flush
	)
	return meterProvider, nil
}

// Experimental - logging signal
func newLoggerProvider() (*log.LoggerProvider, error) {
	logExporter, err := stdoutlog.New(stdoutlog.WithPrettyPrint())
	if err != nil {
		return nil, err
	}

	loggerProvider := log.NewLoggerProvider(
		log.WithProcessor(log.NewBatchProcessor(logExporter)),
	)
	return loggerProvider, nil
}



```

---

### `rolldice.go`

```go



package main

import (
	"io"
	"math/rand"
	"net/http"
	"strconv"

	"go.opentelemetry.io/contrib/bridges/otelslog"
	"go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp"
	"go.opentelemetry.io/otel"
	"go.opentelemetry.io/otel/attribute"
	"go.opentelemetry.io/otel/metric"
)

// instrumentation lib name
const name = "go.opentelemetry.io/contrib/examples/dice"

var (
	tracer  = otel.Tracer(name)
	meter   = otel.Meter(name)
	logger  = otelslog.NewLogger(name) // logging
	rollCnt metric.Int64Counter
)

func init() { // initialization of rollCnt
	var err error
	rollCnt, err = meter.Int64Counter("dice.rolls",
		metric.WithDescription("The number of rolls by roll value"),
		metric.WithUnit("{roll}"))
	if err != nil {
		panic(err)
	}
}

func rolldice(w http.ResponseWriter, r *http.Request) {
	ctx, span := tracer.Start(r.Context(), "roll")
	defer span.End()

	roll := 1 + rand.Intn(6)

	var msg string
	if player := r.PathValue("player"); player != "" {
		msg = player + " is rolling the dice"
	} else {
		msg = "Anonymous player is rolling the dice"
	}
	logger.InfoContext(ctx, msg, "result", roll) // records result in the logging

	rollValueAttr := attribute.Int("roll.value", roll)
	span.SetAttributes(rollValueAttr) // records a span attribute

	rollCnt.Add(ctx, 1, metric.WithAttributes(rollValueAttr)) // records a measurement

	resp := strconv.Itoa(roll) + "\n"
	if _, err := io.WriteString(w, resp); err != nil {
		logger.ErrorContext(ctx, "Write failed", "error", err)
	}

	client := http.Client{ // outgoing propagation is not handled by server middleware
		Transport: otelhttp.NewTransport(http.DefaultTransport), // inject trace headers, like: propagator.Inject(ctx, headers)
	}
	req, _ := http.NewRequestWithContext(ctx, "GET", "http://localhost:8080/checkluck", nil)
	resp2, err := client.Do(req)
	if err != nil {
		logger.ErrorContext(ctx, "downstream request failed", "error", err)
	} else {
		resp2.Body.Close()
	}

	// if no otelhttp transport
	//prop := otel.GetTextMapPropagator()
	//
	//req, _ := http.NewRequestWithContext(ctx, "GET", "http://localhost:8080/checkluck", nil)
	//
	//// inject trace context into HTTP headers
	//prop.Inject(ctx, propagation.HeaderCarrier(req.Header))
	//
	//client := http.Client{}
	//resp2, err := client.Do(req)
	//if err != nil {
	//	logger.ErrorContext(ctx, "downstream request failed", "error", err)
	//} else {
	//	resp2.Body.Close()
	//}
}

func checkluck(w http.ResponseWriter, r *http.Request) {
	ctx, span := tracer.Start(r.Context(), "checkluck")
	defer span.End()

	logger.InfoContext(ctx, "checking luck")

	io.WriteString(w, "ok\n")
}

// if no otelhttp middleware
//func checkluck(w http.ResponseWriter, r *http.Request) {
//	prop := otel.GetTextMapPropagator()
//
//	// extract context from incoming headers
//	ctx := prop.Extract(r.Context(), propagation.HeaderCarrier(r.Header))
//
//	ctx, span := tracer.Start(ctx, "checkluck")
//	defer span.End()
//
//	logger.InfoContext(ctx, "checking luck")
//
//	io.WriteString(w, "ok\n")
//}



```

---

## 2\. Before OpenTelemetry: what this Go server is already teaching

Even before adding telemetry, this code already teaches several important Go concepts.

### `context.Background()`

`context.Background()` is the root context. It carries no deadline, no cancellation, and no values.

It is basically the root of a context tree.

### `signal.NotifyContext(...)`

This line:

```go


ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)


```

creates a child context that gets cancelled when `CTRL+C` sends `SIGINT`.

That means the server can use one shared cancellation signal for graceful shutdown.

### `BaseContext`

This line:

```go


BaseContext: func(net.Listener) context.Context { return ctx }


```

is subtle and important.

It means every connection accepted by the server starts from that context.

So the shape is roughly:

- `context.Background()`
  - signal-aware server context
    - request context created by `net/http`
      - child spans and downstream propagation contexts

This matters because when the root server context is cancelled, the request contexts derived from it can also be cancelled.

Or in other words:

1. `ctx` is created with `signal.NotifyContext` (cancels on CTRL+C).

2. `http.Server` is configured with:


   ```text


   BaseContext: func(net.Listener) context.Context { return ctx }


   ```

3. `srv.ListenAndServe()` starts the server.

4. Inside `Serve(listener)` the server calls:


   ```text


   baseCtx := srv.BaseContext(listener)


   ```

5. Context hierarchy:


   ```text


   ctx
     ↓
   baseCtx
     ↓
   connection context
     ↓
   request context (r.Context())


   ```

6. When CTRL+C happens, `ctx` is cancelled → all request contexts are cancelled.


### `chan error`

This line:

```go


srvErr := make(chan error, 1)


```

creates a channel of `error` values, buffered with capacity 1.

Channels are Go’s concurrency-safe way of passing values between goroutines.

This code launches the server in a goroutine and communicates the eventual error back to the main goroutine.

---

## 3\. What OpenTelemetry standardizes

One of the first useful things to understand is what OpenTelemetry actually standardizes.

It does **not** standardize the observability backend.

It standardizes the instrumentation layer:

- traces
- metrics
- logs
- propagation format

It defines:

- data models
- semantic conventions
- propagation format
- SDKs and APIs
- collectors/exporters

That means you instrument once and can send data to many backends.

---

## 4\. The three telemetry signals: traces, metrics, logs

These are not the same kind of data.

### Metrics

Metrics are aggregated numerical measurements over time.

Examples:

- request count
- latency histogram
- body size histogram
- custom counter like `dice.rolls`

Metrics answer questions like:

- how many?
- how much?
- how often?
- how fast, statistically?

### Logs

Logs are timestamped records of discrete events.

Examples:

- “Anonymous player is rolling the dice”
- “downstream request failed”
- “Write failed”

Logs answer questions like:

- what exactly happened?
- what was the message?
- what metadata came with it?

### Traces

Traces represent execution structure. A trace is made of spans. Each span is one unit of work.

Examples:

- HTTP request span
- manual `roll` span
- outgoing HTTP client span
- downstream `checkluck` span

Traces answer questions like:

- what happened during this request?
- what called what?
- where did latency happen?
- which service or component did the work?

---

## 5\. Why these three signals complement each other

This little dice app is actually a great miniature observability system.

For one request, you can get:

- a **server span** created automatically by `otelhttp`
- a **manual internal span** for the roll logic
- a **log record** linked to the trace and span
- a **metric** incremented with the roll value as an attribute
- a **downstream HTTP client span**
- a **downstream server span**
- a **downstream internal span**

That means one user request can generate a full observability graph.

---

## 6\. The OpenTelemetry SDK bootstrap

The whole SDK setup happens in `setupOTelSDK`.

This function sets four pieces of global state:

1. propagator
2. tracer provider
3. meter provider
4. logger provider

### Why tracer and meter are registered on `otel`

These are registered through:

```go


otel.SetTracerProvider(tracerProvider)
otel.SetMeterProvider(meterProvider)
otel.SetTextMapPropagator(prop)


```

because the main `otel` package acts as the global entry point for tracing, metrics, and propagation.

### Why logger uses `global.SetLoggerProvider(...)`

Logs are a bit inconsistent because logging arrived later in the OpenTelemetry Go ecosystem. That’s why the logger provider is registered through:

```go


global.SetLoggerProvider(loggerProvider)


```

instead of `otel.SetLoggerProvider(...)`.

So yes, the API is a bit uneven here.

---

## 7\. The propagator: what it is really doing

This is one of the most misunderstood parts.

### The code

```go


func newPropagator() propagation.TextMapPropagator {
	return propagation.NewCompositeTextMapPropagator(
		propagation.TraceContext{},
		propagation.Baggage{},
	)
}


```

This does **not** create spans.

It defines how trace context travels between processes.

The two components are:

- `TraceContext{}`: W3C trace context propagation ( `traceparent`, `tracestate`)
- `Baggage{}`: key-value metadata that can travel with the trace

### What propagation solves

Inside one process, trace context lives in `context.Context`.

Across processes, that context must be serialized into something transportable, usually HTTP headers.

So propagation does:

- **inject** context into a carrier, like HTTP headers
- **extract** context from a carrier, like HTTP headers

### Conceptual flow

Service A:

- create a span
- get a context containing that span
- inject the trace context into HTTP headers

Service B:

- read the HTTP headers
- extract the trace context
- start a new span from that context
- new span becomes a child in the same trace

### Why it matters

Without propagation, distributed tracing would break at service boundaries.

You’d get two separate traces instead of one causal chain.

---

## 8\. Tracer provider: spans, resources, batching

### Trace exporter

The trace exporter is:

```go


traceExporter, err := stdouttrace.New(stdouttrace.WithPrettyPrint())


```

This means finished spans are written to stdout as pretty JSON.

In production, you’d usually use OTLP and send them to an OpenTelemetry Collector or backend, not stdout.

### Resource metadata

This part is critical:

```go


res, _ := resource.Merge(
	resource.Default(),
	resource.NewWithAttributes(
		semconv.SchemaURL,
		semconv.ServiceName("dice-service"),
	),
)


```

This creates a `Resource`, which is metadata about the entity producing telemetry.

That metadata includes:

- `service.name`
- `telemetry.sdk.language`
- `telemetry.sdk.name`
- `telemetry.sdk.version`
- plus whatever `resource.Default()` can detect, like host/process/runtime information

This is **not** span-specific metadata.

It is service/process-level metadata attached to all telemetry produced by that provider.

### Batch span processor

This is also important:

```go


trace.WithBatcher(traceExporter, trace.WithBatchTimeout(time.Second))


```

This means:

- ended spans are queued
- a background goroutine batches them
- they are flushed periodically, here every second

This is why exporting spans does not block the request path directly.

### Why batching exists

If every `span.End()` directly exported over the network, overhead would be much higher.

Batching makes tracing far more practical.

---

## 9\. Meter provider: periodic flush and background goroutine

The metric provider uses:

```go


metric.NewPeriodicReader(metricExporter, metric.WithInterval(3*time.Second))


```

This means the SDK starts a background goroutine whose job is to periodically collect and export metrics.

That goroutine does not create race conditions by itself. Metric instruments and aggregators are designed to be safe for concurrent use.

### Important consequence

Metric export is periodic and aggregated.

You do **not** record a metric and immediately see one exported line per call.

Instead, many measurements are accumulated and then exported as aggregated datapoints.

That is why metrics feel very different from logs.

---

## 10\. Logger provider: the experimental logging signal

This example also sets up logging through:

```go


log.NewLoggerProvider(
	log.WithProcessor(log.NewBatchProcessor(logExporter)),
)


```

This means log records also pass through a batch processor and are exported to stdout.

This is useful because logs can be correlated with traces if they are emitted with a context containing a span.

---

## 11\. Instrumentation scope: what `otel.Tracer(name)` really means

This line often confuses people:

```go

const name = "go.opentelemetry.io/contrib/examples/dice"
tracer = otel.Tracer(name)
meter  = otel.Meter(name)
logger = otelslog.NewLogger(name)

```

The `name` here is **not** the name of a span.

It is the name of the **instrumentation scope**.

That means:

- `Tracer(name)` identifies which instrumentation source is producing spans
- `Meter(name)` identifies which instrumentation source is producing metrics
- `Logger(name)` identifies which instrumentation source is producing logs

Then later, when you do:

```go


ctx, span := tracer.Start(r.Context(), "roll")


```

the span name is `"roll"`.

So there are two separate concepts:

- instrumentation scope: who produced the telemetry
- span name: what operation happened

### InstrumentationScope vs InstrumentationLibrary

You’ll often see both in stdout output.

They represent the same concept, but `InstrumentationLibrary` is the old name and `InstrumentationScope` is the current one.

---

## 12\. Why `init()` creates `rollCnt`

This line can look weird at first:

```go


func init() {
	var err error
	rollCnt, err = meter.Int64Counter("dice.rolls",
		metric.WithDescription("The number of rolls by roll value"),
		metric.WithUnit("{roll}"))
	if err != nil {
		panic(err)
	}
}


```

It does not record any metric yet.

It creates the **metric instrument**.

Then later, inside the handler, the actual measurement is recorded:

```go


rollCnt.Add(ctx, 1, metric.WithAttributes(rollValueAttr))


```

So the lifecycle is:

1. define the instrument once
2. record measurements with it many times

That is why `rollCnt` is created in `init()` and used later in the request path.

---

## 13\. The middleware-created HTTP span vs the manual `roll` span

This is one of the most important ideas in the whole integration.

### Middleware span

Because the server is wrapped with:

```go


otelhttp.NewHandler(mux, "dice-server")


```

incoming requests automatically get a **SERVER span** representing the HTTP request.

That span contains HTTP request/response metadata.

### Manual span

Inside `rolldice`, this line:

```go


ctx, span := tracer.Start(r.Context(), "roll")


```

creates another span.

Because it uses `r.Context()`, which already contains the middleware-created HTTP span, the new span becomes a **child span**.

So the shape is:

- SERVER span: HTTP request
  - INTERNAL span: `roll`

This is not duplication. It is correct layering.

### Why both exist

They represent different abstraction levels.

The HTTP span tells you:

- method
- path
- status code
- client address
- protocol
- request duration

The internal `roll` span tells you:

- what the application did
- custom attributes like `roll.value`

Without the HTTP span, you lose transport-level observability.

Without the `roll` span, you lose business-level observability.

---

## 14\. Outgoing propagation: why the client transport matters

This part also trips people up.

### Server middleware handles extraction, not outgoing injection

`otelhttp.NewHandler(...)` handles incoming requests. That means it:

- extracts incoming trace headers
- creates a SERVER span
- attaches it to `r.Context()`

But it does **not** instrument your outgoing HTTP client calls.

### That is why this matters

```go


client := http.Client{
	Transport: otelhttp.NewTransport(http.DefaultTransport),
}


```

This transport does two things for outgoing HTTP requests:

1. it creates a CLIENT span
2. it injects the trace headers into the outgoing request

So yes, the server middleware does not handle outgoing injection, which is why the instrumented client transport is necessary.

### Manual alternative

If you didn’t use `otelhttp.NewTransport(...)`, you could manually call:

```go


prop := otel.GetTextMapPropagator()
prop.Inject(ctx, propagation.HeaderCarrier(req.Header))


```

But with `otelhttp.NewTransport(...)`, injection becomes automatic.

---

## 15\. The full trace structure of one request

With the current code, one request to `/rolldice` can produce something like this:

- SERVER span: incoming `GET /rolldice`
  - INTERNAL span: `roll`
    - CLIENT span: outgoing `GET /checkluck`
      - SERVER span: incoming `GET /checkluck`
        - INTERNAL span: `checkluck`

This is exactly what distributed tracing is for.

You can reconstruct the causal execution path across boundaries.

---

## 16\. The log line: why the result is recorded there

This line:

```go


logger.InfoContext(ctx, msg, "result", roll)


```

looks slightly silly in a dice app, but it is pedagogically useful.

It demonstrates structured logs correlated with traces.

That call produces:

- a log message body
- a structured attribute `result`
- the current `TraceID`
- the current `SpanID`

So logs become attached to trace context.

This is the point of emitting it through `InfoContext(ctx, ...)`.

---

## 17\. Annotated log output

Here is the log output, annotated.

```json


// produced by
// logger.InfoContext(ctx, msg, "result", roll)
// because i used:
// otelslog.NewLogger(name) - OtelSlog bridge

{
	"Timestamp": "2026-03-16T18:53:46.572644843+01:00", // when the event happened
	"ObservedTimestamp": "2026-03-16T18:53:46.572649253+01:00", // when the telemetry system saw it
	"Severity": 9,
	"SeverityText": "INFO",
	"Body": {
		"Type": "String",
		"Value": "Anonymous player is rolling the dice"
	},
	"Attributes": [
		{
			"Key": "result",
			"Value": {
				"Type": "Int64",
				"Value": 4
			}
		}
	],
	"TraceID": "19d4dc19c4ce8defe07d6b38e08355d2",
	"SpanID": "ab4b3a85ecb35ec4",
	"TraceFlags": "01",
	"Resource": [
		{
			"Key": "service.name",
			"Value": {
				"Type": "STRING",
				"Value": "unknown_service:dice"
			}
		},
		{
			"Key": "telemetry.sdk.language",
			"Value": {
				"Type": "STRING",
				"Value": "go"
			}
		},
		{
			"Key": "telemetry.sdk.name",
			"Value": {
				"Type": "STRING",
				"Value": "opentelemetry"
			}
		},
		{
			"Key": "telemetry.sdk.version",
			"Value": {
				"Type": "STRING",
				"Value": "1.42.0"
			}
		}
	],
	"Scope": {
		"Name": "go.opentelemetry.io/contrib/examples/dice",
		"Version": "",
		"SchemaURL": "",
		"Attributes": {}
	},
	"DroppedAttributes": 0
}


```

### What it means

- `Timestamp`: when the log event happened
- `ObservedTimestamp`: when the telemetry pipeline observed it
- `Severity`: numeric severity code
- `SeverityText`: human-readable severity
- `Body`: main log message
- `Attributes`: structured log fields, here `result=4`
- `TraceID` and `SpanID`: direct trace correlation
- `Resource`: service/process/runtime metadata
- `Scope`: instrumentation scope
- `DroppedAttributes`: how many log attributes were dropped due to limits

### Why `service.name` is `unknown_service:dice` here

Your tracer provider is configured with an explicit resource, but the logger provider in the current code does not attach the same custom resource.

That’s why logs and metrics may show `unknown_service:dice` instead of `dice-service`.

If you want perfect consistency, the logger provider and meter provider should be configured with the same explicit resource as the tracer provider.

---

## 18\. Annotated metric output

Here is the metric export.

```json


{
	"Resource": [
		{
			"Key": "service.name",
			"Value": {
				"Type": "STRING",
				"Value": "unknown_service:dice"
			}
		},
		{
			"Key": "telemetry.sdk.language",
			"Value": {
				"Type": "STRING",
				"Value": "go"
			}
		},
		{
			"Key": "telemetry.sdk.name",
			"Value": {
				"Type": "STRING",
				"Value": "opentelemetry"
			}
		},
		{
			"Key": "telemetry.sdk.version",
			"Value": {
				"Type": "STRING",
				"Value": "1.42.0"
			}
		}
	],
	"ScopeMetrics": [
		{
			"Scope": {
				"Name": "go.opentelemetry.io/contrib/examples/dice",
				"Version": "",
				"SchemaURL": "",
				"Attributes": null
			},
			"Metrics": [
				{
					"Name": "dice.rolls",
					"Description": "The number of rolls by roll value",
					"Unit": "{roll}",
					"Data": {
						"DataPoints": [
							{
								"Attributes": [
									{
										"Key": "roll.value",
										"Value": {
											"Type": "INT64",
											"Value": 5
										}
									}
								],
								"StartTime": "2026-03-16T18:53:40.989159464+01:00",
								"Time": "2026-03-16T18:53:46.990082501+01:00",
								"Value": 2,
								"Exemplars": [
									{
										"FilteredAttributes": null,
										"Time": "2026-03-16T18:53:45.886435685+01:00",
										"Value": 1,
										"SpanID": "YPl/LDRkDss=",
										"TraceID": "NVpSfS8jIMVMmy1PK7JBdg=="
									},
									{
										"FilteredAttributes": null,
										"Time": "2026-03-16T18:53:46.388663502+01:00",
										"Value": 1,
										"SpanID": "JgqKPaqlNeA=",
										"TraceID": "p+ZSBy3a4TLsi+5W19+cqg=="
									}
								]
							},
							{
								"Attributes": [
									{
										"Key": "roll.value",
										"Value": {
											"Type": "INT64",
											"Value": 1
										}
									}
								],
								"StartTime": "2026-03-16T18:53:40.989159464+01:00",
								"Time": "2026-03-16T18:53:46.990082501+01:00",
								"Value": 2,
								"Exemplars": [
									{
										"FilteredAttributes": null,
										"Time": "2026-03-16T18:53:44.446866885+01:00",
										"Value": 1,
										"SpanID": "RlfZ2MALr7U=",
										"TraceID": "o3XejQBHnNusyA1WE45WlQ=="
									},
									{
										"FilteredAttributes": null,
										"Time": "2026-03-16T18:53:46.149389985+01:00",
										"Value": 1,
										"SpanID": "ICvfO3v8fBM=",
										"TraceID": "LUwjVswDPS9wWH8G//4BeA=="
									}
								]
							},
							{
								"Attributes": [
									{
										"Key": "roll.value",
										"Value": {
											"Type": "INT64",
											"Value": 4
										}
									}
								],
								"StartTime": "2026-03-16T18:53:40.989159464+01:00",
								"Time": "2026-03-16T18:53:46.990082501+01:00",
								"Value": 1,
								"Exemplars": [
									{
										"FilteredAttributes": null,
										"Time": "2026-03-16T18:53:46.572661163+01:00",
										"Value": 1,
										"SpanID": "q0s6heyzXsQ=",
										"TraceID": "GdTcGcTOje/gfWs44INV0g=="
									}
								]
							}
						],
						"Temporality": "CumulativeTemporality",
						"IsMonotonic": true
					}
				}
			]
		},
		{
			"Scope": {
				"Name": "go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp",
				"Version": "0.67.0",
				"SchemaURL": "",
				"Attributes": null
			},
			"Metrics": [
				{
					"Name": "http.server.request.body.size",
					"Description": "Size of HTTP server request bodies.",
					"Unit": "By",
					"Data": {
						"DataPoints": [
							{
								"Attributes": [
									{
										"Key": "http.request.method",
										"Value": {
											"Type": "STRING",
											"Value": "GET"
										}
									},
									{
										"Key": "http.response.status_code",
										"Value": {
											"Type": "INT64",
											"Value": 200
										}
									},
									{
										"Key": "network.protocol.name",
										"Value": {
											"Type": "STRING",
											"Value": "http"
										}
									},
									{
										"Key": "network.protocol.version",
										"Value": {
											"Type": "STRING",
											"Value": "1.1"
										}
									},
									{
										"Key": "server.address",
										"Value": {
											"Type": "STRING",
											"Value": "localhost"
										}
									},
									{
										"Key": "server.port",
										"Value": {
											"Type": "INT64",
											"Value": 8080
										}
									},
									{
										"Key": "url.scheme",
										"Value": {
											"Type": "STRING",
											"Value": "http"
										}
									}
								],
								"StartTime": "2026-03-16T18:53:40.989651691+01:00",
								"Time": "2026-03-16T18:53:46.990114041+01:00",
								"Count": 5,
								"Bounds": [
									0,
									5,
									10,
									25,
									50,
									75,
									100,
									250,
									500,
									750,
									1000,
									2500,
									5000,
									7500,
									10000
								],
								"BucketCounts": [
									5,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0
								],
								"Min": 0,
								"Max": 0,
								"Sum": 0,
								"Exemplars": [
									{
										"FilteredAttributes": null,
										"Time": "2026-03-16T18:53:46.572678723+01:00",
										"Value": 0,
										"SpanID": "TKqdI4xhWho=",
										"TraceID": "GdTcGcTOje/gfWs44INV0g=="
									}
								]
							}
						],
						"Temporality": "CumulativeTemporality"
					}
				},
				{
					"Name": "http.server.response.body.size",
					"Description": "Size of HTTP server response bodies.",
					"Unit": "By",
					"Data": {
						"DataPoints": [
							{
								"Attributes": [
									{
										"Key": "http.request.method",
										"Value": {
											"Type": "STRING",
											"Value": "GET"
										}
									},
									{
										"Key": "http.response.status_code",
										"Value": {
											"Type": "INT64",
											"Value": 200
										}
									},
									{
										"Key": "network.protocol.name",
										"Value": {
											"Type": "STRING",
											"Value": "http"
										}
									},
									{
										"Key": "network.protocol.version",
										"Value": {
											"Type": "STRING",
											"Value": "1.1"
										}
									},
									{
										"Key": "server.address",
										"Value": {
											"Type": "STRING",
											"Value": "localhost"
										}
									},
									{
										"Key": "server.port",
										"Value": {
											"Type": "INT64",
											"Value": 8080
										}
									},
									{
										"Key": "url.scheme",
										"Value": {
											"Type": "STRING",
											"Value": "http"
										}
									}
								],
								"StartTime": "2026-03-16T18:53:40.989655211+01:00",
								"Time": "2026-03-16T18:53:46.990121631+01:00",
								"Count": 5,
								"Bounds": [
									0,
									5,
									10,
									25,
									50,
									75,
									100,
									250,
									500,
									750,
									1000,
									2500,
									5000,
									7500,
									10000
								],
								"BucketCounts": [
									0,
									5,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0
								],
								"Min": 2,
								"Max": 2,
								"Sum": 10,
								"Exemplars": [
									{
										"FilteredAttributes": null,
										"Time": "2026-03-16T18:53:46.572680173+01:00",
										"Value": 2,
										"SpanID": "TKqdI4xhWho=",
										"TraceID": "GdTcGcTOje/gfWs44INV0g=="
									}
								]
							}
						],
						"Temporality": "CumulativeTemporality"
					}
				},
				{
					"Name": "http.server.request.duration",
					"Description": "Duration of HTTP server requests.",
					"Unit": "s",
					"Data": {
						"DataPoints": [
							{
								"Attributes": [
									{
										"Key": "http.request.method",
										"Value": {
											"Type": "STRING",
											"Value": "GET"
										}
									},
									{
										"Key": "http.response.status_code",
										"Value": {
											"Type": "INT64",
											"Value": 200
										}
									},
									{
										"Key": "network.protocol.name",
										"Value": {
											"Type": "STRING",
											"Value": "http"
										}
									},
									{
										"Key": "network.protocol.version",
										"Value": {
											"Type": "STRING",
											"Value": "1.1"
										}
									},
									{
										"Key": "server.address",
										"Value": {
											"Type": "STRING",
											"Value": "localhost"
										}
									},
									{
										"Key": "server.port",
										"Value": {
											"Type": "INT64",
											"Value": 8080
										}
									},
									{
										"Key": "url.scheme",
										"Value": {
											"Type": "STRING",
											"Value": "http"
										}
									}
								],
								"StartTime": "2026-03-16T18:53:40.989660941+01:00",
								"Time": "2026-03-16T18:53:46.990125021+01:00",
								"Count": 5,
								"Bounds": [
									0.005,
									0.01,
									0.025,
									0.05,
									0.075,
									0.1,
									0.25,
									0.5,
									0.75,
									1,
									2.5,
									5,
									7.5,
									10
								],
								"BucketCounts": [
									5,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0,
									0
								],
								"Min": 0.000056511,
								"Max": 0.000122582,
								"Sum": 0.000395567,
								"Exemplars": [
									{
										"FilteredAttributes": null,
										"Time": "2026-03-16T18:53:46.572681863+01:00",
										"Value": 0.000074441,
										"SpanID": "TKqdI4xhWho=",
										"TraceID": "GdTcGcTOje/gfWs44INV0g=="
									}
								]
							}
						],
						"Temporality": "CumulativeTemporality"
					}
				}
			]
		}
	]
}


```

### What this shows

#### Custom metric

The first metric scope contains your custom metric:

- `dice.rolls`

This is your `Int64Counter`.

Each datapoint is grouped by the metric attribute `roll.value`.

So:

- `roll.value=5` with `Value=2` means two rolls produced a 5
- `roll.value=1` with `Value=2` means two rolls produced a 1
- `roll.value=4` with `Value=1` means one roll produced a 4

#### Why `roll.value` appears both in spans and metrics

Because you intentionally attach the same semantic value to two different telemetry signals.

- in the span, `roll.value` is metadata about one operation
- in the metric, `roll.value` is a dimension used to group datapoints

This is good because it creates a shared vocabulary across telemetry.

#### Exemplars

The exemplars are fascinating.

They connect a metric datapoint back to concrete traces:

- a metric sample includes `SpanID`
- and `TraceID`

That means metrics can point back to specific traces.

This is one of the elegant bridges between statistical telemetry and per-request telemetry.

#### Auto-generated HTTP metrics

The second metric scope comes from `otelhttp`.

It contains histogram metrics like:

- `http.server.request.body.size`
- `http.server.response.body.size`
- `http.server.request.duration`

These were not created manually by you.

They are automatic metrics emitted by HTTP instrumentation.

---

## 19\. Histograms: bounds, buckets, min, max, sum

The histogram output is very often confusing the first time you see it.

### Bounds

`Bounds` define the histogram bucket boundaries.

For example:

- `0`
- `5`
- `10`
- `25`
- `50`
- ...

These are predefined bucket upper bounds.

They are **not** dynamically centered around your observed values.

### BucketCounts

`BucketCounts` tell you how many values fell into each bucket.

For example, this request body size histogram:

- `Count = 5`
- `Bounds = [0, 5, 10, ...]`
- `BucketCounts = [5, 0, 0, ...]`

means:

- all 5 observed values were in the first bucket `<= 0`

That makes sense because GET requests usually have empty request bodies.

### Min / Max / Sum

These are exactly what they look like:

- `Min`: smallest observed value
- `Max`: largest observed value
- `Sum`: total of all values

For response size:

- `Min = 2`
- `Max = 2`
- `Sum = 10`
- `Count = 5`

That means you served five responses, each 2 bytes long, for a total of 10 bytes.

### Why there are several histograms

You are not seeing “three histograms for one metric”.

You are seeing **three distinct HTTP metrics**, each aggregated as a histogram:

- request body size
- response body size
- request duration

That is why you see three different histogram structures.

---

## 20\. Annotated internal span output

Here is the manual internal span for `roll`.

```json


{
	"Name": "roll",
	"SpanContext": {
		"TraceID": "2d4c2356cc033d2f70587f06fffe0178",
		"SpanID": "202bdf3b7bfc7c13",
		"TraceFlags": "01",
		"TraceState": "",
		"Remote": false
	},
	"Parent": { // parent span created by the middleware
		"TraceID": "2d4c2356cc033d2f70587f06fffe0178",
		"SpanID": "654e9bbe7191de44",
		"TraceFlags": "01",
		"TraceState": "",
		"Remote": false
	},
	"SpanKind": 1,
	"StartTime": "2026-03-16T18:53:46.149362124+01:00",
	"EndTime": "2026-03-16T18:53:46.149393525+01:00",
	"Attributes": [
		{
			"Key": "roll.value",
			"Value": {
				"Type": "INT64",
				"Value": 1
			}
		}
	],
	"Events": null,
	"Links": null,
	"Status": {
		"Code": "Unset",
		"Description": ""
	},
	"DroppedAttributes": 0,
	"DroppedEvents": 0,
	"DroppedLinks": 0,
	"ChildSpanCount": 0,
	"Resource": [
		{
			"Key": "service.name",
			"Value": {
				"Type": "STRING",
				"Value": "dice-service"
			}
		},
		{
			"Key": "telemetry.sdk.language",
			"Value": {
				"Type": "STRING",
				"Value": "go"
			}
		},
		{
			"Key": "telemetry.sdk.name",
			"Value": {
				"Type": "STRING",
				"Value": "opentelemetry"
			}
		},
		{
			"Key": "telemetry.sdk.version",
			"Value": {
				"Type": "STRING",
				"Value": "1.42.0"
			}
		}
	],
	"InstrumentationScope": {
		"Name": "go.opentelemetry.io/contrib/examples/dice",
		"Version": "",
		"SchemaURL": "",
		"Attributes": null
	},
	"InstrumentationLibrary": {
		"Name": "go.opentelemetry.io/contrib/examples/dice",
		"Version": "",
		"SchemaURL": "",
		"Attributes": null
	}
}


```

### What this means

#### `SpanContext`

Contains the current span identity.

- `TraceID`: identifies the whole trace
- `SpanID`: identifies this specific span
- `TraceFlags`: includes sampling info

#### `Parent`

This span has a parent because it was started from `r.Context()` and `r.Context()` already contained the HTTP middleware span.

So yes: the `Parent` field is there because your manual `roll` span is nested under the middleware-created request span.

#### `SpanKind`

`1` means `INTERNAL`.

OpenTelemetry span kind values are:

- `0`: UNSPECIFIED
- `1`: INTERNAL // like the one coming from actual handlers: rolldice - checkluck
- `2`: SERVER // like the one coming from the otelhttp midleware
- `3`: CLIENT
- `4`: PRODUCER
- `5`: CONSUMER

Your `roll` span is application logic inside the service, so `INTERNAL` is correct.

#### `Events`

Events are timestamped annotations inside the span. Here there are none.

If you had called `span.AddEvent("cache_miss")`, they would appear here.

#### `Links`

Links connect spans that are related but not parent/child. This is common in async systems like queues.

#### `Status`

This is application-level span status.

`Unset` means no explicit status was set.

`OK` → The operation completed successfully.

`ERROR` → The operation failed.

`UNSET` → No explicit status was set.

Important nuance

In OpenTelemetry’s semantic conventions:

-\> Success does NOT require OK.

The recommended pattern is:

- Leave status UNSET for normal operations

- Set ERROR when something fails


If you had done something like `span.SetStatus(codes.Error, "database timeout")`, it would show up here.

#### `DroppedAttributes`, `DroppedEvents`, `DroppedLinks`

These counters show whether the SDK dropped excess attributes, events, or links due to limits.

#### `ChildSpanCount`

This counts **direct children**, not grandchildren.

It is not the full subtree size.

Internally, the SDK can update this when child spans are started with this span as parent. The batch exporter then flushes already-computed span data.

The source of truth for trace reconstruction is still:

- `TraceID`
- `SpanID`
- `ParentSpanID`

not `ChildSpanCount`.

#### `Resource`

This is metadata about the service/process producing the span.

#### `InstrumentationScope`

This says which instrumentation source created the span.

For your manual span, the scope is your own dice package instrumentation name.

---

## 21\. Annotated server span output

Here is the middleware-created SERVER span.

```json


{
	"Name": "/",
	"SpanContext": {
		"TraceID": "31a1f15a06bbb44571cb33219dcb7f22", // 16 bytes
		"SpanID": "93802ddd3b3272ae", // 8 bytes
		"TraceFlags": "01",
		"TraceState": "",
		"Remote": false
	},
	"Parent": {
		"TraceID": "00000000000000000000000000000000", // 16 bytes - this span has no parent, so it is zeroed
		"SpanID": "0000000000000000", // 8 bytes
		"TraceFlags": "00",
		"TraceState": "",
		"Remote": false
	},
	"SpanKind": 2,
	"StartTime": "2026-03-16T18:39:56.865384074+01:00",
	"EndTime": "2026-03-16T18:39:56.865453734+01:00",
	"Attributes": [ // automatically set by otelhttp - standard attrs defined by OpenTelemetry HTTP Semantic conventions
		{
			"Key": "server.address",
			"Value": {
				"Type": "STRING",
				"Value": "localhost"
			}
		},
		{
			"Key": "http.request.method",
			"Value": {
				"Type": "STRING",
				"Value": "GET"
			}
		},
		{
			"Key": "url.scheme",
			"Value": {
				"Type": "STRING",
				"Value": "http"
			}
		},
		{
			"Key": "server.port",
			"Value": {
				"Type": "INT64",
				"Value": 8080
			}
		},
		{
			"Key": "network.peer.address",
			"Value": {
				"Type": "STRING",
				"Value": "127.0.0.1"
			}
		},
		{
			"Key": "network.peer.port", // TCP port of the client - may change for each conn, that is an ephemeral port
			"Value": {
				"Type": "INT64",
				"Value": 43812
			}
		},
		{
			"Key": "user_agent.original",
			"Value": {
				"Type": "STRING",
				"Value": "Mozilla/5.0 (X11; Linux x86_64; rv:148.0) Gecko/20100101 Firefox/148.0"
			}
		},
		{
			"Key": "client.address",
			"Value": {
				"Type": "STRING",
				"Value": "127.0.0.1"
			}
		},
		{
			"Key": "url.path",
			"Value": {
				"Type": "STRING",
				"Value": "/rolldice"
			}
		},
		{
			"Key": "network.protocol.version",
			"Value": {
				"Type": "STRING",
				"Value": "1.1"
			}
		},
		{
			"Key": "http.response.body.size",
			"Value": {
				"Type": "INT64",
				"Value": 19
			}
		},
		{
			"Key": "http.response.status_code",
			"Value": {
				"Type": "INT64",
				"Value": 200
			}
		}
	],
	"Events": null,
	"Links": null,
	"Status": {
		"Code": "Unset",
		"Description": ""
	},
	"DroppedAttributes": 0,
	"DroppedEvents": 0,
	"DroppedLinks": 0,
	"ChildSpanCount": 0,
	"Resource": [
		{
			"Key": "service.name",
			"Value": {
				"Type": "STRING",
				"Value": "dice-service"
			}
		},
		{
			"Key": "telemetry.sdk.language",
			"Value": {
				"Type": "STRING",
				"Value": "go"
			}
		},
		{
			"Key": "telemetry.sdk.name",
			"Value": {
				"Type": "STRING",
				"Value": "opentelemetry"
			}
		},
		{
			"Key": "telemetry.sdk.version",
			"Value": {
				"Type": "STRING",
				"Value": "1.42.0"
			}
		}
	],
	"InstrumentationScope": {
		"Name": "go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp",
		"Version": "0.67.0",
		"SchemaURL": "",
		"Attributes": null
	},
	"InstrumentationLibrary": { // same as InstrumentationScope, just deprecated
		"Name": "go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp",
		"Version": "0.67.0",
		"SchemaURL": "",
		"Attributes": null
	}
}


```

### What this means

#### Root span and zero parent IDs

This span has no parent.

That is why its parent trace/span IDs are all zeros.

OpenTelemetry uses zero IDs to represent an invalid or absent parent context.

#### Why `TraceID` is longer than `SpanID`

- `TraceID` is 16 bytes = 128 bits
- `SpanID` is 8 bytes = 64 bits

Hex encoding means:

- 16 bytes -> 32 hex characters
- 8 bytes -> 16 hex characters

Trace IDs need more global uniqueness than span IDs.

#### `SpanKind = 2`

This is a `SERVER` span.

That is correct because this span represents the server handling an incoming HTTP request.

#### Standard HTTP attributes

These attributes were not manually added by you.

They were automatically attached by `otelhttp` using OpenTelemetry’s HTTP semantic conventions.

Examples:

- `http.request.method`
- `http.response.status_code`
- `server.address`
- `url.path`
- `network.peer.address`

#### `network.peer.port`

This is the client-side TCP port of the connection.

It is often an ephemeral port chosen by the client OS. It may change from request to request.

#### `InstrumentationScope`

This span was produced by `otelhttp`, so the scope is the `otelhttp` instrumentation package, not your dice package.

---

## 22\. What the middleware actually automates

### On the server side

`otelhttp.NewHandler(...)` automatically does:

- extract trace context from incoming headers
- create a SERVER span
- attach it to the request context
- set standard HTTP span attributes
- emit standard HTTP metrics

### On the client side

`otelhttp.NewTransport(...)` automatically does:

- create a CLIENT span
- inject trace context into outgoing request headers

This distinction matters.

The server middleware handles **incoming extraction**.

The instrumented client transport handles **outgoing injection**.

---

## 23\. Why the manual `checkluck` span is still correct

Inside `checkluck`, you do:

```go


ctx, span := tracer.Start(r.Context(), "checkluck")


```

This does **not** override the middleware span.

It creates another child span.

So the downstream request has:

- a SERVER span created automatically by the middleware
- an INTERNAL `checkluck` span created manually by your code

Again, this is the correct transport/business-logic layering.

---

## 24\. Span kinds beyond INTERNAL, SERVER, CLIENT

The example uses:

- `INTERNAL`
- `SERVER`
- `CLIENT`

But OpenTelemetry also defines:

- `PRODUCER`
- `CONSUMER`

These are for asynchronous systems like queues or event buses.

### `PRODUCER`

Used when publishing a message into a queue or topic.

### `CONSUMER`

Used when receiving or processing a message from a queue or topic.

This is different from `CLIENT`/ `SERVER` because async messaging is not request/response in the same instant.

---

## 25\. What this whole example teaches structurally

This dice app shows nearly the full OpenTelemetry mental model in miniature.

### Service-level metadata

Defined by `Resource`.

### Instrumentation source identity

Defined by instrumentation scope.

### Request-level work

Represented by spans.

### Discrete event-level detail

Represented by logs.

### Statistical aggregates

Represented by metrics.

### Cross-service continuity

Represented by propagators and automatic header injection/extraction.

---

## 26\. The most useful mental model I ended up with

This is the model that made the whole thing click for me.

### Context in Go

`context.Context` is the vehicle that carries:

- cancellation
- deadlines
- trace context
- baggage

### Middleware spans

These represent transport-level boundaries.

### Manual spans

These represent business logic inside the service.

### Propagation

This serializes trace context into headers and reconstructs it on the other side.

### Metrics

These aggregate measurements over time and flush in the background.

### Logs

These record timestamped events and can be attached to traces if they use a context containing a span.

---

## 27\. A compact trace tree for this app

The full execution shape can be summarized as:

- SERVER span: `GET /rolldice`
  - INTERNAL span: `roll`
    - log: `"Anonymous player is rolling the dice"`, `result=4`
    - metric increment: `dice.rolls{roll.value=4}`
    - CLIENT span: `GET /checkluck`
      - SERVER span: `GET /checkluck`
        - INTERNAL span: `checkluck`
          - log: `"checking luck"`

That is a lot of observability from a tiny amount of code.

---

## 28\. What was genuinely surprising to me

A few things were much clearer after digging through the output.

### 1\. The middleware and manual spans are supposed to coexist

They are not duplicates. They represent different layers.

### 2\. Propagation is mostly invisible once instrumentation is correct

It feels abstract until you see it in action with a downstream HTTP call.

### 3\. Metrics are much less “event-like” than logs or spans

They are aggregated snapshots, often exported periodically.

### 4\. The stdout output is verbose but actually very educational

It exposes the raw data model.

### 5\. Resource and instrumentation scope are easy to confuse

But they answer different questions:

- Resource: who produced the telemetry
- Scope: which library/instrumentation produced it

---

## 29\. Things I would improve in this example

A few practical improvements would make the example stronger.

### Use the same explicit resource for traces, metrics, and logs

That would avoid `unknown_service:dice` in some outputs and `dice-service` in others.

### Reuse the HTTP client

The client could be a package-level variable instead of recreated per request.

### Handle errors from `http.NewRequestWithContext(...)` and `io.WriteString(...)` more thoroughly

The code is a demo, so it cuts corners.

### Possibly rename some comments

For example “automatic injection by middleware” should be distinguished between:

- server extraction by server middleware
- client injection by instrumented transport

---

## 30\. Final takeaway

What looked messy at first turned out to be fairly coherent once I mapped each piece to its responsibility.

### Go gives you the control flow primitives

- contexts
- goroutines
- channels
- graceful shutdown

### OpenTelemetry layers observability on top of that

- tracer provider for spans
- meter provider for metrics
- logger provider for logs
- propagator for cross-process trace continuity

### `otelhttp` then automates the transport layer

- server-side extraction and SERVER spans
- client-side injection and CLIENT spans

And once you understand that separation, the whole model becomes much easier to reason about.

---

## 31\. The shortest summary possible

If I had to compress the whole day into a few lines:

- `context.Context` carries cancellation and trace context
- `otelhttp.NewHandler(...)` extracts incoming trace context and creates SERVER spans
- `tracer.Start(r.Context(), "roll")` creates a child INTERNAL span
- `otelhttp.NewTransport(...)` injects outgoing trace headers and creates CLIENT spans
- logs become trace-aware when emitted with `InfoContext(ctx, ...)`
- metrics are aggregated and flushed in the background
- stdout exporters expose the raw OpenTelemetry data model
- `Resource` identifies the service
- `InstrumentationScope` identifies which instrumentation created telemetry
- propagation is what turns separate services into one distributed trace

That was the missing mental model.

---

## 32\. Closing note

If you are reading OpenTelemetry Go examples and feel that the code looks more magical than explanatory, you’re not crazy.

A lot of the important behavior is hidden behind:

- `context.Context`
- middleware
- instrumented transports
- SDK background workers

Once you inspect the stdout spans, logs, and metrics carefully, the model finally becomes concrete.

And after that, the API starts to feel much less mysterious.