import pytest
from unittest.mock import AsyncMock, patch
from trading_bot.client import ExchangeClient
from trading_bot.models import Order

pytestmark = pytest.mark.asyncio
async def test_client_connect():
    client = ExchangeClient("localhost", 25000, "TEAM")
    with patch("asyncio.open_connection", return_value=(AsyncMock(), AsyncMock())) as mock_conn:
        await client.connect()
        mock_conn.assert_called_once_with("localhost", 25000)

@pytest.mark.asyncio
async def test_client_send_order():
    client = ExchangeClient("localhost", 25000, "TEAM")
    client.writer = AsyncMock()
    order = Order(type="add", order_id=1, symbol="BOND", dir="BUY", price=1000, size=10)
    await client.send_order(order)
    client.writer.write.assert_called()
