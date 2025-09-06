from __future__ import annotations
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

from .orderbook import OrderBook

log = logging.getLogger("history")

class OrderbookHistory:
    """Gerencia persistência histórica do orderbook."""
    
    def __init__(self, db_path: str = "data/orderbook_history.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self) -> None:
        """Inicializa o banco de dados SQLite."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS orderbook_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    symbol TEXT NOT NULL,
                    market_type TEXT NOT NULL,
                    best_bid REAL,
                    best_ask REAL,
                    mid_price REAL,
                    spread REAL,
                    spread_pct REAL,
                    bid_levels INTEGER,
                    ask_levels INTEGER,
                    total_updates INTEGER,
                    sequence_errors INTEGER,
                    error_rate REAL,
                    snapshot_data TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_symbol_timestamp 
                ON orderbook_snapshots(symbol, timestamp)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON orderbook_snapshots(timestamp)
            """)
    
    def save_snapshot(self, book: OrderBook, symbol: str, market_type: str) -> None:
        """Salva um snapshot do orderbook no histórico."""
        try:
            stats = book.get_stats()
            snapshot_data = {
                "bids": [[p, str(q)] for p, q in book.bids.items()],
                "asks": [[p, str(q)] for p, q in book.asks.items()],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO orderbook_snapshots 
                    (symbol, market_type, best_bid, best_ask, mid_price, spread, spread_pct,
                     bid_levels, ask_levels, total_updates, sequence_errors, error_rate, snapshot_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    symbol,
                    market_type,
                    stats.get('best_bid'),
                    stats.get('best_ask'),
                    stats.get('mid_price'),
                    stats.get('spread'),
                    stats.get('spread_pct'),
                    stats.get('bid_levels'),
                    stats.get('ask_levels'),
                    stats.get('total_updates'),
                    stats.get('sequence_errors'),
                    stats.get('error_rate'),
                    json.dumps(snapshot_data)
                ))
        except Exception as e:
            log.error(f"Erro ao salvar snapshot: {e}")
    
    def get_snapshots(
        self, 
        symbol: str, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict]:
        """Recupera snapshots históricos."""
        query = "SELECT * FROM orderbook_snapshots WHERE symbol = ?"
        params = [symbol]
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_latest_snapshot(self, symbol: str) -> Optional[Dict]:
        """Recupera o snapshot mais recente para um símbolo."""
        snapshots = self.get_snapshots(symbol, limit=1)
        return snapshots[0] if snapshots else None
    
    def restore_orderbook(self, snapshot_id: int) -> Optional[OrderBook]:
        """Restaura um orderbook a partir de um snapshot histórico."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT snapshot_data FROM orderbook_snapshots WHERE id = ?", 
                (snapshot_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                return None
            
            try:
                snapshot_data = json.loads(row['snapshot_data'])
                book = OrderBook()
                book.apply_snapshot(
                    snapshot_data['bids'], 
                    snapshot_data['asks']
                )
                return book
            except Exception as e:
                log.error(f"Erro ao restaurar orderbook: {e}")
                return None
    
    def get_statistics(
        self, 
        symbol: str, 
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict:
        """Calcula estatísticas agregadas do período."""
        query = """
            SELECT 
                COUNT(*) as total_snapshots,
                AVG(spread) as avg_spread,
                AVG(spread_pct) as avg_spread_pct,
                AVG(bid_levels) as avg_bid_levels,
                AVG(ask_levels) as avg_ask_levels,
                AVG(error_rate) as avg_error_rate,
                MIN(best_bid) as min_bid,
                MAX(best_ask) as max_ask,
                AVG(best_bid) as avg_bid,
                AVG(best_ask) as avg_ask
            FROM orderbook_snapshots 
            WHERE symbol = ?
        """
        params = [symbol]
        
        if start_time:
            query += " AND timestamp >= ?"
            params.append(start_time.isoformat())
        
        if end_time:
            query += " AND timestamp <= ?"
            params.append(end_time.isoformat())
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            row = cursor.fetchone()
            
            if row and row['total_snapshots'] > 0:
                return dict(row)
            return {}
    
    def cleanup_old_data(self, days_to_keep: int = 30) -> int:
        """Remove dados antigos do banco."""
        cutoff_date = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_to_keep)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM orderbook_snapshots WHERE timestamp < ?",
                (cutoff_date.isoformat(),)
            )
            deleted_count = cursor.rowcount
        
        log.info(f"Removidos {deleted_count} snapshots antigos")
        return deleted_count
