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
    stock_data_90d = yf.download(symbol, period="3mo")
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
            'Date': [], 
            'Open': [], 
            'High': [], 
            'Low': [], 
            'Close': [], 
            'Open to High %': [], 
            'Open to Low %': [],
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
                pct_change_low_to_close = ((row['Low'] - row['Close']) / row['Close']) * 100
                pct_change_high_to_close = ((row['Close'] - row['High']) / row['High']) * 100

                # Get the current price
                current_price = get_current_price(symbol)


                # Add data to the period dictionary
                stock_data[period]['Date'].append(date.strftime('%Y-%m-%d'))
                stock_data[period]['Open'].append(float(row['Open']))
                stock_data[period]['High'].append(float(row['High']))
                stock_data[period]['Low'].append(float(row['Low']))
                stock_data[period]['Close'].append(float(row['Close']))
                stock_data[period]['Open to High %'].append(pct_change_high)
                stock_data[period]['Open to Low %'].append(pct_change_low)
                stock_data[period]['Low to Close %'].append(pct_change_low_to_close)
                stock_data[period]['High to Close %'].append(pct_change_high_to_close)



        # Calculate average high % change and low % change for each period
            stock_data[period]['Avg Open to High %'] = sum(stock_data[period]['Open to High %']) / len(stock_data[period]['Open to High %'])
            stock_data[period]['Avg Open to Low %'] = sum(stock_data[period]['Open to Low %']) / len(stock_data[period]['Open to Low %'])
            stock_data[period]['Max Open to High %'] = max(stock_data[period]['Open to High %'])
            stock_data[period]['Min Open to High %'] = min(stock_data[period]['Open to High %'])
            stock_data[period]['Max Open to Low %'] = max(stock_data[period]['Open to Low %'])
            stock_data[period]['Min Open to Low %'] = min(stock_data[period]['Open to Low %'])
            #stock_data[period]['High to Low % Change'] = ((stock_data[period]['High'] - stock_data[period]['Low']) / stock_data[period]['Low']) * 100

        max_high = max(stock_data[period]['High'])
        max_low = min(stock_data[period]['Low'])
        print("High: " + str(max_high))
        print("Low: " + str(max_low))
        stock_data[period]['High to Low % Change'] = ((max_low - max_high)/max_high) * 100
        stock_data[period]['High to Current % Change'] = ((current_price - max_high) / max_high) * 100

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