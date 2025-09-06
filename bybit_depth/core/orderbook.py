from __future__ import annotations
from decimal import Decimal
from typing import Dict, List, Tuple, Optional
import logging

log = logging.getLogger("orderbook")

class OrderBook:
    """Mantém um livro de ofertas local (bids/asks) e aplica snapshots e deltas."""

    def __init__(self) -> None:
        self.bids: Dict[str, Decimal] = {}
        self.asks: Dict[str, Decimal] = {}
        self.last_update_id: Optional[int] = None
        self.symbol: Optional[str] = None
        self.market_type: Optional[str] = None
        self._sequence_errors: int = 0
        self._total_updates: int = 0

    # ----------------- Aplicação de eventos -----------------
    def apply_snapshot(self, bids: List[List[str]], asks: List[List[str]], update_id: Optional[int] = None) -> None:
        """Aplica um snapshot completo do orderbook."""
        self.bids.clear()
        self.asks.clear()
        for p, s in bids:
            self.bids[p] = Decimal(s)
        for p, s in asks:
            self.asks[p] = Decimal(s)
        self.last_update_id = update_id
        self._total_updates += 1
        self._clean()
        log.debug(f"Snapshot aplicado: {len(self.bids)} bids, {len(self.asks)} asks, update_id={update_id}")

    def apply_delta(self, bids: List[List[str]], asks: List[List[str]], update_id: Optional[int] = None) -> bool:
        """
        Aplica um delta ao orderbook.
        
        Returns:
            bool: True se o delta foi aplicado com sucesso, False se houve erro de sequência
        """
        # Validar sequência de updates
        if update_id is not None and self.last_update_id is not None:
            if update_id <= self.last_update_id:
                self._sequence_errors += 1
                log.warning(f"Erro de sequência: update_id={update_id} <= last_update_id={self.last_update_id}")
                return False
        
        # Aplicar delta
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
        
        self.last_update_id = update_id
        self._total_updates += 1
        self._clean()
        return True

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

    # ----------------- Métricas e Estatísticas -----------------
    def get_stats(self) -> Dict[str, any]:
        """Retorna estatísticas do orderbook."""
        bb = self.best_bid()
        ba = self.best_ask()
        mid = self.mid()
        
        spread = None
        spread_pct = None
        if bb and ba:
            spread = float(ba - bb)
            if mid:
                spread_pct = (spread / float(mid)) * 100
        
        return {
            "symbol": self.symbol,
            "market_type": self.market_type,
            "best_bid": float(bb) if bb else None,
            "best_ask": float(ba) if ba else None,
            "mid_price": float(mid) if mid else None,
            "spread": spread,
            "spread_pct": spread_pct,
            "bid_levels": len(self.bids),
            "ask_levels": len(self.asks),
            "total_levels": len(self.bids) + len(self.asks),
            "last_update_id": self.last_update_id,
            "total_updates": self._total_updates,
            "sequence_errors": self._sequence_errors,
            "error_rate": (self._sequence_errors / max(1, self._total_updates)) * 100
        }

    def get_liquidity_stats(self, depth_pct: float = 1.0) -> Dict[str, float]:
        """Calcula estatísticas de liquidez em uma faixa de preços."""
        mid = self.mid()
        if not mid:
            return {}
        
        lower_bound = mid * (Decimal(1) - Decimal(depth_pct) / Decimal(100))
        upper_bound = mid * (Decimal(1) + Decimal(depth_pct) / Decimal(100))
        
        bid_liquidity = sum(q for p, q in self.bids.items() if Decimal(p) >= lower_bound)
        ask_liquidity = sum(q for p, q in self.asks.items() if Decimal(p) <= upper_bound)
        
        return {
            "bid_liquidity": float(bid_liquidity),
            "ask_liquidity": float(ask_liquidity),
            "total_liquidity": float(bid_liquidity + ask_liquidity),
            "liquidity_imbalance": float(bid_liquidity - ask_liquidity),
            "liquidity_ratio": float(bid_liquidity / ask_liquidity) if ask_liquidity > 0 else float('inf')
        }
