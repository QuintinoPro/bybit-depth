from __future__ import annotations
from decimal import Decimal
from typing import Dict, List, Tuple, Optional

class OrderBook:
    """Mantém um livro de ofertas local (bids/asks) e aplica snapshots e deltas."""

    def __init__(self) -> None:
        self.bids: Dict[str, Decimal] = {}
        self.asks: Dict[str, Decimal] = {}

    # ----------------- Aplicação de eventos -----------------
    def apply_snapshot(self, bids: List[List[str]], asks: List[List[str]]) -> None:
        self.bids.clear()
        self.asks.clear()
        for p, s in bids:
            self.bids[p] = Decimal(s)
        for p, s in asks:
            self.asks[p] = Decimal(s)
        self._clean()

    def apply_delta(self, bids: List[List[str]], asks: List[List[str]]) -> None:
        for p, s in bids:
            q = Decimal(s)
            if q == 0:
                self.bids.pop(p, None)
            else:
                self.bids[p] = q
        for p, s in asks:
            q = Decimal(s)
            if q == 0:
                self.asks.pop(p, None)
            else:
                self.asks[p] = q
        self._clean()

    def _clean(self) -> None:
        for p in [k for k, v in self.bids.items() if v <= 0]:
            self.bids.pop(p, None)
        for p in [k for k, v in self.asks.items() if v <= 0]:
            self.asks.pop(p, None)

    # ----------------- Consultas -----------------
    def best_bid(self) -> Optional[Decimal]:
        if not self.bids:
            return None
        return max(Decimal(p) for p in self.bids.keys())

    def best_ask(self) -> Optional[Decimal]:
        if not self.asks:
            return None
        return min(Decimal(p) for p in self.asks.keys())

    def mid(self) -> Optional[Decimal]:
        bb = self.best_bid()
        ba = self.best_ask()
        if bb is None or ba is None:
            return None
        return (bb + ba) / 2

    def size_at(self, price: Decimal) -> Tuple[Decimal, Optional[str]]:
        s = self.bids.get(str(price))
        if s is not None:
            return s, "bid"
        s = self.asks.get(str(price))
        if s is not None:
            return s, "ask"
        return Decimal(0), None

    def top_levels(self, side: str, n: int = 10) -> List[Tuple[Decimal, Decimal]]:
        if side == "bid":
            levels = sorted((Decimal(p), q) for p, q in self.bids.items())
            levels = levels[::-1]
        else:
            levels = sorted((Decimal(p), q) for p, q in self.asks.items())
        return levels[:n]

    # ----------------- Cumulativos p/ gráfico -----------------
    def cumulative_bids(self) -> List[Tuple[Decimal, Decimal]]:
        levels = sorted((Decimal(p), q) for p, q in self.bids.items())
        levels = levels[::-1]  # desc
        out: List[Tuple[Decimal, Decimal]] = []
        run = Decimal(0)
        for price, qty in levels:
            run += qty
            out.append((price, run))
        return out

    def cumulative_asks(self) -> List[Tuple[Decimal, Decimal]]:
        levels = sorted((Decimal(p), q) for p, q in self.asks.items())
        out: List[Tuple[Decimal, Decimal]] = []
        run = Decimal(0)
        for price, qty in levels:
            run += qty
            out.append((price, run))
        return out
