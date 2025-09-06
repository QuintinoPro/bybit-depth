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
from ..core.history import OrderbookHistory

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
    stats: bool = typer.Option(False, help="Mostrar estatísticas detalhadas"),
    liquidity: Optional[float] = typer.Option(None, help="Análise de liquidez em ±pct%"),
    symbol: str = typer.Option(settings.symbol, help="Símbolo ex.: BTCUSDT, BTC-26SEP25"),
    depth: int = typer.Option(settings.depth, help="Profundidade"),
    market: str = typer.Option(settings.market, help="linear|inverse|spot"),
    from_file: Optional[str] = typer.Option(None, help="JSON gerado pelo runner"),
):
    """Consultas de DOM (info, nível, bandas, paredes, estatísticas)."""
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

    if stats:
        stats_data = book.get_stats()
        print("📊 Estatísticas do Orderbook:")
        print(f"  Símbolo: {stats_data['symbol']}")
        print(f"  Tipo: {stats_data['market_type']}")
        print(f"  Best Bid: {stats_data['best_bid']}")
        print(f"  Best Ask: {stats_data['best_ask']}")
        print(f"  Mid Price: {stats_data['mid_price']}")
        print(f"  Spread: {stats_data['spread']} ({stats_data['spread_pct']:.4f}%)")
        print(f"  Níveis: {stats_data['bid_levels']} bids, {stats_data['ask_levels']} asks")
        print(f"  Updates: {stats_data['total_updates']} (erros: {stats_data['sequence_errors']})")
        print(f"  Taxa de erro: {stats_data['error_rate']:.2f}%")

    if liquidity is not None:
        liq_stats = book.get_liquidity_stats(liquidity)
        print(f"💧 Análise de Liquidez (±{liquidity}%):")
        print(f"  Liquidez Bid: {liq_stats['bid_liquidity']:.2f}")
        print(f"  Liquidez Ask: {liq_stats['ask_liquidity']:.2f}")
        print(f"  Total: {liq_stats['total_liquidity']:.2f}")
        print(f"  Desequilíbrio: {liq_stats['liquidity_imbalance']:.2f}")
        print(f"  Ratio Bid/Ask: {liq_stats['liquidity_ratio']:.2f}")

@app.command("monitor")
def monitor_cmd(
    symbol: str = typer.Option(settings.symbol, help="Símbolo ex.: BTCUSDT, BTC-26SEP25"),
    depth: int = typer.Option(settings.depth, help="Profundidade"),
    market: str = typer.Option(settings.market, help="linear|inverse|spot"),
    interval: float = typer.Option(1.0, help="Intervalo de atualização em segundos"),
    duration: Optional[float] = typer.Option(None, help="Duração do monitoramento (segundos)"),
):
    """Monitora o orderbook em tempo real."""
    import time
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    
    console = Console()
    
    async def monitor_loop():
        client = BybitWSClient(symbol, depth, market)
        task = asyncio.create_task(client.run_forever())
        
        try:
            await client.wait_connected(10.0)
            console.print(f"🔗 Conectado ao {symbol} ({market})")
            
            start_time = time.time()
            while True:
                if duration and (time.time() - start_time) >= duration:
                    break
                    
                stats = client.book.get_stats()
                liq_stats = client.book.get_liquidity_stats(1.0)
                
                # Criar tabela de estatísticas
                table = Table(title=f"📊 {symbol} - Orderbook Monitor")
                table.add_column("Métrica", style="cyan")
                table.add_column("Valor", style="green")
                
                table.add_row("Best Bid", f"{stats['best_bid']:.2f}" if stats['best_bid'] else "N/A")
                table.add_row("Best Ask", f"{stats['best_ask']:.2f}" if stats['best_ask'] else "N/A")
                table.add_row("Mid Price", f"{stats['mid_price']:.2f}" if stats['mid_price'] else "N/A")
                table.add_row("Spread", f"{stats['spread']:.4f} ({stats['spread_pct']:.4f}%)" if stats['spread'] else "N/A")
                table.add_row("Níveis", f"{stats['bid_levels']} bids, {stats['ask_levels']} asks")
                table.add_row("Updates", f"{stats['total_updates']} (erros: {stats['sequence_errors']})")
                table.add_row("Liquidez Bid", f"{liq_stats['bid_liquidity']:.2f}")
                table.add_row("Liquidez Ask", f"{liq_stats['ask_liquidity']:.2f}")
                table.add_row("Desequilíbrio", f"{liq_stats['liquidity_imbalance']:.2f}")
                
                console.clear()
                console.print(table)
                
                await asyncio.sleep(interval)
                
        finally:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    asyncio.run(monitor_loop())

@app.command("symbols")
def symbols_cmd():
    """Lista símbolos suportados e seus tipos."""
    from ..core.models import parse_symbol_type
    
    test_symbols = [
        "BTCUSDT", "ETHUSDT", "ADAUSDT",  # Spot/Perpétuos
        "BTC-26SEP25", "ETH-26SEP25",     # Futuros datados
        "BTCUSDC", "ETHUSDC",             # Outros pares
    ]
    
    print("🔍 Análise de Símbolos:")
    for symbol in test_symbols:
        info = parse_symbol_type(symbol)
        print(f"  {symbol:12} -> {info['type']:9} | {info['base']}/{info['quote']} | Expiry: {info['expiry'] or 'N/A'}")

@app.command("history")
def history_cmd(
    symbol: str = typer.Option(settings.symbol, help="Símbolo para análise histórica"),
    hours: int = typer.Option(24, help="Horas para trás"),
    limit: int = typer.Option(100, help="Limite de registros"),
    stats: bool = typer.Option(False, help="Mostrar estatísticas agregadas"),
):
    """Análise de dados históricos do orderbook."""
    from datetime import datetime, timezone, timedelta
    
    history = OrderbookHistory()
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=hours)
    
    snapshots = history.get_snapshots(symbol, start_time, end_time, limit)
    
    if not snapshots:
        print(f"❌ Nenhum dado histórico encontrado para {symbol} nas últimas {hours}h")
        return
    
    print(f"📈 Histórico de {symbol} (últimas {hours}h):")
    print(f"  Total de snapshots: {len(snapshots)}")
    
    if stats:
        stats_data = history.get_statistics(symbol, start_time, end_time)
        if stats_data:
            print(f"  Spread médio: {stats_data.get('avg_spread', 0):.4f} ({stats_data.get('avg_spread_pct', 0):.4f}%)")
            print(f"  Níveis médios: {stats_data.get('avg_bid_levels', 0):.1f} bids, {stats_data.get('avg_ask_levels', 0):.1f} asks")
            print(f"  Taxa de erro média: {stats_data.get('avg_error_rate', 0):.2f}%")
            print(f"  Preço bid médio: {stats_data.get('avg_bid', 0):.2f}")
            print(f"  Preço ask médio: {stats_data.get('avg_ask', 0):.2f}")
    
    # Mostrar últimos 5 snapshots
    print(f"\n📊 Últimos {min(5, len(snapshots))} snapshots:")
    for i, snapshot in enumerate(snapshots[:5]):
        timestamp = snapshot['timestamp']
        print(f"  {i+1}. {timestamp} | Bid: {snapshot['best_bid']:.2f} | Ask: {snapshot['best_ask']:.2f} | Spread: {snapshot['spread']:.4f}")

@app.command("restore")
def restore_cmd(
    snapshot_id: int = typer.Argument(..., help="ID do snapshot para restaurar"),
    output_file: str = typer.Option("restored_orderbook.json", help="Arquivo de saída"),
):
    """Restaura um orderbook a partir de um snapshot histórico."""
    history = OrderbookHistory()
    book = history.restore_orderbook(snapshot_id)
    
    if not book:
        print(f"❌ Snapshot {snapshot_id} não encontrado")
        return
    
    # Salvar orderbook restaurado
    payload = {
        "symbol": "restored",
        "bids": [[p, str(q)] for p, q in book.bids.items()],
        "asks": [[p, str(q)] for p, q in book.asks.items()],
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(payload, f)
    
    print(f"✅ Orderbook restaurado salvo em {output_file}")
    print(f"   Níveis: {len(book.bids)} bids, {len(book.asks)} asks")

if __name__ == "__main__":
    app()
