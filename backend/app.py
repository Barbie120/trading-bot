from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)

# Example data (replace with TradingView fetched data)
trade_data = pd.DataFrame([
    {"time": "2023-11-01", "trade_type": "Buy", "profit": 12.5},
    {"time": "2023-11-02", "trade_type": "Sell", "profit": -3.2}
])

@app.route("/")
def home():
    return "Trading Bot Dashboard"

@app.route("/trades")
def trades():
    return jsonify(trade_data.to_dict(orient="records"))

@app.route("/stats")
def stats():
    win_rate = (trade_data["profit"] > 0).mean() * 100
    return jsonify({"win_rate": win_rate})

if __name__ == "__main__":
    app.run(debug=True)

