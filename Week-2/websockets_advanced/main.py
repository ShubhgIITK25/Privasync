from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse
from datetime import datetime
import json
import logging 

logging.basicConfig(level=logging.INFO) #basicConfig() is the global configuration for the entire logging system. It sets up how logs behave across the whole application. # level=logging.INFO means — only show logs of INFO level and above:
logger = logging.getLogger(__name__)

app = FastAPI()

VALID_TOKENS = {"token-alice", "token-bob", "token-charlie"}


class ConnectionManager:
    def __init__(self):
        # { websocket: username }
        self.active_connections: dict[WebSocket, str] = {} #here its a dict , not a list because we want to associate each websocket connection with a username. This way, when a message comes in from a particular websocket, we can easily look up which user sent it. The key is the WebSocket object (the connection), and the value is the username of the connected client.
        # In-memory message history (last 50 messages)
        self.message_history: list[dict] = []

    async def connect(self, websocket: WebSocket, username: str):
        """to acept connection and register the user."""
        await websocket.accept()
        self.active_connections[websocket] = username # Store the username associated with this websocket connection in the active_connections dictionary. The key is the websocket object, and the value is the username string.
        logger.info(f" {username} connected. Total: {len(self.active_connections)}")

# This is the logging object created earlier at the top of the file:
# pythonlogger = logging.getLogger(__name__)
# includes log level, timestamp, and module name automatically.

    def disconnect(self, websocket: WebSocket):
        username = self.active_connections.pop(websocket, "Unknown")
        logger.info(f" {username} disconnected. Total: {len(self.active_connections)}")
        return username

    def build_message(self, username: str, text: str, msg_type: str = "chat") -> dict:
        return {
            "type": msg_type,
            "username": username,
            "text": text,
            "timestamp": datetime.utcnow().strftime("%H:%M:%S"), # # formats it as a string → "14:35:22"
        }

    def save_to_history(self, message: dict):
        """Store message, keeping only the last 50."""
        self.message_history.append(message)
        if len(self.message_history) > 50:
            self.message_history.pop(0)

    async def broadcast(self, message: dict):
        """Send a message to every connected client."""
        payload = json.dumps(message)
        disconnected = []
        for websocket in self.active_connections:
            try:
                await websocket.send_text(payload)
            except Exception:
                disconnected.append(websocket)
        # Clean up any broken connections found during broadcast
        for ws in disconnected:
            self.disconnect(ws)

    async def send_history(self, websocket: WebSocket):
        """Send past messages to a newly joined user."""
        for msg in self.message_history:
            await websocket.send_text(json.dumps(msg))


manager = ConnectionManager()


@app.websocket("/communicate")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),       # e.g. ws://localhost:5000/communicate?token=token-alice
    username: str = Query(...),    # e.g. &username=Alice
):
    #  Auth check — reject if token is invalid
    if token not in VALID_TOKENS:
        logger.warning(f" Rejected connection: invalid token '{token}'")
        await websocket.close(code=1008)  # 1008 = Policy Violation
        return

    # Accept and register the connection
    await manager.connect(websocket, username)

    # Send message history to the newly joined user
    await manager.send_history(websocket)

    # Announce to everyone that this user joined
    join_msg = manager.build_message(username="System", text=f"{username} has joined the chat ", msg_type="system")
    await manager.broadcast(join_msg)

    try:
        while True:
            # Wait for an incoming message from this client
            raw = await websocket.receive_text()

            try:
                incoming = json.loads(raw)
                text = incoming.get("text", "").strip()
            except json.JSONDecodeError:
                # Fallback: treat as plain text if client sends non-JSON
                text = raw.strip()

            if not text:
                continue

            # Build a structured message and broadcast to all
            message = manager.build_message(username=username, text=text)
            manager.save_to_history(message)
            await manager.broadcast(message)
            logger.info(f" [{username}]: {text}")

            # Server bot — generates and broadcasts a response based on the message
            bot_reply = None
            text_lower = text.lower()
            if any(greet in text_lower for greet in ["hello", "hi", "hey"]):
                bot_reply = f" Hey {username}! Welcome to the chat."
            elif "bye" in text_lower or "goodbye" in text_lower:
                bot_reply = f"See you later, {username}!"
            elif "how are you" in text_lower:
                bot_reply = " I'm just a server, but I'm doing great! Thanks for asking."
            elif "?" in text:
                bot_reply = " That's a great question! I'm just a bot though — ask the humans."
            elif any(word in text_lower for word in ["thanks", "thank you", "thx"]):
                bot_reply = " You're welcome!"

            if bot_reply:
                server_msg = manager.build_message(username="Server Bot", text=bot_reply, msg_type="bot")
                manager.save_to_history(server_msg)
                await manager.broadcast(server_msg)
                logger.info(f" [Server Bot]: {bot_reply}")

    except WebSocketDisconnect:
        # Announce departure on disconnect
        username = manager.disconnect(websocket)
        leave_msg = manager.build_message(username="System", text=f"{username} has left the chat ", msg_type="system")
        await manager.broadcast(leave_msg)


@app.get("/")
async def root():
    return {"status": "ok", "active_connections": len(manager.active_connections)}
    