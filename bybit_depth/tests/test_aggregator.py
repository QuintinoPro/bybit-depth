from bybit_depth.core.orderbook import OrderBook
from bybit_depth.core.aggregator import imbalance, detect_walls, band_liquidity

def make_book():
    ob = OrderBook()
    ob.apply_snapshot([["99","2"],["98","1"]],[["101","2"],["102","8"]])
    return ob

def test_imbalance():
    ob = make_book()
    obi = imbalance(ob, top_n=2)
    assert 0 <= obi <= 1

def test_walls():
    ob = make_book()
    walls = detect_walls(ob, side="ask", std_k=1.0, min_abs=5.0, top_n=5)
    assert walls

def test_band():
    ob = make_book()
    res = band_liquidity(ob, pct=1.0)
    assert res is not None
    assert "bids" in res and "asks" in res
