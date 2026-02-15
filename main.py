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
last_signal = None

while True:
    try:
        close, high, low = get_candles()

        emaFast = ema(close, 20)
        emaSlow = ema(close, 50)

        macd = ema(close, 12) - ema(close, 26)
        macdSignal = ema(macd, 9)

        rsiVal = rsi(np.array(close))[-1]
        atrVal = atr(np.array(high), np.array(low), np.array(close))[-1]
        atrPrev = atr(np.array(high), np.array(low), np.array(close))[-2]

        trendUp = emaFast[-1] > emaSlow[-1]
        trendDown = emaFast[-1] < emaSlow[-1]
        volOk = atrVal > atrPrev

        buy = trendUp and rsiVal < 35 and macd[-1] > macdSignal[-1] and macd[-2] <= macdSignal[-2] and volOk
        sell = trendDown and rsiVal > 65 and macd[-1] < macdSignal[-1] and macd[-2] >= macdSignal[-2] and volOk

        if buy and last_signal != "BUY":
            bot.send_message(chat_id=CHAT_ID, text="📈 OTC BUY Signal (Russo Sniper)")
            last_signal = "BUY"

        if sell and last_signal != "SELL":
            bot.send_message(chat_id=CHAT_ID, text="📉 OTC SELL Signal (Russo Sniper)")
            last_signal = "SELL"

    except Exception as e:
        print("Error:", e)

    time.sleep(60)
