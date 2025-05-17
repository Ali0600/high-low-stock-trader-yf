from flask import Flask, render_template, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import yfinance as yf
import pandas as pd
from pandas.tseries.offsets import BDay
from curl_cffi import requests
import numpy as np


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stocks.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define the time periods and their corresponding number of days
time_periods = {
    '5d': 5,
    '10d': 10,
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
        session = requests.Session(impersonate="chrome", timeout=20)
        stock_data_3m = yf.download(symbol, period="3mo", session=session, timeout=20, auto_adjust=False)
        print(f"Downloaded data for {symbol}")
    except Exception as e:
        print(f"Error downloading data for {symbol}: {e}")
        return {}  # Return empty dict on error
    
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
    
    # Print an example of the data structure to debug
    print(f"Data sample (first row): {stock_data_3m.iloc[0]}")
    
    # Filter out weekends (non-business days)
    stock_data_3m = stock_data_3m[stock_data_3m.index.dayofweek < 5]
    
    # Get the last date in the data
    last_date = stock_data_3m.index[-1]
    
    # Get current price once instead of for each day
    current_price = get_current_price(symbol)
    print(f"Current price for {symbol}: {current_price}")
    
    # Initialize dictionary to store stock data
    stock_data = {}
    
    # Create a mapping for period to business days to avoid redundant code
    business_days_map = {
        '5d': pd.date_range(end=last_date, periods=time_periods['5d'], freq=BDay()),
        '10d': pd.date_range(end=last_date, periods=time_periods['10d'], freq=BDay()),
        '30d': pd.date_range(end=last_date, periods=time_periods['30d']+1, freq=BDay()),
        '60d': pd.date_range(end=last_date, periods=time_periods['60d']+4, freq=BDay()),
        '90d': pd.date_range(end=last_date, periods=time_periods['90d']+5, freq=BDay())
    }
    
    for period, days in time_periods.items():
        business_days = business_days_map[period]
        
        # Pre-filter relevant data for this period to avoid repeated lookups
        period_dates = [date for date in business_days if date in stock_data_3m.index]
        period_data = stock_data_3m.loc[period_dates]
        
        # Initialize data structure for this period
        date_strings = [date.strftime('%Y-%m-%d') for date in period_dates]
        
        # Create empty lists for data
        opens = []
        highs = []
        lows = []
        closes = []
        
        # Extract data as individual scalar values to avoid type issues
        for date in period_dates:
            try:
                # Get the row for this date
                row = stock_data_3m.loc[date]
                
                # Handle single value or Series appropriately
                if isinstance(row, pd.Series):
                    open_val = float(row['Open'])
                    high_val = float(row['High'])
                    low_val = float(row['Low'])
                    close_val = float(row['Close'])
                else:
                    # For DataFrame result, take the first row
                    open_val = float(row.iloc[0]['Open'])
                    high_val = float(row.iloc[0]['High'])
                    low_val = float(row.iloc[0]['Low'])
                    close_val = float(row.iloc[0]['Close'])
                
                # Append the scalar values to our lists
                opens.append(open_val)
                highs.append(high_val)
                lows.append(low_val)
                closes.append(close_val)
            except Exception as e:
                print(f"Error extracting data for {symbol} on {date}: {e}")
                # Skip this date if we can't process it
                continue
        
        # If we have no data for this period, use empty lists
        if not opens:
            print(f"No data found for period {period}")
            high_to_open_pct = []
            low_to_open_pct = []
            low_to_close_pct = []
            high_to_close_pct = []
            max_high = 0
            min_low = 0
        else:
            # Calculate percentage changes with scalar values
            high_to_open_pct = []
            low_to_open_pct = []
            low_to_close_pct = []
            high_to_close_pct = []
            
            # Process each data point individually
            for i in range(len(opens)):
                try:
                    open_val = opens[i]
                    high_val = highs[i]
                    low_val = lows[i]
                    close_val = closes[i]
                    
                    # Calculate individual percentages
                    h_open = ((high_val - open_val) / open_val) * 100 if open_val != 0 else 0
                    l_open = ((low_val - open_val) / open_val) * 100 if open_val != 0 else 0
                    l_close = ((close_val - low_val) / low_val) * 100 if low_val != 0 else 0
                    h_close = ((close_val - high_val) / high_val) * 100 if high_val != 0 else 0
                    
                    high_to_open_pct.append(h_open)
                    low_to_open_pct.append(l_open)
                    low_to_close_pct.append(l_close)
                    high_to_close_pct.append(h_close)
                except Exception as e:
                    print(f"Error processing data point {i} for {symbol} {period}: {e}")
                    # Add default values if calculation fails
                    high_to_open_pct.append(0)
                    low_to_open_pct.append(0)
                    low_to_close_pct.append(0)
                    high_to_close_pct.append(0)
            
            # Find max/min values safely from scalar lists
            try:
                max_high = max(highs) if highs else 0
                min_low = min(lows) if lows else 0
            except Exception as e:
                print(f"Error finding max/min values for {symbol} {period}: {e}")
                max_high = 0
                min_low = 0
        
        # Calculate percentage changes from current price
        pct_change_to_max = ((max_high - current_price) / current_price) * 100 if current_price > 0 and isinstance(max_high, (int, float)) else 0
        pct_change_to_min = ((min_low - current_price) / current_price) * 100 if current_price > 0 and isinstance(min_low, (int, float)) else 0
        
        # Calculate statistics in one go
        avg_high_pct = sum(high_to_open_pct) / len(high_to_open_pct) if high_to_open_pct else 0
        max_high_pct = max(high_to_open_pct) if high_to_open_pct else 0
        min_high_pct = min(high_to_open_pct) if high_to_open_pct else 0
        
        avg_low_pct = sum(low_to_open_pct) / len(low_to_open_pct) if low_to_open_pct else 0
        max_low_pct = max(low_to_open_pct) if low_to_open_pct else 0
        min_low_pct = min(low_to_open_pct) if low_to_open_pct else 0
        
        # This section was moved down, so we can remove it here
        
        # Calculate statistics with error handling
        try:
            avg_high_pct = sum(high_to_open_pct) / len(high_to_open_pct) if high_to_open_pct else 0
            max_high_pct = max(high_to_open_pct) if high_to_open_pct else 0
            min_high_pct = min(high_to_open_pct) if high_to_open_pct else 0
            
            avg_low_pct = sum(low_to_open_pct) / len(low_to_open_pct) if low_to_open_pct else 0
            max_low_pct = max(low_to_open_pct) if low_to_open_pct else 0
            min_low_pct = min(low_to_open_pct) if low_to_open_pct else 0
        except Exception as e:
            print(f"Error calculating statistics for {symbol} {period}: {e}")
            avg_high_pct = 0
            max_high_pct = 0
            min_high_pct = 0
            avg_low_pct = 0
            max_low_pct = 0
            min_low_pct = 0
        
        # Create lists for repeated values with correct length
        list_length = len(date_strings)
        max_high_list = [max_high] * list_length if list_length > 0 else []
        max_low_list = [max(lows) if lows else 0] * list_length if list_length > 0 else []
        min_low_list = [min_low] * list_length if list_length > 0 else []
        current_price_list = [current_price] * list_length if list_length > 0 else []
        pct_change_to_max_list = [pct_change_to_max] * list_length if list_length > 0 else []
        pct_change_to_min_list = [pct_change_to_min] * list_length if list_length > 0 else []
            
        # Store all data at once with proper types for JSON serialization
        stock_data[period] = {
            'Date': date_strings,
            'Open': opens,  # Already validated scalar values
            'High': highs,  # Already validated scalar values
            'Low': lows,    # Already validated scalar values
            'Close': closes, # Already validated scalar values
            'High to Open %': high_to_open_pct,
            'Low to Open %': low_to_open_pct,
            'Low to Close %': low_to_close_pct,
            'High to Close %': high_to_close_pct,
            'Max High': max_high_list,
            'Max Low': max_low_list,
            'Min Low': min_low_list,
            'Current Price': current_price_list,
            '% Change from Highest Price to Current': pct_change_to_max_list,
            '% Change from Lowest Price to Current': pct_change_to_min_list,
            'Avg High % Change': avg_high_pct,
            'Max High % Change': max_high_pct,
            'Min High % Change': min_high_pct,
            'Avg Low % Change': avg_low_pct,
            'Max Low % Change': max_low_pct,
            'Min Low % Change': min_low_pct
        }
    
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
        # Get the symbol(s) from the form and split by commas
        symbols_input = request.form['symbol']
        symbols = [s.strip().upper() for s in symbols_input.split(',') if s.strip()]
        
        # Get price from form
        try:
            stock_price = float(request.form['price'])
        except ValueError:
            stock_price = 0.0  # Default to 0 if invalid price
        
        # Track success/failure for each symbol
        results = []
        
        try:
            with app.app_context():
                # Process each symbol
                for symbol in symbols:
                    if not symbol:  # Skip empty symbols
                        continue
                        
                    try:
                        print(f"Processing symbol: {symbol}")
                        existing_stock = TrackedStock.query.filter_by(symbol=symbol).first()
                        
                        if existing_stock:
                            # Update existing stock
                            existing_stock.price = stock_price
                            # Update the data as well
                            existing_stock.data = track_stock(symbol)
                            results.append(f"Updated {symbol}")
                        else:
                            # Track new stock and get data
                            stock_data = track_stock(symbol)
                            if stock_data:
                                new_stock = TrackedStock(symbol=symbol, price=stock_price, data=stock_data)
                                db.session.add(new_stock)
                                results.append(f"Added {symbol}")
                    except Exception as e:
                        error_msg = f"Error tracking {symbol}: {str(e)}"
                        print(error_msg)
                        results.append(error_msg)
                
                # Commit all changes at once after processing all symbols
                db.session.commit()
            
            # Get all stocks to display
            with app.app_context():
                all_stocks = TrackedStock.query.all()
            
            # Generate summary message
            summary = ", ".join(results)
            return render_template('trackedstocks.html', tracked_stocks=all_stocks, 
                                  period=time_periods.keys(), 
                                  message=f"Processed stocks: {summary}")
        except Exception as e:
            print(f"Error tracking stocks: {e}")
            # Continue to show existing stocks even if adding new ones fails
            with app.app_context():
                all_stocks = TrackedStock.query.all()
            return render_template('trackedstocks.html', tracked_stocks=all_stocks, 
                                  period=time_periods.keys(), 
                                  error=f"Error tracking stocks: {e}")
    else:
        # Handle GET request
        with app.app_context():
            all_stocks = TrackedStock.query.all()
            tracked_symbols = [stock.symbol for stock in all_stocks]
            print(f"Currently tracked symbols: {tracked_symbols}")
      
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