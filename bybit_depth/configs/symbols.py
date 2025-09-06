from __future__ import annotations
from typing import Dict, List, Tuple

# Símbolos disponíveis por tipo de mercado
SYMBOLS_BY_MARKET = {
    "linear": [
        # Perpétuos
        "BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "DOGEUSDT", "XRPUSDT",
        "MATICUSDT", "AVAXUSDT", "LINKUSDT", "UNIUSDT", "ATOMUSDT", "DOTUSDT",
        # Futuros datados
        "BTC-26SEP25", "ETH-26SEP25", "ADA-26SEP25", "SOL-26SEP25",
        "BTC-31DEC24", "ETH-31DEC24", "ADA-31DEC24", "SOL-31DEC24",
    ],
    "inverse": [
        # Futuros inversos
        "BTCUSD", "ETHUSD", "ADAUSD", "SOLUSD", "DOGEUSD", "XRPUSD",
        "MATICUSD", "AVAXUSD", "LINKUSD", "UNIUSD", "ATOMUSD", "DOTUSD",
    ],
    "spot": [
        # Spot trading
        "BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "DOGEUSDT", "XRPUSDT",
        "MATICUSDT", "AVAXUSDT", "LINKUSDT", "UNIUSDT", "ATOMUSDT", "DOTUSDT",
        "BTCUSDC", "ETHUSDC", "ADAUSDC", "SOLUSDC",
        "BTCBUSD", "ETHBUSD", "ADABUSD", "SOLBUSD",
    ]
}

# Símbolos populares para exibição
POPULAR_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "DOGEUSDT", "XRPUSDT",
    "MATICUSDT", "AVAXUSDT", "LINKUSDT", "UNIUSDT", "ATOMUSDT", "DOTUSDT"
]

# Configurações de profundidade por tipo de mercado
DEPTH_OPTIONS = {
    "linear": [10, 25, 50, 100, 200],
    "inverse": [10, 25, 50, 100, 200],
    "spot": [10, 25, 50, 100, 200]
}

# Configurações de refresh rate
REFRESH_OPTIONS = [
    (250, "250ms - Ultra rápido"),
    (500, "500ms - Rápido"),
    (1000, "1s - Normal"),
    (2000, "2s - Lento"),
    (5000, "5s - Muito lento")
]

def get_symbols_for_market(market: str) -> List[str]:
    """Retorna símbolos disponíveis para um tipo de mercado."""
    return SYMBOLS_BY_MARKET.get(market.lower(), [])

def get_market_types() -> List[str]:
    """Retorna tipos de mercado disponíveis."""
    return list(SYMBOLS_BY_MARKET.keys())

def get_depth_options(market: str) -> List[int]:
    """Retorna opções de profundidade para um tipo de mercado."""
    return DEPTH_OPTIONS.get(market.lower(), [10, 25, 50, 100])

def get_refresh_options() -> List[Tuple[int, str]]:
    """Retorna opções de refresh rate."""
    return REFRESH_OPTIONS
