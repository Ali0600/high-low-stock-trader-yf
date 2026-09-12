# high-low-stock-trader-yf

A Flask dashboard that shows how far a stock moves from its open, high and low each day, over the last few months.

You enter a ticker. The app downloads 3 months of daily open/high/low/close prices from Yahoo Finance (via `yfinance`) and gets the current price. It then works out daily percentage moves over 4 windows: the last 5, 30, 60 and 90 trading days. For each window it also reports the average, biggest and smallest moves. It shows how far the current price sits from the window's highest high and lowest low. Tickers you choose to track are saved in a SQLite database (`stocks.db`) with their computed data, and a second page lists them all.

## Run it

There is no `requirements.txt`. Install the packages `app.py` imports, then start the app:

```bash
pip install flask flask-sqlalchemy flask-migrate yfinance pandas numpy curl_cffi
python app.py
```

The app runs in debug mode on Flask's default port, http://localhost:5000. On every start it drops and recreates the database tables, so tracked tickers do not survive a restart. Requests to Yahoo Finance go through a `curl_cffi` session that looks like Chrome, with a 20-second timeout.

Pages:

- `/` — home page with links to the two tools.
- `/stock-tracker` — enter one ticker and see its tables.
- `/tracked-stocks` — enter one or more tickers (comma-separated) and a price. The app saves them and shows every tracked ticker's tables.

Known issue: `track_stock` in `app.py` and `templates/index.html` still refer to a `10d` window that is commented out of `time_periods`. Until that line is restored or the references removed, computing a ticker raises `KeyError: '10d'`.

## Layout

- `app.py` — the whole app: the `TrackedStock` model, the `track_stock` calculation and 3 routes.
- `templates/homepage.html` — landing page.
- `templates/index.html` — the single-ticker tracker page.
- `templates/trackedstocks.html` — the tracked-tickers dashboard.
- `package.json` — declares an npm `yfinance` package. Nothing in the app uses it; the app is Python only.
- `.gitignore` — keeps `*.db`, `migrations/` and `instance/` out of git.

## Experience Gained

- Computed 4 per-day percentage metrics (high-to-open, low-to-open, low-to-close, high-to-close) and 2 current-price metrics over 4 windows (5, 30, 60 and 90 trading days) from 3 months of Yahoo Finance data.
- Summarised each window with 6 statistics (average, max and min of the high and low moves) and stored the results as JSON in SQLite through SQLAlchemy.
- Served it as a Flask app with 3 routes and a 20-second timeout on every market-data request.
