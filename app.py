from flask import Flask, jsonify
import pandas as pd
import joblib
import os

app = Flask(__name__)

# โหลดโมเดลและข้อมูล
try:
    model = joblib.load("xgb_model.pkl")
    df = pd.read_csv("xauusd_ready.csv")
    X = df.drop(columns=['target', 'Price'])
except Exception as e:
    model = None
    X = None
    error = str(e)

@app.route('/')
def home():
    if model is None:
        return jsonify({"error": error})
    try:
        prediction = model.predict(X)
        signal = int(prediction[-1])
        return jsonify({
            "signal": "BUY" if signal == 1 else "SELL",
            "index": len(prediction) - 1
        })
    except Exception as e:
        return jsonify({"error": str(e)})

# รันบน 0.0.0.0 และใช้ PORT จาก Render
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
