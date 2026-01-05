import yfinance as yf
import json

def check_news(ticker_symbol):
    print(f"Checking news for {ticker_symbol}...")
    try:
        ticker = yf.Ticker(ticker_symbol)
        news = ticker.news
        print(f"News count: {len(news)}")
        if len(news) > 0:
            print("First news item keys:", news[0].keys())
            print("First news item sample:", json.dumps(news[0], indent=2))
        else:
            print("No news found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_news("AAPL")
    check_news("005930.KS")
