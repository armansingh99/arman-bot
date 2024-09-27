import os
import smtplib
import time
import pandas as pd
from polygon import RESTClient
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Polygon API key from environment variables
POLYGON_API_KEY = os.getenv('cdNJB86_9z2SCL0oUrBQdcH3hQpoJLnj')

# Email credentials from environment variables
EMAIL_USER = os.getenv('arman@apnagenie.co.in')
EMAIL_PASS = os.getenv('a@213582')
EMAIL_TO = os.getenv('arman@apnagenie.co.in')

# Function to fetch historical stock data (5-minute candlestick)
def fetch_stock_data(symbol, timespan='minute', multiplier=5, from_date=None, to_date=None):
    client = RESTClient(POLYGON_API_KEY)
    response = client.get_aggs(ticker=symbol, multiplier=multiplier, timespan=timespan, from_=from_date, to=to_date)
    data = pd.DataFrame(response)
    data['timestamp'] = pd.to_datetime(data['t'], unit='ms')
    data['close'] = data['c']
    return data[['timestamp', 'close']]

# Supertrend Calculation
def calculate_supertrend(df, period=7, multiplier=3):
    df['TR'] = abs(df['close'] - df['close'].shift(1))
    df['ATR'] = df['TR'].rolling(period).mean()
    df['upper_band'] = df['close'] + (multiplier * df['ATR'])
    df['lower_band'] = df['close'] - (multiplier * df['ATR'])
    df['Supertrend'] = df['upper_band']  # Simple rule for demo purposes
    return df[['timestamp', 'close', 'Supertrend']]

# Send Email Notification
def send_email_notification(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_TO
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            text = msg.as_string()
            server.sendmail(EMAIL_USER, EMAIL_TO, text)
    except Exception as e:
        print(f"Error sending email: {e}")

# Main function to check stocks and send notification
def check_stocks_and_notify():
    stocks_to_monitor = ['AAPL', 'TSLA', 'GOOGL']  # Example stock symbols
    for symbol in stocks_to_monitor:
        data = fetch_stock_data(symbol)
        supertrend_data = calculate_supertrend(data)

        # Filter stocks where Supertrend is applied (this is a simple demo condition)
        last_row = supertrend_data.iloc[-1]
        if last_row['Supertrend'] > last_row['close']:
            subject = f"Supertrend Alert for {symbol}"
            body = f"Supertrend applied on {symbol} at {last_row['timestamp']}.\nPrice: {last_row['close']}\nSupertrend: {last_row['Supertrend']}"
            send_email_notification(subject, body)
            print(f"Alert sent for {symbol}.")

# Run the bot every 5 minutes
if __name__ == '__main__':
    while True:
        check_stocks_and_notify()
        time.sleep(300)  # Wait for 5 minutes (300 seconds) before running again
