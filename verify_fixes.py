import utils
import json

def test_fixes():
    print("Testing Translation...")
    text = "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide."
    translated = utils.translate_text(text)
    print(f"Original: {text[:50]}...")
    print(f"Translated: {translated[:50]}...")
    
    print("\nTesting News Fetching (AAPL)...")
    news = utils.get_news("AAPL")
    print(f"News count: {len(news)}")
    if news:
        print("First news item:", json.dumps(news[0], indent=2, ensure_ascii=False))
        
    print("\nTesting News Fetching (005930.KS)...")
    news_kr = utils.get_news("005930.KS")
    print(f"News count: {len(news_kr)}")
    if news_kr:
        print("First news item:", json.dumps(news_kr[0], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_fixes()
