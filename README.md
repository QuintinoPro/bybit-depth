# 📊 bybit-depth

Sistema completo para análise de Depth of Market (DOM) da Bybit com interface visual reativa e CLI avançado.

## 🚀 **Funcionalidades Principais**

- **🔌 Conexão WebSocket**: API v5 da Bybit (linear, inverse, spot)
- **📈 OrderBook em Tempo Real**: Reconstrução via snapshot + deltas
- **🎨 Interface Visual**: Dashboard Streamlit reativo com gráficos Plotly
- **💻 CLI Avançado**: Comandos typer para monitoramento e análise
- **💾 Persistência Histórica**: Banco SQLite para snapshots
- **🧪 Testes Abrangentes**: 14/14 testes passando

## ⚡ **Setup Rápido**

```bash
# Clone e instalação
git clone https://github.com/QuintinoPro/bybit-depth.git
cd bybit-depth
pip install -r requirements.txt

# Interface visual (recomendado)
streamlit run bybit_depth/viz/streamlit_app.py

# Ou monitoramento CLI
python3 -m bybit_depth.cli.main monitor --symbol BTCUSDT --market linear
```

## 📊 **Símbolos Suportados**

### **Mercado Linear (Perpétuos)**
- **Perpétuos**: BTCUSDT, ETHUSDT, SOLUSDT, ADAUSDT, DOGEUSDT, XRPUSDT
- **Futuros Datados**: BTC-26SEP25, ETH-26SEP25, SOL-31DEC24

### **Mercado Spot**
- BTCUSDT, ETHUSDT, SOLUSDT, BTCUSDC, ETHUSDC

### **Mercado Inverse**
- BTCUSD, ETHUSD, SOLUSD, ADAUSD

## 🎯 **Como Usar**

### **1. Interface Visual (Recomendado)**
```bash
streamlit run bybit_depth/viz/streamlit_app.py
```

**Na interface:**
1. Escolha o mercado e símbolo na barra lateral
2. Clique em "✅ Aplicar Configuração"
3. Aguarde a conexão e observe o gráfico!

### **2. CLI para Monitoramento**
```bash
# Monitoramento em tempo real
python3 -m bybit_depth.cli.main monitor --symbol BTCUSDT --market linear

# Análise de profundidade
python3 -m bybit_depth.cli.main depth --info --stats --symbol BTCUSDT

# Análise histórica
python3 -m bybit_depth.cli.main history --symbol BTCUSDT --hours 24 --stats

# Lista de símbolos
python3 -m bybit_depth.cli.main symbols
```

### **3. Runner com Parâmetros**
```bash
python3 -m bybit_depth.runner --symbol ETHUSDT --market spot --depth 50
```

## 🏗️ **Arquitetura**

```
bybit_depth/
├── core/                    # Núcleo do sistema
│   ├── models.py           # Modelos Pydantic + parsing de símbolos
│   ├── orderbook.py        # OrderBook com validação de sequência
│   ├── ws_client.py        # Cliente WebSocket com reconexão
│   ├── aggregator.py       # Análises de liquidez e paredes
│   └── history.py          # Persistência histórica SQLite
├── configs/                 # Configurações
│   ├── settings.py         # Configurações gerais
│   └── symbols.py          # Símbolos por tipo de mercado
├── cli/                     # Interface CLI
│   └── main.py             # Comandos typer avançados
├── viz/                     # Visualização
│   ├── streamlit_app.py    # Interface visual reativa
│   └── plots.py            # Gráficos Plotly
├── tests/                   # Testes unitários
└── utils/                   # Utilitários
```

## 🔧 **Tecnologias**

- **Python 3.9+**
- **WebSocket**: `websockets==12.0`
- **Interface**: `streamlit>=1.35.0` + `plotly>=5.22.0`
- **CLI**: `typer>=0.12.3` + `rich>=13.7.1`
- **Dados**: `pydantic>=2.7.0` + `pandas>=2.2.2`
- **Testes**: `pytest>=8.2.0`

## 📚 **Documentação**

- **`SETUP_QUICK.md`**: Setup rápido em 5 minutos
- **`INTERFACE_GUIDE.md`**: Guia completo da interface
- **`CURSOR_CONTEXT.md`**: Contexto completo para Cursor
- **`CHANGELOG.md`**: Histórico de mudanças e melhorias

## 🧪 **Testes**

```bash
# Executar todos os testes
python3 -m pytest bybit_depth/tests/ -v

# Testes específicos
python3 -m pytest bybit_depth/tests/test_models.py -v
python3 -m pytest bybit_depth/tests/test_orderbook_advanced.py -v
```

## 🚨 **Solução de Problemas**

### **Interface Não Reage às Mudanças**
- Clique em "✅ Aplicar Configuração" após mudar configurações
- Verifique se a conexão está ativa (status verde)

### **WebSocket Não Conecta**
- Verifique se o símbolo é válido para o mercado selecionado
- Teste com `python3 -m bybit_depth.cli.main symbols`

### **Erro de Importação**
- Execute `pip install -r requirements.txt --force-reinstall`
- Verifique se está no diretório correto

## 🎯 **Funcionalidades Avançadas**

### **Métricas de OrderBook**
- Spread absoluto e percentual
- Análise de liquidez em faixas de preço
- Detecção de paredes (níveis anômalos)
- Estatísticas de qualidade (taxa de erro, updates)

### **Persistência Histórica**
- Banco SQLite para snapshots históricos
- Análise de tendências e estatísticas
- Restauração de orderbooks históricos

### **Validação de Sequência**
- Controle de `update_id` para consistência
- Rejeição de deltas fora de ordem
- Métricas de qualidade em tempo real

## 🚀 **Desenvolvimento**

```bash
# Verificar linting
ruff check bybit_depth/

# Formatar código
black bybit_depth/

# Verificar tipos
mypy bybit_depth/

# Executar testes
python3 -m pytest bybit_depth/tests/ -v
```

## 📈 **Roadmap**

- [ ] Sistema de alertas para condições específicas
- [ ] Backtesting com dados históricos
- [ ] Monitoramento de múltiplos símbolos
- [ ] API REST para integração externa
- [ ] Dashboard com mais visualizações

## 🤝 **Contribuição**

1. Fork o projeto
2. Crie uma branch para sua feature
3. Execute os testes: `python3 -m pytest bybit_depth/tests/ -v`
4. Commit suas mudanças
5. Push para a branch
6. Abra um Pull Request

## 📄 **Licença**

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

**Sistema bybit-depth - Análise avançada de Depth of Market da Bybit** 🚀
