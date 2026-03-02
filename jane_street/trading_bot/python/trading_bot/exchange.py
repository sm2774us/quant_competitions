import json
import socket
from typing import Dict, Any, Optional
import logging

class Exchange:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.reader = None
        self.logger = logging.getLogger(__name__)

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.reader = self.socket.makefile('r', encoding='utf-8')

    def send(self, message: Dict[str, Any]):
        if not self.socket:
            raise RuntimeError("Not connected to exchange")
        data = json.dumps(message) + "
"
        self.socket.sendall(data.encode('utf-8'))

    def receive(self) -> Optional[Dict[str, Any]]:
        if not self.reader:
            raise RuntimeError("Not connected to exchange")
        line = self.reader.readline()
        if not line:
            return None
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to decode JSON: {line}")
            return None

    def close(self):
        if self.socket:
            self.socket.close()
            self.socket = None
            self.reader = None
