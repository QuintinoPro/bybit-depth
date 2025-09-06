from __future__ import annotations
import pytest
from bybit_depth.core.models import parse_symbol_type

def test_parse_perpetual_symbols():
    """Testa parsing de símbolos perpétuos."""
    test_cases = [
        ("BTCUSDT", {"base": "BTC", "quote": "USDT", "type": "perpetual", "expiry": None}),
        ("ETHUSDT", {"base": "ETH", "quote": "USDT", "type": "perpetual", "expiry": None}),
        ("ADAUSDC", {"base": "ADA", "quote": "USDC", "type": "perpetual", "expiry": None}),
        ("BTCBTC", {"base": "BTC", "quote": "BTC", "type": "perpetual", "expiry": None}),
    ]
    
    for symbol, expected in test_cases:
        result = parse_symbol_type(symbol)
        assert result == expected, f"Falha para {symbol}: esperado {expected}, obtido {result}"

def test_parse_futures_symbols():
    """Testa parsing de símbolos de futuros datados."""
    test_cases = [
        ("BTC-26SEP25", {"base": "BTC", "quote": "USDT", "type": "futures", "expiry": "26SEP25"}),
        ("ETH-26SEP25", {"base": "ETH", "quote": "USDT", "type": "futures", "expiry": "26SEP25"}),
        ("ADA-31DEC24", {"base": "ADA", "quote": "USDT", "type": "futures", "expiry": "31DEC24"}),
    ]
    
    for symbol, expected in test_cases:
        result = parse_symbol_type(symbol)
        assert result == expected, f"Falha para {symbol}: esperado {expected}, obtido {result}"

def test_parse_spot_symbols():
    """Testa parsing de símbolos spot."""
    test_cases = [
        ("BTCUSDT", {"base": "BTC", "quote": "USDT", "type": "perpetual", "expiry": None}),  # Perpétuo tem prioridade
        ("ETHUSDC", {"base": "ETH", "quote": "USDC", "type": "perpetual", "expiry": None}),
    ]
    
    for symbol, expected in test_cases:
        result = parse_symbol_type(symbol)
        assert result == expected, f"Falha para {symbol}: esperado {expected}, obtido {result}"

def test_parse_invalid_symbols():
    """Testa parsing de símbolos inválidos."""
    invalid_symbols = [
        "INVALID",
        "BTC-",
        "-26SEP25",
        "BTC-26SEP",
        "BTC-26SEP25-EXTRA",
        "",
        "123",
    ]
    
    for symbol in invalid_symbols:
        result = parse_symbol_type(symbol)
        # Deve retornar um fallback para perpétuo
        assert result["type"] == "perpetual"
        assert result["expiry"] is None
