from __future__ import annotations
import asyncio
from decimal import Decimal
import json
import os
from typing import Optional

import typer
from rich import print

from ..configs.settings import settings
from ..core.orderbook import OrderBook
from ..core.ws_client import BybitWSClient
from ..core.aggregator import imbalance, band_liquidity, detect_walls

app = typer.Typer(help="Bybit DOM CLI")

def _read_json_book(path: str) -> Optional[OrderBook]:
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        book = OrderBook()
        book.apply_snapshot(payload.get("bids", []), payload.get("asks", []))
        return book
    except Exception:
        return None

async def _connect_once(symbol: str, depth: int, market: str, duration: float = 2.0) -> OrderBook:
    client = BybitWSClient(symbol, depth, market)
    task = asyncio.create_task(client.run_forever())
    await client.wait_connected(5.0)
    await asyncio.sleep(duration)
    task.cancel()
    return client.book

@app.command("depth")
def depth_cmd(
    info: bool = typer.Option(False, help="Mostrar info geral"),
    level: Optional[float] = typer.Option(None, help="Preço para consulta"),
    pct: Optional[float] = typer.Option(None, help="Faixa ±pct% ao redor do mid"),
    walls: Optional[float] = typer.Option(None, help="Limiar absoluto para paredes"),
    symbol: str = typer.Option(settings.symbol, help="Símbolo ex.: BTCUSDT"),
    depth: int = typer.Option(settings.depth, help="Profundidade"),
    market: str = typer.Option(settings.market, help="linear|spot"),
    from_file: Optional[str] = typer.Option(None, help="JSON gerado pelo runner"),
):
    """Consultas de DOM (info, nível, bandas, paredes)."""
    book: Optional[OrderBook] = None
    if from_file:
        book = _read_json_book(from_file)
    if not book:
        book = asyncio.run(_connect_once(symbol, depth, market))

    if info:
        bb = book.best_bid()
        ba = book.best_ask()
        mid = book.mid()
        obi = imbalance(book, top_n=10)
        print({"best_bid": str(bb), "best_ask": str(ba), "mid": str(mid), "imbalance": obi})

    if level is not None:
        q, side = book.size_at(Decimal(str(level)))
        print({"price": level, "qty": float(q), "side": side})

    if pct is not None:
        res = band_liquidity(book, pct=float(pct))
        print(res)

    if walls is not None:
        w_asks = detect_walls(book, side="ask", min_abs=walls)
        w_bids = detect_walls(book, side="bid", min_abs=walls)
        print({"ask_walls": [(float(p), float(q)) for p, q in w_asks],
               "bid_walls": [(float(p), float(q)) for p, q in w_bids]})

if __name__ == "__main__":
    app()
