from __future__ import annotations
import pytest
from decimal import Decimal
from bybit_depth.core.orderbook import OrderBook

def test_orderbook_sequence_validation():
    """Testa validação de sequência de updates."""
    book = OrderBook()
    
    # Aplicar snapshot
    book.apply_snapshot([["100", "1"]], [["101", "1"]], update_id=1)
    assert book.last_update_id == 1
    
    # Delta válido (sequência crescente)
    success = book.apply_delta([["100.5", "0.5"]], [], update_id=2)
    assert success is True
    assert book.last_update_id == 2
    
    # Delta inválido (sequência decrescente)
    success = book.apply_delta([["100.6", "0.5"]], [], update_id=1)
    assert success is False
    assert book.last_update_id == 2  # Não deve mudar
    
    # Delta sem update_id deve ser aceito
    success = book.apply_delta([["100.7", "0.5"]], [], update_id=None)
    assert success is True

def test_orderbook_statistics():
    """Testa cálculo de estatísticas do orderbook."""
    book = OrderBook()
    book.symbol = "BTCUSDT"
    book.market_type = "linear"
    
    # Aplicar dados de teste
    book.apply_snapshot(
        [["100", "1"], ["99", "2"], ["98", "3"]], 
        [["101", "1"], ["102", "2"], ["103", "3"]],
        update_id=1
    )
    
    stats = book.get_stats()
    
    assert stats["symbol"] == "BTCUSDT"
    assert stats["market_type"] == "linear"
    assert stats["best_bid"] == 100.0
    assert stats["best_ask"] == 101.0
    assert stats["mid_price"] == 100.5
    assert stats["spread"] == 1.0
    assert abs(stats["spread_pct"] - 0.9950248756218906) < 0.0001  # (1.0 / 100.5) * 100
    assert stats["bid_levels"] == 3
    assert stats["ask_levels"] == 3
    assert stats["total_levels"] == 6
    assert stats["last_update_id"] == 1
    assert stats["total_updates"] == 1
    assert stats["sequence_errors"] == 0
    assert stats["error_rate"] == 0.0

def test_liquidity_stats():
    """Testa cálculo de estatísticas de liquidez."""
    book = OrderBook()
    
    # Criar orderbook com liquidez concentrada
    book.apply_snapshot(
        [["100", "10"], ["99", "5"], ["98", "1"]], 
        [["101", "8"], ["102", "4"], ["103", "2"]],
        update_id=1
    )
    
    # Teste com faixa de 1%
    liq_stats = book.get_liquidity_stats(1.0)
    
    # Mid price = 100.5, faixa = 99.495 a 101.505
    # Bids na faixa: 100 (10) + 99 (5) = 15 (mas 99 < 99.495, então só 100)
    # Asks na faixa: 101 (8) + 102 (4) = 12 (mas 102 > 101.505, então só 101)
    assert liq_stats["bid_liquidity"] == 10.0  # Apenas preço 100 está na faixa
    assert liq_stats["ask_liquidity"] == 8.0   # Apenas preço 101 está na faixa
    assert liq_stats["total_liquidity"] == 18.0
    assert liq_stats["liquidity_imbalance"] == 2.0
    assert liq_stats["liquidity_ratio"] == 1.25  # 10/8

def test_orderbook_edge_cases():
    """Testa casos extremos do orderbook."""
    book = OrderBook()
    
    # Orderbook vazio
    stats = book.get_stats()
    assert stats["best_bid"] is None
    assert stats["best_ask"] is None
    assert stats["mid_price"] is None
    assert stats["spread"] is None
    assert stats["spread_pct"] is None
    
    # Apenas bids
    book.apply_snapshot([["100", "1"]], [], update_id=1)
    stats = book.get_stats()
    assert stats["best_bid"] == 100.0
    assert stats["best_ask"] is None
    assert stats["mid_price"] is None
    
    # Apenas asks
    book.apply_snapshot([], [["101", "1"]], update_id=2)
    stats = book.get_stats()
    assert stats["best_bid"] is None
    assert stats["best_ask"] == 101.0
    assert stats["mid_price"] is None

def test_orderbook_cleanup():
    """Testa limpeza de níveis com quantidade zero ou negativa."""
    book = OrderBook()
    
    # Aplicar dados com quantidades zero/negativas
    book.apply_snapshot(
        [["100", "1"], ["99", "0"], ["98", "-1"]], 
        [["101", "1"], ["102", "0"], ["103", "-1"]],
        update_id=1
    )
    
    # Apenas níveis com quantidade positiva devem permanecer
    assert len(book.bids) == 1
    assert len(book.asks) == 1
    assert "100" in book.bids
    assert "101" in book.asks
    assert "99" not in book.bids
    assert "98" not in book.bids
    assert "102" not in book.asks
    assert "103" not in book.asks

def test_cumulative_calculations():
    """Testa cálculos cumulativos para gráficos."""
    book = OrderBook()
    
    book.apply_snapshot(
        [["100", "1"], ["99", "2"], ["98", "3"]], 
        [["101", "1"], ["102", "2"], ["103", "3"]],
        update_id=1
    )
    
    # Bids cumulativos (ordem decrescente de preço)
    cum_bids = book.cumulative_bids()
    expected_bids = [(Decimal("100"), Decimal("1")), (Decimal("99"), Decimal("3")), (Decimal("98"), Decimal("6"))]
    assert cum_bids == expected_bids
    
    # Asks cumulativos (ordem crescente de preço)
    cum_asks = book.cumulative_asks()
    expected_asks = [(Decimal("101"), Decimal("1")), (Decimal("102"), Decimal("3")), (Decimal("103"), Decimal("6"))]
    assert cum_asks == expected_asks
