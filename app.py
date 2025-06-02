from flask import Flask, jsonify
import pandas as pd
import joblib

app = Flask(__name__)
model = joblib.load("xgb_model.pkl")
df = pd.read_csv("xauusd_ready.csv")
X = df.drop(columns=['target', 'Price'])

@app.route('/')
def home():
    df['predicted_signal'] = model.predict(X)
    latest_signal = df['predicted_signal'].iloc[-1]
    return jsonify({"latest_signal": "BUY" if latest_signal == 1 else "SELL"})

if __name__ == '__main__':
    app.run()
