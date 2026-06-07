# Overview

In this project, We explored how WebSockets work and bu
lt a small real-time application using them. Before diving into the code, it is important to understand how WebSockets differ from traditional HTTP communication and how they establish a connection with the server.

### Topics Covered

- What are WebSockets?
- How are they different from HTTP requests?
- What is a TCP connection?
- How do WebSockets establish a connection over TCP?
- What is a handshake?
- Code overview
- Relationship Between TCP and WebSocket Handshakes


### Project Link

`https://github.com/ritgit24/Privasync/tree/master/Week-2`

---

# What are WebSockets?

WebSockets are a communication protocol that allows a client (browser or application) and a server to maintain a persistent two-way connection.

Unlike HTTP, where the client sends a request and waits for a response, WebSockets keep the connection open after it is established. This allows both the client and server to send messages whenever they want without creating a new connection every time.

## HTTP vs WebSockets

### HTTP

- Client sends a request.
- Server sends a response.
- Communication ends.
- A new request is needed for more data.

### WebSockets

- Connection is established once.
- Connection stays open.
- Client and server can communicate at any time.
- Suitable for real-time applications.

---

# What is a TCP Connection?

TCP (Transmission Control Protocol) is a protocol used for reliable communication between two devices over a network.

Before any data is exchanged, a TCP connection is established between the client and the server. TCP ensures that:

- Data arrives successfully.
- Data arrives in the correct order.
- Lost packets are retransmitted.

You can think of TCP as the reliable communication channel on top of which WebSockets operate.

---

# How Do WebSockets Establish a Connection?

WebSockets do not directly start communicating with the server.

The process looks like this:

1. A TCP connection is established.
2. The client sends an HTTP request asking to upgrade the connection to WebSocket.
3. The server accepts the request.
4. The protocol switches from HTTP to WebSocket.
5. The same TCP connection is reused for real-time communication.

After the upgrade, both the client and server can exchange messages freely without repeatedly making HTTP requests.

---

# What is a Handshake?

A handshake is the process through which two systems agree on how they are going to communicate.

In WebSockets, the handshake begins as a normal HTTP request. The client asks the server if it supports WebSockets and wants to upgrade the connection.

If the server accepts the request, it responds with:

    HTTP/1.1 101 Switching Protocols
    
## TCP Three-Way Handshake

Before a WebSocket connection can be established, the client and server must first create a TCP connection. TCP uses a process called the **Three-Way Handshake** to establish a reliable communication channel.

The handshake consists of three steps:

### 1. SYN

The client initiates the connection by sending a **SYN (Synchronize)** packet to the server.

```text
Client                          Server
   | -------- SYN -----------> |
```
---

### 2. SYN-ACK

The server receives the SYN packet and responds with a **SYN-ACK** packet.

- SYN → Indicates the server wants to establish the connection.
- ACK → Acknowledges receipt of the client's SYN.

```text
Client                          Server
   | -------- SYN -----------> |
   | <------ SYN-ACK --------- |
```


---

### 3. ACK

The client acknowledges the server's SYN by sending an **ACK** packet.

```text
Client                          Server
   | -------- SYN -----------> |
   | <------ SYN-ACK --------- |
   | -------- ACK -----------> |
```

At this point, the TCP connection is successfully established and both sides are ready to exchange data.

### Why is the Three-Way Handshake Important?

The handshake ensures that:

- Both client and server can send data.
- Both client and server can receive data.
- Both sides agree on the starting sequence numbers used to track packets.
- Communication is reliable before any application data is exchanged.

Since WebSockets operate on top of TCP, this handshake always happens before the WebSocket handshake begins.

---

## Relationship Between TCP and WebSocket Handshakes

When a browser creates a WebSocket connection, the process is actually:

```text
1. TCP Three-Way Handshake
   SYN
   SYN-ACK
   ACK

2. HTTP Upgrade Request
   GET /communicate HTTP/1.1
   Upgrade: websocket

3. Server Response
   HTTP/1.1 101 Switching Protocols

4. WebSocket Communication Begins
```

```text
Browser
   │
   ├── TCP Handshake
   │      SYN
   │      SYN-ACK
   │      ACK
   │
   ├── HTTP Upgrade Request
   │
   ├── HTTP/1.1 101 Switching Protocols
   │
   └── WebSocket Messages
```

This means that **every WebSocket connection first establishes a TCP connection through the Three-Way Handshake and then performs the WebSocket Handshake using an HTTP Upgrade request.**

# Code Overview

This project implements a simple real-time chat application using **FastAPI WebSockets** on the backend and **JavaScript WebSockets** on the frontend.

The application supports:

- Real-time messaging
- User authentication using tokens
- Join/leave notifications
- Message history
- A simple server bot
- Broadcasting messages to all connected users

---

## 1. Creating a WebSocket Connection (Frontend)

When a user enters their username and token, the browser creates a WebSocket connection with the server.

```javascript
const url = `ws://localhost:5000/communicate?token=${token}&username=${username}`;
ws = new WebSocket(url);
```

**Purpose:**

- Opens a persistent connection with the backend.
- Sends the token and username as query parameters.
- Initiates the WebSocket handshake automatically.

After this point, the browser and server can exchange messages in real time.

---

## 2. WebSocket Endpoint (Backend)

```python
@app.websocket("/communicate")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    username: str = Query(...),
):
```

**Purpose:**

- Acts as the entry point for all WebSocket connections.
- Receives the username and token from the client.
- Handles authentication and communication.

Every connected user communicates through this endpoint.

---

## 3. Authentication Check

```python
if token not in VALID_TOKENS:
    await websocket.close(code=1008)
    return
```

**Purpose:**

- Validates incoming users before accepting the connection.
- Rejects users with invalid tokens.

This prevents unauthorized users from joining the chat.

---

## 4. Managing Active Connections

```python
self.active_connections[websocket] = username
```

**Purpose:**

- Stores all currently connected users.
- Associates each WebSocket connection with a username.



This helps identify who sent each message.

---

## 5. Broadcasting Messages

```python
async def broadcast(self, message: dict):
    payload = json.dumps(message)

    for websocket in self.active_connections:
        await websocket.send_text(payload)
```

**Purpose:**

- Sends a message to every connected user.
- Ensures all users receive updates instantly.

Whenever one user sends a message, every connected client receives it.

---

## 6. Receiving Messages

```python
raw = await websocket.receive_text()

incoming = json.loads(raw)
text = incoming.get("text", "").strip()
```

**Purpose:**

- Waits for a message from a client.
- Converts JSON data into Python objects.
- Extracts the message text.

This is the core part of the chat functionality.

---

## 7. Message History

```python
self.message_history.append(message)
```

**Purpose:**

- Stores previous chat messages.
- Maintains the last 50 messages.

When a new user joins, they can see recent conversation history instead of an empty chat window.

---

## 8. Sending History to New Users

```python
await manager.send_history(websocket)
```

**Purpose:**

- Sends previously stored messages to a newly connected user.
- Improves user experience by showing recent conversations.

---

## 9. Join and Leave Notifications

```python
join_msg = manager.build_message(
    username="System",
    text=f"{username} has joined the chat",
    msg_type="system"
)
```

**Purpose:**

- Notifies everyone when a user joins.
- Similar logic is used when a user disconnects.

Example:

```text
Alice has joined the chat
Bob has left the chat
```

---

## 10. Server Bot Responses

```python
if any(greet in text_lower for greet in ["hello", "hi", "hey"]):
    bot_reply = f"Hey {username}! Welcome to the chat."
```

**Purpose:**

- Detects simple keywords in user messages.
- Generates automated responses.
- Broadcasts bot replies to all users.

Example:

```text
Alice: Hello
Server Bot: Hey Alice! Welcome to the chat.
```

---

## Communication Flow

```
User
  │
Frontend (HTML, CSS, JavaScript)
  │
WebSocket Connection
  │
FastAPI Server
  │
Connection Manager
  │
  ├── Store Users
  ├── Store Messages
  ├── Broadcast Messages
  └── Generate Bot Replies
  │
All Connected Users
```

---

## Conclusion

Through this project, We learnt how WebSockets establish a persistent connection between a client and a server, enabling real-time communication.
