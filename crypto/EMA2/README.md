**Technical Specification Document**

**Project:** Binance EMA Crypto Trading Bot\
**Author:** Neil Patel

---

## **1. Introduction**

This document provides a technical specification for a Python-based crypto trading bot that executes trades on Binance using Exponential Moving Averages (EMA) as trading signals. The bot is designed to automate cryptocurrency trades based on trend analysis.

## **2. Dependencies**

The script requires the following dependencies:

- `binance.client` – Connects to the Binance API for trading and data retrieval.
- `pandas` – Handles data processing and analysis.
- `numpy` – Used for numerical computations.
- `time` & `datetime` – Manages script timing.
- `smtplib` & `email.mime.text` – Handles email notifications.

## **3. Configuration & Setup**

Before running the script, configure the following parameters:

- **Binance API Keys:**
  ```python
  api_key = 'APIKEY'
  api_secret = 'APISECRET'
  ```
- **Email Configuration:**
  ```python
  EMAIL_ADDRESS = 'EMAIL_ADDRESS'
  EMAIL_PASSWORD = 'EMAIL APP PW'
  TO_EMAILS = ['abc@abc.com', 'def@def.com']
  ```
- **Trading Parameters:**
  ```python
  state = {
      "trend": None,
      "balance": None,
      "position": None,
      "max_usdt": 10000,  # Maximum amount of USDT to trade
  }
  ```

## **4. Functions & Features**

### **4.1 Email Notification System**

Sends email notifications for trade execution and errors.

```python
def send_email(subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = ', '.join(TO_EMAILS)
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
```

### **4.2 Binance API Initialization**

Connects to Binance API.

```python
client = Client(api_key, api_secret)
```

### **4.3 Fetching Market Data**

Retrieves historical price data.

```python
def fetch_ohlcv(symbol, interval='1h', limit=1000):
    candles = client.get_historical_klines(symbol, interval, limit=limit)
    df = pd.DataFrame(candles, columns=[...])
    return df
```

### **4.4 EMA Calculation**

Computes Exponential Moving Averages for trend detection.

```python
def calculate_ema(df, period):
    return df['close'].ewm(span=period, adjust=False).mean()
```

### **4.5 Trading Strategy Execution**

Executes buy/sell trades based on EMA signals. The periods can be chosen based on how reactive the user wants to be to market fluctuations.

```python
def trade(symbol):
    df = fetch_ohlcv(symbol)
    short_ema = calculate_ema(df, 1)
    long_ema = calculate_ema(df, 7)

    if short_ema.iloc[-1] > long_ema.iloc[-1]:
        buy(symbol, df['close'].iloc[-1])
    else:
        sell(symbol, df['close'].iloc[-1])
```

### **4.6 Order Execution**

Handles buy and sell orders.

```python
def place_order(side, symbol, quantity):
    try:
        order = client.order_market_buy(symbol=symbol, quantity=quantity) if side == 'BUY' else client.order_market_sell(symbol=symbol, quantity=quantity)
        return order
    except Exception as e:
        send_email(f"Order Failed: {symbol}", str(e))
```

### **4.7 Main Trading Loop**

Continuously monitors the market and executes trades.

```python
while True:
    trade('BTCUSDT')
    time.sleep(60)
```

## **5. Customization & Parameters**

The following parameters can be customized:

| Parameter          | Description                        | Default Value                    |
| ------------------ | ---------------------------------- | -------------------------------- |
| `symbol`           | Trading pair (e.g., BTCUSDT)       | `'BTCUSDT'`                      |
| `max_usdt`         | Max USDT to spend                  | `10000`                          |
| `short_ema`        | Short EMA period                   | `1`                              |
| `long_ema`         | Long EMA period                    | `7`                              |
| `email_recipients` | List of email addresses for alerts | `['abc@abc.com', 'def@def.com']` |

---

## **6. Usage Guide**

1. Install dependencies:
   ```bash
   pip install python-binance pandas numpy
   ```
2. Update API keys and email settings in the script.
3. Enter the custom parameters to match personal preferences (see 'Customization & Parameters' above
4. Run the script:
   ```bash
   python trading_bot.py
   ```
5. Monitor logs and email alerts for trade execution details.

## **7. How the Trading Bot Works (Step-by-Step)**

User Input & Setup
1. The user selects trading pairs (e.g., BTC/USDT) and configures bot settings such as EMA lengths, trade size, and risk tolerance.
2. API keys are provided (read and trade permissions only, no withdrawals).

Fetching Market Data
1. The bot connects to the Binance API to retrieve live price data.
2. It calculates two EMAs (e.g., a short-term 9-period EMA and a longer-term 21-period EMA).

Signal Generation
1. A buy signal is triggered when the short EMA crosses above the long EMA (bullish crossover).
2. A sell signal is triggered when the short EMA crosses below the long EMA (bearish crossover).

Trade Execution
1. The bot places market orders setting quantity to the full balance held (by checking spot balance in Binance).
2. It accounts for fees to ensure trades can execute regardless of adverse price movements

Trade Logging & Notifications
1. The bot continuously runs, monitoring EMAs and price movements.
2. Users receive email notifications when trades are placed.

---

## **7. Conclusion**

This trading bot is designed for automated cryptocurrency trading using EMA-based strategies. It could be further improved by integrating additional indicators, risk management rules, and improved error handling.



