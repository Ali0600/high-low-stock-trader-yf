from flask import Flask, render_template, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
import yfinance as yf
import pandas as pd
from pandas.tseries.offsets import BDay
from curl_cffi import requests


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stocks.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define the time periods and their corresponding number of days
time_periods = {
    '5d': 5,
    #'10d': 10,
    '30d': 30,
    '60d': 60,
    '90d': 90,
}

class TrackedStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)
    data = db.Column(db.JSON, nullable=True)

def get_current_price(symbol):
    try:
        session = requests.Session(impersonate="chrome")
        stock = yf.Ticker(symbol, session=session)
        return stock.info.get('currentPrice', stock.info.get('regularMarketPrice', 0.0))
    except Exception as e:
        print(f"Error getting price for {symbol}: {e}")
        return 0.0


# Here I could add a variable to track the timeframe.
def track_stock(symbol):
    # Get the stock data for 3 months with a timeout
    try:
        session = requests.Session(impersonate="chrome", timeout=20)  # Add timeout
        stock_data_3m = yf.download(symbol, period="3mo", session=session, timeout=20)
        print(f"Downloaded data for {symbol}")
    except Exception as e:
        print(f"Error downloading data for {symbol}: {e}")
        return {}  # Return empty dict on error
        
    print(stock_data_3m)
    # Check if we got any data
    if len(stock_data_3m) == 0:
        print(f"No data found for symbol: {symbol}")
        # Return empty data structure with proper keys
        empty_data = {}
        for period in time_periods.keys():
            empty_data[period] = {
                'Date': [], 'Open': [], 'High': [], 'Low': [], 'Close': [], 
                'High to Open %': [], 'Low to Open %': [], 'Low to Close %': [], 'High to Close %': [],
                'Max High': [], 'Max Low': [], 'Min Low': [], 'Current Price': [],
                '% Change from Highest Price to Current': [], '% Change from Lowest Price to Current': [],
                'Avg High % Change': 0, 'Avg Low % Change': 0, 'Max High % Change': 0,
                'Min High % Change': 0, 'Max Low % Change': 0, 'Min Low % Change': 0
            }
        return empty_data
    # Filter out weekends (non-business days)
    stock_data_3m = stock_data_3m[stock_data_3m.index.dayofweek < 5]
    # Get the last date in the data
    last_date = stock_data_3m.index[-1]

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
            'Current Price': [], 
        }
<<<<<<< HEAD
=======



>>>>>>> f953ffeed147a6f1d2e93157813f19f88958f886
        # Iterate over each business day's data for the specified period
        for date in business_days:
            if date in stock_data_3m.index:
                row = stock_data_3m.loc[date]

<<<<<<< HEAD
                # Convert to float to ensure we're using scalar values, not Series
                if isinstance(row, pd.Series):
                    # Handle Series objects
                    high = float(row['High'].iloc[0]) if isinstance(row['High'], pd.Series) else float(row['High'])
                    low = float(row['Low'].iloc[0]) if isinstance(row['Low'], pd.Series) else float(row['Low'])
                    open_price = float(row['Open'].iloc[0]) if isinstance(row['Open'], pd.Series) else float(row['Open'])
                    close = float(row['Close'].iloc[0]) if isinstance(row['Close'], pd.Series) else float(row['Close'])
                else:
                    # Handle DataFrame objects
                    high = float(row.iloc[0]['High'])
                    low = float(row.iloc[0]['Low'])
                    open_price = float(row.iloc[0]['Open'])
                    close = float(row.iloc[0]['Close'])
                
                # Calculate percentage changes
                pct_change_high = ((high - open_price) / open_price) * 100 if open_price != 0 else 0
                pct_change_low = ((low - open_price) / open_price) * 100 if open_price != 0 else 0
                pct_change_low_to_close = ((close - low) / low) * 100 if low != 0 else 0
                pct_change_high_to_close = ((close - high) / high) * 100 if high != 0 else 0

                # Calculate the max and min within each time period
                max_high = max(stock_data[period]['High']) if stock_data[period]['High'] else high
                max_low = max(stock_data[period]['Low']) if stock_data[period]['Low'] else low
                min_low = min(stock_data[period]['Low']) if stock_data[period]['Low'] else low

                # Get the current price
                current_price = get_current_price(symbol)
                # Calculate percentage change from current price to max and min
                # Use a default value if current_price is 0 to avoid division by zero
                if current_price > 0:
                    pct_change_to_max = ((max_high - current_price) / current_price) * 100
                    pct_change_to_min = ((min_low - current_price) / current_price) * 100
                else:
                    pct_change_to_max = 0
                    pct_change_to_min = 0
=======
                # Calculate percentage changes for each day
                pct_change_high = ((row['High'] - row['Open']) / row['Open']) * 100
                pct_change_low = ((row['Low'] - row['Open']) / row['Open']) * 100
                pct_change_low_to_close = ((row['Low'] - row['Close']) / row['Close']) * 100
                pct_change_high_to_close = ((row['Close'] - row['High']) / row['High']) * 100

                # Get the current price
                current_price = get_current_price(symbol)
>>>>>>> f953ffeed147a6f1d2e93157813f19f88958f886


                # Add data to the period dictionary
                stock_data[period]['Date'].append(date.strftime('%Y-%m-%d'))
<<<<<<< HEAD
                stock_data[period]['Open'].append(open_price)  
                stock_data[period]['High'].append(high)  
                stock_data[period]['Low'].append(low)  
                stock_data[period]['Close'].append(close)  
                stock_data[period]['High to Open %'].append(pct_change_high)
                stock_data[period]['Low to Open %'].append(pct_change_low)
=======
                stock_data[period]['Open'].append(float(row['Open']))
                stock_data[period]['High'].append(float(row['High']))
                stock_data[period]['Low'].append(float(row['Low']))
                stock_data[period]['Close'].append(float(row['Close']))
                stock_data[period]['Open to High %'].append(pct_change_high)
                stock_data[period]['Open to Low %'].append(pct_change_low)
>>>>>>> f953ffeed147a6f1d2e93157813f19f88958f886
                stock_data[period]['Low to Close %'].append(pct_change_low_to_close)
                stock_data[period]['High to Close %'].append(pct_change_high_to_close)


        # Calculate average high % change and low % change for each period
<<<<<<< HEAD
        try:
            if stock_data[period]['High to Open %']:
                stock_data[period]['Avg High % Change'] = sum(stock_data[period]['High to Open %']) / len(stock_data[period]['High to Open %'])
                stock_data[period]['Max High % Change'] = max(stock_data[period]['High to Open %'])
                stock_data[period]['Min High % Change'] = min(stock_data[period]['High to Open %'])
            else:
                stock_data[period]['Avg High % Change'] = 0
                stock_data[period]['Max High % Change'] = 0
                stock_data[period]['Min High % Change'] = 0
                
            if stock_data[period]['Low to Open %']:
                stock_data[period]['Avg Low % Change'] = sum(stock_data[period]['Low to Open %']) / len(stock_data[period]['Low to Open %'])
                stock_data[period]['Max Low % Change'] = max(stock_data[period]['Low to Open %'])
                stock_data[period]['Min Low % Change'] = min(stock_data[period]['Low to Open %'])
            else:
                stock_data[period]['Avg Low % Change'] = 0
                stock_data[period]['Max Low % Change'] = 0
                stock_data[period]['Min Low % Change'] = 0
        except Exception as e:
            print(f"Error calculating statistics for {symbol} {period}: {e}")
            # Set default values if calculation fails
            stock_data[period]['Avg High % Change'] = 0
            stock_data[period]['Avg Low % Change'] = 0
            stock_data[period]['Max High % Change'] = 0
            stock_data[period]['Min High % Change'] = 0
            stock_data[period]['Max Low % Change'] = 0
            stock_data[period]['Min Low % Change'] = 0
    
=======
            stock_data[period]['Avg Open to High %'] = sum(stock_data[period]['Open to High %']) / len(stock_data[period]['Open to High %'])
            stock_data[period]['Avg Open to Low %'] = sum(stock_data[period]['Open to Low %']) / len(stock_data[period]['Open to Low %'])
            stock_data[period]['Max Open to High %'] = max(stock_data[period]['Open to High %'])
            stock_data[period]['Min Open to High %'] = min(stock_data[period]['Open to High %'])
            stock_data[period]['Max Open to Low %'] = max(stock_data[period]['Open to Low %'])
            stock_data[period]['Min Open to Low %'] = min(stock_data[period]['Open to Low %'])
            #stock_data[period]['High to Low % Change'] = ((stock_data[period]['High'] - stock_data[period]['Low']) / stock_data[period]['Low']) * 100

        max_high_index = stock_data[period]['High'].index(max(stock_data[period]['High'])) #This is used so it starts the calculation from AFTER the highest value
        max_high = max(stock_data[period]['High'])
        #max_low = min(stock_data[period]['Low'])
        max_low = min(stock_data[period]['Low'][max_high_index:])

        print("High of " +  period + ": "  + str(max_high))
        print("Low of " + period + ": " + str(max_low))
        stock_data[period]['High to Low % Change'] = ((max_low - max_high)/max_high) * 100
        stock_data[period]['High to Current % Change'] = ((current_price - max_high) / max_high) * 100

        print(stock_data[period]['High'].index(max_high)) 
        print(stock_data[period]['High'][max_high_index:])
        print(min(stock_data[period]['Low'][max_high_index:]))

>>>>>>> f953ffeed147a6f1d2e93157813f19f88958f886

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
        try:
            stock_price = float(request.form['price'])
        except ValueError:
            stock_price = 0.0  # Default to 0 if invalid price
        
        try:
            with app.app_context():
                existing_stock = TrackedStock.query.filter_by(symbol=symbol).first()
                if existing_stock:
                    existing_stock.price = stock_price
                    # Update the data as well
                    existing_stock.data = track_stock(symbol)
                else:
                    # Track the stock and get data
                    stock_data = track_stock(symbol)
                    if stock_data:
                        new_stock = TrackedStock(symbol=symbol, price=stock_price, data=stock_data)
                        db.session.add(new_stock)

                db.session.commit()
            
            with app.app_context():
                all_stocks = TrackedStock.query.all()
            
            return render_template('trackedstocks.html', tracked_stocks=all_stocks, period=time_periods.keys())
        except Exception as e:
            print(f"Error tracking stock {symbol}: {e}")
            # Continue to show existing stocks even if adding new one fails
            with app.app_context():
                all_stocks = TrackedStock.query.all()
            return render_template('trackedstocks.html', tracked_stocks=all_stocks, period=time_periods.keys(), error=f"Error tracking {symbol}: {e}")
    else:
        # Handle GET request
        with app.app_context():
            all_stocks = TrackedStock.query.all()
            print(all_stocks)
            tracked_symbols = [stock.symbol for stock in all_stocks]
            print(tracked_symbols)
            
            # Debug the actual structure of data being retrieved from DB
            for stock in all_stocks:
                print(f"Stock: {stock.symbol}")
                if stock.data:
                    print(f"Data keys: {stock.data.keys()}")
                    for period in time_periods.keys():
                        if period in stock.data:
                            print(f"Period {period} exists in data")
                            if 'Avg High % Change' in stock.data[period]:
                                print(f"  'Avg High % Change' exists for {period}")
                        else:
                            print(f"Period {period} MISSING from data!")
                else:
                    print(f"No data for {stock.symbol}")
      
        return render_template('trackedstocks.html', tracked_stocks=all_stocks, period=time_periods.keys())

def create_tables(force_recreate=True):
    with app.app_context():
        if force_recreate:
            db.drop_all()
            print("Database tables dropped!")
        
        # Check if tables exist
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        if not existing_tables or force_recreate:
            db.create_all()
            print("Database tables created!")
        else:
            print("Database tables already exist.")

if __name__ == '__main__':
    create_tables()  # Create tables before running the app
    app.run(debug=True)