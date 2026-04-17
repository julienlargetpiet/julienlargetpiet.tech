All code excerpts below are **highlights** of the full implementation.
See the complete source on GitHub:
[julienlargetpiet/HTTP\_Server](https://github.com/julienlargetpiet/HTTP_Server).


## Why write your own server?

When you think of writing an HTTP server in Rust, the obvious choices are production-grade stacks like
Hyper, Actix-Web, or Warp. They’re excellent—and in production you should likely use them.
But building a server from first principles forces you to understand what actually happens:
accepting sockets, parsing a protocol, and coordinating concurrency safely.


## Beginner-friendly intro: HTTP and Rust in 5 minutes

### What an HTTP server really does

- **Listen** on a TCP port for incoming connections.
- **Parse** each incoming byte stream into a structured HTTP request (method, path, version, headers, body).
- **Respond** with a valid HTTP response (status line, headers, body).

### Why Rust helps

- **Ownership & borrowing** ensure memory safety without a GC.
- **Zero-cost abstractions** keep overhead predictable for I/O-heavy code.
- **Send/Sync guarantees** and types like `Arc<T>` and `Mutex<T>` help you write correct concurrent code.

## Design overview (deep-dive)

The server is intentionally minimal: it uses the standard library to accept TCP connections,
a simple parser to transform raw bytes into a request, and a response builder to serialize a reply.
State that must live across requests (e.g., sessions) is kept behind thread-safe primitives.


### 1) Bootstrapping the listener

At its core, an HTTP server is a loop around a `TcpListener`:

```rust

use std::net::TcpListener;
use std::io::Result;

fn main() -> Result<()> {
    let listener = TcpListener::bind("127.0.0.1:8080")?;
    println!("Server running at http://127.0.0.1:8080");

    for stream in listener.incoming() {
        let stream = match stream {
            Ok(s) => s,
            Err(e) => {
                eprintln!("Failed to accept connection: {e}");
                continue;
            }
        };
        handle_connection(stream); // highlight: see repo for full function
    }
    Ok(())
}

```

### 2) Parsing HTTP/1.1 by hand

A raw request is a sequence of bytes terminated by CRLFs. The minimum viable parser:
split the request line, collect headers until a blank line, then read the body (if any)
based on `Content-Length`.


```rust

struct Request {
    method: String,
    path: String,
    version: String,
    headers: Vec<(String, String)>,
    body: Vec<u8>,
}

// highlight: simplified; see repo for full parser
fn parse_request(buf: &[u8]) -> Option<Request> {
    let text = std::str::from_utf8(buf).ok()?;
    let mut lines = text.split("\r\n");

    let request_line = lines.next()?;
    let mut parts = request_line.split_whitespace();
    let method = parts.next()?.to_string();
    let path = parts.next()?.to_string();
    let version = parts.next()?.to_string();

    let mut headers = Vec::new();
    for line in &mut lines {
        if line.is_empty() { break; }
        if let Some((k, v)) = line.split_once(":") {
            headers.push((k.trim().to_string(), v.trim().to_string()));
        }
    }

    Some(Request { method, path, version, headers, body: Vec::new() })
}

```

### Dynamic resources: serving files and images

Once the request is parsed, the `path` field tells the server what resource is being requested.
A simple router can check if the path corresponds to a dynamic resource, such as an image, CSS file, or any static asset.


```rust

fn handle_request(req: Request) -> Vec<u8> {
    match req.path.as_str() {
        "/" => make_response("200 OK", b"Hello, world!"),
        p if p.starts_with("/images/") => {
            // highlight: load dynamic file from disk
            if let Ok(bytes) = std::fs::read(&p[1..]) {
                make_response("200 OK", &bytes)
            } else {
                make_response("404 Not Found", b"File not found")
            }
        }
        p if p.starts_with("/files/") => {
            if let Ok(bytes) = std::fs::read(&p[1..]) {
                make_response("200 OK", &bytes)
            } else {
                make_response("404 Not Found", b"File not found")
            }
        }
        _ => make_response("404 Not Found", b"Resource not found"),
    }
}

```

This approach lets you use the same parsing logic to redirect requests to dynamic resources.
For example, a request to `/images/logo.png` can directly return the file from disk.
Although simple, it demonstrates how low-level parsing empowers you to build your own static or dynamic file serving system without a framework.


### 3) Building responses

Responses mirror requests: a status line, headers, and an optional body. Always include a
`Content-Length` for HTTP/1.1 unless you use chunked transfer encoding.


```rust

fn make_response(status: &str, body: &[u8]) -> Vec<u8> {
    let headers = format!(
        "HTTP/1.1 {status}\r\nContent-Length: {}\r\nConnection: close\r\n\r\n",
        body.len()
    );
    let mut out = headers.into_bytes();
    out.extend_from_slice(body);
    out
}

```

### 4) Concurrency model

The simplest approach is a thread-per-connection. For better control, add a thread pool.
Shared state (e.g., a set of session tokens) can be wrapped in `Arc<Mutex<...>>`.


```rust

use std::sync::{Arc, Mutex};
use std::collections::HashSet;

// highlight: shared session store
type Token = [u8; 32];

struct AppState {
    sessions: Mutex<HashSet<Token>>,
}

fn main() {
    let state = Arc::new(AppState { sessions: Mutex::new(HashSet::new()) });
    // pass `state.clone()` into each connection handler
}

```

### 5) Session/token handling

Tokens can be issued on login and validated per request. This example demonstrates the pattern,
not the full security story (e.g., expiry, secure storage, signing).


```rust

fn issue_token(state: &Arc<AppState>) -> Token {
    use rand::RngCore;
    let mut t = [0u8; 32];
    rand::thread_rng().fill_bytes(&mut t);
    state.sessions.lock().unwrap().insert(t);
    t
}

fn validate_token(state: &Arc<AppState>, t: &Token) -> bool {
    state.sessions.lock().unwrap().contains(t)
}

```

### 6) Graceful shutdown

It’s good practice to intercept termination signals (e.g., SIGINT) and stop accepting new connections,
then let in-flight requests complete. The exact implementation depends on the runtime model you choose.


## Error handling and robustness

- **Parsing:** Reject malformed request lines or headers early. Return `400 Bad Request`.
- **Bounds:** Enforce maximum header size and body size to prevent abuse.
- **Keep-Alive:** Either implement it fully (including timeouts) or set `Connection: close` consistently.
- **Thread pool:** Use a bounded pool to avoid exhausting system resources under load.
- **Backpressure:** Consider queue limits or drop strategies when overloaded.

## Trade-offs vs. a framework

- **Control:** You see every byte and every lock—useful for learning and specialized needs.
- **Maintenance:** You must track protocol details, security patches, and edge cases yourself.
- **Features:** Routing, middleware, TLS, HTTP/2, and async are non-trivial to rebuild.
- **Performance:** Hand-rolled can be fast, but frameworks have years of optimization.

## Where to go next

- **Routing:** Map paths to handlers with a small router (trie or hashmap).
- **Keep-Alive:** Support persistent connections with proper timeouts.
- **TLS:** Add HTTPS with `rustls`.
- **HTTP/2:** Consider integrating a library rather than rolling your own.
- **Async I/O:** Migrate to non-blocking sockets and an async runtime for scalability.
- **Observability:** Logging, metrics, and structured error reporting.

## Conclusion

Writing an HTTP server from scratch in Rust makes the protocol concrete and the language’s guarantees tangible.
You’ll understand sockets, parsing, concurrency, and state—all the things frameworks cleverly hide.
Use a framework when you need to ship, but build a server at least once to truly grasp what you’re shipping.


Remember: the code snippets here are only **highlights**.
For the complete implementation and context, check the repository:
[HTTP\_Server on GitHub](https://github.com/julienlargetpiet/HTTP_Server).