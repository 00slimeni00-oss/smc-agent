"""Scan entry: fetch groups, evaluate, print/email. Run: python scan.py"""
import os
import config
import data
import smc

def scan_pair(trade, confirmer, crypto=True):
    try:
        if crypto:
            t = data.fetch_binance(config.BINANCE_MAP[trade], "1h", 300)
            c = data.fetch_binance(config.BINANCE_MAP[confirmer], "1h", 300)
        else:
            t = data.fetch_yahoo(config.YAHOO_MAP[trade], "60m", "1mo")
            c = data.fetch_yahoo(config.YAHOO_MAP[confirmer], "60m", "1mo")
    except Exception as e:
        return {"pair": trade, "signal": False, "reason": f"data error {e}"}
    p = config.PARAMS
    r = smc.evaluate(t, c, p["swing_lookback"], p["smt_tolerance_candles"],
                     p["displacement_atr_mult"], p["min_rr"])
    r["pair"] = trade
    r["confirmer"] = confirmer
    return r

def main():
    groups = [("BTCUSD", "ETHUSD", True), ("EURUSD", "GBPUSD", False),
              ("GBPUSD", "EURUSD", False), ("GBPJPY", "EURJPY", False)]
    results = [scan_pair(t, c, k) for t, c, k in groups]
    for r in results:
        if r.get("signal"):
            print(f"SIGNAL {r['pair']} {r['direction']} entry={r['entry']:.2f} "
                  f"SL={r['sl']:.2f} TP={r['tp']:.2f} RR={r['rr']:.2f} grade={r['grade']}")
        else:
            print(f"NO TRADE {r['pair']}: {r.get('reason')}")
    return results

if __name__ == "__main__":
    main()
