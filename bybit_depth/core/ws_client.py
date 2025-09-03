from __future__ import annotations
import asyncio
import json
import logging
from typing import Optional

import websockets

from ..configs.settings import settings
from .models import WSOrderbookMessage
from .orderbook import OrderBook
from ..utils.retry import backoff_retry

log = logging.getLogger("ws_client")

class BybitWSClient:
    def __init__(self, symbol: str, depth: int, market: str) -> None:
        self.symbol = symbol
        self.depth = depth
        self.market = market
        self.ws_url = settings.ws_linear if market.lower() == "linear" else settings.ws_spot
        self.book = OrderBook()
        self._task: Optional[asyncio.Task] = None
        self._connected = asyncio.Event()

    async def run_forever(self) -> None:
        attempt = 0
        while True:
            try:
                await self._connect_and_listen()
                attempt = 0  # reset on clean exit
            except Exception as e:  # noqa: BLE001
                log.exception("WS error: %s", e)
                attempt += 1
                await backoff_retry(attempt=attempt)

    async def _connect_and_listen(self) -> None:
        sub_msg = {
            "op": "subscribe",
            "args": [f"orderbook.{self.depth}.{self.symbol}"],
        }
        ping_interval = 20

        log.info("Connecting to %s", self.ws_url)
        async with websockets.connect(self.ws_url, ping_interval=ping_interval) as ws:
            await ws.send(json.dumps(sub_msg))
            log.info("Subscribed to %s", sub_msg["args"][0])
            self._connected.set()

            async for raw in ws:
                try:
                    msg = WSOrderbookMessage.model_validate_json(raw)
                except Exception:
                    log.debug("Non-matching WS payload: %s", raw)
                    continue

                if not msg.data:
                    continue

                if msg.type == "snapshot":
                    b = msg.data.b or []
                    a = msg.data.a or []
                    self.book.apply_snapshot(b, a)
                elif msg.type == "delta":
                    b = msg.data.b or []
                    a = msg.data.a or []
                    self.book.apply_delta(b, a)

    async def wait_connected(self, timeout: float = 10.0) -> bool:
        try:
            await asyncio.wait_for(self._connected.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            return False
