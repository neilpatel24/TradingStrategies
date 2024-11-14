# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
from binance.client import Client
from datetime import datetime, timedelta

# Initialize Binance client (replace 'your_api_key' and 'your_api_secret' with your credentials)
client = Client(api_key='your_api_key', api_secret='your_api_secret')

# Define parameters for the data request
symbol = 'BTCUSDT'
interval = Client.KLINE_INTERVAL_1DAY  # Daily interval
days = 365  # Last year
end_date = datetime.now()
start_date = end_date - timedelta(days=days)

# Fetch historical data
klines = client.get_historical_klines(symbol, interval, start_date.strftime("%d %b, %Y"), end_date.strftime("%d %b, %Y"))

# Convert data into a DataFrame
btc_df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                       'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
                                       'taker_buy_quote_asset_volume', 'ignore'])

# Keep only the necessary columns and convert data types
btc_df = btc_df[['timestamp', 'close']]
btc_df['timestamp'] = pd.to_datetime(btc_df['timestamp'], unit='ms')
btc_df.set_index('timestamp', inplace=True)
btc_df['close'] = btc_df['close'].astype(float)

# Calculate moving averages: 50-day, 100-day, and 200-day
btc_df['MA50'] = btc_df['close'].rolling(window=50).mean()
btc_df['MA100'] = btc_df['close'].rolling(window=100).mean()
btc_df['MA200'] = btc_df['close'].rolling(window=200).mean()

# Plot the Close Price and Moving Averages
plt.figure(figsize=(14, 7))
plt.plot(btc_df['close'], label='Close Price', color='blue')
plt.plot(btc_df['MA50'], label='50-day MA', color='orange', linestyle='--')
plt.plot(btc_df['MA100'], label='100-day MA', color='green', linestyle='--')
plt.plot(btc_df['MA200'], label='200-day MA', color='red', linestyle='--')

# Enhancing the plot
plt.title("BTC/USDT Close Price with 50, 100, and 200 Day Moving Averages (Last Year)")
plt.xlabel("Date")
plt.ylabel("Price (USDT)")
plt.legend()
plt.grid(visible=True, linestyle='--', alpha=0.5)
plt.show()
