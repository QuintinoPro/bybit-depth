from __future__ import annotations
import asyncio
import json
import os
from pathlib import Path

from .configs.settings import settings
from .core.ws_client import BybitWSClient
from .utils.logging import setup_logging

DATA_PATH = Path(settings.data_file)

async def main() -> None:
    setup_logging()
    client = BybitWSClient(settings.symbol, settings.depth, settings.market)
    writer = asyncio.create_task(writer_task(client))
    await client.run_forever()
    await writer

async def writer_task(client: BybitWSClient) -> None:
    await client.wait_connected(10.0)
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    while True:
        payload = {
            "symbol": client.symbol,
            "bids": [[p, str(q)] for p, q in client.book.bids.items()],
            "asks": [[p, str(q)] for p, q in client.book.asks.items()],
        }
        tmp = DATA_PATH.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(payload, f)
        os.replace(tmp, DATA_PATH)
        await asyncio.sleep(1.0)

if __name__ == "__main__":
    asyncio.run(main())
