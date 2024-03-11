from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import yfinance as yf
import pandas as pd
from pandas.tseries.offsets import BDay

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stocks.db'
db = SQLAlchemy(app)

class TrackedStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    
with app.app_context():
    db.create_all()

tracked_stocks_set = set()


def track_stock(symbol):
    # Get the stock data for 1 year
    stock_data_1y = yf.download(symbol, period="1y")

    # Filter out weekends (non-business days)
    stock_data_1y = stock_data_1y[stock_data_1y.index.dayofweek < 5]

    # Get the last date in the data
    last_date = stock_data_1y.index[-1]

    # Define the time periods and their corresponding number of days
    time_periods = {
        '5d': 5,
        '10d': 10,
        '30d': 30,
        '60d': 60,
        '90d': 90,
        '1y': 365
    }

     # Initialize dictionary to store stock data
    stock_data = {}
    for period, days in time_periods.items():
        # Get the last n business days
        if period == '5d':
            business_days = pd.date_range(end=last_date, periods=days, freq=BDay())
        elif period == '10d':
            business_days = pd.date_range(end=last_date, periods=days, freq=BDay())
        elif period == '30d':
            business_days = pd.date_range(end=last_date, periods=days+1, freq=BDay())
        elif period == '60d':
            business_days = pd.date_range(end=last_date, periods=days+4, freq=BDay())
        elif period == '90d':
            business_days = pd.date_range(end=last_date, periods=days+5, freq=BDay())


        # Initialize lists to store data for each period
        stock_data[period] = {
            'Date': [], 'Open': [], 'High': [], 'Low': [], 'Close': [], 'High % Change': [], 'Low % Change': [],
            'Low to Close %': [], 'High to Close %': []
        }

        # Iterate over each business day's data for the specified period
        for date in business_days:
            if date in stock_data_1y.index:
                row = stock_data_1y.loc[date]

                # Calculate percentage changes for each day
                pct_change_high = ((row['High'] - row['Open']) / row['Open']) * 100
                pct_change_low = ((row['Low'] - row['Open']) / row['Open']) * 100
                pct_change_low_to_close = ((row['Close'] - row['Low']) / row['Low']) * 100
                pct_change_high_to_close = ((row['Close'] - row['High']) / row['High']) * 100

                # Add data to the period dictionary
                stock_data[period]['Date'].append(date.strftime('%Y-%m-%d'))
                stock_data[period]['Open'].append(row['Open'])
                stock_data[period]['High'].append(row['High'])
                stock_data[period]['Low'].append(row['Low'])
                stock_data[period]['Close'].append(row['Close'])
                stock_data[period]['High % Change'].append(pct_change_high)
                stock_data[period]['Low % Change'].append(pct_change_low)
                stock_data[period]['Low to Close %'].append(pct_change_low_to_close)
                stock_data[period]['High to Close %'].append(pct_change_high_to_close)


        # Calculate average high % change and low % change for each period
        if stock_data[period]['High % Change']:
            stock_data[period]['Avg High % Change'] = sum(stock_data[period]['High % Change']) / len(stock_data[period]['High % Change'])
            stock_data[period]['Avg Low % Change'] = sum(stock_data[period]['Low % Change']) / len(stock_data[period]['Low % Change'])
            stock_data[period]['Max High % Change'] = max(stock_data[period]['High % Change'])
            stock_data[period]['Min High % Change'] = min(stock_data[period]['High % Change'])
            stock_data[period]['Max Low % Change'] = max(stock_data[period]['Low % Change'])
            stock_data[period]['Min Low % Change'] = min(stock_data[period]['Low % Change'])
    

    return stock_data

@app.route('/stock-tracker', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        symbol = request.form['symbol']
        stock_data = track_stock(symbol)

        return render_template('index.html', stock_data=stock_data)
    else:
        return render_template('index.html', stock_data=None)
    
@app.route('/', methods=['GET'])
def home():
    return render_template('homepage.html')

@app.route('/tracked-stocks', methods=['GET', 'POST'])
def track_stocks():
    if request.method == 'POST':
        symbol = request.form['symbol']
        with app.app_context():
            existing_stock = TrackedStock.query.filter_by(symbol=symbol).first()
            if not existing_stock:
                new_stock = TrackedStock(symbol=symbol)
                db.session.add(new_stock)
                db.session.commit()
    with app.app_context():
        tracked_stocks = TrackedStock.query.all()
        tracked_symbols = [stock.symbol for stock in tracked_stocks]
        

    return render_template('trackedstocks.html', tracked_stocks=tracked_symbols)

if __name__ == '__main__':
    app.run(debug=True)