import asyncio, logging
from telegram import Update
from telegram.ext import Application,CommandHandler,ContextTypes
logger=logging.getLogger(__name__)
class BotApp:
    def __init__(self,config,storage,data,engine,watcher,executor): self.config,self.storage,self.data,self.engine,self.watcher,self.executor=config,storage,data,engine,watcher,executor
    def authorized(self,u): return bool(u.effective_chat and u.effective_chat.id in self.config.telegram_allowed_chat_ids)
    async def start(self,u,c):
        if self.authorized(u): await u.message.reply_text("Polybot is running in paper mode.")
    async def status(self,u,c):
        if self.authorized(u): await u.message.reply_text(f"wallets={len(self.storage.wallets())} execution={'live' if self.config.execution.enabled else 'paper'}")
    async def handle_signal(self,s): logger.info("Signal %s: %s",s.id,await self.executor.execute(s))
    async def poll(self): await self.watcher.run(self.handle_signal)
    def run(self):
        if not self.config.telegram_token: raise RuntimeError("TELEGRAM_BOT_TOKEN is required")
        app=Application.builder().token(self.config.telegram_token).build(); app.add_handler(CommandHandler("start",self.start)); app.add_handler(CommandHandler("status",self.status)); loop=asyncio.new_event_loop(); asyncio.set_event_loop(loop); loop.create_task(self.poll()); app.run_polling()
