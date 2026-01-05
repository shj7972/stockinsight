import utils
import traceback

def test_ticker(ticker):
    print(f"Testing {ticker}...")
    try:
        print("Fetching data...")
        history, info = utils.get_stock_data(ticker)
        print("Data fetched.")
        
        print("Fetching news...")
        news = utils.get_news(ticker)
        print("News fetched.")
        
        print("Calculating metrics...")
        metrics = utils.calculate_metrics(history)
        print("Metrics calculated.")
        
        print("Analyzing sentiment...")
        sentiment, details = utils.analyze_sentiment(news)
        print("Sentiment analyzed.")
        
        print("Generating advice...")
        verdict, advice = utils.generate_advice(metrics, sentiment)
        print("Advice generated.")
        
        print(f"Success for {ticker}")
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    test_ticker("AAPL")
    test_ticker("005930.KS")
