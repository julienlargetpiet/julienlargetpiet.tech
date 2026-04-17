## Introduction

_InFoEnd_ is my first experiment with building a secure chatroom application in Go. The goal: create a real-time messaging system where messages are encrypted end-to-end, such that even the server cannot read them.

To make it feel like a proper client, not just a toy, I added a terminal UI using the `tview` library and relied on the WebSocket protocol for message transport. The result is a multi-room chat platform that demonstrates encryption, networking, and terminal UI in one place.

## Architecture Overview

The system consists of two roles: **Admin (server)** and **Clients**.

### Illustration images

![](/assets/common_files/gochat1.jpg)

![](/assets/common_files/gochat2.jpg)

### Server (Admin)

- Responsible for creating chatrooms.
- For each room, generates a unique 32-byte AES key.
- Distributes this AES key securely to clients via their RSA public keys.
- Once all clients of the chatroom have handshaked with the server (by generating and sharing their RSA public key) and each has received the AES key safely, the server deletes its own copy of the AES key.
- From then on, it only relays encrypted messages between clients without the ability to decrypt them.

### Clients

- On startup, each client generates its own RSA keypair.
- Sends the public key to the server when joining a chatroom.
- Receives the chatroom’s AES key encrypted with the client’s RSA public key.
- Decrypts it locally with their private key and uses it for all message encryption and decryption.

This setup ensures that the server cannot read chatroom traffic. Only clients in the room share the AES key, and even if the server is compromised later, past messages remain secure.

## Encryption Workflow

### Key Setup

- **RSA**: used only to distribute the AES session key.
- **AES-256-GCM**: used for actual message encryption.

### Message Flow

1. Admin creates a room and generates an AES-256 key.
2. Each client joins and shares its RSA public key with the server.
3. The server encrypts the AES key with each client’s RSA public key and sends it to them.
4. Once all clients in the room have received their encrypted copy, the server destroys its copy of the AES key.
5. From then on, messages are encrypted with AES-GCM before being sent over WebSocket.
6. Receiving clients decrypt with the same AES key.

AES-GCM was chosen because it supports variable-length messages and provides both confidentiality and integrity through authenticated encryption.

## Terminal User Interface (tview)

Instead of plain stdin/stdout, the application uses `tview` (a higher-level library built on top of `tcell`) to create a split-screen terminal interface:

- Chat history pane displays past messages in real time.
- Input box where the user types their next message.
- Room selection so clients can specify which room to join at connection time.

This makes the app feel like a true chat client, while remaining entirely terminal-based.

## Chatrooms and Admin Workflow

- **Admin Role**: runs the server, creates chatrooms, generates and distributes AES keys, then deletes its copy once all clients have received it, and from then on only relays traffic.
- **Clients**: choose which chatroom to join, and only participants with the distributed AES key can decrypt messages.
- **Isolation by Design**: each chatroom uses a unique AES key, and keys are discarded by the server after distribution, so it cannot decrypt any traffic.

## What Worked Well

- **WebSocket transport**: kept connections simple and bidirectional.
- **tview UI**: provided a responsive, user-friendly terminal interface.
- **Key distribution model**: simple but effective — ensures end-to-end encryption after the initial handshake.
- **Learning value**: forced me to think carefully about encryption lifecycles.

## Limitations

- **Authentication**: nothing prevents a man-in-the-middle from injecting a fake RSA key.
- **Persistence**: chatrooms and keys only exist during runtime.
- **NAT/firewall issues**: fine in controlled environments, but not yet Internet-scale.
- **Server trust**: even though it doesn’t store keys, the server is still trusted for distribution.

## Conclusion

_InFoEnd_ is not production-ready, but it shows how Go, WebSockets, RSA/AES-GCM encryption, and a terminal UI can come together to form an end-to-end encrypted chatroom.

For me, it was both a learning exercise and a fun way to explore cryptography and networking.

👉 [GitHub Repo](https://github.com/julienlargetpiet/InFoEnd)