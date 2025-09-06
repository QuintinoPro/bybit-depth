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
import subprocess
import threading

import streamlit as st

from bybit_depth.configs.settings import settings
from bybit_depth.configs.symbols import get_symbols_for_market, get_market_types, get_depth_options, get_refresh_options
from bybit_depth.core.orderbook import OrderBook
from bybit_depth.core.models import parse_symbol_type
from bybit_depth.viz.plots import depth_figure

st.set_page_config(page_title="Bybit DOM", layout="wide")

st.title("📊 Bybit Depth of Market (DOM)")
st.caption("Configure o mercado e símbolo desejado, depois clique em 'Aplicar Configuração'.")

# Inicializar session state
if 'config_applied' not in st.session_state:
    st.session_state.config_applied = False
if 'runner_process' not in st.session_state:
    st.session_state.runner_process = None
if 'current_config' not in st.session_state:
    st.session_state.current_config = {}

with st.sidebar:
    st.header("⚙️ Configurações")
    
    # Seletor de tipo de mercado
    market_types = get_market_types()
    selected_market = st.selectbox(
        "Tipo de Mercado",
        options=market_types,
        index=market_types.index(settings.market) if settings.market in market_types else 0,
        help="Escolha entre Linear (perpétuos), Inverse (futuros inversos) ou Spot"
    )
    
    # Seletor de símbolo baseado no mercado
    available_symbols = get_symbols_for_market(selected_market)
    if available_symbols:
        # Filtrar símbolos populares primeiro
        popular_symbols = [s for s in available_symbols if s in ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "DOGEUSDT", "XRPUSDT"]]
        other_symbols = [s for s in available_symbols if s not in popular_symbols]
        sorted_symbols = popular_symbols + other_symbols
        
        selected_symbol = st.selectbox(
            "Símbolo",
            options=sorted_symbols,
            index=0,
            help="Escolha o ativo para análise"
        )
    else:
        selected_symbol = st.text_input("Símbolo", value=settings.symbol)
    
    # Seletor de profundidade
    depth_options = get_depth_options(selected_market)
    selected_depth = st.selectbox(
        "Profundidade",
        options=depth_options,
        index=depth_options.index(settings.depth) if settings.depth in depth_options else 2,
        help="Número de níveis de preço a serem exibidos"
    )
    
    # Seletor de refresh rate
    refresh_options = get_refresh_options()
    selected_refresh = st.selectbox(
        "Taxa de Atualização",
        options=[opt[0] for opt in refresh_options],
        format_func=lambda x: next(opt[1] for opt in refresh_options if opt[0] == x),
        index=2,  # 1s por padrão
        help="Frequência de atualização do gráfico"
    )
    
    # Informações do símbolo selecionado
    if selected_symbol:
        symbol_info = parse_symbol_type(selected_symbol)
        st.info(f"""
        **Informações do Símbolo:**
        - **Tipo:** {symbol_info['type'].title()}
        - **Base:** {symbol_info['base']}
        - **Quote:** {symbol_info['quote']}
        - **Expiry:** {symbol_info['expiry'] or 'N/A'}
        """)
    
    st.divider()
    
    # Botão de aplicação de configuração
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Aplicar Configuração", type="primary", use_container_width=True):
            # Salvar configuração atual
            st.session_state.current_config = {
                'market': selected_market,
                'symbol': selected_symbol,
                'depth': selected_depth,
                'refresh': selected_refresh
            }
            
            # Parar processo anterior se existir
            if st.session_state.runner_process:
                try:
                    st.session_state.runner_process.terminate()
                    st.session_state.runner_process = None
                except:
                    pass
            
            # Iniciar novo processo
            try:
                cmd = [
                    'python3', '-m', 'bybit_depth.runner',
                    '--symbol', selected_symbol,
                    '--market', selected_market,
                    '--depth', str(selected_depth),
                    '--data-file', f'data/orderbook_{selected_symbol}_{selected_market}.json'
                ]
                
                st.session_state.runner_process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                st.session_state.config_applied = True
                st.success(f"✅ Conectando ao {selected_symbol} ({selected_market})...")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erro ao iniciar conexão: {e}")
    
    with col2:
        if st.button("🛑 Parar Conexão", type="secondary", use_container_width=True):
            if st.session_state.runner_process:
                try:
                    st.session_state.runner_process.terminate()
                    st.session_state.runner_process = None
                    st.session_state.config_applied = False
                    st.success("🛑 Conexão parada")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro ao parar conexão: {e}")
    
    # Status da conexão
    if st.session_state.config_applied and st.session_state.runner_process:
        if st.session_state.runner_process.poll() is None:
            st.success("🟢 Conectado e funcionando")
        else:
            st.error("🔴 Conexão perdida")
            st.session_state.config_applied = False
    
    st.divider()
    
    # Configurações avançadas
    st.subheader("🔧 Configurações Avançadas")
    data_file = st.text_input(
        "Arquivo JSON", 
        value=f"data/orderbook_{selected_symbol}_{selected_market}.json" if st.session_state.config_applied else settings.data_file,
        disabled=st.session_state.config_applied
    )
    
    # Instruções
    st.markdown("""
    **💡 Como usar:**
    1. Escolha o mercado e símbolo
    2. Clique em "Aplicar Configuração"
    3. Aguarde a conexão ser estabelecida
    4. O gráfico será atualizado automaticamente
    """)

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
        return None

# Exibir informações da configuração atual
if st.session_state.config_applied and st.session_state.current_config:
    config = st.session_state.current_config
    st.info(f"""
    **📊 Configuração Ativa:**
    - **Mercado:** {config['market'].title()}
    - **Símbolo:** {config['symbol']}
    - **Profundidade:** {config['depth']}
    - **Refresh:** {config['refresh']}ms
    """)

# Container principal
placeholder = st.empty()

# Loop principal apenas se a configuração foi aplicada
if st.session_state.config_applied and st.session_state.current_config:
    config = st.session_state.current_config
    data_file = f"data/orderbook_{config['symbol']}_{config['market']}.json"
    
    # Criar diretório se não existir
    os.makedirs(os.path.dirname(data_file), exist_ok=True)
    
    # Contador para keys únicos
    if 'counter' not in st.session_state:
        st.session_state.counter = 0
    
    while st.session_state.config_applied:
        st.session_state.counter += 1
        
        # Verificar se o processo ainda está rodando
        if st.session_state.runner_process and st.session_state.runner_process.poll() is not None:
            st.error("🔴 Processo do runner parou inesperadamente")
            st.session_state.config_applied = False
            break
        
        book = load_book_from_json(data_file)
        
        with placeholder.container():
            if book is None or (not book.bids and not book.asks):
                st.warning("⏳ Aguardando dados... Verifique se a conexão foi estabelecida.")
                st.markdown(f"""
                **🔄 Conectando ao {config['symbol']} ({config['market']}):**
                ```bash
                python3 -m bybit_depth.runner --symbol {config['symbol']} --market {config['market']} --depth {config['depth']}
                ```
                """)
            else:
                bb = book.best_bid()
                ba = book.best_ask()
                mid = book.mid()

                c_b = book.cumulative_bids()
                c_a = book.cumulative_asks()
                fig = depth_figure(c_b, c_a)

                # Métricas principais
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Best Bid", f"{bb:.2f}" if bb else "-", delta=None)
                col2.metric("Best Ask", f"{ba:.2f}" if ba else "-", delta=None)
                col3.metric("Mid Price", f"{mid:.2f}" if mid else "-", delta=None)
                
                # Spread
                spread = float(ba - bb) if bb and ba else 0
                spread_pct = (spread / float(mid)) * 100 if mid and spread > 0 else 0
                col4.metric("Spread", f"{spread:.4f}", f"{spread_pct:.4f}%")

                # Gráfico de profundidade
                st.plotly_chart(fig, use_container_width=True, key=f"depth_chart_{st.session_state.counter}")

                # Tabelas de níveis
                st.subheader(f"📈 Top {min(10, config['depth'])} Níveis - {config['symbol']}")
                c1, c2 = st.columns(2)
                
                with c1:
                    st.markdown("**🔵 Bids (Compras)**")
                    bids = [(str(p), str(q)) for p, q in book.top_levels("bid", min(10, config['depth']))]
                    if bids:
                        st.dataframe(bids, width='stretch', hide_index=True)
                    else:
                        st.text("Nenhum bid disponível")
                
                with c2:
                    st.markdown("**🔴 Asks (Vendas)**")
                    asks = [(str(p), str(q)) for p, q in book.top_levels("ask", min(10, config['depth']))]
                    if asks:
                        st.dataframe(asks, width='stretch', hide_index=True)
                    else:
                        st.text("Nenhum ask disponível")

                # Estatísticas adicionais
                if hasattr(book, 'get_stats'):
                    stats = book.get_stats()
                    st.subheader("📊 Estatísticas do Orderbook")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Níveis Bid", stats.get('bid_levels', 0))
                    col2.metric("Níveis Ask", stats.get('ask_levels', 0))
                    col3.metric("Total Updates", stats.get('total_updates', 0))
                    col4.metric("Erros de Sequência", stats.get('sequence_errors', 0))

        # Pausa baseada no refresh rate
        time.sleep(max(0.25, config['refresh'] / 1000.0))
        
        # Verificar se o usuário mudou a configuração
        if not st.session_state.config_applied:
            break

else:
    # Tela inicial quando nenhuma configuração foi aplicada
    st.info("""
    **🚀 Bem-vindo ao Bybit DOM!**
    
    Para começar:
    1. Configure o mercado e símbolo na barra lateral
    2. Clique em "Aplicar Configuração"
    3. Aguarde a conexão ser estabelecida
    4. O gráfico será atualizado automaticamente
    """)
    
    # Mostrar exemplo de configuração
    st.subheader("📋 Exemplo de Configuração")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Mercado Linear (Perpétuos)**")
        st.code("BTCUSDT, ETHUSDT, SOLUSDT")
    
    with col2:
        st.markdown("**Mercado Spot**")
        st.code("BTCUSDT, ETHUSDT, ADAUSDT")
    
    with col3:
        st.markdown("**Futuros Datados**")
        st.code("BTC-26SEP25, ETH-26SEP25")