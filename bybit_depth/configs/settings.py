from __future__ import annotations
import os
from dataclasses import dataclass

@dataclass
class Settings:
    market: str = os.getenv("MARKET", "linear")  # 'linear', 'inverse' ou 'spot'
    symbol: str = os.getenv("SYMBOL", "BTCUSDT")
    depth: int = int(os.getenv("DEPTH", "50"))

    ws_linear: str = os.getenv("WS_LINEAR", "wss://stream.bybit.com/v5/public/linear")
    ws_inverse: str = os.getenv("WS_INVERSE", "wss://stream.bybit.com/v5/public/inverse")
    ws_spot: str = os.getenv("WS_SPOT", "wss://stream.bybit.com/v5/public/spot")
    rest_base: str = os.getenv("REST_BASE", "https://api.bybit.com")

    data_file: str = os.getenv("DATA_FILE", "./data/orderbook_latest.json")
    refresh_ms: int = int(os.getenv("REFRESH_MS", "1500"))

    def ws_url(self) -> str:
        if self.market.lower() == "linear":
            return self.ws_linear
        elif self.market.lower() == "inverse":
            return self.ws_inverse
        else:  # spot
            return self.ws_spot

settings = Settings()
