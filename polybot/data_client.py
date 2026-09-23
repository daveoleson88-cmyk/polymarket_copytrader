from __future__ import annotations
from datetime import datetime
from typing import Any
import httpx
class DataClient:
    def __init__(self, base_url, token=None):
        self.client=httpx.AsyncClient(base_url=base_url.rstrip("/"),headers={"Authorization":f"Bearer {token}"} if token else {},timeout=20)
    async def wallet_trades(self,wallet,limit=100):
        r=await self.client.get("/trades",params={"user":wallet,"limit":limit}); r.raise_for_status(); x=r.json(); return x if isinstance(x,list) else x.get("data",[])
    async def leaderboard(self,limit=25):
        r=await self.client.get("/v1/leaderboard",params={"limit":limit}); r.raise_for_status(); x=r.json(); return x if isinstance(x,list) else x.get("data",[])
    @staticmethod
    def trade_timestamp(t):
        v=t.get("timestamp") or t.get("createdAt") or 0
        if isinstance(v,(int,float)): return float(v)/(1000 if v>10000000000 else 1)
        try: return datetime.fromisoformat(str(v).replace("Z","+00:00")).timestamp()
        except ValueError: return 0.0
    async def close(self): await self.client.aclose()
