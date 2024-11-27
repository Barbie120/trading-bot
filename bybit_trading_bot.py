import ccxt
import pandas as pd
from datetime import datetime, timedelta
import pytz
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import schedule
import time
import logging
from threading import Thread
import hashlib
import numpy as np

# Load environment variables from .env
load_dotenv()
api_key = os.getenv("API_KEY")
secret_key = os.getenv("SECRET_KEY")
webhook_secret = os.getenv("WEBHOOK_SECRET")

# Initialize Bybit exchange
exchange = ccxt.bybit({
    'apiKey': api_key,
    'secret': secret_key,
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'},  # Use 'future' for futures accounts
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

# Tracking trades and wins
trade_count = 0
win_count = 0
last_trade_time = None
cooldown_period = timedelta(minutes=15)

# Flask app for webhook
app = Flask(__name__)

# Logging setup
logging.basicConfig(filename='trading_bot.log', level=logging.INFO, format='%(asctime)s %(message)s')

# Fetch OHLCV data
def fetch_ohlcv():
    """Fetch OHLCV data from Bybit."""
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        logging.error(f"Error fetching OHLCV data: {e}")
        return None

# Calculate ATR for position sizing
def calculate_atr(df, period=14):
    """Calculate Average True Range for better risk management."""
    df['tr'] = np.maximum(df['high'] - df['low'], np.maximum(abs(df['high'] - df['close'].shift()), abs(df['low'] - df['close'].shift())))
    df['atr'] = df['tr'].rolling(window=period).mean()
    return df['atr'].iloc[-1]

# Place an order
def place_order(side, price, amount):
    """Place an order on Bybit."""
    try:
        order = exchange.create_order(symbol, 'limit', side, amount, price, {'leverage': leverage})
        logging.info(f"Placed {side} order: {order}")
    except Exception as e:
        logging.error(f"Order failed: {e}")

# Check if trading conditions are met
def should_trade():
    """Determine if trading conditions are met."""
    now = datetime.now(aest)
    return hours[0] <= now.hour < hours[1] and now.weekday() in days

# Check if the bot can trade again
def can_trade_again():
    global last_trade_time
    now = datetime.now(aest)
    if last_trade_time is None or now - last_trade_time > cooldown_period:
        last_trade_time = now
        return True
    return False

# Main trading logic
def trade_logic():
    """Main trading logic for executing trades."""
    if not can_trade_again():
        logging.info("Cooldown period, no trading allowed")
        return

    df = fetch_ohlcv()
    if df is None or df.empty:
        return

    global trade_count, win_count
    try:
        last_row = df.iloc[-1]
        confirmation_row = df.iloc[-2]

        if should_trade():
            atr = calculate_atr(df)
            risk_per_trade = portfolio_value * 0.01  # Risk 1% of portfolio per trade
            trade_amount = (risk_per_trade / atr) if atr > 0 else 0

            if last_row['close'] > last_row['open'] and confirmation_row['close'] < confirmation_row['open']:
                place_order('buy', last_row['close'], trade_amount)
                trade_count += 1
                # Simulate a win for demo purposes
                if last_row['close'] < df.iloc[-3]['close']:
                    win_count += 1
            elif last_row['close'] < last_row['open'] and confirmation_row['close'] > confirmation_row['open']:
                place_order('sell', last_row['close'], trade_amount)
                trade_count += 1
                # Simulate a win for demo purposes
                if last_row['close'] > df.iloc[-3]['close']:
                    win_count += 1
    except Exception as e:
        logging.error(f"Error in trading logic: {e}")

# Webhook endpoint
def is_valid_webhook(data, received_hash):
    """Validate the webhook request."""
    computed_hash = hashlib.sha256((data + webhook_secret).encode('utf-8')).hexdigest()
    return computed_hash == received_hash

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook to receive TradingView alerts and execute trades."""
    try:
        data = request.json
        received_hash = request.headers.get("X-Signature")

        if not is_valid_webhook(data.get("action"), received_hash):
            return jsonify({"error": "Invalid signature"}), 403

        action = data.get("action")
        trade_symbol = data.get("symbol", "BTC/USDT")
        amount = data.get("amount", 0.01)

        if action == "buy":
            order = exchange.create_market_buy_order(trade_symbol, amount)
            return jsonify({"message": "Buy order executed", "order": order})
        elif action == "sell":
            order = exchange.create_market_sell_order(trade_symbol, amount)
            return jsonify({"message": "Sell order executed", "order": order})
        else:
            return jsonify({"error": "Invalid action"}), 400
    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# Endpoint to display trade stats
@app.route('/stats', methods=['GET'])
def get_stats():
    """Endpoint to get trading statistics."""
    win_rate = (win_count / trade_count * 100) if trade_count > 0 else 0
    return jsonify({
        "trades_made": trade_count,
        "win_rate_percentage": win_rate
    })

# Run the trading bot
def run_bot():
    """Run the trading bot on a schedule."""
    logging.info(f"Running bot at {datetime.now()}")
    trade_logic()

# Schedule the bot
schedule.every(15).minutes.do(run_bot)

# Run Flask app and scheduled bot
if __name__ == '__main__':
    # Run Flask app in a separate thread
    flask_thread = Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False))
    flask_thread.start()

    # Run scheduled tasks in the main thread
    while True:
        schedule.run_pending()
        time.sleep(1)
