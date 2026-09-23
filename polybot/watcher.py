import asyncio, logging, time
logger=logging.getLogger(__name__)
class Watcher:
    def __init__(self,data,storage,engine,poll_interval=15): self.data,self.storage,self.engine,self.poll_interval=data,storage,engine,poll_interval; self.running=False
    async def run(self,on_signal):
        self.running=True
        while self.running:
            for row in self.storage.wallets():
                try:
                    for t in await self.data.wallet_trades(row["address"]):
                        i=str(t.get("id") or t.get("transactionHash") or "")
                        if not i or not self.storage.unseen_trade(i): continue
                        t["_timestamp"]=self.data.trade_timestamp(t); self.storage.mark_trade_seen(i,row["address"],t)
                        s=self.engine.from_trade(row["address"],t)
                        if s and time.time()-s.timestamp<=self.engine.config.max_signal_age_seconds: await on_signal(s)
                except Exception: logger.exception("Wallet polling failed")
            await asyncio.sleep(self.poll_interval)
    def stop(self): self.running=False
