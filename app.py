from flask import Flask, jsonify
import yfinance as yf
import pandas as pd
import ta
import joblib
import requests
import os

app = Flask(__name__)

BOT_TOKEN = "7939869219:AAE3f92rtma1w549m4qiWbqm6W3e0JcT2Tk"
CHAT_ID = "5134209145"

model = joblib.load("xgb_model.pkl")

def fetch_realtime_data():
    data = yf.download("XAUUSD=X", period="5d", interval="1h")
    df = data.copy()
    df['EMA20'] = ta.trend.ema_indicator(df['Close'], window=20)
    df['EMA50'] = ta.trend.ema_indicator(df['Close'], window=50)
    df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
    macd = ta.trend.macd(df['Close'])
    df['MACD'] = macd.macd_diff()
    df = df.dropna()
    return df

@app.route('/')
def ai_signal():
    try:
        df = fetch_realtime_data()
        latest = df.iloc[-1:]
        X = latest[['EMA20', 'EMA50', 'RSI', 'MACD']]
        prediction = model.predict(X)[0]
        signal = "BUY" if prediction == 1 else "SELL"
        msg = f"🔔 AI Signal: {signal}\nPrice: {latest['Close'].values[0]:.2f}"

        # ส่งไป Telegram
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", params={
            "chat_id": CHAT_ID,
            "text": msg
        })

        return jsonify({"signal": signal})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
