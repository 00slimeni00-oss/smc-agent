"""Backtest stub: sliding evaluate over history. Run: python backtest.py"""
import config
import data
import smc

def backtest_pair(trade, confirmer, crypto=True, window=60):
    if crypto:
        t = data.fetch_binance(config.BINANCE_MAP[trade], "1h", 500)
        c = data.fetch_binance(config.BINANCE_MAP[confirmer], "1h", 500)
    else:
        t = data.fetch_yahoo(config.YAHOO_MAP[trade], "60m", "3mo")
        c = data.fetch_yahoo(config.YAHOO_MAP[confirmer], "60m", "3mo")
    p = config.PARAMS
    hits = []
    n = min(len(t), len(c))
    for end in range(window, n):
        r = smc.evaluate(t[:end], c[:end], p["swing_lookback"],
                         p["smt_tolerance_candles"], p["displacement_atr_mult"], p["min_rr"])
        if r.get("signal"):
            r["idx"] = end
            r["pair"] = trade
            hits.append(r)
    print(f"{trade}: {len(hits)} signals in window")
    for h in hits[-10:]:
        print(f"  idx={h['idx']} {h['direction']} entry={h['entry']:.2f} grade={h['grade']}")
    return hits

if __name__ == "__main__":
    backtest_pair("BTCUSD", "ETHUSD", True)
