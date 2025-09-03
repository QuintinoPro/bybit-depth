from __future__ import annotations
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

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
