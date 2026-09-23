from __future__ import annotations
import json, os
from dataclasses import dataclass, field, asdict
from pathlib import Path
@dataclass
class PolymarketConfig:
    data_api_base: str = "https://data-api.polymarket.com"
    data_api_token: str|None = None
@dataclass
class WatchlistConfig:
    mode: str = "manual"
    manual_wallets: list[str] = field(default_factory=list)
    auto_limit: int = 25
    min_quality_score: float = .6
@dataclass
class SignalConfig:
    min_trade_usd: float = 25.0
    max_signal_age_seconds: int = 180
    min_confidence: float = .55
    copy_sell_orders: bool = True
@dataclass
class ExecutionConfig:
    enabled: bool = False
    max_order_usd: float = 25.0
    max_daily_usd: float = 100.0
    dry_run: bool = True
    private_key: str|None = None
@dataclass
class Config:
    polymarket: PolymarketConfig = field(default_factory=PolymarketConfig)
    watchlist: WatchlistConfig = field(default_factory=WatchlistConfig)
    signal: SignalConfig = field(default_factory=SignalConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    db_path: str = "polybot.db"
    poll_interval_seconds: int = 15
    telegram_token: str|None = None
    telegram_allowed_chat_ids: list[int] = field(default_factory=list)
    @classmethod
    def load(cls, path="config.json"):
        p=Path(path)
        if not p.exists():
            c=cls(); p.write_text(json.dumps(asdict(c),indent=2)+"\n"); return c
        r=json.loads(p.read_text())
        return cls(PolymarketConfig(**r.get("polymarket",{})),WatchlistConfig(**r.get("watchlist",{})),SignalConfig(**r.get("signal",{})),ExecutionConfig(**r.get("execution",{})),r.get("db_path","polybot.db"),int(r.get("poll_interval_seconds",15)),telegram_allowed_chat_ids=[int(x) for x in r.get("telegram_allowed_chat_ids",[])])
    def apply_env_secrets(self):
        self.telegram_token=os.getenv("TELEGRAM_BOT_TOKEN") or None
        self.polymarket.data_api_token=os.getenv("POLYMARKET_DATA_API_TOKEN") or None
        self.execution.private_key=os.getenv("POLYMARKET_PRIVATE_KEY") or None
        if os.getenv("EXECUTION_ENABLED") is not None: self.execution.enabled=os.getenv("EXECUTION_ENABLED").lower()=="true"
        if os.getenv("EXECUTION_DRY_RUN") is not None: self.execution.dry_run=os.getenv("EXECUTION_DRY_RUN").lower()=="true"
    def validate(self):
        p=[]
        if not self.telegram_token: p.append("TELEGRAM_BOT_TOKEN is missing")
        if not self.telegram_allowed_chat_ids: p.append("telegram_allowed_chat_ids must contain at least one chat ID")
        if self.watchlist.mode not in {"manual","auto","hybrid"}: p.append("watchlist.mode must be manual, auto, or hybrid")
        if self.execution.enabled and not self.execution.private_key: p.append("POLYMARKET_PRIVATE_KEY is required for live execution")
        if self.execution.enabled and self.execution.dry_run: p.append("execution cannot be enabled while dry_run is true")
        return p
