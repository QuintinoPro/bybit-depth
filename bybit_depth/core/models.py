from __future__ import annotations
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
import re

class OrderbookData(BaseModel):
    s: Optional[str] = None              # symbol
    b: List[List[str]] = Field(default_factory=list)  # bids: [[price, size], ...]
    a: List[List[str]] = Field(default_factory=list)  # asks: [[price, size], ...]
    ts: Optional[int] = None
    u: Optional[int] = None              # update id

class WSOrderbookMessage(BaseModel):
    topic: Optional[str] = None
    type: Optional[Literal["snapshot", "delta"]] = None
    ts: Optional[int] = None
    data: Optional[OrderbookData] = None

def parse_symbol_type(symbol: str) -> dict:
    """
    Analisa o símbolo para determinar o tipo de contrato.
    
    Retorna:
        {
            'base': 'BTC',
            'quote': 'USDT', 
            'type': 'perpetual'|'futures'|'spot',
            'expiry': None|'26SEP25' (para futuros)
        }
    """
    # Padrões para diferentes tipos de contratos
    perpetual_pattern = r'^([A-Z]+)(USDT|USDC|BTC|ETH)$'
    futures_pattern = r'^([A-Z]+)-(\d{2}[A-Z]{3}\d{2})$'
    spot_pattern = r'^([A-Z]+)(USDT|USDC|BTC|ETH)$'
    
    # Verificar se é futuro datado (ex: BTC-26SEP25)
    futures_match = re.match(futures_pattern, symbol)
    if futures_match:
        return {
            'base': futures_match.group(1),
            'quote': 'USDT',  # Assumindo USDT para futuros
            'type': 'futures',
            'expiry': futures_match.group(2)
        }
    
    # Verificar se é perpétuo ou spot
    perpetual_match = re.match(perpetual_pattern, symbol)
    if perpetual_match:
        return {
            'base': perpetual_match.group(1),
            'quote': perpetual_match.group(2),
            'type': 'perpetual',
            'expiry': None
        }
    
    # Fallback para spot
    spot_match = re.match(spot_pattern, symbol)
    if spot_match:
        return {
            'base': spot_match.group(1),
            'quote': spot_match.group(2),
            'type': 'spot',
            'expiry': None
        }
    
    # Se não conseguir identificar, assumir perpétuo
    return {
        'base': symbol,
        'quote': 'USDT',
        'type': 'perpetual',
        'expiry': None
    }
