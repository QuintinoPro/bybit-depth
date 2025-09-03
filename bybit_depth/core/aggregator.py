from __future__ import annotations
from decimal import Decimal
from typing import List, Tuple, Dict, Optional
from statistics import mean, pstdev

from .orderbook import OrderBook

def imbalance(book: OrderBook, top_n: int = 10) -> Optional[float]:
    bids = book.top_levels("bid", top_n)
    asks = book.top_levels("ask", top_n)
    if not bids or not asks:
        return None
    sum_b = sum(q for _, q in bids)
    sum_a = sum(q for _, q in asks)
    total = sum_b + sum_a
    if total == 0:
        return None
    return float(sum_b / total)

def detect_walls(book: OrderBook, side: str = "ask", std_k: float = 2.5, min_abs: float = 0.0, top_n: int = 50) -> List[Tuple[Decimal, Decimal]]:
    levels = book.top_levels("ask" if side == "ask" else "bid", top_n)
    if not levels:
        return []
    sizes = [float(q) for _, q in levels]
    m = mean(sizes)
    s = pstdev(sizes) if len(sizes) > 1 else 0.0
    walls = []
    for price, qty in levels:
        if float(qty) >= max(min_abs, m + std_k * s):
            walls.append((price, qty))
    return walls

def band_liquidity(book: OrderBook, pct: float = 0.1) -> Optional[Dict[str, float]]:
    mid = book.mid()
    if mid is None:
        return None
    lower = mid * (Decimal(1) - Decimal(pct)/Decimal(100))
    upper = mid * (Decimal(1) + Decimal(pct)/Decimal(100))

    bid_sum = sum(q for p, q in book.top_levels("bid", 9999) if p >= lower)
    ask_sum = sum(q for p, q in book.top_levels("ask", 9999) if p <= upper)
    return {"lower": float(lower), "upper": float(upper), "bids": float(bid_sum), "asks": float(ask_sum)}
