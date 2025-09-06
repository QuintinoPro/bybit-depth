# 🤖 Cursor Context - bybit-depth

## 📋 **Visão Geral do Projeto**

**bybit-depth** é um sistema completo para análise de Depth of Market (DOM) da Bybit, desenvolvido em Python com interface visual Streamlit e CLI avançado. O sistema conecta na API WebSocket v5 da Bybit, reconstrói orderbooks em tempo real e oferece análises avançadas de liquidez e métricas de trading.

## 🎯 **Objetivos do Sistema**

1. **Conexão WebSocket**: Conectar na API v5 da Bybit (linear, inverse, spot)
2. **Reconstrução de Orderbook**: Manter livro de ordens local consistente via snapshot + deltas
3. **Persistência**: Salvar dados em JSON e banco SQLite histórico
4. **Interface Visual**: Dashboard Streamlit interativo com gráficos Plotly
5. **CLI Avançado**: Comandos typer para análise e monitoramento
6. **Suporte Completo**: Perpétuos, futuros datados, spot, inverse

## 🏗️ **Arquitetura do Sistema**

```
bybit_depth/
├── core/                    # Núcleo do sistema
│   ├── models.py           # Modelos Pydantic + parsing de símbolos
│   ├── orderbook.py        # Classe OrderBook com validação de sequência
│   ├── ws_client.py        # Cliente WebSocket com reconexão automática
│   ├── aggregator.py       # Análises de liquidez e paredes
│   └── history.py          # Persistência histórica SQLite
├── configs/                 # Configurações
│   ├── settings.py         # Configurações gerais
│   └── symbols.py          # Símbolos por tipo de mercado
├── cli/                     # Interface de linha de comando
│   └── main.py             # Comandos typer avançados
├── viz/                     # Visualização
│   ├── streamlit_app.py    # Interface visual reativa
│   └── plots.py            # Gráficos Plotly
├── tests/                   # Testes unitários
│   ├── test_models.py      # Testes de parsing
│   ├── test_orderbook_advanced.py  # Testes de orderbook
│   └── test_aggregator.py  # Testes de análises
└── utils/                   # Utilitários
    ├── logging.py          # Configuração de logs
    └── retry.py            # Backoff exponencial
```

## 🔧 **Tecnologias e Dependências**

### **Core Dependencies:**
- **websockets==12.0**: Cliente WebSocket assíncrono
- **pydantic>=2.7.0**: Validação de dados e modelos
- **httpx>=0.27.0**: Cliente HTTP assíncrono
- **pandas>=2.2.2**: Manipulação de dados
- **numpy>=1.26.4**: Cálculos numéricos

### **Interface:**
- **streamlit>=1.35.0**: Interface visual reativa
- **plotly>=5.22.0**: Gráficos interativos
- **typer>=0.12.3**: CLI avançado
- **rich>=13.7.1**: Formatação de terminal

### **Desenvolvimento:**
- **pytest>=8.2.0**: Framework de testes
- **mypy>=1.10.0**: Verificação de tipos
- **ruff>=0.5.0**: Linter rápido
- **black>=24.4.2**: Formatação de código

## 🚀 **Funcionalidades Principais**

### **1. Conexão WebSocket Inteligente**
```python
# Suporte a múltiplos mercados
client = BybitWSClient(symbol="BTCUSDT", depth=50, market="linear")
client = BybitWSClient(symbol="BTC-26SEP25", depth=50, market="linear")  # Futuro
client = BybitWSClient(symbol="BTCUSD", depth=50, market="inverse")      # Inverse
```

**Características:**
- Reconexão automática com backoff exponencial
- Validação de sequência de updates
- Heartbeat configurável
- Tratamento robusto de erros

### **2. OrderBook com Validação de Sequência**
```python
book = OrderBook()
book.apply_snapshot(bids, asks, update_id=1)  # Snapshot inicial
success = book.apply_delta(bids, asks, update_id=2)  # Delta com validação
```

**Métricas Disponíveis:**
- `get_stats()`: Estatísticas completas
- `get_liquidity_stats()`: Análise de liquidez
- `cumulative_bids/asks()`: Dados para gráficos
- `detect_walls()`: Identificação de paredes

### **3. Interface Streamlit Reativa**
```python
# Seletores dinâmicos
selected_market = st.selectbox("Tipo de Mercado", market_types)
selected_symbol = st.selectbox("Símbolo", available_symbols)
selected_depth = st.selectbox("Profundidade", depth_options)

# Botão de confirmação
if st.button("✅ Aplicar Configuração"):
    # Aplica mudanças e reconecta automaticamente
```

**Características:**
- Seletores inteligentes por tipo de mercado
- Botão de confirmação para mudanças
- Status visual da conexão
- Métricas em tempo real
- Gráficos interativos Plotly

### **4. CLI Avançado**
```bash
# Monitoramento em tempo real
python3 -m bybit_depth.cli.main monitor --symbol BTCUSDT --market linear

# Análise de profundidade
python3 -m bybit_depth.cli.main depth --info --stats --liquidity 1.0

# Análise histórica
python3 -m bybit_depth.cli.main history --symbol BTCUSDT --hours 24 --stats

# Lista de símbolos suportados
python3 -m bybit_depth.cli.main symbols
```

### **5. Persistência Histórica**
```python
history = OrderbookHistory()
history.save_snapshot(book, symbol, market_type)
snapshots = history.get_snapshots(symbol, start_time, end_time)
stats = history.get_statistics(symbol, start_time, end_time)
```

## 📊 **Tipos de Contratos Suportados**

### **Mercado Linear (Perpétuos)**
- **Símbolos**: BTCUSDT, ETHUSDT, SOLUSDT, ADAUSDT, DOGEUSDT, XRPUSDT
- **Futuros Datados**: BTC-26SEP25, ETH-26SEP25, SOL-31DEC24
- **API**: `wss://stream.bybit.com/v5/public/linear`

### **Mercado Spot**
- **Símbolos**: BTCUSDT, ETHUSDT, SOLUSDT, BTCUSDC, ETHUSDC
- **API**: `wss://stream.bybit.com/v5/public/spot`

### **Mercado Inverse**
- **Símbolos**: BTCUSD, ETHUSD, SOLUSD, ADAUSD
- **API**: `wss://stream.bybit.com/v5/public/inverse`

## 🔍 **Parsing Inteligente de Símbolos**

```python
from bybit_depth.core.models import parse_symbol_type

# Exemplos de parsing
parse_symbol_type("BTCUSDT")      # {'base': 'BTC', 'quote': 'USDT', 'type': 'perpetual', 'expiry': None}
parse_symbol_type("BTC-26SEP25")  # {'base': 'BTC', 'quote': 'USDT', 'type': 'futures', 'expiry': '26SEP25'}
parse_symbol_type("BTCUSD")       # {'base': 'BTC', 'quote': 'USD', 'type': 'perpetual', 'expiry': None}
```

## 🧪 **Sistema de Testes**

```bash
# Executar todos os testes
python3 -m pytest bybit_depth/tests/ -v

# Testes específicos
python3 -m pytest bybit_depth/tests/test_models.py -v
python3 -m pytest bybit_depth/tests/test_orderbook_advanced.py -v
```

**Cobertura de Testes:**
- Parsing de símbolos (perpétuos, futuros, spot)
- Validação de sequência de orderbook
- Cálculos de liquidez e estatísticas
- Persistência histórica
- Casos extremos e edge cases

## ⚙️ **Configuração e Uso**

### **Variáveis de Ambiente**
```bash
export MARKET=linear          # linear, inverse, spot
export SYMBOL=BTCUSDT         # Símbolo padrão
export DEPTH=50               # Profundidade do orderbook
export WS_LINEAR=wss://...    # URL WebSocket linear
export WS_INVERSE=wss://...   # URL WebSocket inverse
export WS_SPOT=wss://...      # URL WebSocket spot
```

### **Execução do Sistema**
```bash
# 1. Interface visual (recomendado)
streamlit run bybit_depth/viz/streamlit_app.py

# 2. Runner com parâmetros
python3 -m bybit_depth.runner --symbol BTCUSDT --market linear --depth 50

# 3. Monitoramento CLI
python3 -m bybit_depth.cli.main monitor --symbol ETHUSDT --market spot
```

## 🎯 **Fluxo de Dados**

1. **Conexão WebSocket** → Recebe mensagens de orderbook
2. **Validação de Sequência** → Verifica update_id para consistência
3. **Aplicação de Updates** → Snapshot inicial + deltas incrementais
4. **Cálculo de Métricas** → Spread, liquidez, estatísticas
5. **Persistência** → JSON para interface + SQLite para histórico
6. **Visualização** → Gráficos Plotly + métricas em tempo real

## 🔧 **Padrões de Desenvolvimento**

### **Estrutura de Código**
- **Type Hints**: Todos os métodos com anotações de tipo
- **Pydantic Models**: Validação automática de dados
- **Async/Await**: Operações assíncronas para WebSocket
- **Error Handling**: Tratamento robusto de exceções
- **Logging**: Sistema de logs estruturado

### **Convenções**
- **Snake_case**: Para funções e variáveis
- **PascalCase**: Para classes
- **UPPER_CASE**: Para constantes
- **Docstrings**: Documentação em todos os métodos públicos

## 🚨 **Pontos de Atenção**

### **Validação de Sequência**
- O sistema valida `update_id` para garantir consistência
- Deltas com ID menor ou igual são rejeitados
- Em caso de erro, pode ser necessário novo snapshot

### **Reconexão WebSocket**
- Backoff exponencial com jitter para evitar spam
- Limite de 10 tentativas consecutivas
- Reset de contadores em reconexões bem-sucedidas

### **Performance**
- OrderBook usa `Decimal` para precisão monetária
- Limpeza automática de níveis com quantidade zero/negativa
- Índices SQLite otimizados para consultas históricas

## 📈 **Métricas e Análises**

### **Métricas de OrderBook**
- **Spread**: Diferença entre best bid e ask
- **Spread %**: Spread como porcentagem do preço médio
- **Liquidez**: Volume total em faixas de preço
- **Desequilíbrio**: Assimetria entre bids e asks
- **Paredes**: Níveis com volume anômalo

### **Métricas de Qualidade**
- **Taxa de Erro**: Porcentagem de deltas rejeitados
- **Total de Updates**: Contador de mensagens processadas
- **Níveis Ativos**: Quantidade de níveis bid/ask

## 🎨 **Interface Visual**

### **Componentes Principais**
- **Seletores**: Mercado, símbolo, profundidade, refresh rate
- **Métricas**: Best bid/ask, mid price, spread
- **Gráfico**: Profundidade cumulativa Plotly
- **Tabelas**: Níveis bid/ask em tempo real
- **Estatísticas**: Métricas de qualidade do orderbook

### **Controles**
- **Aplicar Configuração**: Confirma mudanças e reconecta
- **Parar Conexão**: Para processo atual
- **Status Visual**: Verde (conectado) / Vermelho (desconectado)

## 🔄 **Fluxo de Desenvolvimento**

1. **Modificar Código** → Fazer alterações nos arquivos
2. **Executar Testes** → `python3 -m pytest bybit_depth/tests/ -v`
3. **Verificar Linting** → `ruff check bybit_depth/`
4. **Testar Interface** → `streamlit run bybit_depth/viz/streamlit_app.py`
5. **Commit e Push** → `git add . && git commit -m "..." && git push`

## 📚 **Recursos Adicionais**

### **Documentação**
- `CHANGELOG.md`: Histórico de mudanças
- `INTERFACE_GUIDE.md`: Guia de uso da interface
- `README.md`: Documentação principal

### **Exemplos de Uso**
```python
# Exemplo: Análise de liquidez
book = OrderBook()
# ... aplicar dados ...
liq_stats = book.get_liquidity_stats(1.0)  # ±1% do mid price
print(f"Liquidez Bid: {liq_stats['bid_liquidity']}")
print(f"Liquidez Ask: {liq_stats['ask_liquidity']}")
print(f"Desequilíbrio: {liq_stats['liquidity_imbalance']}")
```

### **Debugging**
```python
# Ativar logs detalhados
import logging
logging.basicConfig(level=logging.DEBUG)

# Verificar status do orderbook
stats = book.get_stats()
print(f"Updates: {stats['total_updates']}")
print(f"Erros: {stats['sequence_errors']}")
print(f"Taxa de erro: {stats['error_rate']:.2f}%")
```

## 🎯 **Próximas Melhorias Sugeridas**

1. **Alertas**: Sistema de notificações para condições específicas
2. **Backtesting**: Análise de dados históricos
3. **Múltiplos Símbolos**: Monitoramento simultâneo
4. **API REST**: Endpoints para integração externa
5. **Dashboard Avançado**: Mais visualizações e métricas

---

**Este documento serve como contexto completo para o Cursor entender o projeto bybit-depth e acelerar o desenvolvimento em qualquer máquina.** 🚀
