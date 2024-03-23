import asyncio
import json
import os
import sys
import websockets

from core import Core
import logging

logger = logging.getLogger("root")

core = Core()


class WebSocketServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    async def handle_client(self, websocket, path):
        async for message in websocket:
            print(f"Received message from client: {message}")
            response = f"Received message from client: {message}"
            await websocket.send(response)

    async def start(self):
        server = await websockets.serve(self.handle_client, self.host, self.port, ping_timeout=None)
        print(f"WebSocket server started at ws://{self.host}:{self.port}")
        await server.wait_closed()


async def start(core: Core):
    manifest = {
        "name": "Плагин вебсокет сервера",
        "version": "0.1",
        "is_active": True,
        "default_options": {
            "host": "localhost",
            "port": 8765,
        }
    }
    return manifest


async def start_with_options(core: Core, manifest: dict):
    host = manifest["options"]["host"]
    port = manifest["options"]["port"]
    server = WebSocketServer(host, port)

    asyncio.run_coroutine_threadsafe(server.start(), asyncio.get_running_loop())
