from binance.client import Client
import pandas as pd
import numpy as np
import time
import datetime
import matplotlib.pyplot as plt

# Set up Binance API (replace 'your_key' and 'your_secret' with actual API keys)
api_key = 'api-key-here'
api_secret = 'secret-key-here'

# Initialize Binance API with the provided credentials
client = Client(api_key, api_secret)

# Function to fetch historical OHLCV data (candles)
def fetch_ohlcv(symbol, interval='1h', limit=500):
    # Fetch the historical candlestick data from Binance
    candles = client.get_historical_klines(symbol, interval, limit=limit)
    
    # Convert the fetched data to a DataFrame
    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_vol', 'number_of_trades', 'taker_buy_base_vol', 'taker_buy_quote_vol', 'ignore'])
    
    # Convert timestamp to a readable date format
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    
    # Convert prices to float for calculations
    df['close'] = df['close'].astype(float)
    return df

# Function to calculate EMA
def calculate_ema(df, period):
    return df['close'].ewm(span=period, adjust=False).mean()

# Function to plot the price data with EMAs
def plot_ema_chart(df, short_ema, long_ema, symbol):
    plt.figure(figsize=(14, 8))
    plt.plot(df.index, df['close'], label='Close Price', color='blue')
    plt.plot(df.index, short_ema, label='50-period EMA', color='green', linestyle='--')
    plt.plot(df.index, mid_ema, label='100-period EMA', color='yellow', linestyle='--')
    plt.plot(df.index, long_ema, label='200-period EMA', color='red', linestyle='--')
    plt.title(f"{symbol} Price and EMAs")
    plt.xlabel("Date")
    plt.ylabel("Price (USDT)")
    plt.legend()
    plt.show()

# Function to place a market buy order
def place_buy_order(symbol, quantity):
    print(f"Placing Buy Order for {quantity} {symbol}")
    order = client.order_market_buy(symbol=symbol, quantity=quantity)
    return order

# Function to place a market sell order
def place_sell_order(symbol, quantity):
    print(f"Placing Sell Order for {quantity} {symbol}")
    order = client.order_market_sell(symbol=symbol, quantity=quantity)
    return order

# Function to check if we should buy/sell
def trade(symbol):
    df = fetch_ohlcv(symbol)
    
    # Calculate EMAs
    short_ema = calculate_ema(df, 50)  # 50-period EMA (Short-term)
    long_ema = calculate_ema(df, 200)  # 200-period EMA (Long-term)
    mid_ema = calculate_ema(df,100) # 100-period EMA (mid-term)
    
    # Get the latest values of short and long EMAs
    last_short_ema = short_ema.iloc[-1]
    last_long_ema = long_ema.iloc[-1]
    prev_short_ema = short_ema.iloc[-2]
    prev_long_ema = long_ema.iloc[-2]
    last_mid_ema = mid_ema.iloc[-1]
    prev_mid_ema = mid_ema.iloc[-2]
    
    # Print the current EMA values regardless of buy/sell signal
    print(f"Checking {symbol} | Short EMA: {last_short_ema:.2f} | Mid EMA: {last_mid_ema:.2f} | Long EMA: {last_long_ema:.2f}")

    # Plot EMAs and price data
    # plot_ema_chart(df, short_ema, long_ema, symbol)
    
    # Check if short EMA crosses above long EMA (Buy Signal)
    if last_short_ema > last_long_ema and prev_short_ema <= prev_long_ema:
        print(f"Buy Signal: {symbol} | Short EMA: {last_short_ema} | Long EMA: {last_long_ema}")
        # Example: Buy 0.001 BTC (you can modify the quantity based on your balance)
        place_buy_order(symbol, 0.001)
    
    # Check if short EMA crosses below long EMA (Sell Signal)
    elif last_short_ema < last_long_ema and prev_short_ema >= prev_long_ema:
        print(f"Sell Signal: {symbol} | Short EMA: {last_short_ema} | Long EMA: {last_long_ema}")
        # Example: Sell 0.001 BTC (you can modify the quantity based on your balance)
        place_sell_order(symbol, 0.001)

# Main function to monitor the market and trade based on signals
def run_trading_bot():
    symbol = 'BTCUSDT'  # Set trading pair (e.g., BTC/USDT)
    while True:
        print(f"Checking signals for {symbol} at {datetime.datetime.now()} ")
        trade(symbol)
        time.sleep(60)  # Wait 60 seconds before checking again

if __name__ == '__main__':
    run_trading_bot()
