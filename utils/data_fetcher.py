import yfinance as yf
import pandas as pd
import numpy as np

def fetch_stock_data(stock_symbol, interval="1wk"):
    stock = yf.Ticker(stock_symbol)
    df = stock.history(period="max", interval=interval)

    if not df.empty:
        df.index = df.index.tz_localize(None)
        df = df[df.index >= (pd.Timestamp.now() - pd.DateOffset(years=10))]

    return df

def get_stock_suggestions(query):
    query = query.upper()
    suggestions = []

    try:
        search_results = yf.Ticker(query)
        if search_results.history(period="1d").empty is False:
            return [query]
    except:
        pass

    return suggestions

def fetch_index_regression(index_symbol):
    df = fetch_stock_data(index_symbol, "1wk")

    if df is not None and not df.empty:
        prices = df["Close"].dropna()
        x = np.arange(len(prices))
        coef = np.polyfit(x, prices.values, 1)
        regression_line = np.poly1d(coef)(x)
        return pd.Series(regression_line, index=df.index)

    return None
