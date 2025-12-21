import yfinance as yf
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from deep_translator import GoogleTranslator

def translate_text(text, target_lang='ko'):
    """Translates text to target language."""
    try:
        if not text:
            return ""
        translator = GoogleTranslator(source='auto', target=target_lang)
        return translator.translate(text)
    except Exception as e:
        return text

def get_index_data(ticker_symbol):
    """Fetches index data for major indices."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        history = ticker.history(period="2d")
        if history is None or history.empty:
            return None, None, None
        
        current_price = history['Close'].iloc[-1]
        prev_price = history['Close'].iloc[-2] if len(history) > 1 else current_price
        change = current_price - prev_price
        change_pct = (change / prev_price * 100) if prev_price != 0 else 0
        
        return current_price, change, change_pct
    except Exception as e:
        return None, None, None

def get_stock_data(ticker_symbol):
    """Fetches stock history and info."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        history = ticker.history(period="1y")
        info = ticker.info
        return history, info
    except Exception as e:
        return None, None

def get_news(ticker_symbol):
    """Fetches news for a given ticker."""
    try:
        ticker = yf.Ticker(ticker_symbol)
        news = ticker.news
        
        if not news:
            return []
        
        # Handle new yfinance news structure
        processed_news = []
        for item in news:
            try:
                title = None
                link = None
                publisher = 'Unknown'
                
                # Try to extract title from various possible locations
                if 'title' in item:
                    title = item['title']
                elif 'content' in item and isinstance(item['content'], dict):
                    title = item['content'].get('title')
                
                # Try to extract link from various possible locations
                if 'link' in item:
                    link = item['link']
                elif 'url' in item:
                    link = item['url']
                elif 'content' in item and isinstance(item['content'], dict):
                    if 'clickThroughUrl' in item['content']:
                        if isinstance(item['content']['clickThroughUrl'], dict):
                            link = item['content']['clickThroughUrl'].get('url')
                        elif isinstance(item['content']['clickThroughUrl'], str):
                            link = item['content']['clickThroughUrl']
                
                # Try to extract publisher from various possible locations
                if 'publisher' in item:
                    if isinstance(item['publisher'], dict):
                        publisher = item['publisher'].get('displayName', 'Unknown')
                    elif isinstance(item['publisher'], str):
                        publisher = item['publisher']
                elif 'provider' in item:
                    if isinstance(item['provider'], dict):
                        publisher = item['provider'].get('displayName', 'Unknown')
                    elif isinstance(item['provider'], str):
                        publisher = item['provider']
                elif 'content' in item and isinstance(item['content'], dict):
                    if 'provider' in item['content']:
                        if isinstance(item['content']['provider'], dict):
                            publisher = item['content']['provider'].get('displayName', 'Unknown')
                        elif isinstance(item['content']['provider'], str):
                            publisher = item['content']['provider']
                
                # Only add if we have at least a title
                if title:
                    processed_news.append({
                        'title': title,
                        'link': link or '#',
                        'publisher': publisher
                    })
            except Exception as e:
                # Skip items that can't be processed
                continue
                
        return processed_news
    except Exception as e:
        # Return empty list on any error
        return []

def calculate_metrics(df):
    """Calculates technical indicators."""
    if df is None or df.empty:
        return None
    
    # Work on a copy to avoid modifying the original dataframe
    df = df.copy()
    
    # Ensure column names are lowercase
    df.columns = [c.lower() for c in df.columns]
    
    # SMA
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    
    # RSI (14)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    rs = gain / loss
    df['rsi_14'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp12 = df['close'].ewm(span=12, adjust=False).mean()
    exp26 = df['close'].ewm(span=26, adjust=False).mean()
    macd = exp12 - exp26
    signal = macd.ewm(span=9, adjust=False).mean()
    
    df['macds'] = macd - signal # Using histogram/difference as signal strength indicator or just store signal?
    # Wait, the original code used 'macds' which usually means MACD Signal line in stockstats? 
    # Let's check stockstats docs or assumption. 
    # stockstats 'macds' is the MACD Signal line.
    # stockstats 'macd' is the MACD line.
    # stockstats 'macdh' is the MACD Histogram.
    
    # My generate_advice uses 'macds'.
    # "if macd > 0:" where macd = last_row['macds']
    # "MACD가 상승 추세를 보이고 있습니다."
    
    # If I want to check trend, I should probably compare MACD line vs Signal line (Histogram).
    # But if I stick to previous logic:
    # "if macd > 0" -> implies MACD Signal > 0? Or MACD > 0?
    # Let's assume 'macds' meant MACD Signal line.
    
    df['macds'] = macd # Let's just use the MACD line itself for simplicity if the logic was "MACD > 0" (Bullish trend above zero line)
    # Or if the logic was "MACD > Signal" (Bullish crossover).
    
    # Let's look at generate_advice again.
    # if macd > 0: advice.append("MACD가 상승 추세를 보이고 있습니다.")
    # This usually means MACD histogram > 0 (MACD > Signal) OR MACD line > 0.
    # Given the text "MACD가 상승 추세를 보이고 있습니다", it likely means MACD is increasing or positive.
    # Let's use MACD Histogram (MACD - Signal) as 'macds' for "trend strength" or just MACD line.
    
    # To be safe and useful:
    # Let's calculate MACD and Signal.
    # And let 'macds' be the MACD line (value).
    # Because "MACD > 0" is a standard check for bullish trend.
    
    df['macds'] = macd
    
    return df

def analyze_sentiment(news_items):
    """Analyzes sentiment of news headlines."""
    if not news_items or len(news_items) == 0:
        return 0.0, []
    
    try:
        analyzer = SentimentIntensityAnalyzer()
        sentiments = []
        
        for item in news_items:
            try:
                title = item.get('title', '')
                if not title or not title.strip():
                    continue
                    
                score = analyzer.polarity_scores(title)
                sentiments.append({
                    'title': title,
                    'link': item.get('link', '#'),
                    'publisher': item.get('publisher', 'Unknown'),
                    'compound': score['compound'],
                    'pos': score['pos'],
                    'neu': score['neu'],
                    'neg': score['neg']
                })
            except Exception as e:
                # Skip items that can't be analyzed
                continue
        
        if not sentiments:
            return 0.0, []
            
        avg_sentiment = sum(s['compound'] for s in sentiments) / len(sentiments)
        return avg_sentiment, sentiments
    except Exception as e:
        return 0.0, []

def generate_advice(metrics_df, sentiment_score):
    """Generates investment advice based on technicals and sentiment."""
    if metrics_df is None or metrics_df.empty:
        return "데이터 부족으로 조언을 생성할 수 없습니다."
        
    last_row = metrics_df.iloc[-1]
    price = last_row['close']
    rsi = last_row['rsi_14']
    macd = last_row['macds']
    sma20 = last_row['sma_20']
    sma50 = last_row['sma_50']
    
    advice = []
    score = 0
    
    # Technical Analysis
    if rsi < 30:
        advice.append("📉 RSI가 30 미만으로 과매도 구간입니다. 반등 가능성이 있습니다.")
        score += 1
    elif rsi > 70:
        advice.append("📈 RSI가 70 초과로 과매수 구간입니다. 조정 가능성이 있습니다.")
        score -= 1
        
    if macd > 0:
        advice.append("📊 MACD가 상승 추세를 보이고 있습니다.")
        score += 0.5
    else:
        advice.append("📊 MACD가 하락 추세를 보이고 있습니다.")
        score -= 0.5
        
    if price > sma20:
        advice.append("💹 주가가 20일 이동평균선 위에 있습니다. 단기 상승 추세입니다.")
        score += 0.5
    else:
        advice.append("💹 주가가 20일 이동평균선 아래에 있습니다. 단기 하락 추세입니다.")
        score -= 0.5
        
    # Sentiment Analysis
    if sentiment_score > 0.05:
        advice.append("📰 뉴스 감성 분석 결과 긍정적입니다.")
        score += 1
    elif sentiment_score < -0.05:
        advice.append("📰 뉴스 감성 분석 결과 부정적입니다.")
        score -= 1
    else:
        advice.append("📰 뉴스 감성 분석 결과 중립적입니다.")
        
    # Final Verdict
    if score >= 2:
        verdict = "강력 매수 (Strong Buy) 🚀"
    elif score >= 0.5:
        verdict = "매수 (Buy) ✅"
    elif score > -0.5:
        verdict = "보류 (Hold) ✋"
    elif score > -2:
        verdict = "매도 (Sell) ❌"
    else:
        verdict = "강력 매도 (Strong Sell) 📉"
        
    return verdict, advice
