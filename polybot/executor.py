import logging
logger=logging.getLogger(__name__)
class Executor:
    def __init__(self,config,storage): self.config,self.storage=config,storage
    async def execute(self,signal):
        size=min(signal.size_usd,self.config.execution.max_order_usd)
        if self.storage.daily_order_total()+size>self.config.execution.max_daily_usd: self.storage.add_order(signal.id,"rejected",{"size_usd":size}); return "rejected: daily limit"
        payload={"size_usd":size,"token_id":signal.token_id,"side":signal.side,"price":signal.price}
        if not self.config.execution.enabled or self.config.execution.dry_run: self.storage.add_order(signal.id,"paper",payload); logger.info("Paper order: %s",payload); return f"paper order: ${size:.2f}"
        raise RuntimeError("Live signing is not configured; keep execution.dry_run=true")
