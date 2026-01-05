import yfinance as yf
import json

def check_keys():
    try:
        ticker = yf.Ticker("AAPL")
        news = ticker.news
        if news:
            print("Keys:", list(news[0].keys()))
            print("Content:", json.dumps(news[0]['content'], indent=2))
    except Exception as e:
        print(e)

if __name__ == "__main__":
    check_keys()
