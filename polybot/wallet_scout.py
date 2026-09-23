async def refresh_auto_watchlist(data,storage,config):
    n=0
    for e in await data.leaderboard(config.auto_limit):
        a=e.get("address") or e.get("proxyWallet")
        if a:
            score=min(1.0,max(0.0,float(e.get("score") or e.get("profit") or 0)/100000))
            if score>=config.min_quality_score: storage.upsert_wallet(a,"auto",score); n+=1
    return n
