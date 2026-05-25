from fastapi import FastAPI, WebSocket, WebSocketDisconnect #an exception that fires when a client disconnects.

class ConnectionManager: #Defines a class to manage all active WebSocket connections. active_connections is a list that tracks every currently connected client.
    def __init__(self):                                                                                                                     #self is the instance of the class that is being created. __init__ is a special method that runs when you create an instance of the class. It initializes the active_connections list to be empty.
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept() ## waits for handshake to complete with client
        self.active_connections.append(websocket) #accept() completes the WebSocket handshake with the client (required before sending/receiving). The connection is then added to the tracking list.
        # add to THIS instance's list

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message) #Sends a text message to one specific client (identified by their websocket object).

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

app = FastAPI()
manager = ConnectionManager() #instance of ConnectionManagerclass

@app.websocket("/communicate")
async def websocket_endpoint(websocket: WebSocket):  #When a client connects to ws://host/communicate, FastAPI:
# Detects the incoming WebSocket connection
# Instantiates a WebSocket object internally
# Injects it into your function as the websocket parameter — based on the type hint WebSocket
# This is FastAPI's dependency injection system — it reads the type hint websocket: WebSocket and knows to create and pass a WebSocket instance automatically. You never call
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Received the message from your side: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)