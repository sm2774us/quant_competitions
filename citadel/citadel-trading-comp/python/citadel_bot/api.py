import httpx
from typing import List, Dict, Optional
from .models import Security, OrderBook, News, CaseStatus, Limit, OrderResponse

class TradingApi:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {"X-API-Key": api_key}
        self.client = httpx.Client(base_url=base_url, headers=self.headers, timeout=10.0)

    def get_case(self) -> CaseStatus:
        resp = self.client.get("/v1/case")
        resp.raise_for_status()
        return CaseStatus(**resp.json())

    def get_securities(self) -> Dict[str, Security]:
        resp = self.client.get("/v1/securities")
        resp.raise_for_status()
        return {s["ticker"]: Security(**s) for s in resp.json()}

    def get_order_book(self, ticker: str) -> OrderBook:
        resp = self.client.get("/v1/securities/book", params={"ticker": ticker})
        resp.raise_for_status()
        data = resp.json()
        return OrderBook(ticker=ticker, bids=data["bids"], asks=data["asks"])

    def get_news(self, limit: int = 10) -> List[News]:
        resp = self.client.get("/v1/news", params={"limit": limit})
        resp.raise_for_status()
        return [News(**n) for n in resp.json()]

    def get_limits(self) -> List[Limit]:
        resp = self.client.get("/v1/limits")
        resp.raise_for_status()
        return [Limit(**l) for l in resp.json()]

    def post_order(self, ticker: str, type: str, action: str, quantity: int, price: Optional[float] = None) -> OrderResponse:
        params = {
            "ticker": ticker,
            "type": type,
            "action": action,
            "quantity": quantity
        }
        if price is not None:
            params["price"] = price
        
        resp = self.client.post("/v1/orders", params=params)
        resp.raise_for_status()
        return OrderResponse(**resp.json())

    def close(self):
        self.client.close()
