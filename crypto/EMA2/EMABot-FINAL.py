from binance.client import Client
import pandas as pd
import numpy as np
import time
import datetime
import smtplib
from email.mime.text import MIMEText

# Binance API Keys
# api_key = 'APIKEY' 
# api_secret = 'APISECRET'

# Email configuration
EMAIL_ADDRESS = 'EMAIL_ADDRESS'
EMAIL_PASSWORD = 'EMAIL APP PW'
TO_EMAILS = ['abc@abc.com,def@def.com']  # Comma seperated list of recipient emails

# Function to send an email
def send_email(subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = ', '.join(TO_EMAILS)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

# Initialize Binance API
client = Client(api_key, api_secret)

# State Management for Each Coin Instance
state = {
    "trend": None,      # Placeholder for the current trend: "bullish" or "bearish"
    "balance": None,    # Will be fetched dynamically
    "position": None,   # Will be fetched dynamically
    "max_usdt": 10000,     # Max USDT to spend for this instance (example: 50 USDT)
}

# Function to fetch LOT_SIZE filter details
def get_lot_size_filter(symbol):
    exchange_info = client.get_exchange_info()
    for s in exchange_info['symbols']:
        if s['symbol'] == symbol:
            for f in s['filters']:
                if f['filterType'] == 'LOT_SIZE':
                    return {
                        'minQty': float(f['minQty']),
                        'maxQty': float(f['maxQty']),
                        'stepSize': float(f['stepSize'])
                    }
    return None

# Function to adjust the quantity to match LOT_SIZE rules
def adjust_quantity_to_lot_size(quantity, lot_size_filter):
    step_size = lot_size_filter['stepSize']
    adjusted_quantity = quantity - (quantity % step_size)
    return round(adjusted_quantity, 4)


# Add initial_correction function here
def initial_correction(symbol, trend):
    """
    Aligns the bot's position with the current trend at the start.
    If bullish, ensures the position is held. If bearish, ensures no holdings.
    """
    holdings = get_current_holdings(symbol)  # Fetch current holdings
    if trend == "bullish" and holdings == 0:
        # Buy assets to align with bullish trend
        price = float(client.get_symbol_ticker(symbol=symbol)['price'])
        lot_size_filter = get_lot_size_filter(symbol)
        quantity = adjust_quantity_to_lot_size(state['balance'] / price, lot_size_filter)
        client.order_market_buy(symbol=symbol, quantity=quantity)
        state["position"] = quantity
        state["balance"] = 0  # Fully invested
        print(f"Initial correction: Bought {quantity} of {symbol}.")
        send_email(f"Initial correction: Bought {quantity} of {symbol}", f"Buy executed at {price:.2f}")
    elif trend == "bearish" and holdings > 0:
        # Sell all holdings to align with bearish trend
        client.order_market_sell(symbol=symbol, quantity=holdings)
        state["position"] = 0
        state["balance"] += holdings * float(client.get_symbol_ticker(symbol=symbol)['price'])
        print(f"Initial correction: Sold all holdings of {symbol}.")
        send_email(f"Initial correction: Sold all holdings of {symbol}", f"Sell executed at {price:.2f}")
        
# Function to fetch OHLCV data
def fetch_ohlcv(symbol, interval='1h', limit=1000):
    candles = client.get_historical_klines(symbol, interval, limit=limit)
    df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                        'quote_asset_vol', 'number_of_trades', 'taker_buy_base_vol',
                                        'taker_buy_quote_vol', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df['close'] = df['close'].astype(float)
    return df

# Function to calculate EMA
def calculate_ema(df, period):
    return df['close'].ewm(span=period, adjust=False).mean()

# Function to get current holdings of the symbol
def get_current_holdings(symbol):
    """Fetch current holdings of the symbol from Binance, treating amounts below minQty as zero."""
    try:
        # Fetch the user's account balances
        account_info = client.get_account()
        balances = account_info['balances']
        
        # Find the free balance of the specified asset
        for asset in balances:
            if asset['asset'] == symbol[:-4]:  # Remove "USDT" from the symbol (e.g., "LINKUSDT" -> "LINK")
                position = float(asset['free'])  # Free balance of the coin
                
                # Fetch the LOT_SIZE filter to get the minQty
                lot_size_filter = get_lot_size_filter(symbol)
                if lot_size_filter:
                    min_qty = lot_size_filter['minQty']
                    
                    # Treat holdings less than minQty as zero
                    if position < min_qty:
                        print(f"Held position ({position}) is below the minimum quantity ({min_qty}). Treating it as zero.")
                        return 0
                
                return position
        
        # If the asset is not found, return 0
        return 0
    except Exception as e:
        print(f"Error fetching holdings for {symbol}: {e}")
        return 0

# Function to initialize the trend
def initialize_trend(symbol):
    df = fetch_ohlcv(symbol)
    short_ema = calculate_ema(df, 7)
    long_ema = calculate_ema(df, 25)

    if short_ema.iloc[-1] > long_ema.iloc[-1]:
        return "bullish"
    else:
        return "bearish"

# Function to place buy and sell orders
def place_order(side, symbol, quantity):
    try:
        if side == 'BUY':
            print(f"Placing Buy Order for {quantity} {symbol}")
            order = client.order_market_buy(symbol=symbol, quantity=quantity)
        elif side == 'SELL':
            print(f"Placing Sell Order for {quantity} {symbol}")
            order = client.order_market_sell(symbol=symbol, quantity=quantity)
        
        status = order.get('status')
        executed_qty = float(order.get('executedQty', 0))
        price = (
            sum(float(fill['price']) * float(fill['qty']) for fill in order.get('fills', [])) / executed_qty
            if executed_qty > 0 else None
        )

        print(f"{side} Order Placed: Status = {status}, Quantity = {executed_qty}, Price = {price}")

        # Send email notification
        subject = f"{side} Order for {symbol} - Status: {status}"
        message = (
            f"{side} Order Details:\n"
            f"Status: {status}\n"
            f"Quantity: {executed_qty}\n"
            f"Price: {price:.2f}\n"
        )
        send_email(subject, message)

        return {
            "status": status,
            "quantity": executed_qty,
            "price": price
        }
    except Exception as e:
        print(f"Error placing {side} order: {e}")
        subject = f"{side} Order Failed for {symbol}"
        message = f"An error occurred while placing the {side} order:\n{e}"
        send_email(subject, message)

        return None

# Buy and Sell Execution Functions
def buy(symbol, price):
    global state
    if state['balance'] > 0:
        if state['position'] == 0:  # If no position (initial buy)
            # Use max_usdt to limit the amount spent
            available_usdt_to_spend = min(state['balance'], state['max_usdt']) * 0.99  # Reserve 1% for fees
        else:
            # After initialization, use the balance generated from sales
            available_usdt_to_spend = state['balance'] * 0.99  # Reserve 1% for fees
        
        # Calculate the quantity to buy based on the available USDT
        trade_quantity = available_usdt_to_spend / price
        
        # Adjust quantity according to lot size filter
        lot_size_filter = get_lot_size_filter(symbol)
        if lot_size_filter:
            trade_quantity = adjust_quantity_to_lot_size(trade_quantity, lot_size_filter)
        else:
            print("Unable to adjust quantity to LOT_SIZE.")
            return

        # Log balance and trade details
        print(f"Available USDT to spend: {available_usdt_to_spend}, Trade Quantity: {trade_quantity}, Price: {price}")

        # Place the buy order
        try:
            order_response = place_order('BUY', symbol, trade_quantity)
            if order_response and order_response['status'] == 'FILLED':  # Check if the order was filled
                state['position'] = trade_quantity
                state['balance'] -= available_usdt_to_spend  # Reduce balance by the amount spent
                print(f"Buy successful: Position = {state['position']}, Balance = {state['balance']}")
            else:
                print("Buy order not filled, balance not updated.")
        except Exception as e:
            print(f"Error during buy: {e}")
            send_email("Buy Order Failed", f"Error: {e}")

def sell(symbol, price):
    global state
    if state['position'] > 0:
        lot_size_filter = get_lot_size_filter(symbol)
        trade_quantity = adjust_quantity_to_lot_size(state['position'], lot_size_filter)
        order_response = place_order('SELL', symbol, trade_quantity)
        if order_response:
            # Calculate the total value of the sale
            sale_value = price * trade_quantity
            
            # Update state: position is 0, balance is the sale value in USDT
            state['balance'] += sale_value
            state['position'] = 0  # All coins converted to cash
            print(f"Sell successful: Position = {state['position']}, Balance = {state['balance']}")

# Trading Logic
def trade(symbol):
    global state

    # Fetch OHLCV data and calculate EMAs
    df = fetch_ohlcv(symbol)
    short_ema = calculate_ema(df, 1)
    long_ema = calculate_ema(df, 7)

    last_short_ema = short_ema.iloc[-1]
    last_long_ema = long_ema.iloc[-1]
    last_close_price = df['close'].iloc[-1]

    print(f"Checking {symbol} | Last Close: {last_close_price:.2f} | Short EMA: {last_short_ema:.2f} | Long EMA: {last_long_ema:.2f}")

    # Determine current trend
    current_trend = "bullish" if last_short_ema > last_long_ema else "bearish"

    # Check for buy/sell signals based on trend change
    if current_trend == "bullish" and state["trend"] != "bullish":
        print("Buy signal detected.")
        buy(symbol, last_close_price)
        send_email(f"Buy Signal for {symbol}", f"Buy executed at {last_close_price:.2f}")
        state["trend"] = "bullish"

    elif current_trend == "bearish" and state["trend"] != "bearish":
        print("Sell signal detected.")
        sell(symbol, last_close_price)
        send_email(f"Sell Signal for {symbol}", f"Sell executed at {last_close_price:.2f}")
        state["trend"] = "bearish"

# Main Function
def run_trading_bot():
    global state

    symbol = 'BTCUSDT'
    max_usdt = 10000  # Example max amount to spend on the first buy

    try:
        # Fetch current holdings of symbol
        initial_holdings = get_current_holdings(symbol)

        # Fetch current USDT balance
        account_info = client.get_account() # retrieves all your balances (e.g., LINK, USDT, BTC, etc.)
        usdt_balance = 0
        for asset in account_info['balances']: # this part finds my current USDT balance
            if asset['asset'] == 'USDT':
                usdt_balance = float(asset['free'])

        # Fetch the current price of symbol
        initial_price = float(client.get_symbol_ticker(symbol=symbol)['price'])

        # Initialize state
        state["trend"] = initialize_trend(symbol)
        state["position"] = initial_holdings
        state["balance"] = usdt_balance  # Set to actual USDT balance
        state["max_usdt"] = max_usdt  # Set the max USDT to spend on the first buy
        print(f"Initial State: Trend = {state['trend']}, Position = {state['position']}, Balance = {state['balance']}")

        # Perform initial correction based on the trend
        initial_correction(symbol, state["trend"])

    except Exception as e:
        print(f"Error during initialization: {e}")
        send_email("Trading Bot Error", f"Error during initialization: {e}")

    # Main trading loop
    while True:
        trade(symbol)
        time.sleep(60)

# Run the bot
if __name__ == "__main__":
    run_trading_bot()
