# File: bybit_trading_bot.py

import ccxt
import pandas as pd
from datetime import datetime
import pytz
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import schedule
import time

# Load environment variables
load_dotenv()
api_key = os.getenv("API_KEY")
secret_key = os.getenv("SECRET_KEY")

# Initialize Bybit exchange
exchange = ccxt.bybit({
    'apiKey': api_key,
    'secret': secret_key,
    'enableRateLimit': True,
})

# Trading parameters
symbol = "BTC/USDT"
timeframe = "15m"
leverage = 20
portfolio_value = 100  # Initial portfolio value in USDT
max_trade_value = portfolio_value * 0.2  # Max 20% of portfolio
aest = pytz.timezone("Australia/Sydney")  # AEST timezone
hours = (8, 23)  # Trading hours in AEST time
days = (0, 4)  # Monday to Friday

# Flask app for webhook
app = Flask(__name__)

# Fetch OHLCV data
def fetch_ohlcv():
    """Fetch OHLCV data from Bybit."""
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f"Error fetching OHLCV data: {e}")
        return None

# Calculate Fibonacci retracement levels
def calculate_fibonacci(high, low):
    """Calculate Fibonacci retracement levels."""
    diff = high - low
    return {
        '0.236': low + diff * 0.236,
        '0.5': low + diff * 0.5,
        '0.618': low + diff * 0.618,
    }

# Place an order
def place_order(side, price, amount):
    """Place an order on Bybit."""
    try:
        order = exchange.create_order(symbol, 'limit', side, amount, price, {'leverage': leverage})
        print(f"Placed {side} order: {order}")
    except Exception as e:
        print(f"Order failed: {e}")

# Determine if trading conditions are met
def should_trade():
    """Determine if trading conditions are met."""
    now = datetime.now(aest)
    return hours[0] <= now.hour < hours[1] and now.weekday() in days

# Main trading logic
def trade_logic():
    """Main trading logic for executing trades."""
    df = fetch_ohlcv()
    if df is None or df.empty:
        return

    try:
        last_row = df.iloc[-1]
        confirmation_row = df.iloc[-2]

        if should_trade():
            trade_amount = (max_trade_value / last_row['close']) * leverage
            if last_row['close'] > last_row['open'] and confirmation_row['close'] < confirmation_row['open']:
                place_order('buy', last_row['close'], trade_amount)
            elif last_row['close'] < last_row['open'] and confirmation_row['close'] > confirmation_row['open']:
                place_order('sell', last_row['close'], trade_amount)
    except Exception as e:
        print(f"Error in trading logic: {e}")

# Webhook endpoint
@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook to receive TradingView alerts and execute trades."""
    try:
        data = request.json
        print(f"Received Webhook: {data}")

        # Parse TradingView signal
        action = data.get("action")
        trade_symbol = data.get("symbol", "BTC/USDT")  # Default to BTC/USDT
        amount = data.get("amount", 0.01)  # Example: Fixed trade amount

        if action == "buy":
            order = exchange.create_market_buy_order(trade_symbol, amount)
            return jsonify({"message": "Buy order executed", "order": order})
        elif action == "sell":
            order = exchange.create_market_sell_order(trade_symbol, amount)
            return jsonify({"message": "Sell order executed", "order": order})
        else:
            return jsonify({"error": "Invalid action"}), 400
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# Function to run the trading bot
def run_bot():
    """Run the trading bot on a schedule."""
    print(f"Running bot at {datetime.now()}")
    trade_logic()

# Schedule the bot
schedule.every(15).minutes.do(run_bot)

# Run Flask app and bot
if __name__ == '__main__':
    # Flask will run in parallel to the bot's scheduled tasks
    from threading import Thread

    # Run Flask app in a separate thread
    flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False))
    flask_thread.start()

    # Run scheduled tasks in the main thread
    while True:
        schedule.run_pending()
        time.sleep(1)

import requests

url = "http://127.0.0.1:5000/webhook"
payload = {
    "action": "buy",
    "symbol": "BTC/USDT",
    "amount": 0.01
}
headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)
print("Response:", response.json())
