from __future__ import annotations
import logging
from typing import Optional

import httpx

from ..configs.settings import settings

log = logging.getLogger("rest_client")

class RESTClient:
    """Cliente REST (opcional) para obter snapshot inicial do orderbook."""

    def __init__(self, market: str = "linear") -> None:
        self.market = market
        self.base = settings.rest_base

    async def fetch_orderbook(self, symbol: str, limit: int = 200) -> Optional[dict]:
        # Ex.: /v5/market/orderbook?category=linear&symbol=BTCUSDT&limit=200
        params = {
            "category": "linear" if self.market.lower() == "linear" else "spot",
            "symbol": symbol,
            "limit": str(limit),
        }
        url = f"{self.base}/v5/market/orderbook"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(url, params=params)
                r.raise_for_status()
                return r.json()
        except Exception as e:  # noqa: BLE001
            log.warning("REST snapshot failed: %s", e)
            return None
