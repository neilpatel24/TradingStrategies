import pandas as pd
import matplotlib.pyplot as plt
from binance.client import Client
import numpy as np

# Binance API keys (replace with actual keys if needed for fetching historical data)
api_key = 'api-key-here'
api_secret = 'secret-key-here'

# Initialize Binance client
client = Client(api_key, api_secret)

# Fetch historical OHLCV data (candles)
def fetch_ohlcv(symbol, interval='1h', limit=1000):
    candles = client.get_historical_klines(symbol, interval, limit=limit)
    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_vol', 'number_of_trades', 'taker_buy_base_vol', 'taker_buy_quote_vol', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df['close'] = df['close'].astype(float)
    return df

# Calculate EMA
def calculate_ema(df, period):
    return df['close'].ewm(span=period, adjust=False).mean()

# Backtest function
def backtest(symbol):
    # Fetch data
    df = fetch_ohlcv(symbol)

    # Calculate EMAs
    df['short_ema'] = calculate_ema(df, 50)
    df['mid_ema'] = calculate_ema(df, 100)
    df['long_ema'] = calculate_ema(df, 200)

    # Initialize variables for backtesting
    initial_balance = 1000.0  # Starting balance in USD
    balance = initial_balance
    position = 0  # Position in BTC
    trade_log = []

    for i in range(1, len(df)):
        # Get current and previous EMA values
        short_ema = df['short_ema'].iloc[i]
        mid_ema = df['mid_ema'].iloc[i]
        long_ema = df['long_ema'].iloc[i]
        prev_short_ema = df['short_ema'].iloc[i - 1]
        prev_long_ema = df['long_ema'].iloc[i - 1]

        # Check for Buy Signal
        if short_ema > long_ema and prev_short_ema <= prev_long_ema and position == 0:
            position = balance / df['close'].iloc[i]  # Buy BTC with entire balance
            balance = 0  # Set cash balance to zero
            trade_log.append(('Buy', df.index[i], df['close'].iloc[i], position))
            print(f"Buying at {df['close'].iloc[i]:.2f} on {df.index[i]}")

        # Check for Sell Signal
        elif short_ema < long_ema and prev_short_ema >= prev_long_ema and position > 0:
            balance = position * df['close'].iloc[i]  # Sell BTC for USD
            position = 0  # Set BTC position to zero
            trade_log.append(('Sell', df.index[i], df['close'].iloc[i], balance))
            print(f"Selling at {df['close'].iloc[i]:.2f} on {df.index[i]}")

    # Final portfolio value if position is held
    if position > 0:
        balance = position * df['close'].iloc[-1]
        trade_log.append(('Final Sell', df.index[-1], df['close'].iloc[-1], balance))

    # Calculate performance
    total_return = (balance - initial_balance) / initial_balance * 100
    print(f"\nInitial Balance: ${initial_balance:.2f}")
    print(f"Final Balance: ${balance:.2f}")
    print(f"Total Return: {total_return:.2f}%")

    # Plotting the backtest results
    plt.figure(figsize=(14, 8))
    plt.plot(df['close'], label='Close Price', color='blue', alpha=0.5)
    plt.plot(df['short_ema'], label='50-period EMA', color='green', linestyle='--')
    plt.plot(df['mid_ema'], label='100-period EMA', color='orange', linestyle='--')
    plt.plot(df['long_ema'], label='200-period EMA', color='red', linestyle='--')

    # Plot buy/sell markers
    for action, date, price, _ in trade_log:
        color = 'green' if action == 'Buy' else 'red'
        plt.scatter(date, price, color=color, marker='^' if action == 'Buy' else 'v', s=100, label=f"{action} @ ${price:.2f}")

    plt.title(f"Backtest Results for {symbol}")
    plt.xlabel("Date")
    plt.ylabel("Price (USDT)")
    plt.legend()
    plt.show()

# Run the backtest
backtest('BTCUSDT')
