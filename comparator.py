# Stock Comparison Module
# Compares two stocks and returns their data for analysis

import pandas as pd
import numpy as np

# These functions will be imported from other modules
# from data_fetcher import fetch_history
# from predictor import get_prediction
# from news_analyzer import get_sentiment


def get_comparison_data(ticker_a, ticker_b):
    """
    Compare two stocks by fetching their data.
    
    Args:
        ticker_a: First stock ticker (e.g., 'AAPL')
        ticker_b: Second stock ticker (e.g., 'MSFT')
    
    Returns:
        Dictionary with data for both stocks
    """
    
    # Check if tickers are valid
    if not ticker_a or not ticker_b:
        return None
    
    ticker_a = ticker_a.upper()
    ticker_b = ticker_b.upper()
    
    # Get data for first stock
    data_a = get_stock_data(ticker_a)
    
    # Get data for second stock
    data_b = get_stock_data(ticker_b)
    
    # If no data for both stocks, return None
    if data_a is None and data_b is None:
        return None
    
    # Return comparison result
    result = {
        ticker_a: data_a,
        ticker_b: data_b
    }
    
    return result


def get_stock_data(ticker):
    """
    Get all comparison data for a single stock.
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        Dictionary with stock data or None if error
    """
    
    stock_data = {}
    
    # Get current price
    try:
        history = fetch_history(ticker)
        if history is not None and len(history) > 0:
            current_price = history['Close'].iloc[-1]
            stock_data['current_price'] = float(current_price)
        else:
            stock_data['current_price'] = None
    except:
        print(f"Error getting current price for {ticker}")
        stock_data['current_price'] = None
    
    # Get 30 day history
    try:
        history = fetch_history(ticker)
        if history is not None and len(history) > 0:
            prices = history['Close'].tail(30).tolist()
            stock_data['historical_prices_30d'] = prices
        else:
            stock_data['historical_prices_30d'] = None
    except:
        print(f"Error getting 30 day history for {ticker}")
        stock_data['historical_prices_30d'] = None
    
    # Get 7 day prediction
    try:
        pred = get_prediction(ticker)
        if pred is not None:
            future_preds = pred.get('future_preds')
            if future_preds is not None:
                pred_list = future_preds.tolist() if isinstance(future_preds, np.ndarray) else list(future_preds)
                stock_data['predicted_price_7d'] = pred_list[:7]
            else:
                stock_data['predicted_price_7d'] = None
        else:
            stock_data['predicted_price_7d'] = None
    except:
        print(f"Error getting prediction for {ticker}")
        stock_data['predicted_price_7d'] = None
    
    # Get sentiment score
    try:
        sentiment = get_sentiment(ticker)
        if sentiment is not None:
            stock_data['sentiment_score'] = float(sentiment)
        else:
            stock_data['sentiment_score'] = None
    except:
        print(f"Error getting sentiment for {ticker}")
        stock_data['sentiment_score'] = None
    
    # Get backtest MSE
    try:
        pred = get_prediction(ticker)
        if pred is not None:
            mse = pred.get('backtest_mse')
            if mse is not None:
                stock_data['backtest_mse'] = float(mse)
            else:
                stock_data['backtest_mse'] = None
        else:
            stock_data['backtest_mse'] = None
    except:
        print(f"Error getting backtest MSE for {ticker}")
        stock_data['backtest_mse'] = None
    
    return stock_data


# Mock function placeholders - replace with real imports
def fetch_history(ticker):
    raise NotImplementedError("Import from data_fetcher")

def get_prediction(ticker):
    raise NotImplementedError("Import from predictor")

def get_sentiment(ticker):
    raise NotImplementedError("Import from news_analyzer")
