"""Entry point. Run with: python main.py"""
from __future__ import annotations
import asyncio, logging, sys
from dotenv import load_dotenv
from polybot.bot import BotApp
from polybot.config import Config
from polybot.data_client import DataClient
from polybot.executor import Executor
from polybot.signal_engine import SignalEngine
from polybot.storage import Storage
from polybot.wallet_scout import refresh_auto_watchlist
from polybot.watcher import Watcher
logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger=logging.getLogger("polybot.main")
async def bootstrap(config,storage,data):
    wl=config.watchlist
    if wl.mode in ("auto","hybrid"): logger.info("Initial auto-watchlist refresh: %d wallets",await refresh_auto_watchlist(data,storage,wl))
    if wl.mode in ("manual","hybrid"):
        for a in wl.manual_wallets: storage.upsert_wallet(a,"manual",1.0)
def main():
    load_dotenv(); config=Config.load(); config.apply_env_secrets(); problems=config.validate()
    if problems:
        for p in problems: logger.error("Config problem: %s",p)
        sys.exit(1)
    storage=Storage(config.db_path); data=DataClient(config.polymarket.data_api_base,config.polymarket.data_api_token)
    try:
        asyncio.run(bootstrap(config,storage,data)); engine=SignalEngine(storage,config.signal); watcher=Watcher(data,storage,engine,config.poll_interval_seconds); bot=BotApp(config,storage,data,engine,watcher,Executor(config,storage)); bot.run()
    finally: asyncio.run(data.close()); storage.close()
if __name__=="__main__": main()
