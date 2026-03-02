import json
import asyncio
import logging
from typing import AsyncIterator, Optional
from .models import ExchangeMessage, Order

logger = logging.getLogger(__name__)

class ExchangeClient:
    def __init__(self, hostname: str, port: int, team_name: str):
        self.hostname = hostname
        self.port = port
        self.team_name = team_name
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None

    async def connect(self):
        logger.info(f"Connecting to {self.hostname}:{self.port}")
        self.reader, self.writer = await asyncio.open_connection(self.hostname, self.port)
        await self.send({"type": "hello", "team": self.team_name.upper()})

    async def send(self, message: dict):
        if not self.writer:
            raise ConnectionError("Not connected")
        data = json.dumps(message) + "\n"
        self.writer.write(data.encode())
        await self.writer.drain()

    async def send_order(self, order: Order):
        await self.send(order.model_dump(exclude_none=True))

    async def messages(self) -> AsyncIterator[dict]:
        if not self.reader:
            raise ConnectionError("Not connected")
        while True:
            line = await self.reader.readline()
            if not line:
                break
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                logger.error(f"Failed to decode message: {line}")

    async def close(self):
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
