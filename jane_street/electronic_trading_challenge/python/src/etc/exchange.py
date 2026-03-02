import json
import socket
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ExchangeConnection:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self._socket = None
        self._reader = None

    def connect(self):
        logger.info(f"Connecting to {self.host}:{self.port}")
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self.host, self.port))
        self._reader = self._socket.makefile('r', encoding='utf-8')

    def close(self):
        if self._socket:
            self._socket.close()
            self._socket = None
            self._reader = None

    def read(self) -> Optional[Dict[str, Any]]:
        if not self._reader:
            return None
        line = self._reader.readline()
        if not line:
            return None
        return json.loads(line)

    def write(self, message: Dict[str, Any]):
        if not self._socket:
            return
        data = json.dumps(message) + "
"
        self._socket.sendall(data.encode('utf-8'))

    def send_hello(self, team_name: str):
        self.write({"type": "hello", "team": team_name.upper()})

    def place_order(self, order_id: int, symbol: str, side: str, price: int, size: int):
        self.write({
            "type": "add",
            "order_id": order_id,
            "symbol": symbol,
            "dir": side,
            "price": price,
            "size": size
        })

    def cancel_order(self, order_id: int):
        self.write({
            "type": "cancel",
            "order_id": order_id
        })

    def convert(self, order_id: int, symbol: str, side: str, size: int):
        self.write({
            "type": "convert",
            "order_id": order_id,
            "symbol": symbol,
            "dir": side,
            "size": size
        })
