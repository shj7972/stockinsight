import pandas as pd
from stockstats import StockDataFrame
import yfinance as yf

def test_manual():
    print("Testing manual dataframe...")
    data = {
        'open': [10, 11, 12, 13, 14] * 10,
        'close': [11, 12, 13, 14, 15] * 10,
        'high': [12, 13, 14, 15, 16] * 10,
        'low': [9, 10, 11, 12, 13] * 10,
        'volume': [100, 100, 100, 100, 100] * 10
    }
    df = pd.DataFrame(data)
    try:
        stock = StockDataFrame.retype(df)
        print("SMA 2:", stock['sma_2'])
        print("Manual test passed.")
    except Exception as e:
        print(f"Manual test failed: {e}")

def test_yfinance():
    print("\nTesting yfinance dataframe...")
    try:
        ticker = yf.Ticker("AAPL")
        df = ticker.history(period="1mo")
        print("Columns:", df.columns)
        stock = StockDataFrame.retype(df.copy())
        print("SMA 5:", stock['sma_5'])
        print("yfinance test passed.")
    except Exception as e:
        print(f"yfinance test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_manual()
    test_yfinance()
