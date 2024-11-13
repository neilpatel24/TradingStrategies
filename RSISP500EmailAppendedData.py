import yfinance as yf
import pandas as pd
from pytickersymbols import PyTickerSymbols
import numpy as np
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import os

# Function to calculate RSI
def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period, min_periods=1).mean()
    avg_loss = loss.rolling(window=period, min_periods=1).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Function to calculate Sharpe ratio
def calculate_sharpe_ratio(data):
    returns = data['Close'].pct_change().dropna()
    sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252)  # Annualized Sharpe ratio
    return sharpe_ratio

# Function to calculate Sortino ratio
def calculate_sortino_ratio(data):
    returns = data['Close'].pct_change().dropna()
    downside_returns = returns[returns < 0]
    sortino_ratio = returns.mean() / downside_returns.std() * np.sqrt(252)  # Annualized Sortino ratio
    return sortino_ratio

# Email sending function
def send_email(to_address, subject, body, attachment_path):
    from_address = 'ENTER SENDER EMAIL ADDRESS HERE'
    password = 'ENTER EMAIL APP PASSWORD'
    
    # Setup the MIME
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject
    
    # Attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))
    
    # Open the file to be sent
    attachment = open(attachment_path, "rb")
    
    # Instance of MIMEBase and named as part
    part = MIMEBase('application', 'octet-stream')
    
    # Change the payload into encoded form
    part.set_payload((attachment).read())
    
    # Encode into base64
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f"attachment; filename= {attachment_path}")
    
    # Attach the instance 'part' to instance 'msg'
    msg.attach(part)
    
    # Create SMTP session for sending the mail
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_address, password)
    
    text = msg.as_string()
    server.sendmail(from_address, to_address, text)
    server.quit()

# Get the list of stocks you want to include in the analysis. The below provides a static list but you can analyse the full S&P 500 by removing the array and inserting [stock['symbol'] for stock in sp500_symbols], if not use ['TSLA', 'NVDA', 'AAPL', 'MSFT', 'MSTR', 'AMZN', 'META', 'INTC'] for testing.
stock_data = PyTickerSymbols()
sp500_symbols = stock_data.get_stocks_by_index('S&P 500')
symbols = [stock['symbol'] for stock in sp500_symbols]

# Create DataFrames to store the results
buy_signal_results = pd.DataFrame(columns=['Ticker', 'RSI_Yesterday', 'RSI_Today'])
sell_signal_results = pd.DataFrame(columns=['Ticker', 'RSI_Yesterday', 'RSI_Today'])

# Loop through each stock and calculate the 14-day RSI
for symbol in symbols:
    data = yf.download(symbol, period='3mo')
    data['RSI'] = calculate_rsi(data)
    if len(data['RSI']) > 1:
        rsi_yesterday = data['RSI'].iloc[-2]
        rsi_today = data['RSI'].iloc[-1]

# Now attach a buy or sell signal depending on the RSI calculations. You can adjust the thresholds to your preference.        
        if rsi_yesterday < 51 and rsi_today > 51:
            buy_signal_results = pd.concat([buy_signal_results, pd.DataFrame({'Ticker': [symbol], 'RSI_Yesterday': [rsi_yesterday], 'RSI_Today': [rsi_today]})], ignore_index=True)
        
        if rsi_yesterday < 71 and rsi_today > 71:
            sell_signal_results = pd.concat([sell_signal_results, pd.DataFrame({'Ticker': [symbol], 'RSI_Yesterday': [rsi_yesterday], 'RSI_Today': [rsi_today]})], ignore_index=True)

# Add recent performance data and Sharpe/Sortino ratios
performance_data = []

for symbol in symbols:
    data = yf.download(symbol, period='1y')
    
    if len(data) > 1:
        # Calculate performance over different time periods
        performance_1d = (data['Close'].iloc[-1] / data['Close'].iloc[-2] - 1) * 100 if len(data) > 1 else None
        performance_7d = (data['Close'].iloc[-1] / data['Close'].iloc[-8] - 1) * 100 if len(data) > 7 else None
        performance_14d = (data['Close'].iloc[-1] / data['Close'].iloc[-15] - 1) * 100 if len(data) > 14 else None
        performance_1m = (data['Close'].iloc[-1] / data['Close'].iloc[-22] - 1) * 100 if len(data) > 22 else None
        performance_3m = (data['Close'].iloc[-1] / data['Close'].iloc[-66] - 1) * 100 if len(data) > 66 else None
        performance_6m = (data['Close'].iloc[-1] / data['Close'].iloc[-132] - 1) * 100 if len(data) > 132 else None
        performance_1y = (data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100 if len(data) > 0 else None
        
        # Calculate Sharpe and Sortino ratios
        sharpe_ratio = calculate_sharpe_ratio(data) if len(data) > 1 else None
        sortino_ratio = calculate_sortino_ratio(data) if len(data) > 1 else None
        
        # Get the latest close price
        latest_close_price = data['Close'].iloc[-1]
        
        performance_data.append({
            'Ticker': symbol,
            'Latest Close Price': latest_close_price,
            '1D Performance': performance_1d,
            '7D Performance': performance_7d,
            '14D Performance': performance_14d,
            '1M Performance': performance_1m,
            '3M Performance': performance_3m,
            '6M Performance': performance_6m,
            '1Y Performance': performance_1y,
            'Sharpe Ratio': sharpe_ratio,
            'Sortino Ratio': sortino_ratio
        })

performance_df = pd.DataFrame(performance_data)

# Merge performance data with buy and sell signal results
buy_signal_results = pd.merge(buy_signal_results, performance_df, on='Ticker', how='left')
sell_signal_results = pd.merge(sell_signal_results, performance_df, on='Ticker', how='left')

# Add the current date and time to the buy and sell signal DataFrames
current_datetime = datetime.now()
buy_signal_results['DateTime'] = current_datetime
sell_signal_results['DateTime'] = current_datetime

# Define the filename
filename = 'rsi_signals_master.xlsx'

# Get the current date and time for the timestamp (no longer required as we want a static filename now)
# current_datetime_filename = datetime.now().strftime('%Y%m%d_%H%M%S')

# Check if the file already exists 
if os.path.exists(filename): 
    
    # Load the existing data 
    existing_buy_signals = pd.read_excel(filename, sheet_name='Buy_Signals') 
    existing_sell_signals = pd.read_excel(filename, sheet_name='Sell_Signals') 

    # Count the number of existing signals
    num_existing_buy_signals = len(existing_buy_signals)
    num_existing_sell_signals = len(existing_sell_signals)    
    
    # Append new data to existing data 
    buy_signal_results = pd.concat([existing_buy_signals, buy_signal_results], ignore_index=True)
    sell_signal_results = pd.concat([existing_sell_signals, sell_signal_results], ignore_index=True)

# Save the results to an Excel file with separate sheets 
with pd.ExcelWriter(filename) as writer:
    buy_signal_results.to_excel(writer, sheet_name='Buy_Signals', index=False) 
    sell_signal_results.to_excel(writer, sheet_name='Sell_Signals', index=False)


# Save the results to an Excel file with separate sheets (no longer required due to new append function above)
#filename = f'rsi_signals_{current_datetime_filename}.xlsx'
#with pd.ExcelWriter(filename) as writer:
#    buy_signal_results.to_excel(writer, sheet_name='Buy_Signals', index=False)
#   sell_signal_results.to_excel(writer, sheet_name='Sell_Signals', index=False)

# Read the Excel file
df_buy = pd.read_excel(filename, sheet_name='Buy_Signals')
df_sell = pd.read_excel(filename, sheet_name='Sell_Signals')

# Calculate the number of rows altogether now with the new data added
num_buy_signals = len(df_buy)
num_sell_signals = len(df_sell)

# Calculate the number of rows added by the latest update
new_buy_signals_added = num_buy_signals - num_existing_buy_signals
new_sell_signals_added = num_sell_signals - num_existing_sell_signals

# Send the email with the attachment
send_email(
    to_address='ADD RECIPIENT EMAIL ADDRESS HERE',
    subject='Daily RSI Signals Report',
    body=f"""\
Hi Benchod,

Here are the latest signals from the RSI5171 strategy:

- Total Number of buy signals recorded: {num_buy_signals}
- Total Number of sell signals recorded: {num_sell_signals}

- New buy Signals added since last update: {new_buy_signals_added}
- New sell Signals added since last update: {new_sell_signals_added}

Best regards,
Neil
""",
    attachment_path=filename
)

print(f"Data saved to spreadsheet and email sent, last run on {current_datetime}")