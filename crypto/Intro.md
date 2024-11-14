# EMA Backtesting
The `EMA-Crypto-Backtest.py` file is a Python script used for backtesting a cryptocurrency trading strategy based on Exponential Moving Averages (EMA). Here are the main components:

- The script imports necessary libraries such as `pandas`, `matplotlib.pyplot`, `binance.client`, and `numpy`.
- API Keys: Placeholder for Binance API keys.
- Binance Client: Initializes the Binance client using the provided API keys.
- Fetch Historical Data: Defines a function `fetch_ohlcv` to fetch historical OHLCV (Open, High, Low, Close, Volume) data from Binance.
- Calculate EMA: Defines a function `calculate_ema` to calculate the EMA for a given period.
- Backtest Function: Defines the `backtest` function which:
  - Fetches historical data.
  - Calculates short, mid, and long EMAs (50, 100, and 200 periods).
  - Initializes variables for backtesting including initial balance and position.
  - Uses a loop to iterate through the data and checks for buy/sell signals based on EMA crossovers.
  - Logs trades and updates balance and position accordingly.

The script is designed to test the effectiveness of an EMA-based trading strategy using historical data from Binance.
