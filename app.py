from flask import Flask, render_template, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
import yfinance as yf
import pandas as pd
from pandas.tseries.offsets import BDay

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stocks.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define the time periods and their corresponding number of days
time_periods = {
    '5d': 5,
    #'10d': 10,
    #'30d': 30,
    #'60d': 60,
    #'90d': 90,
}

def create_tables():
    db.create_all()

class TrackedStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)
    data = db.Column(db.JSON, nullable=True)

def get_current_price(symbol):
    stock = yf.Ticker(symbol)
    return stock.info['currentPrice']

def track_stock(symbol):
    # Get the stock data for 1 year
    stock_data_1y = yf.download(symbol, period="1y")
    stock_data_90d = yf.download(symbol, period="90d")
    #print(stock_data_1y)
    print(len(stock_data_90d))
    # Get the last date in the data
    last_date = stock_data_1y.index[-1]
    print(last_date)

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
            'Date': [], 'Open': [], 'High': [], 'Low': [], 'Close': [], 'High to Open %': [], 'Low to Open %': [],
            'Low to Close %': [], 'High to Close %': [],
            'Max High': [], 'Max Low': [], 'Min Low': [], 'Current Price': [], 
            '% Change from Highest Price to Current': [], '% Change from Lowest Price to Current': []
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

                # Calculate the max and min within each time period
                max_high = max(stock_data[period]['High']) if stock_data[period]['High'] else row['High']
                max_low = max(stock_data[period]['Low']) if stock_data[period]['Low'] else row['Low']
                min_low = min(stock_data[period]['Low']) if stock_data[period]['Low'] else row['Low']

                # Get the current price
                current_price = get_current_price(symbol)

                # Calculate percentage change from current price to max and min
                pct_change_to_max = ((max_high - current_price) / current_price) * 100
                pct_change_to_min = ((min_low - current_price) / current_price) * 100


                # Add data to the period dictionary
                stock_data[period]['Date'].append(date.strftime('%Y-%m-%d'))
                stock_data[period]['Open'].append(float(row['Open']))
                stock_data[period]['High'].append(float(row['High']))
                stock_data[period]['Low'].append(float(row['Low']))
                stock_data[period]['Close'].append(float(row['Close']))
                stock_data[period]['High to Open %'].append(pct_change_high)
                stock_data[period]['Low to Open %'].append(pct_change_low)
                stock_data[period]['Low to Close %'].append(pct_change_low_to_close)
                stock_data[period]['High to Close %'].append(pct_change_high_to_close)
                stock_data[period]['Max High'].append(max_high)
                stock_data[period]['Max Low'].append(max_low)
                stock_data[period]['Min Low'].append(min_low)
                stock_data[period]['% Change from Highest Price to Current'].append(pct_change_to_max)
                stock_data[period]['% Change from Lowest Price to Current'].append(pct_change_to_min)



        # Calculate average high % change and low % change for each period
            stock_data[period]['Avg High % Change'] = sum(stock_data[period]['High to Open %']) / len(stock_data[period]['High to Open %'])
            stock_data[period]['Avg Low % Change'] = sum(stock_data[period]['Low to Open %']) / len(stock_data[period]['Low to Open %'])
            stock_data[period]['Max High % Change'] = max(stock_data[period]['High to Open %'])
            stock_data[period]['Min High % Change'] = min(stock_data[period]['High to Open %'])
            stock_data[period]['Max Low % Change'] = max(stock_data[period]['Low to Open %'])
            stock_data[period]['Min Low % Change'] = min(stock_data[period]['Low to Open %'])

        #print("Period " + period + ":")
        #print(stock_data[period])
    

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

    try:
        with app.app_context():
            db.create_all()  # Create the table if it doesn't exist
    except sqlalchemy.exc.OperationalError as e:
        return "Error in creating database tables: " + str(e), 500

    if request.method == 'POST':
        symbol = request.form['symbol']
        stock_price = request.form['price']

        with app.app_context():
            existing_stock = TrackedStock.query.filter_by(symbol=symbol).first()
            if existing_stock:
                existing_stock.price = stock_price
            else:
                new_stock = TrackedStock(symbol=symbol, price=stock_price, data=track_stock(symbol))
                db.session.add(new_stock)

            db.session.commit()
        
        with app.app_context():
            all_stocks = TrackedStock.query.all()
        
        return render_template('trackedstocks.html', tracked_stocks=all_stocks, period=time_periods.keys())
    else:
        # Handle GET request
        with app.app_context():
            all_stocks = TrackedStock.query.all()
            print(all_stocks)
            tracked_symbols = [stock.symbol for stock in all_stocks]
            print(tracked_symbols)
      
        return render_template('trackedstocks.html', tracked_stocks=all_stocks, period=time_periods.keys())

if __name__ == '__main__':
    app.run(debug=True)