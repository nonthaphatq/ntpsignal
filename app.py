import os
import threading
import time
import requests
import pandas as pd
import joblib
from flask import Flask, jsonify

# ========== CONFIG ==========
BOT_TOKEN = "7939869219:AAE3f92rtma1w549m4qiWbqm6W3e0JcT2Tk"
CHAT_ID = "5134209145"
MODEL_PATH = "xgb_model.pkl"
DATA_PATH = "xauusd_ready.csv"
FETCH_INTERVAL = 60  # วิเคราะห์ทุก 60 วินาที

# ========== FLASK SETUP ==========
app = Flask(__name__)
model = None
X = None

# ========== LOAD MODEL ==========
try:
    model = joblib.load(MODEL_PATH)
except Exception as e:
    model = None
    print(f"❌ Error loading model: {e}")

# ========== AI ANALYSIS FUNCTION ==========
def analyze_and_send():
    while True:
        try:
            df = pd.read_csv(DATA_PATH)
            X = df.drop(columns=['target', 'Price'])
            prediction = model.predict(X)
            signal = int(prediction[-1])
            msg = f"📢 AI Signal: {'BUY' if signal == 1 else 'SELL'} (index: {len(prediction)-1})"
            print(msg)
            send_telegram(msg)
        except Exception as e:
            print(f"❌ Error during prediction: {e}")

        time.sleep(FETCH_INTERVAL)

# ========== TELEGRAM FUNCTION ==========
def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")

# ========== FLASK ROUTE ==========
@app.route('/')
def home():
    return jsonify({"status": "✅ AI Signal Server Running"})

# ========== BACKGROUND THREAD ==========
def start_background():
    thread = threading.Thread(target=analyze_and_send)
    thread.daemon = True
    thread.start()

# ========== RUN ==========
if __name__ == '__main__':
    start_background()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
