import yfinance as yf
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from deep_translator import GoogleTranslator
import requests
from bs4 import BeautifulSoup

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

    except Exception as e:
        return None, None

def get_naver_news(ticker_code):
    """Crawls news from Naver Finance for Korean stocks."""
    try:
        # Remove suffix (e.g. 005930.KS -> 005930)
        code = ticker_code.split('.')[0]
        url = f"https://finance.naver.com/item/news_news.naver?code={code}&page=1"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': f'https://finance.naver.com/item/main.naver?code={code}'
        }
        
        response = requests.get(url, headers=headers)
        # response.encoding = 'euc-kr' # Naver usually uses euc-kr but sometimes it varies
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_items = []
        
        # Select news tables (titles usually in 'title' class or link)
        # Check if we got anything
        articles = soup.select('td.title > a')
        if not articles:
             # Try fallback structure or logging
             print(f"No articles found for {code}. Status: {response.status_code}")

        providers = soup.select('td.info') # Press name
        
        for i, article in enumerate(articles):
            if i >= 10: # Limit to 10 items
                break
                
            title = article.get_text().strip()
            link = "https://finance.naver.com" + article['href']
            
            # Provider parsing might not align perfectly with select list if structure varies,
            # but usually it's parallel.
            provider = "Naver Finance"
            if i < len(providers):
                provider = providers[i].get_text().strip()
            
            news_items.append({
                'title': title,
                'link': link,
                'publisher': provider
            })
            
        return news_items
        
    except Exception as e:
        print(f"Naver News Error: {e}")
        return []

def get_news(ticker_symbol):
    """Fetches news for a given ticker."""
    
    # Check if Korean stock
    if ticker_symbol.endswith('.KS') or ticker_symbol.endswith('.KQ'):
        return get_naver_news(ticker_symbol)

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
                
                # Setup Translator
                # Check if text is likely Korean (simple heuristic)
                is_korean = any(ord(char) >= 0xAC00 and ord(char) <= 0xD7A3 for char in title)
                
                text_to_analyze = title
                if is_korean:
                    try:
                        # Translate to English for VADER
                        translator = GoogleTranslator(source='auto', target='en')
                        text_to_analyze = translator.translate(title)
                    except:
                        pass # Fallback to original text if translation fails
                    
                score = analyzer.polarity_scores(text_to_analyze)
                sentiments.append({
                    'title': title, # Keep original title for display
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

def format_market_cap(value, ticker):
    """Formats market cap to readable string (e.g. 100조, $2B)."""
    if not value:
        return "N/A"
    
    try:
        value = float(value)
    except:
        return str(value)

    is_krw = ticker.endswith('.KS') or ticker.endswith('.KQ')
    currency = "₩" if is_krw else "$"
    
    if is_krw:
        # Korean Won (Unit: Jo, Eok)
        if value >= 1000000000000: # 1 Jo
            return f"{currency}{value/1000000000000:.2f}조"
        elif value >= 100000000: # 1 Eok
            return f"{currency}{value/100000000:.0f}억"
        else:
            return f"{currency}{value:,.0f}"
    else:
        # USD (Unit: T, B, M)
        if value >= 1000000000000: # Trillion
            return f"{currency}{value/1000000000000:.2f}T"
        elif value >= 1000000000: # Billion
            return f"{currency}{value/1000000000:.2f}B"
        elif value >= 1000000: # Million
            return f"{currency}{value/1000000:.2f}M"
        else:
             return f"{currency}{value:,.0f}"

def format_price_short(value, ticker):
    """Formats price to be short (e.g. 1.5만, $150)."""
    if not value:
        return "N/A"
    
    try:
        value = float(value)
    except:
        return str(value)

    is_krw = ticker.endswith('.KS') or ticker.endswith('.KQ')
    currency = "₩" if is_krw else "$"
    
    if is_krw:
        # Korean Won (Shorten >= 10,000)
        if value >= 10000: 
            # Example: 15300 -> 15,300
            return f"{value:,.0f}"
        else:
            return f"{value:,.0f}"
    else:
        # USD (Standard 2 decimals)
        return f"{currency}{value:,.2f}"
