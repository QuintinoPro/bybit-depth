# ⚡ Setup Rápido - bybit-depth

## 🚀 **Configuração em 5 Minutos**

### **1. Clone e Instalação**
```bash
git clone https://github.com/QuintinoPro/bybit-depth.git
cd bybit-depth
pip install -r requirements.txt
```

### **2. Teste Rápido**
```bash
# Verificar se tudo está funcionando
python3 -m pytest bybit_depth/tests/ -v

# Testar CLI
python3 -m bybit_depth.cli.main symbols

# Testar runner
python3 -m bybit_depth.runner --help
```

### **3. Interface Visual (Recomendado)**
```bash
streamlit run bybit_depth/viz/streamlit_app.py
```

**Na interface:**
1. Escolha o mercado (Linear, Spot, Inverse)
2. Selecione o símbolo (BTCUSDT, ETHUSDT, etc.)
3. Clique em "✅ Aplicar Configuração"
4. Aguarde a conexão e observe o gráfico!

## 🎯 **Comandos Essenciais**

### **Interface Visual**
```bash
streamlit run bybit_depth/viz/streamlit_app.py
```

### **Monitoramento CLI**
```bash
python3 -m bybit_depth.cli.main monitor --symbol BTCUSDT --market linear
```

### **Runner com Parâmetros**
```bash
python3 -m bybit_depth.runner --symbol ETHUSDT --market spot --depth 50
```

### **Análise de Dados**
```bash
python3 -m bybit_depth.cli.main depth --info --stats --symbol BTCUSDT
python3 -m bybit_depth.cli.main history --symbol BTCUSDT --stats
```

## 📊 **Símbolos Suportados**

### **Mercado Linear (Perpétuos)**
- BTCUSDT, ETHUSDT, SOLUSDT, ADAUSDT, DOGEUSDT, XRPUSDT
- Futuros: BTC-26SEP25, ETH-26SEP25, SOL-31DEC24

### **Mercado Spot**
- BTCUSDT, ETHUSDT, SOLUSDT, BTCUSDC, ETHUSDC

### **Mercado Inverse**
- BTCUSD, ETHUSD, SOLUSD, ADAUSD

## 🔧 **Configuração Avançada**

### **Variáveis de Ambiente**
```bash
export MARKET=linear
export SYMBOL=BTCUSDT
export DEPTH=50
```

### **Arquivo .env**
```bash
MARKET=linear
SYMBOL=BTCUSDT
DEPTH=50
WS_LINEAR=wss://stream.bybit.com/v5/public/linear
WS_SPOT=wss://stream.bybit.com/v5/public/spot
WS_INVERSE=wss://stream.bybit.com/v5/public/inverse
```

## 🚨 **Solução de Problemas**

### **Erro de Importação**
```bash
# Verificar se está no diretório correto
pwd
# Deve mostrar: /path/to/bybit-depth

# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

### **Interface Não Carrega**
```bash
# Verificar se Streamlit está instalado
pip list | grep streamlit

# Executar com debug
streamlit run bybit_depth/viz/streamlit_app.py --logger.level debug
```

### **WebSocket Não Conecta**
```bash
# Testar conectividade
python3 -c "import websockets; print('WebSocket OK')"

# Verificar logs
python3 -m bybit_depth.runner --symbol BTCUSDT --market linear
```

## 📚 **Documentação Completa**

- **`CURSOR_CONTEXT.md`**: Contexto completo para Cursor
- **`INTERFACE_GUIDE.md`**: Guia detalhado da interface
- **`CHANGELOG.md`**: Histórico de mudanças
- **`README.md`**: Documentação principal

## 🎯 **Próximos Passos**

1. **Teste a interface** com diferentes símbolos
2. **Explore os comandos CLI** disponíveis
3. **Configure variáveis de ambiente** se necessário
4. **Leia a documentação** para funcionalidades avançadas

## 🚀 **Desenvolvimento**

### **Estrutura do Projeto**
```
bybit_depth/
├── core/           # Núcleo (orderbook, websocket, models)
├── configs/        # Configurações
├── cli/            # Interface CLI
├── viz/            # Interface visual
├── tests/          # Testes
└── utils/          # Utilitários
```

### **Comandos de Desenvolvimento**
```bash
# Executar testes
python3 -m pytest bybit_depth/tests/ -v

# Verificar linting
ruff check bybit_depth/

# Formatar código
black bybit_depth/

# Verificar tipos
mypy bybit_depth/
```

---

**Sistema pronto para uso! 🎉**
