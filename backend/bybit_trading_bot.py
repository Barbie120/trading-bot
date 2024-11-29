import time
from pybit.unified_trading import HTTP
from tradingview_ta import TA_Handler, Interval

# Bybit Testnet Configuration
api_key = "s4FGt4J2oc4UoLa2vD"
api_secret = "ASgjidd9Qq0VdadQutFXWDQAIo0Fz45AdNTOvi"

# Initialize the Bybit testnet client
session = HTTP(
    testnet=True,  # Ensures you're using the testnet environment
    api_key=api_key,
    api_secret=api_secret
)

# Bot Configurations
leverage = 20
portfolio_usdt = 100
max_trade_percentage = 0.1  # Max 10% of portfolio per trade
time_zone_offset = 11  # AEST offset
trade_days = ["Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


# Helper Functions
def get_indicator_signal(trading_symbol, indicator_name, interval):
    """
    Fetches a signal from TradingView indicators.
    """
    analysis = TA_Handler(
        symbol=trading_symbol,
        screener="crypto",
        exchange="BYBIT",
        interval=interval
    )
    return analysis.get_analysis().indicators.get(indicator_name)


def calculate_fibonacci(high, low):
    """
    Calculates Fibonacci retracement levels.
    """
    levels = {
        "0.236": high - 0.236 * (high - low),
        "0.5": high - 0.5 * (high - low),
        "1.618": high + 1.618 * (high - low),
        "2.618": high + 2.618 * (high - low),
        "3.381": high + 3.381 * (high - low),
        "4.018": high + 4.018 * (high - low)
    }
    return levels


def place_order(trading_symbol, side, price, qty, order_type="Limit"):
    """
    Places an order using Bybit API.
    """
    session.place_order(
        category="linear",
        symbol=trading_symbol,
        side=side,
        order_type=order_type,
        qty=qty,
        price=price,
        time_in_force="GoodTillCancel"
    )


def trade(trading_symbol):
    """
    Implements the trading strategy based on the configured criteria.
    """
    today = time.strftime("%A")
    if today not in trade_days:
        print(f"No trading today ({today})")
        return

    try:
        # Fetch buy signal and sell signal
        buy_signal = get_indicator_signal(trading_symbol, "YourBuySignal", Interval.INTERVAL_1_HOUR)
        sell_signal = get_indicator_signal(trading_symbol, "YourSellSignal", Interval.INTERVAL_1_HOUR)

        if buy_signal:
            high, low = 50, 30  # Replace with actual values (e.g., fetched via an API)
            fib_levels = calculate_fibonacci(high, low)
            print(f"Buy Signal: Fibonacci Levels - {fib_levels}")

            # First Entry
            trade_amount = portfolio_usdt * leverage * max_trade_percentage
            place_order(trading_symbol, "Buy", fib_levels["0.236"], trade_amount / 3)

            # Second Entry
            place_order(trading_symbol, "Buy", fib_levels["0.5"], trade_amount / 3)

            # Third Entry
            place_order(trading_symbol, "Buy", fib_levels["0.236"], trade_amount / 3)

        if sell_signal:
            high, low = 50, 30  # Replace with actual values (e.g., fetched via an API)
            fib_levels = calculate_fibonacci(high, low)
            print(f"Sell Signal: Fibonacci Levels - {fib_levels}")

            # First Entry
            trade_amount = portfolio_usdt * leverage * max_trade_percentage
            place_order(trading_symbol, "Sell", fib_levels["0.236"], trade_amount / 3)

            # Second Entry
            place_order(trading_symbol, "Sell", fib_levels["0.5"], trade_amount / 3)

            # Third Entry
            place_order(trading_symbol, "Sell", fib_levels["0.236"], trade_amount / 3)

    except Exception as e:
        print(f"Error while trading: {e}")


# Main Loop with Graceful Exit
if __name__ == "__main__":
    symbol = "BTCUSDT"
    try:
        while True:
            trade(symbol)
            time.sleep(3600)  # Adjust based on desired frequency (e.g., hourly)
    except KeyboardInterrupt:
        print("\nTrading bot interrupted. Exiting gracefully...")
