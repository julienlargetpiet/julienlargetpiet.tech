I built a tiny chatroom that runs entirely in the terminal, written in C, with all messages encrypted.
This article is my engineering story: why I did it, how the design evolved, what broke (and why), and the practical
lessons I’m taking to my next low-level project.


The code lives here: [github.com/julienlargetpiet/Chat](https://github.com/julienlargetpiet/Chat).
It’s a simple, scrappy program that uses sockets, `pthread`, `ncurses` for the TUI,
SDL for a small “poke” sound, and OpenSSL’s EVP API for AES encryption.


## Why a chatroom in C, and why the terminal?

I like C for the same reason some people like rebuilding engines: it’s brutally honest.
If I forget to check a return code, leak a buffer, or mix up a length, I pay the price immediately.
A chatroom touches a lot of systems topics—processes, sockets, concurrency, UI, and crypto—so it’s a great canvas
to practice the fundamentals without magic frameworks hiding the details. Also, a terminal UI forces clarity:
no CSS, no layout engines, just characters you draw yourself.


## What I set out to build

- A server that accepts multiple clients, keeps them in “chatrooms,” and broadcasts messages appropriately.
- A client that feels responsive in the terminal: input at the bottom, scrolling messages above.
- All traffic encrypted with AES, end-to-end between each client and the server.
- Basic authentication, so only allowed users can enter a given chatroom.
- A fun “poke” feature that plays a little sound on the receiver’s terminal.

## Server design - Overview

```c

int server_fd = socket(AF_INET, SOCK_STREAM, 0);
bind(server_fd, (struct sockaddr*)&addr, sizeof(addr));
listen(server_fd, SOMAXCONN);

for (;;) {
    int client_fd = accept(server_fd, NULL, NULL);
    if (client_fd < 0) continue;

    pthread_t tid;
    int *fd = malloc(sizeof(int));
    *fd = client_fd;
    pthread_create(&tid, NULL, client_thread, fd);
    pthread_detach(tid);
}

```

## Client design - Overview

The client needed to feel like a real chat app, even though it runs in a terminal.
For that, I leaned on `ncurses`. It’s a library that lets you manage multiple “windows” inside a terminal,
control cursor position, handle scrolling, and capture keystrokes without echoing them directly.
Instead of juggling raw ANSI escape codes, `ncurses` gave me tools to structure the UI cleanly.


### Using ncurses for a split interface

I split the client into two main windows: a history window (scrolling messages) and an input window.
`ncurses` made it easy to redraw them independently and keep the interface smooth.


```c

WINDOW *history = newwin(LINES - 1, COLS, 0, 0);
WINDOW *input   = newwin(1, COLS, LINES - 1, 0);

scrollok(history, TRUE);
keypad(input, TRUE);

for (;;) {
    werase(input);
    mvwprintw(input, 0, 0, "> %s", draft);
    wrefresh(input);

    int ch = wgetch(input);
    if (ch == KEY_BACKSPACE) { /* edit draft */ }
    else if (ch == '\n') { send_encrypted(draft); draft[0] = '\0'; }
    else { /* append char */ }

    drain_incoming_messages(); // redraw history window with new messages
}

```

`scrollok()` allowed the history to grow without me handling manual line wrapping.
`wgetch()` captured user input in a non-blocking loop. And since the history redraw was tied
to incoming network messages, the chat felt responsive without freezing the UI when waiting on the socket.


## Encryption with OpenSSL EVP

```c

int encrypt_aes(const unsigned char *in, int in_len,
                const unsigned char *key, const unsigned char *iv,
                unsigned char *out)
{
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) return -1;

    int len = 0, out_len = 0;
    if (EVP_EncryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, key, iv) != 1) goto fail;
    if (EVP_EncryptUpdate(ctx, out, &len, in, in_len) != 1) goto fail;
    out_len = len;
    if (EVP_EncryptFinal_ex(ctx, out + len, &len) != 1) goto fail;
    out_len += len;

    EVP_CIPHER_CTX_free(ctx);
    return out_len;
fail:
    EVP_CIPHER_CTX_free(ctx);
    return -1;
}

```

## Lessons learned

- `ncurses` was key to making the terminal UI feel like a real app.
- Always handle partial writes with `send()`.
- Keep ncurses rendering in a single thread.
- Always generate fresh IVs for AES.
- Verbose, boring code beats clever one-liners when handling memory.

## Conclusion

Writing this encrypted chatroom in C taught me to respect the details: every byte matters, every return code matters.
`ncurses` in particular reminded me how much you can achieve in a terminal without any GUI toolkit.
It gave the project a “real app” feel while staying in the command line.
The full project is open here:
[julienlargetpiet/Chat](https://github.com/julienlargetpiet/Chat).


Inspired by [https://beej.us/guide/bgnet/html/](https://beej.us/guide/bgnet/html/)

Or on this server: [here](/assets/common_files/Beejs.html)