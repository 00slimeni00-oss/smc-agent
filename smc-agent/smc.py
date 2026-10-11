"""SMC core: sweep + SMT + shift + OB/FVG + RR. Pure functions for testability."""

def atr(candles, period=14):
    trs = []
    for i in range(1, len(candles)):
        h, l, pc = candles[i]["h"], candles[i]["l"], candles[i-1]["c"]
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    if not trs:
        return 0
    p = trs[-period:] if len(trs) >= period else trs
    return sum(p) / len(p)

def swing_high(candles, lookback=5):
    if len(candles) < lookback * 2 + 1:
        return None
    i = len(candles) - lookback - 1
    h = candles[i]["h"]
    window = candles[i - lookback:i + lookback + 1]
    if h == max(c["h"] for c in window):
        return (i, h)
    return None

def swing_low(candles, lookback=5):
    if len(candles) < lookback * 2 + 1:
        return None
    i = len(candles) - lookback - 1
    l = candles[i]["l"]
    window = candles[i - lookback:i + lookback + 1]
    if l == min(c["l"] for c in window):
        return (i, l)
    return None

def detect_sweep(candles, lookback=5):
    """Return {'dir':'bullish_sweep'|'bearish_sweep', 'level':x} or None.
    bullish_sweep = sweep of low (sell-side) then close back above = long setup.
    bearish_sweep = sweep of high then close back below = short setup."""
    sh = swing_high(candles, lookback)
    sl = swing_low(candles, lookback)
    last = candles[-1]
    if sh and last["h"] > sh[1] and last["c"] < sh[1]:
        return {"dir": "bearish_sweep", "level": sh[1]}
    if sl and last["l"] < sl[1] and last["c"] > sl[1]:
        return {"dir": "bullish_sweep", "level": sl[1]}
    return None

def swept_high_recent(candles, lookback=5, tol=3):
    """Did price sweep a recent swing high within last tol candles?"""
    for end in range(len(candles) - tol, len(candles)):
        if end < lookback * 2 + 1:
            continue
        if detect_sweep(candles[:end + 1], lookback) is not None:
            d = detect_sweep(candles[:end + 1], lookback)
            if d["dir"] == "bearish_sweep":
                return True
    return False

def detect_smt(trade_candles, confirm_candles, direction, lookback=5, tol=3):
    """SMT bearish: trade sweeps high, confirmer does NOT. Bullish: inverse."""
    if direction == "bearish_sweep":
        t = swept_high_recent(trade_candles, lookback, tol)
        c = swept_high_recent(confirm_candles, lookback, tol)
        return t and not c
    if direction == "bullish_sweep":
        # sweep-low check: mirror via inverted candles
        def swept_low(cs):
            inv = [{"o": -x["o"], "h": -x["l"], "l": -x["h"], "c": -x["c"]} for x in cs]
            return swept_high_recent(inv, lookback, tol)
        t = swept_low(trade_candles[-20:])
        c = swept_low(confirm_candles[-20:])
        return t and not c
    return False

def detect_shift(candles, direction, atr_mult=1.5, period=14):
    if len(candles) < 3:
        return False
    a = atr(candles, period) or 1e-9
    last = candles[-1]
    body = abs(last["c"] - last["o"])
    if body < atr_mult * a:
        return False
    if direction == "bearish_sweep":
        return last["c"] < min(c["l"] for c in candles[-4:-1])
    if direction == "bullish_sweep":
        return last["c"] > max(c["h"] for c in candles[-4:-1])
    return False

def find_fvg(candles):
    """Return latest bullish/bearish FVG zone or None."""
    for i in range(len(candles) - 1, 2, -1):
        # bearish FVG: low[i-2] > high[i]
        if candles[i - 2]["l"] > candles[i]["h"]:
            return {"type": "bearish_fvg", "top": candles[i - 2]["l"], "bot": candles[i]["h"]}
        if candles[i - 2]["h"] < candles[i]["l"]:
            return {"type": "bullish_fvg", "top": candles[i]["l"], "bot": candles[i - 2]["h"]}
    return None

def find_ob(candles, direction):
    """OB = last opposite candle before displacement."""
    if len(candles) < 3:
        return None
    disp = candles[-1]
    prev = candles[-2]
    if direction == "bearish_sweep" and prev["c"] > prev["o"]:
        return {"type": "bearish_ob", "top": prev["h"], "bot": prev["l"]}
    if direction == "bullish_sweep" and prev["c"] < prev["o"]:
        return {"type": "bullish_ob", "top": prev["h"], "bot": prev["l"]}
    return {"type": "bearish_ob" if direction == "bearish_sweep" else "bullish_ob",
            "top": disp["h"], "bot": disp["l"]}

def check_rr(entry, sl, tp):
    risk = abs(entry - sl)
    reward = abs(tp - entry)
    if risk == 0:
        return 0
    return reward / risk

def evaluate(trade_candles, confirm_candles, lookback=5, tol=3, atr_mult=1.5, min_rr=2.0):
    """Full 5-rule check. Returns dict with pass/fail + levels."""
    sweep = detect_sweep(trade_candles, lookback)
    if not sweep:
        return {"signal": False, "reason": "no sweep"}
    smt = detect_smt(trade_candles, confirm_candles, sweep["dir"], lookback, tol)
    if not smt:
        return {"signal": False, "reason": "sweep but no SMT"}
    if not detect_shift(trade_candles, sweep["dir"], atr_mult):
        return {"signal": False, "reason": "no shift/displacement"}
    fvg = find_fvg(trade_candles)
    ob = find_ob(trade_candles, sweep["dir"])
    poi = None
    grade = "B"
    # entry = sweep level retest proxy = last close
    last_close = trade_candles[-1]["c"]
    if fvg and ob:
        # overlap check
        overlap = not (fvg["top"] < ob["bot"] or fvg["bot"] > ob["top"])
        grade = "A+" if overlap else "B"
        poi = {"fvg": fvg, "ob": ob, "overlap": overlap}
    elif fvg or ob:
        poi = {"fvg": fvg, "ob": ob, "overlap": False}
    else:
        return {"signal": False, "reason": "no OB/FVG"}
    short = sweep["dir"] == "bearish_sweep"
    entry = last_close
    if short:
        sl = sweep["level"]
        tp = entry - (sl - entry) * min_rr  # enforce exactly min_rr for planning
    else:
        sl = sweep["level"]
        tp = entry + (entry - sl) * min_rr
    rr = check_rr(entry, sl, tp)
    if rr < min_rr:
        return {"signal": False, "reason": f"RR {rr:.2f} < {min_rr}"}
    return {"signal": True, "direction": "SHORT" if short else "LONG",
            "entry": entry, "sl": sl, "tp": tp, "rr": rr,
            "grade": grade, "poi": poi, "sweep": sweep}
