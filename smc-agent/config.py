# SMC agent config - locked spec
TRADE_PAIRS = ["BTCUSD", "EURUSD", "GBPUSD", "GBPJPY"]
CONFIRM_MAP = {
    "BTCUSD": ["ETHUSD"],
    "EURUSD": ["GBPUSD"],
    "GBPUSD": ["EURUSD"],
    "GBPJPY": ["EURJPY"],
}
# fetch symbols per provider
BINANCE_MAP = {"BTCUSD": "BTCUSDT", "ETHUSD": "ETHUSDT"}
YAHOO_MAP = {
    "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X",
    "GBPJPY": "GBPJPY=X", "EURJPY": "EURJPY=X",
    "BTCUSD": "BTC-USD", "ETHUSD": "ETH-USD",
}
TIMEFRAMES = {"crypto": "1h", "forex": "4h"}
PARAMS = {
    "swing_lookback": 5,
    "smt_tolerance_candles": 3,
    "atr_period": 14,
    "displacement_atr_mult": 1.5,
    "min_rr": 2.0,
    "risk_reward_tp1_mult": 2.0,
}
SCAN_TIMES_UTC = ["07:00", "12:00", "16:00", "20:00"]
EMAIL_SUBJECT_PREFIX = "[SMC-AGENT]"
