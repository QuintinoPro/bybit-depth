import pytest
from bybit_depth.core.orderbook import OrderBook

@pytest.mark.asyncio
async def test_dummy_ws_flow():
    ob = OrderBook()
    ob.apply_snapshot([], [])
    assert ob.best_bid() is None
    assert ob.best_ask() is None
