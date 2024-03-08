from flask import Flask, render_template, request
import yfinance as yf
import pandas as pd
from pandas.tseries.offsets import BDay

app = Flask(__name__)

def track_stock(symbol):
    # Get the stock data for 1 year
    stock_data_1y = yf.download(symbol, period="1y")

    # Filter out weekends (non-business days)
    stock_data_1y = stock_data_1y[stock_data_1y.index.dayofweek < 5]

    # Get the last date in the data
    last_date = stock_data_1y.index[-1]

    # Initialize dictionaries to store data for each time period
    stock_data = {
        '1y': {'Date': [], 'Open': [], 'High': [], 'Low': [], 'Close': [], 'High % Change': [], 'Low % Change': []},
        '90d': {'Date': [], 'Open': [], 'High': [], 'Low': [], 'Close': [], 'High % Change': [], 'Low % Change': []},
        '60d': {'Date': [], 'Open': [], 'High': [], 'Low': [], 'Close': [], 'High % Change': [], 'Low % Change': []},
        '30d': {'Date': [], 'Open': [], 'High': [], 'Low': [], 'Close': [], 'High % Change': [], 'Low % Change': []},
        '10d': {'Date': [], 'Open': [], 'High': [], 'Low': [], 'Close': [], 'High % Change': [], 'Low % Change': []},
        '5d': {'Date': [], 'Open': [], 'High': [], 'Low': [], 'Close': [], 'High % Change': [], 'Low % Change': []}
    }

    # Get the last 5 business days
    business_days = pd.date_range(end=last_date, periods=5, freq=BDay())

    # Iterate over each business day's data for the last 5 days
    for date in business_days:
        if date in stock_data_1y.index:
            row = stock_data_1y.loc[date]

            # Calculate percentage changes for each day
            pct_change_high = ((row['High'] - row['Open']) / row['Open']) * 100
            pct_change_low = ((row['Low'] - row['Open']) / row['Open']) * 100

            # Add data to the 7 day dictionary
            stock_data['5d']['Date'].append(date.strftime('%Y-%m-%d'))
            stock_data['5d']['Open'].append(row['Open'])
            stock_data['5d']['High'].append(row['High'])
            stock_data['5d']['Low'].append(row['Low'])
            stock_data['5d']['Close'].append(row['Close'])
            stock_data['5d']['High % Change'].append(pct_change_high)
            stock_data['5d']['Low % Change'].append(pct_change_low)

    # Get the last 10 business days
    business_days = pd.date_range(end=last_date, periods=11, freq=BDay())

    # Iterate over each business day's data for the last 10 days
    for date in business_days:
        if date in stock_data_1y.index:
            row = stock_data_1y.loc[date]

            # Calculate percentage changes for each day
            pct_change_high = ((row['High'] - row['Open']) / row['Open']) * 100
            pct_change_low = ((row['Low'] - row['Open']) / row['Open']) * 100

            # Add data to the 14 day dictionary
            stock_data['10d']['Date'].append(date.strftime('%Y-%m-%d'))
            stock_data['10d']['Open'].append(row['Open'])
            stock_data['10d']['High'].append(row['High'])
            stock_data['10d']['Low'].append(row['Low'])
            stock_data['10d']['Close'].append(row['Close'])
            stock_data['10d']['High % Change'].append(pct_change_high)
            stock_data['10d']['Low % Change'].append(pct_change_low)

    # Get the last 30 business days
    business_days = pd.date_range(end=last_date, periods=31, freq=BDay())

    # Iterate over each business day's data for the last 30 days
    for date in business_days:
        if date in stock_data_1y.index:
            row = stock_data_1y.loc[date]

            # Calculate percentage changes for each day
            pct_change_high = ((row['High'] - row['Open']) / row['Open']) * 100
            pct_change_low = ((row['Low'] - row['Open']) / row['Open']) * 100

            # Add data to the 30 day dictionary
            stock_data['30d']['Date'].append(date.strftime('%Y-%m-%d'))
            stock_data['30d']['Open'].append(row['Open'])
            stock_data['30d']['High'].append(row['High'])
            stock_data['30d']['Low'].append(row['Low'])
            stock_data['30d']['Close'].append(row['Close'])
            stock_data['30d']['High % Change'].append(pct_change_high)
            stock_data['30d']['Low % Change'].append(pct_change_low)

    # Get the last 60 business days
    business_days = pd.date_range(end=last_date, periods=64, freq=BDay())

    # Iterate over each business day's data for the last 60 days
    for date in business_days:
        if date in stock_data_1y.index:
            row = stock_data_1y.loc[date]

            # Calculate percentage changes for each day
            pct_change_high = ((row['High'] - row['Open']) / row['Open']) * 100
            pct_change_low = ((row['Low'] - row['Open']) / row['Open']) * 100

            # Add data to the 60 day dictionary
            stock_data['60d']['Date'].append(date.strftime('%Y-%m-%d'))
            stock_data['60d']['Open'].append(row['Open'])
            stock_data['60d']['High'].append(row['High'])
            stock_data['60d']['Low'].append(row['Low'])
            stock_data['60d']['Close'].append(row['Close'])
            stock_data['60d']['High % Change'].append(pct_change_high)
            stock_data['60d']['Low % Change'].append(pct_change_low)

    # Get the last 90 business days
    business_days = pd.date_range(end=last_date, periods=95, freq=BDay())

    # Iterate over each business day's data for the last 90 days
    for date in business_days:
        if date in stock_data_1y.index:
            row = stock_data_1y.loc[date]

            # Calculate percentage changes for each day
            pct_change_high = ((row['High'] - row['Open']) / row['Open']) * 100
            pct_change_low = ((row['Low'] - row['Open']) / row['Open']) * 100

            # Add data to the 90 day dictionary
            stock_data['90d']['Date'].append(date.strftime('%Y-%m-%d'))
            stock_data['90d']['Open'].append(row['Open'])
            stock_data['90d']['High'].append(row['High'])
            stock_data['90d']['Low'].append(row['Low'])
            stock_data['90d']['Close'].append(row['Close'])
            stock_data['90d']['High % Change'].append(pct_change_high)
            stock_data['90d']['Low % Change'].append(pct_change_low)

    # Calculate average high % change and low % change for each period
    for period in ['5d', '10d', '30d', '60d', '90d']:
        if stock_data[period]['High % Change']:
            stock_data[period]['Avg High % Change'] = sum(stock_data[period]['High % Change']) / len(stock_data[period]['High % Change'])
            stock_data[period]['Avg Low % Change'] = sum(stock_data[period]['Low % Change']) / len(stock_data[period]['Low % Change'])
            stock_data[period]['Max High % Change'] = max(stock_data[period]['High % Change'])
            stock_data[period]['Min High % Change'] = min(stock_data[period]['High % Change'])
            stock_data[period]['Max Low % Change'] = max(stock_data[period]['Low % Change'])
            stock_data[period]['Min Low % Change'] = min(stock_data[period]['Low % Change'])

    return stock_data

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        symbol = request.form['symbol']
        stock_data = track_stock(symbol)

        return render_template('index.html', stock_data=stock_data)
    else:
        return render_template('index.html', stock_data=None)

if __name__ == '__main__':
    app.run(debug=True)
