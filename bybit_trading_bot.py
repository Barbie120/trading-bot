import ccxt
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

# Load Bybit API keys from .env
API_KEY = os.getenv('BYBIT_API_KEY')
SECRET_KEY = os.getenv('BYBIT_SECRET_KEY')

# Configure Bybit with ccxt
exchange = ccxt.bybit({
    'apiKey': API_KEY,
    'secret': SECRET_KEY,
    'enableRateLimit': True,
})


def get_tradingview_signal():
    # Here you would typically configure TradingView Webhook signals to be received via a server endpoint
    # For simplicity, I'll show a dummy request, in practice, you would receive webhook data
    return {
        "action": "buy",  # or "sell"
        "price": 50000  # hypothetical price value
    }


def calculate_fibonacci(low, high):
    fib_levels = {
        "0.236": high - (high - low) * 0.236,
        "0.5": high - (high - low) * 0.5,
        "1.618": high + (high - low) * 1.618,
        "2.618": high + (high - low) * 2.618,
        "3.381": high + (high - low) * 3.381,
        "4.018": high + (high - low) * 4.018,
    }
    return fib_levels


def execute_trade(signal, leverage=20):
    order = None  # Initialize order variable
    try:
        # Set leverage
        exchange.set_leverage(leverage, 'BTC/USDT')

        if signal['action'] == 'buy':
            order = exchange.create_market_buy_order('BTC/USDT', 0.01)  # Example size
        elif signal['action'] == 'sell':
            order = exchange.create_market_sell_order('BTC/USDT', 0.01)

        if order:
            print(f"Order executed: {order}")

    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    # Only trade between 6am - 11pm US time
    now = datetime.datetime.now()

    # Check time constraints (between 6 AM to 11 PM) and weekdays (Monday to Saturday)
    if 6 <= now.hour < 23:
        if now.weekday() < 6:  # Monday to Saturday
            signal = get_tradingview_signal()
            if signal:
                execute_trade(signal)


if __name__ == '__main__':
    main()
