"""Data fetch: Binance for crypto, Yahoo for forex/crypto fallback. Stdlib only."""
import json
import urllib.request

BINANCE_BASE = "https://api.binance.com/api/v3/klines"
YAHOO_BASE = "https://query1.finance.yahoo.com/v8/finance/chart"

def _get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

def fetch_binance(symbol="BTCUSDT", interval="1h", limit=300):
    url = f"{BINANCE_BASE}?symbol={symbol}&interval={interval}&limit={limit}"
    raw = _get_json(url)
    out = []
    for k in raw:
        out.append({"o": float(k[1]), "h": float(k[2]), "l": float(k[3]), "c": float(k[4])})
    return out

def fetch_yahoo(ticker="EURUSD=X", interval="60m", rng="1mo"):
    url = f"{YAHOO_BASE}/{ticker}?interval={interval}&range={rng}"
    j = _get_json(url)
    res = j["chart"]["result"][0]
    q = res["indicators"]["quote"][0]
    out = []
    for o, h, l, c in zip(q["open"] or [], q["high"] or [], q["low"] or [], q["close"] or []):
        if None in (o, h, l, c):
            continue
        out.append({"o": o, "h": h, "l": l, "c": c})
    return out
