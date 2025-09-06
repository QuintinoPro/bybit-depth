from __future__ import annotations
import asyncio
import json
import logging
from typing import Optional

import websockets

from ..configs.settings import settings
from .models import WSOrderbookMessage, parse_symbol_type
from .orderbook import OrderBook
from ..utils.retry import backoff_retry

log = logging.getLogger("ws_client")

class BybitWSClient:
    def __init__(self, symbol: str, depth: int, market: str) -> None:
        self.symbol = symbol
        self.depth = depth
        self.market = market
        
        # Determinar URL WebSocket baseado no tipo de mercado
        if market.lower() == "linear":
            self.ws_url = settings.ws_linear
        elif market.lower() == "inverse":
            self.ws_url = settings.ws_inverse
        else:  # spot
            self.ws_url = settings.ws_spot
            
        self.book = OrderBook()
        self.book.symbol = symbol
        self.book.market_type = market
        
        # Analisar tipo de contrato
        symbol_info = parse_symbol_type(symbol)
        log.info(f"Símbolo {symbol} identificado como: {symbol_info}")
        
        self._task: Optional[asyncio.Task] = None
        self._connected = asyncio.Event()
        self._reconnect_count = 0

    async def run_forever(self) -> None:
        attempt = 0
        max_attempts = 10  # Limite de tentativas consecutivas
        
        while True:
            try:
                await self._connect_and_listen()
                attempt = 0  # reset on clean exit
                self._reconnect_count = 0  # reset contador de reconexões
                log.info(f"WebSocket conectado com sucesso para {self.symbol}")
            except websockets.exceptions.ConnectionClosed as e:
                log.warning(f"Conexão WebSocket fechada para {self.symbol}: {e}")
                attempt += 1
                self._reconnect_count += 1
                if attempt >= max_attempts:
                    log.error(f"Máximo de tentativas atingido para {self.symbol}. Parando reconexão.")
                    break
                await backoff_retry(attempt=attempt)
            except Exception as e:  # noqa: BLE001
                log.exception(f"Erro inesperado no WebSocket para {self.symbol}: {e}")
                attempt += 1
                self._reconnect_count += 1
                if attempt >= max_attempts:
                    log.error(f"Máximo de tentativas atingido para {self.symbol}. Parando reconexão.")
                    break
                await backoff_retry(attempt=attempt)

    async def _connect_and_listen(self) -> None:
        sub_msg = {
            "op": "subscribe",
            "args": [f"orderbook.{self.depth}.{self.symbol}"],
        }
        ping_interval = 20
        ping_timeout = 10

        log.info("Conectando ao %s", self.ws_url)
        async with websockets.connect(
            self.ws_url, 
            ping_interval=ping_interval,
            ping_timeout=ping_timeout,
            close_timeout=10
        ) as ws:
            await ws.send(json.dumps(sub_msg))
            log.info("Inscrito em %s", sub_msg["args"][0])
            self._connected.set()

            # Reset contador de erros de sequência ao conectar
            self.book._sequence_errors = 0

            async for raw in ws:
                try:
                    # Validar se a mensagem não está vazia
                    if not raw or raw.strip() == "":
                        continue
                        
                    msg = WSOrderbookMessage.model_validate_json(raw)
                except Exception as e:
                    log.debug("Payload WebSocket inválido: %s - Erro: %s", raw, e)
                    continue

                if not msg.data:
                    continue

                # Validar se o símbolo corresponde
                if msg.data.s and msg.data.s != self.symbol:
                    log.debug("Mensagem para símbolo diferente: %s (esperado: %s)", msg.data.s, self.symbol)
                    continue

                if msg.type == "snapshot":
                    b = msg.data.b or []
                    a = msg.data.a or []
                    self.book.apply_snapshot(b, a, msg.data.u)
                    log.info(f"Snapshot aplicado para {self.symbol}: {len(b)} bids, {len(a)} asks")
                elif msg.type == "delta":
                    b = msg.data.b or []
                    a = msg.data.a or []
                    success = self.book.apply_delta(b, a, msg.data.u)
                    if not success:
                        log.warning(f"Delta rejeitado para {self.symbol} devido a erro de sequência")
                        # Em caso de erro de sequência, pode ser necessário solicitar novo snapshot
                        # ou implementar lógica de recuperação

    async def wait_connected(self, timeout: float = 10.0) -> bool:
        try:
            await asyncio.wait_for(self._connected.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            return False
