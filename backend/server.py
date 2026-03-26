"""FastAPI WebSocket server for Office Assistant."""

import asyncio
import json
import os
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from agent.llm.deepseek import DeepSeekClient
from agent.agents.main_agent import MainAgent

app = FastAPI(title="Office Assistant")

# Initialize Main Agent
llm_client = DeepSeekClient(
    api_key=os.getenv("DEEPSEEK_API_KEY", ""),
    model="deepseek-chat",
    api_base="https://api.deepseek.com/v1",
)
main_agent = MainAgent(llm_client=llm_client)


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def send_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_json(message)


manager = ConnectionManager()


@app.get("/")
async def get_html():
    return HTMLResponse("<h1>Office Assistant Backend Running</h1>")


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "message":
                user_content = message.get("content", "")

                # Send to Main Agent
                response = await main_agent.process(user_content)

                await manager.send_message({
                    "type": "response",
                    "content": response,
                    "agent": "Main Agent",
                }, client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)


@app.on_event("shutdown")
async def shutdown_event():
    await main_agent.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
