from __future__ import annotations
# --- FIX para rodar via `streamlit run bybit_depth\viz\streamlit_app.py` ---
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
# ---------------------------------------------------------------------------

import json
import os
import time

import streamlit as st

from bybit_depth.configs.settings import settings
from bybit_depth.core.orderbook import OrderBook
from bybit_depth.viz.plots import depth_figure

st.set_page_config(page_title="Bybit DOM", layout="wide")

st.title("📊 Bybit Depth of Market (DOM)")
st.caption("Atualize as configurações na barra lateral.")

with st.sidebar:
    data_file = st.text_input("Arquivo JSON (gerado pelo runner)", value=settings.data_file)
    refresh_ms = st.number_input("Refresh (ms)", value=settings.refresh_ms, step=250, min_value=250)
    st.markdown("**Dica:** rode `python -m bybit_depth.runner` em outro terminal.")

placeholder = st.empty()

def load_book_from_json(path: str) -> OrderBook | None:
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        book = OrderBook()
        book.apply_snapshot(payload.get("bids", []), payload.get("asks", []))
        return book
    except Exception as e:  # noqa: BLE001
        st.error(f"Falha ao ler {path}: {e}")
        return None

# contador de refresh para garantir keys únicas a cada iteração
counter = 0

while True:
    counter += 1
    book = load_book_from_json(data_file)
    with placeholder.container():
        if book is None or (not book.bids and not book.asks):
            st.warning("Aguardando dados... Verifique se o runner está executando.")
        else:
            bb = book.best_bid()
            ba = book.best_ask()
            mid = book.mid()

            c_b = book.cumulative_bids()
            c_a = book.cumulative_asks()
            fig = depth_figure(c_b, c_a)

            col1, col2, col3 = st.columns(3)
            col1.metric("Best Bid", f"{bb}" if bb else "-")
            col2.metric("Best Ask", f"{ba}" if ba else "-")
            col3.metric("Mid", f"{mid}" if mid else "-")

            # 👉 KEY ÚNICO evita StreamlitDuplicateElementId
            st.plotly_chart(fig, use_container_width=True, key=f"depth_chart_{counter}")

            st.subheader("Top 10 níveis")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Bids**")
                bids = [(str(p), str(q)) for p, q in book.top_levels("bid", 10)]
                st.table(bids)
            with c2:
                st.markdown("**Asks**")
                asks = [(str(p), str(q)) for p, q in book.top_levels("ask", 10)]
                st.table(asks)

    time.sleep(max(0.25, refresh_ms / 1000.0))
