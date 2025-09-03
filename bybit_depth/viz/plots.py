from __future__ import annotations
from typing import List, Tuple
from decimal import Decimal
import plotly.graph_objects as go

def depth_figure(bids: List[Tuple[Decimal, Decimal]], asks: List[Tuple[Decimal, Decimal]]):
    fig = go.Figure()
    if bids:
        x_b = [float(p) for p, _ in bids[::-1]]  # desenhar crescente
        y_b = [float(c) for _, c in bids[::-1]]
        fig.add_trace(go.Scatter(x=x_b, y=y_b, mode="lines", name="Bids"))
    if asks:
        x_a = [float(p) for p, _ in asks]
        y_a = [float(c) for _, c in asks]
        fig.add_trace(go.Scatter(x=x_a, y=y_a, mode="lines", name="Asks"))
    fig.update_layout(
        title="Depth Chart (cumulativo)",
        xaxis_title="Preço",
        yaxis_title="Quantidade cumulativa",
        hovermode="x unified",
    )
    return fig
