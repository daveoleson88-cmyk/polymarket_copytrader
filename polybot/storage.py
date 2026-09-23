from __future__ import annotations
import json, sqlite3, time
class Storage:
    def __init__(self,path):
        self.db=sqlite3.connect(path,check_same_thread=False); self.db.row_factory=sqlite3.Row
        self.db.executescript("CREATE TABLE IF NOT EXISTS wallets(address TEXT PRIMARY KEY,source TEXT,quality_score REAL,updated_at REAL); CREATE TABLE IF NOT EXISTS seen_trades(trade_id TEXT PRIMARY KEY,wallet TEXT,payload TEXT,seen_at REAL); CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY,signal_id TEXT,status TEXT,payload TEXT,created_at REAL);"); self.db.commit()
    def upsert_wallet(self,address,source,quality_score):
        self.db.execute("INSERT INTO wallets VALUES(?,?,?,?) ON CONFLICT(address) DO UPDATE SET source=excluded.source,quality_score=excluded.quality_score,updated_at=excluded.updated_at",(address.lower(),source,quality_score,time.time())); self.db.commit()
    def wallets(self): return list(self.db.execute("SELECT * FROM wallets ORDER BY quality_score DESC"))
    def unseen_trade(self,i): return self.db.execute("SELECT 1 FROM seen_trades WHERE trade_id=?",(i,)).fetchone() is None
    def mark_trade_seen(self,i,w,p): self.db.execute("INSERT OR IGNORE INTO seen_trades VALUES(?,?,?,?)",(i,w,json.dumps(p),time.time())); self.db.commit()
    def add_order(self,s,status,p): self.db.execute("INSERT INTO orders(signal_id,status,payload,created_at) VALUES(?,?,?,?)",(s,status,json.dumps(p),time.time())); self.db.commit()
    def daily_order_total(self):
        return sum(float(json.loads(r[0]).get("size_usd",0)) for r in self.db.execute("SELECT payload FROM orders WHERE created_at>=? AND status IN ('paper','submitted')",(time.time()-86400,)))
    def close(self): self.db.close()
