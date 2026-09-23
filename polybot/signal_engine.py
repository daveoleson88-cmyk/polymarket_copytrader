from __future__ import annotations
import hashlib,time
from dataclasses import dataclass
class Signal:
    def __init__(self,id,wallet,token_id,side,price,size_usd,timestamp,raw): self.id,self.wallet,self.token_id,self.side,self.price,self.size_usd,self.timestamp,self.raw=id,wallet,token_id,side,price,size_usd,timestamp,raw
class SignalEngine:
    def __init__(self,storage,config): self.storage,self.config=storage,config
    def from_trade(self,wallet,t):
        size=float(t.get("size") or t.get("amount") or 0); price=float(t.get("price") or 0); usd=size*price if price<=1 else size; side=str(t.get("side","BUY")).upper(); token=str(t.get("asset") or t.get("token_id") or "")
        if usd<self.config.min_trade_usd or side=="SELL" and not self.config.copy_sell_orders or not token: return None
        i=hashlib.sha256(f"{wallet}:{t.get('id','')}:{token}:{side}".encode()).hexdigest()[:24]; return Signal(i,wallet,token,side,price,usd,float(t.get("_timestamp",time.time())),t)
