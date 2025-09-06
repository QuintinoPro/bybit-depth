from __future__ import annotations
import asyncio
import json
import os
import argparse
from pathlib import Path

from .configs.settings import settings
from .core.ws_client import BybitWSClient
from .core.history import OrderbookHistory
from .utils.logging import setup_logging

DATA_PATH = Path(settings.data_file)

async def main() -> None:
    parser = argparse.ArgumentParser(description="Bybit Depth Runner")
    parser.add_argument("--symbol", default=settings.symbol, help="Símbolo para conectar")
    parser.add_argument("--market", default=settings.market, help="Tipo de mercado (linear, inverse, spot)")
    parser.add_argument("--depth", type=int, default=settings.depth, help="Profundidade do orderbook")
    parser.add_argument("--data-file", default=settings.data_file, help="Arquivo de dados JSON")
    
    args = parser.parse_args()
    
    setup_logging()
    client = BybitWSClient(args.symbol, args.depth, args.market)
    history = OrderbookHistory()
    
    # Atualizar caminho do arquivo de dados
    global DATA_PATH
    DATA_PATH = Path(args.data_file)
    
    # Criar tasks para escrita de dados
    writer = asyncio.create_task(writer_task(client))
    history_writer = asyncio.create_task(history_writer_task(client, history))
    
    try:
        await client.run_forever()
    finally:
        # Cancelar tasks de escrita
        writer.cancel()
        history_writer.cancel()
        try:
            await asyncio.gather(writer, history_writer, return_exceptions=True)
        except Exception:
            pass

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

async def history_writer_task(client: BybitWSClient, history: OrderbookHistory) -> None:
    """Task para salvar snapshots históricos periodicamente."""
    await client.wait_connected(10.0)
    while True:
        try:
            # Salvar snapshot histórico a cada 5 segundos
            history.save_snapshot(client.book, client.symbol, client.market)
            await asyncio.sleep(5.0)
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")
            await asyncio.sleep(1.0)

if __name__ == "__main__":
    asyncio.run(main())
