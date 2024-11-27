import ccxt
import pandas as pd
from datetime import datetime
import pytz
from dotenv import load_dotenv
import os
import schedule
import time

# Load API keys from .env file
load_dotenv()  # Ensure .env file is in the same directory
api_key = os.getenv('API_KEY')
secret_key = os.getenv('SECRET_KEY')

# Initialize Bybit exchange
exchange = ccxt.bybit({
    'apiKey': api_key,
    'secret': secret_key,
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'},  # Change 'spot' to 'future' for futures accounts
})

# Trading parameters
symbol = 'BTC/USDT'
timeframe = '15m'
leverage = 20
portfolio_value = 100  # Initial portfolio value in USDT
max_trade_value = portfolio_value * 0.2  # Max 20% of portfolio
aest = pytz.timezone('Australia/Sydney')  # AEST timezone
hours = (8, 23)  # Trading hours in AEST time
days = (0, 4)  # Monday to Friday


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


def calculate_fibonacci(high, low):
    """Calculate Fibonacci retracement levels."""
    diff = high - low
    return {
        '0.236': low + diff * 0.236,
        '0.5': low + diff * 0.5,
        '0.618': low + diff * 0.618,
    }


def place_order(side, price, amount):
    """Place an order on Bybit."""
    try:
        order = exchange.create_order(symbol, 'limit', side, amount, price, {'leverage': leverage})
        print(f"Placed {side} order: {order}")
    except Exception as e:
        print(f"Order failed: {e}")


def should_trade():
    """Check trading conditions."""
    now = datetime.now(aest)
    return hours[0] <= now.hour < hours[1] and now.weekday() in days


def trade_logic():
    """Main trading logic."""
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


# Schedule the bot to run every 15 minutes
schedule.every(15).minutes.do(trade_logic)

# Keep the script running
if __name__ == "__main__":
    print("Trading bot started. Waiting for schedule...")
    while True:
        schedule.run_pending()
        time.sleep(1)


