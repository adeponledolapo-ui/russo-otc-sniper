print("Russo OTC Sniper Bot Started")
import time
import requests
import numpy as np
import pandas as pd
from telegram import Bot

# ========== CONFIG ==========
TOKEN = "8286509718:AAEKAEd-hzc9U14fCkzTDtQRrqwZH1n_-r8"
CHAT_ID = "688759657"

SYMBOL = "EURUSD"
TIMEFRAME = "1m"

bot = Bot(TOKEN)

# ===== GET PRICE DATA (REAL FEED) =====
def get_candles():
    url = f"https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval={TIMEFRAME}&limit=100"
    data = requests.get(url).json()
    close = [float(c[4]) for c in data]
    high = [float(c[2]) for c in data]
    low = [float(c[3]) for c in data]
    return close, high, low

# ===== INDICATORS =====
def ema(series, period):
    return pd.Series(series).ewm(span=period).mean().values

def rsi(series, period=14):
    delta = np.diff(series)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = pd.Series(gain).rolling(period).mean()
    avg_loss = pd.Series(loss).rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def atr(high, low, close, period=14):
    tr = np.maximum(high[1:] - low[1:], np.abs(high[1:] - close[:-1]), np.abs(low[1:] - close[:-1]))
    return pd.Series(tr).rolling(period).mean().values

# ===== SNIPER LOOP =====
print("🚀 Russo OTC Sniper Bot Started")

def run():
    print("BOT LOOP ENTERED")

    while True:
        try:
            print("Trying to fetch candles...")

            close, high, low = get_candles()

            print("Candles received:", len(close))

            price = close[-1]
            print("Price:", price)

            ema_fast = ema(close, 20).iloc[-1]
            ema_slow = ema(close, 50).iloc[-1]
            rsi_val = rsi(close).iloc[-1]
            atr_val = atr(high, low, close).iloc[-1]

            print("EMA20:", ema_fast, "EMA50:", ema_slow, "RSI:", rsi_val, "ATR:", atr_val)

            bot.send_message(chat_id=CHAT_ID, text="Bot is alive ✅")

            time.sleep(60)

        except Exception as e:
            print("CRASH:", e)
            time.sleep(5)

run()
