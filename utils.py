import yfinance as yf
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from deep_translator import GoogleTranslator
import requests
from bs4 import BeautifulSoup
import random

# Banner Configuration
BANNERS = [
    {
        "url": "https://promptgenie.kr",
        "img": "/static/promptgenie_banner_234x60.png",
        "title": "PromptGenie - AI 프롬프트 라이브러리",
        "alt": "PromptGenie 배너"
    },
    {
        "url": "https://unsedam.kr",
        "img": "https://unsedam.kr/static/images/banner_link_234x60.png",
        "title": "운세담 - 2026 무료 토정비결 & AI 사주",
        "alt": "운세담 배너"
    },
    {
        "url": "https://vibecheck.page",
        "img": "https://vibecheck.page/images/vibecheck_banner_234x60.png",
        "title": "VibeCheck - 나를 찾는 트렌디한 심리테스트",
        "alt": "VibeCheck 배너"
    },
    {
        "url": "https://irumlab.com",
        "img": "https://irumlab.com/banner_link_234x60.png",
        "title": "이룸랩 - 무료 셀프 작명, 영어 닉네임, 브랜드 네이밍",
        "alt": "이룸랩 배너"
    }
]

def get_random_banners(count=3):
    """Returns a random selection of banners."""
    return random.sample(BANNERS, min(len(BANNERS), count))

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


# --- Caching Logic (TTL 5 mins) ---
import time
from functools import wraps

CACHE_TTL = 300  # 5 minutes
_memory_cache = {}

def ttl_cache(func):
    """Simple in-memory cache with time-to-live."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Helper to make args hashable (convert lists to tuples)
        def make_hashable(value):
            if isinstance(value, list):
                return tuple(make_hashable(v) for v in value)
            if isinstance(value, dict):
                return tuple(sorted((k, make_hashable(v)) for k, v in value.items()))
            return value

        # Create a key based on function name and hashable arguments
        hashable_args = tuple(make_hashable(a) for a in args)
        hashable_kwargs = tuple(sorted((k, make_hashable(v)) for k, v in kwargs.items()))
        
        key = (func.__name__, hashable_args, hashable_kwargs)
        
        current_time = time.time()
        
        # Check cache
        if key in _memory_cache:
            result, timestamp = _memory_cache[key]
            if current_time - timestamp < CACHE_TTL:
                return result
        
        # Call function
        result = func(*args, **kwargs)
        
        # Save to cache
        _memory_cache[key] = (result, current_time)
        return result
    return wrapper

# --- New Features: Sector & Sentiment Analysis ---

import praw

# Reddit API Credentials (User Provided)
REDDIT_CLIENT_ID = "RqwuvRs-4nsicsM46f86Vw"
REDDIT_CLIENT_SECRET = "uW6yIuz0IfSS5Ht-zVL-jyDkPKGeZQ"
REDDIT_USER_AGENT = "android:shj_app:v1.0.0 (by /u/shj)" 

@ttl_cache
def get_sector_performance():
    """Calculates 1-month Relative Strength (RS) vs SPY."""
    # Sector ETFs
    sectors = {
        "XLK": "Technology",
        "XLF": "Financials",
        "XLV": "Healthcare",
        "XLE": "Energy",
        "XLY": "Consumer Disc.",
        "XLP": "Consumer Staples",
        "XLI": "Industrials",
        "XLB": "Materials",
        "XLU": "Utilities",
        "XLRE": "Real Estate",
        "IYZ": "Telecom" # Proxy
    }
    
    performance_data = []
    
    try:
        # Fetch SPY first for baseline
        spy = yf.Ticker("SPY")
        spy_hist = spy.history(period="3mo")
        if spy_hist.empty:
            return []
            
        spy_close = spy_hist['Close']
        spy_1m_return = (spy_close.iloc[-1] / spy_close.iloc[-20] - 1) * 100
        spy_3m_return = (spy_close.iloc[-1] / spy_close.iloc[0] - 1) * 100
        
        # Fetch Sector Data
        tickers = list(sectors.keys())
        data = yf.download(" ".join(tickers), period="3mo", progress="False")['Close']
        
        for ticker, name in sectors.items():
            if ticker not in data:
                continue
                
            series = data[ticker]
            if len(series) < 20: 
                continue
            
            curr = series.iloc[-1]
            prev_1m = series.iloc[-20]
            prev_3m = series.iloc[0]
            
            pct_1m = (curr / prev_1m - 1) * 100
            pct_3m = (curr / prev_3m - 1) * 100
            
            # Relative Strength (RS) vs SPY
            rs_1m = pct_1m - spy_1m_return
            
            performance_data.append({
                'ticker': ticker,
                'name': name,
                'return_1m': pct_1m,
                'return_3m': pct_3m,
                'rs_1m': rs_1m, # Relative Strength
                'current_price': curr
            })
            
        # Sort by 1M RS
        performance_data.sort(key=lambda x: x['rs_1m'], reverse=True)
            
    except Exception as e:
        print(f"Sector Performance Error: {e}")
        
    return performance_data

def get_cycle_recommendation(cycle_type):
    """Returns recommended sectors based on economic cycle."""
    # Simple mapping logic
    recommendations = {
        "rate_cut": {
            "title": "금리 인하기 (Rate Cut)",
            "desc": "유동성이 공급되며 성장주와 소비재가 유리합니다.",
            "bullish": ["XLK (테크)", "XLY (임의소비재)", "XLRE (부동산)"],
            "bearish": ["XLF (금융)"]
        },
        "rate_hike": {
            "title": "금리 인상기 (Rate Hike)",
            "desc": "은행의 이자 마진이 증가하여 금융주가 유리합니다.",
            "bullish": ["XLF (금융)", "XLI (산업재)"],
            "bearish": ["XLK (테크)", "XLRE (부동산)"]
        },
        "inflation": {
            "title": "인플레이션 (Inflation)",
            "desc": "물가 상승을 가격에 전가할 수 있는 원자재 관련주가 유리합니다.",
            "bullish": ["XLE (에너지)", "XLB (소재)", "GLD (금)"],
            "bearish": ["XLY (임의소비재)"]
        },
        "recession": {
            "title": "경기 침체 (Recession)",
            "desc": "경기가 나빠져도 소비를 줄이기 힘든 필수 소비재가 방어적입니다.",
            "bullish": ["XLP (필수소비재)", "XLV (헬스케어)", "XLU (유틸리티)"],
            "bearish": ["XLI (산업재)", "XLE (에너지)"]
        },
        "recovery": {
            "title": "경기 회복 (Recovery)",
            "desc": "경기가 바닥을 찍고 올라올 때 민감하게 반응하는 섹터입니다.",
            "bullish": ["IWM (중소형주)", "XLI (산업재)", "XLY (임의소비재)"],
            "bearish": ["XLU (유틸리티)"]
        }
    }
    return recommendations.get(cycle_type, recommendations['rate_cut'])

def get_reddit_sentiment(ticker):
    """Fetches Reddit posts and calculates sentiment."""
    posts = []
    avg_score = 0
    
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
        
        # Search specifically in WSB and Stocks
        query = f"{ticker}"
        # Fetch top recent posts
        subreddit = reddit.subreddit("wallstreetbets+stocks+investing")
        search_results = subreddit.search(query, sort='new', time_filter='month', limit=10)
        
        analyzer = SentimentIntensityAnalyzer()
        scores = []
        
        for post in search_results:
            # Simple filter to ensure ticker is actually relevant (basic)
            if ticker not in post.title.upper() and ticker not in post.selftext.upper():
                continue
                
            vs = analyzer.polarity_scores(post.title)
            
            posts.append({
                'title': post.title,
                'url': post.url,
                'score': post.score, # Upvotes
                'sentiment': vs['compound'],
                'created': datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d')
            })
            scores.append(vs['compound'])
            
            if len(posts) >= 5:
                break
                
        if scores:
            avg_score = sum(scores) / len(scores)
            
    except Exception as e:
        print(f"Reddit API Error: {e}")
        return 0, []
        
    return avg_score, posts

@ttl_cache
def get_meme_candidates():
    """
    Identifies meme stock candidates based on:
    1. High Volatility (ATR/Price)
    2. Volume Spike (Vol / AvgVol)
    3. Reddit Sentiment & mentions
    """
    candidates = ["CVNA", "UPST", "GME", "AMC", "PLTR", "SOFI", "MARA", "COIN", "TSLA", "NVDA"]
    results = []
    
    try:
        data = yf.download(" ".join(candidates), period="5d", progress=False)
        # Handle MultiIndex
        close = data['Close']
        volume = data['Volume']
        
        for ticker in candidates:
            if ticker not in close:
                continue
            
            # 1. Volatility (Range)
            high_price = close[ticker].max()
            low_price = close[ticker].min()
            volatility = (high_price - low_price) / low_price * 100
            
            # 2. Volume Spike
            avg_vol = volume[ticker].mean()
            curr_vol = volume[ticker].iloc[-1]
            vol_ratio = curr_vol / avg_vol if avg_vol > 0 else 1
            
            # 3. Recent Performance
            start_price = close[ticker].iloc[0]
            end_price = close[ticker].iloc[-1]
            pct_change = (end_price - start_price) / start_price * 100
            
            sentiment_score, _ = get_reddit_sentiment(ticker)
            
            # Score algorithm
            meme_score = (volatility * 0.5) + (vol_ratio * 10) + (abs(pct_change) * 0.5)
            
            results.append({
                'ticker': ticker,
                'price': end_price,
                'change_pct': pct_change,
                'volatility': volatility,
                'volume_ratio': vol_ratio,
                'meme_score': meme_score,
                'reddit_sentiment': sentiment_score
            })
            
        # Sort by Meme Score
        results.sort(key=lambda x: x['meme_score'], reverse=True)
            
    except Exception as e:
        print(f"Meme Candidate Error: {e}")
        
    return results

@ttl_cache
def get_sector_history_data():
    """Fetches history for sector trend chart."""
    sectors = ["XLK", "XLF", "XLV", "XLE", "XLY", "XLP", "XLI", "XLB", "XLU", "XLRE"]
    data_points = {}
    
    try:
        # Fetch all + SPY
        tickers = sectors + ["SPY"]
        hist = yf.download(" ".join(tickers), period="3mo", progress=False)['Close']
        
        # Calculate % Change from start based on RS
        # RS = Sector % Change - SPY % Change
        if 'SPY' not in hist:
            return None
            
        spy_pct = (hist['SPY'] / hist['SPY'].iloc[0] - 1) * 100
        
        df_rs = pd.DataFrame(index=hist.index)
        
        for s in sectors:
            if s in hist:
                s_pct = (hist[s] / hist[s].iloc[0] - 1) * 100
                df_rs[s] = s_pct - spy_pct
                
        # Downsample for chart (every 3rd day roughly) to reduce payload
        df_rs = df_rs.iloc[::2] 
        
        # Convert to simple Dict structure for frontend: { 'XLK': [{date, val}, ...], ... }
        for col in df_rs.columns:
            points = []
            for date, val in df_rs[col].items():
                points.append({
                    'x': date.strftime('%Y-%m-%d'),
                    'y': val
                })
            data_points[col] = points
            
    except Exception as e:
        print(f"Sector History Error: {e}")
        
    return data_points

@ttl_cache
def get_sector_top_stocks(cycle_bullish_sectors):
    """
    Returns top performing stocks within the recommended sectors.
    Hardcoded constituents for major sectors.
    """
    constituents = {
        "XLK": ["AAPL", "MSFT", "NVDA", "AVGO", "ADBE"],
        "XLF": ["JPM", "V", "MA", "BAC", "WFC"],
        "XLV": ["LLY", "UNH", "JNJ", "MRK", "ABBV"],
        "XLE": ["XOM", "CVX", "COP", "SLB", "EOG"],
        "XLY": ["AMZN", "TSLA", "HD", "MCD", "NKE"],
        "XLP": ["PG", "COST", "PEP", "KO", "WMT"],
        "XLI": ["GE", "CAT", "UNP", "HON", "BA"],
        "XLB": ["LIN", "SHW", "FCX", "APD", "NEM"],
        "XLU": ["NEE", "SO", "DUK", "CEG", "AEP"],
        "XLRE": ["PLD", "AMT", "EQIX", "PSA", "O"],
        "IWM": ["MSTR", "SMCI", "CAR", "CROX", "ELF"], # Random midcaps
        "GLD": ["NEM", "GOLD", "RGLD", "AEM", "KGC"] # Miners as proxy
    }
    
    top_picks = []
    
    # Identify target ETFs from the strings "XLK (Tech)" -> "XLK"
    targets = []
    for s_str in cycle_bullish_sectors:
        code = s_str.split(' ')[0]
        targets.append(code)
        
    # Gather candidates
    candidates = []
    for t in targets:
        candidates.extend(constituents.get(t, []))
        
    # Fetch data
    if not candidates:
        return []
        
    try:
        data = yf.download(" ".join(candidates), period="2d", progress=False)['Close']
        for ticker in candidates:
            if ticker not in data:
                continue
                
            series = data[ticker]
            if len(series) < 2:
                continue
                
            change_pct = (series.iloc[-1] / series.iloc[-2] - 1) * 100
            
            top_picks.append({
                'ticker': ticker,
                'price': series.iloc[-1],
                'change_pct': change_pct,
                'sector': next((k for k,v in constituents.items() if ticker in v), "Unknown")
            })
            
        # Sort by best performance today
        top_picks.sort(key=lambda x: x['change_pct'], reverse=True)
        return top_picks[:6] # Top 6
        
    except Exception as e:
        print(f"Top Stocks Error: {e}")
        return []

def get_keywords(text_list):
    """Extracts top keywords from a list of titles."""
    from collections import Counter
    import re
    
    words = []
    stopwords = ["THE", "AND", "TO", "OF", "A", "IN", "IS", "FOR", "ON", "WITH", "IT"]
    
    for text in text_list:
        # Clean
        clean = re.sub(r'[^a-zA-Z\s]', '', text).upper()
        tokens = clean.split()
        for t in tokens:
            if len(t) > 2 and t not in stopwords:
                words.append(t)
                
    count = Counter(words)
    return count.most_common(15)

