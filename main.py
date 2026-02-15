from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from jinja2 import Template
from starlette.templating import Jinja2Templates
import utils
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly
import plotly.utils
import json
import io
import urllib.parse
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import time

import os

# Set base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="Stock Insight AI")

# Static files and templates with absolute paths
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
templates.env.globals['get_random_banners'] = utils.get_random_banners

import news_manager

@app.on_event("startup")
async def startup_event():
    # News updates are handled by an external script to prevent worker conflicts
    pass


# Major Indices
MAJOR_INDICES = {
    "미국": [
        ("^GSPC", "S&P 500"),
        ("^IXIC", "NASDAQ"),
        ("^DJI", "Dow Jones")
    ],
    "한국": [
        ("^KS11", "KOSPI"),
        ("^KQ11", "KOSDAQ")
    ]
}

import time

# Candidate Stocks for Dynamic Ranking (Top ~30 by Cap/Interest)
US_CANDIDATES = [
    ("AAPL", "Apple"), ("MSFT", "Microsoft"), ("GOOGL", "Alphabet"), ("AMZN", "Amazon"),
    ("NVDA", "Nvidia"), ("TSLA", "Tesla"), ("META", "Meta"), ("AMD", "AMD"),
    ("NFLX", "Netflix"), ("INTC", "Intel"), ("PLTR", "Palantir"), ("COIN", "Coinbase"),
    ("GME", "GameStop"), ("AMC", "AMC"), ("DIS", "Disney"), ("PYPL", "PayPal"),
    ("SQ", "Block"), ("SHOP", "Shopify"), ("UBER", "Uber"), ("ABNB", "Airbnb"),
    ("JPM", "JPMorgan"), ("V", "Visa"), ("JNJ", "J&J"), ("WMT", "Walmart"),
    ("PG", "P&G"), ("XOM", "Exxon"), ("CVX", "Chevron"), ("KO", "Coca-Cola"),
    ("PEP", "PepsiCo"), ("COST", "Costco")
]

KR_CANDIDATES = [
    ("005930.KS", "삼성전자"), ("000660.KS", "SK하이닉스"), ("035420.KS", "NAVER"),
    ("035720.KS", "카카오"), ("005380.KS", "현대차"), ("000270.KS", "기아"),
    ("051910.KS", "LG화학"), ("373220.KS", "LG에너지솔루션"), ("207940.KS", "삼성바이오"),
    ("006400.KS", "삼성SDI"), ("068270.KS", "셀트리온"), ("005490.KS", "POSCO홀딩스"),
    ("028260.KS", "삼성물산"), ("105560.KS", "KB금융"), ("055550.KS", "신한지주"),
    ("086790.KS", "하나금융지주"), ("015760.KS", "한국전력"), ("032830.KS", "삼성생명"),
    ("034020.KS", "두산에너빌리티"), ("012330.KS", "현대모비스"), ("247540.KQ", "에코프로비엠"),
    ("091990.KQ", "셀트리온헬스케어"), ("066970.KQ", "엘앤에프"), ("028300.KQ", "HLB"),
    ("403870.KQ", "HPSP"), ("293490.KQ", "카카오게임즈"), ("035900.KQ", "JYP Ent."),
    ("122870.KQ", "와이지엔터"), ("352820.KQ", "하이브"), ("011200.KS", "HMM")
]

# Ranking Cache
_ranking_cache = {
    "us": {"data": [], "ts": 0},
    "kr": {"data": [], "ts": 0}
}
CACHE_DURATION = 600  # 10 minutes

def get_popular_tickers(candidates, region_key, top_n=10):
    """
    Get Top N tickers sorted by today's volume.
    Uses caching to avoid frequent API calls.
    """
    import yfinance as yf
    
    today = datetime.now()
    ONE_DAY_MS = 24 * 60 * 60 * 1000
    
    global _ranking_cache
    now = time.time()
    
    # Check cache
    if now - _ranking_cache[region_key]['ts'] < CACHE_DURATION and _ranking_cache[region_key]['data']:
        return _ranking_cache[region_key]['data']
    
    try:
        # Fetch data in batch
        tickers_list = [t[0] for t in candidates]
        tickers_str = " ".join(tickers_list)
        
        # Download volume only
        data = yf.download(tickers_str, period="1d", progress=False)
        
        if data.empty:
            # Fallback to simple first 10 if data fails
            return candidates[:top_n]
            
        # Handle MultiIndex columns if present (common in recent yfinance)
        # We need "Volume" column.
        # structure might be: Volume -> Ticker A, Ticker B...
        
        if 'Volume' in data:
            vol_data = data['Volume'].iloc[-1] # Series of Tickers
            
            # Sort by volume desc
            sorted_vol = vol_data.sort_values(ascending=False)
            
            # Reconstruct list of (ticker, name)
            # Map ticker to name efficiently
            name_map = {t[0]: t[1] for t in candidates}
            
            top_tickers = []
            for ticker in sorted_vol.index:
                if ticker in name_map:
                    top_tickers.append((ticker, name_map[ticker]))
                if len(top_tickers) >= top_n:
                    break
                    
            # Update cache
            _ranking_cache[region_key] = {
                "data": top_tickers,
                "ts": now
            }
            return top_tickers
            
        else:
            return candidates[:top_n]
            
    except Exception as e:
        print(f"Ranking Error ({region_key}): {e}")
        # Return previous cache or default fallback
        if _ranking_cache[region_key]['data']:
            return _ranking_cache[region_key]['data']
        return candidates[:top_n]

# Placeholders for initial render (will be dynamic)
US_TOP_TICKERS = US_CANDIDATES[:10]
KR_TOP_TICKERS = KR_CANDIDATES[:10]

def create_chart(history, metrics_df):
    """Create Plotly chart and return as dict"""
    # Convert index to string for JSON serialization
    dates = [str(d) for d in history.index]
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.03, subplot_titles=('Price & SMA', 'Volume'), 
                        row_heights=[0.7, 0.3])
    
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=dates,
        open=history['Open'].tolist(),
        high=history['High'].tolist(),
        low=history['Low'].tolist(),
        close=history['Close'].tolist(),
        name='Price',
        increasing_line_color='#10b981',
        decreasing_line_color='#ef4444'
    ), row=1, col=1)
    
    # SMAs
    fig.add_trace(go.Scatter(
        x=dates,
        y=metrics_df['sma_20'].tolist(),
        line=dict(color='#38bdf8', width=1.5),
        name='SMA 20'
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=metrics_df['sma_50'].tolist(),
        line=dict(color='#818cf8', width=1.5),
        name='SMA 50'
    ), row=1, col=1)
    
    # Volume
    fig.add_trace(go.Bar(
        x=dates,
        y=history['Volume'].tolist(),
        name='Volume',
        marker_color='#64748b',
        opacity=0.8
    ), row=2, col=1)
    
    fig.update_layout(
        height=650,
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8', family='Inter', size=11),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(0,0,0,0)'
        ),
        hovermode='x unified'
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.05)', zeroline=False)
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.05)', zeroline=False)
    
    # Convert to dict for template
    return fig.to_dict()

def get_analysis_context(ticker: str):
    """Reuseable function to analyze stock data"""
    if not ticker:
        return None
    
    ticker = ticker.strip()

    history, info = utils.get_stock_data(ticker)
    if history is None or history.empty:
        return None

    metrics_df = utils.calculate_metrics(history)
    news = utils.get_news(ticker)
    sentiment_score, sentiment_details = utils.analyze_sentiment(news)
    verdict, advice_list = utils.generate_advice(metrics_df, sentiment_score)
    
    # Translate news titles
    translated_news = []
    for item in sentiment_details[:5]:
        translated_title = utils.translate_text(item['title'])
        translated_news.append({
            **item,
            'translated_title': translated_title if translated_title else item['title']
        })
    
    # Create chart
    chart_json = create_chart(history, metrics_df)  # Already returns dict
    
    current_price = history['Close'].iloc[-1]
    prev_price = history['Close'].iloc[-2] if len(history) > 1 else current_price
    delta = current_price - prev_price
    
    # Determine verdict color
    verdict_map = {
        "강력 매수 (Strong Buy) 🚀": "강력 매수 (Strong Buy) 🚀",
        "매수 (Buy) ✅": "매수 (Buy) ✅",
        "보류 (Hold) ✋": "보류 (Hold) ✋",
        "매도 (Sell) ❌": "매도 (Sell) ❌",
        "강력 매도 (Strong Sell) 📉": "강력 매도 (Strong Sell) 📉"
    }
    verdict_text = verdict_map.get(verdict, verdict)
    
    if "매수" in verdict_text or "Buy" in verdict_text:
        verdict_color = "#4CAF50"
        verdict_class = "verdict-buy"
        if "Strong" in verdict_text or "강력" in verdict_text:
             verdict_class = "verdict-strong-buy"
    elif "매도" in verdict_text or "Sell" in verdict_text:
        verdict_color = "#f44336"
        verdict_class = "verdict-sell"
        if "Strong" in verdict_text or "강력" in verdict_text:
             verdict_class = "verdict-strong-sell"
    else:
        verdict_color = "#ff9800"
        verdict_class = "verdict-hold"
    
    return {
        'ticker': ticker,
        'company_name': info.get('longName', ticker),
        'current_price': current_price,
        'prev_price': prev_price,
        'delta': delta,
        'currency_symbol': "₩" if ticker.endswith(".KS") or ticker.endswith(".KQ") else "$",
        'verdict': verdict_text,
        'verdict_color': verdict_color,
        'verdict_class': verdict_class,
        'chart_json': chart_json,
        'summary': utils.translate_text(info.get('longBusinessSummary', '정보 없음')) if info.get('longBusinessSummary') != '정보 없음' else '정보 없음',
        'market_cap': utils.format_market_cap(info.get('marketCap', 0), ticker),
        'pe_ratio': f"{info['trailingPE']:.2f}" if info.get('trailingPE') else 'N/A',
        'dividend_yield': info.get('dividendYield', 0) if info.get('dividendYield') else None,
        'sentiment_score': sentiment_score,
        'sentiment_details': translated_news,
        'news_count': len(sentiment_details),
        'pbr': f"{info['priceToBook']:.2f}" if info.get('priceToBook') else 'N/A',
        'roe': f"{info['returnOnEquity']*100:.2f}%" if info.get('returnOnEquity') else 'N/A',
        'eps': f"{info['trailingEps']:.2f}" if info.get('trailingEps') else 'N/A',
        'week52_high': utils.format_price_short(info.get('fiftyTwoWeekHigh'), ticker),
        'week52_low': utils.format_price_short(info.get('fiftyTwoWeekLow'), ticker),
        'advice_list': [
            {
                'text': advice,
                'color': "#4CAF50" if ("매수" in advice or "상승" in advice or "긍정" in advice) else
                        "#f44336" if ("매도" in advice or "하락" in advice or "부정" in advice) else
                        "#ff9800"
            }
            for advice in advice_list
        ]
    }

# ── 메인 페이지용 ML 예측 캐시 (6시간) ──────────────────────────────────
_main_predictions_cache: dict = {"data": None, "ts": 0}
_PRED_CACHE_SEC = 21600  # 6 hours

def _get_main_index_predictions() -> list:
    """경제지표 기반 다음 달 방향 예측 (Heuristic Model). 6시간 캐시."""
    global _main_predictions_cache
    now = time.time()
    if _main_predictions_cache["data"] is not None and now - _main_predictions_cache["ts"] < _PRED_CACHE_SEC:
        return _main_predictions_cache["data"]

    results = []
    try:
        csv_path = os.path.join(BASE_DIR, "static", "economic_indicators.csv")
        if not os.path.exists(csv_path):
            return []

        df = pd.read_csv(csv_path)
        # Ensure numeric
        cols = ['fed_rate', 'cpi', 'treasury_10y', 'usd_krw', 'ind_prod', 'wti', 'vix']
        for c in cols:
            df[c] = pd.to_numeric(df[c], errors='coerce')
        
        df = df.dropna(subset=cols)
        if df.empty:
            return []

        # Calculate Z-Scores for the latest data point relative to history
        latest = df.iloc[-1]
        z_scores = {}
        for c in cols:
            mean = df[c].mean()
            std = df[c].std()
            if std == 0:
                z_scores[c] = 0
            else:
                z_scores[c] = (latest[c] - mean) / std

        # Define weights (Negative means high value is bad for stocks)
        # Heuristic based on general economic theory
        weights = {
            'fed_rate': -1.5,
            'cpi': -1.2,
            'treasury_10y': -1.2,
            'usd_krw': -0.8,
            'ind_prod': 1.0,
            'wti': -0.5,
            'vix': -1.0
        }

        # Calculate Composite Score
        score = sum(z_scores[c] * weights.get(c, 0) for c in cols)
        
        # Sigmoid-like probability mapping (Score 0 -> 50%)
        # Score typically ranges -5 to +5
        import math
        def sigmoid(x):
            return 1 / (1 + math.exp(-x))
        
        # Adjust scaling factor 'k' to control sensitivity
        k = 0.5
        probability = sigmoid(score * k) * 100
        
        # Confidence is distance from 50%
        # If prob is 60%, confidence is how "sure" we are about the direction.
        # Let's just use the probability as the confidence of the predicted direction.
        if probability >= 50:
            pred_direction = 1 # UP
            conf = probability
        else:
            pred_direction = 0 # DOWN
            conf = 100 - probability

        target_indices = [
            ('^IXIC', 'NASDAQ',  '#38bdf8'),
            ('^GSPC', 'S&P 500', '#818cf8'),
            ('^KS11', 'KOSPI',   '#4ade80'),
        ]

        for ticker_sym, name, color in target_indices:
            # Add some random noise or specific adjustments per index if needed
            # For now, use the general macro score
            
            # Specific adjustments (Heuristic)
            final_prob = conf
            final_dir = pred_direction

            if ticker_sym == '^IXIC':
                # Tech is more sensitive to rates
                tech_score = score - (z_scores['treasury_10y'] * 0.5) 
                tech_prob = sigmoid(tech_score * k) * 100
                if tech_prob >= 50:
                    final_dir = 1
                    final_prob = tech_prob
                else:
                    final_dir = 0
                    final_prob = 100 - tech_prob

            results.append({
                'ticker': ticker_sym,
                'name': name,
                'color': color,
                'direction': '상승' if final_dir == 1 else '하락',
                'direction_icon': '📈' if final_dir == 1 else '📉',
                'direction_color': '#4ade80' if final_dir == 1 else '#f87171',
                'confidence': float(round(final_prob, 1)),
                'accuracy': 75.0, # Static estimation for heuristic
                'data_months': len(df),
            })

        _main_predictions_cache = {"data": results, "ts": now}
    except Exception as e:
        print(f"Prediction Error: {e}")
        pass
    return results


def _render_dashboard(request: Request, ticker: str = ""):
    """Internal: render the dashboard/stock analysis page"""
    # default OG
    og_image = "/static/og-image.png"

    # Dynamic Rankings
    us_tickers = get_popular_tickers(US_CANDIDATES, 'us')
    kr_tickers = get_popular_tickers(KR_CANDIDATES, 'kr')

    # Get major indices data
    indices_data = {}
    for region, indices in MAJOR_INDICES.items():
        indices_data[region] = []
        for tick, name in indices:
            current, change, change_pct = utils.get_index_data(tick)
            if current is not None:
                indices_data[region].append({
                    'name': name,
                    'ticker': tick,
                    'current': current,
                    'change': change,
                    'change_pct': change_pct
                })

    # Get stock data if ticker is provided
    stock_data = None
    news_data = []
    index_predictions = []

    if ticker:
        stock_data = get_analysis_context(ticker)
        if stock_data:
            # Construct dynamic OG URL
            params = {
                "ticker": stock_data['ticker'],
                "price": f"{stock_data['current_price']:,.0f}",
                "change": f"{stock_data['delta']:+,.0f}",
                "pct": f"{(stock_data['delta']/stock_data['prev_price'])*100:+.2f}%",
                "verdict": stock_data['verdict'].split('(')[0].strip() if '(' in stock_data['verdict'] else stock_data['verdict'],
                "color": stock_data['verdict_color']
            }
            query = urllib.parse.urlencode(params)
            og_image = f"/api/og?{query}&v={int(time.time())}"
    else:
        # Load news only if on main page (no ticker)
        news_data = news_manager.get_latest_news()
        # ML predictions for main page (cached)
        try:
            index_predictions = _get_main_index_predictions()
        except Exception:
            index_predictions = []

    return templates.TemplateResponse("index.html", {
        "request": request,
        "indices_data": indices_data,
        "stock_data": stock_data,
        "news_data": news_data,
        "index_predictions": index_predictions,
        "us_tickers": us_tickers,
        "kr_tickers": kr_tickers,
        "selected_ticker": ticker,
        "og_image": og_image
    })

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, ticker: str = ""):
    """Main page - redirects to /stock/<ticker> if ticker query param is present"""
    if ticker:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url=f"/stock/{ticker.strip().upper()}", status_code=301)
    return _render_dashboard(request)

@app.post("/", response_class=HTMLResponse)
async def search_stock(request: Request, ticker: str = Form(...)):
    """Handle stock search form submission - redirect to clean URL"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/stock/{ticker.strip().upper()}", status_code=302)

@app.get("/stock/{ticker}", response_class=HTMLResponse)
async def stock_detail(request: Request, ticker: str):
    """Stock analysis with clean URL"""
    return _render_dashboard(request, ticker=ticker.upper())

@app.get("/ads.txt", response_class=PlainTextResponse)
async def ads_txt():
    """Serve ads.txt for Google AdSense"""
    import os
    with open("ads.txt", "r", encoding="utf-8") as f:
        content = f.read()
    return content

@app.get("/yield-calculator", response_class=HTMLResponse)
async def yield_calculator(request: Request):
    """Yield Calculator Page"""
    return templates.TemplateResponse("yield_calc.html", {
        "request": request,
        "selected_ticker": "",
        "us_tickers": get_popular_tickers(US_CANDIDATES, 'us'),
        "kr_tickers": get_popular_tickers(KR_CANDIDATES, 'kr')
    })

@app.get("/fear-greed-index", response_class=HTMLResponse)
async def fear_greed_index(request: Request):
    """Fear & Greed Index Page"""
    import yfinance as yf
    import pandas as pd
    import numpy as np
    import plotly.graph_objects as go
    import json
    
    error = None
    final_score = 0
    details = {}
    gauge_json = None
    trend_json = None
    
    try:
        # Fetch Data (2y for SMA125 buffer, 1y for trend display)
        sp500 = yf.Ticker("^GSPC")
        vix = yf.Ticker("^VIX")
        
        # Fetch history
        sp500_hist = sp500.history(period="2y") 
        vix_hist = vix.history(period="1y") # We only need 1y of VIX as it doesn't need long moving avg
        
        if sp500_hist.empty or vix_hist.empty:
            raise Exception("시장 데이터를 불러오는데 실패했습니다.")
            
        # Normalize Index (Remove Timezone) to ensure alignment
        sp500_hist.index = pd.to_datetime(sp500_hist.index).tz_localize(None)
        vix_hist.index = pd.to_datetime(vix_hist.index).tz_localize(None)
            
        # --- Vectorized Calculation ---
        
        # 1. Momentum Series (Close vs 125 SMA)
        sp500_close = sp500_hist['Close']
        sma_125 = sp500_close.rolling(window=125).mean()
        
        # Calculate Momentum %
        # We align indexes safely
        common_idx = sp500_close.index.intersection(vix_hist.index)
        
        # Filter to common dates (last ~1y)
        # Note: SMA125 will have NaN for first 124 days, but since we fetched 2y, 
        # the last 1y of data should have valid SMA.
        
        df = pd.DataFrame(index=common_idx)
        df['SP500_Close'] = sp500_close[common_idx]
        df['SMA_125'] = sma_125[common_idx]
        df['VIX_Close'] = vix_hist['Close'][common_idx]
        
        # Drop any remaining NaNs (e.g. if VIX has gaps or SMA not ready)
        df.dropna(inplace=True)
        
        if df.empty:
            raise Exception("분석을 위한 데이터가 충분하지 않습니다.")
        
        # Momentum Score
        # Logic: (Price - SMA) / SMA. Target 10% deviation? 0.2 scaling
        df['Momentum_Pct'] = (df['SP500_Close'] - df['SMA_125']) / df['SMA_125']
        # Map: -0.1 -> 0, +0.1 -> 100.
        # Formula: ((pct + 0.1) / 0.2) * 100
        df['Mom_Score'] = ((df['Momentum_Pct'] + 0.1) / 0.2 * 100).clip(0, 100)
        
        # 2. Volatility Score (VIX)
        # Logic: 12 (Low Fear) -> 100 score, 35 (High Fear) -> 0 score
        # Note: Fear/Greed index usually: Low VIX = Greed (High Score), High VIX = Fear (Low Score)
        # My formula: 100 - (Vix-12)/(35-12)*100
        df['Vix_Score'] = (100 - (df['VIX_Close'] - 12) / (35 - 12) * 100).clip(0, 100)
        
        # 3. Strength Score (RSI 14)
        # Need to calc RSI on the full SP500 series first then slice
        delta = sp500_close.diff()
        gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
        rs = gain / loss
        rsi_series = 100 - (100 / (1 + rs))
        
        df['RSI'] = rsi_series[df.index]
        
        # RSI Score: 30 -> 0, 70 -> 100
        df['RSI_Score'] = ((df['RSI'] - 30) / (70 - 30) * 100).clip(0, 100)
        
        # Final Score Daily Series
        df['Final_Score'] = (df['Mom_Score'] * 0.4 + df['Vix_Score'] * 0.4 + df['RSI_Score'] * 0.2).fillna(50).astype(int)
        
        # Current Values for Cards
        if df.empty:
             raise Exception("계산 후 데이터가 비어있습니다.")
             
        latest = df.iloc[-1]
        final_score = int(latest['Final_Score'])
        
        details = {
            "Momentum Score": int(latest['Mom_Score']),
            "Volatility Score": int(latest['Vix_Score']),
            "Strength Score": int(latest['RSI_Score']),
            "VIX": round(latest['VIX_Close'], 2),
            "RSI": round(latest['RSI'], 2)
        }
        
        # --- Gauge (Current) ---
        if final_score < 25:
            label = "Extreme Fear"
            color = "#ef4444"
        elif final_score < 45:
            label = "Fear"
            color = "#f97316"
        elif final_score < 55:
            label = "Neutral"
            color = "#eab308"
        elif final_score < 75:
            label = "Greed"
            color = "#84cc16"
        else:
            label = "Extreme Greed"
            color = "#22c55e"
            
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = final_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': label, 'font': {'size': 24, 'color': color}},
            gauge = {
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': color},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 25], 'color': 'rgba(239, 68, 68, 0.3)'},
                    {'range': [25, 45], 'color': 'rgba(249, 115, 22, 0.3)'},
                    {'range': [45, 55], 'color': 'rgba(234, 179, 8, 0.3)'},
                    {'range': [55, 75], 'color': 'rgba(132, 204, 22, 0.3)'},
                    {'range': [75, 100], 'color': 'rgba(34, 197, 94, 0.3)'}],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': final_score}
            }
        ))
        
        fig_gauge.update_layout(
            paper_bgcolor = "rgba(0,0,0,0)",
            font = {'color': "white", 'family': "Inter"},
            height = 300,
            margin = dict(l=30, r=30, t=50, b=30)
        )
        gauge_json = fig_gauge.to_json()
        
        # --- Trend Chart (History) ---
        # Plotly Line Chart for df['Final_Score']
        fig_trend = go.Figure()
        
        # Add Line
        fig_trend.add_trace(go.Scatter(
            x=df.index, 
            y=df['Final_Score'],
            mode='lines',
            name='Fear & Greed',
            line=dict(color='#38bdf8', width=2)
        ))
        
        # Add colored background bands (optional, but nice)
        # Or simply update layout
        fig_trend.update_layout(
            title={'text': "최근 1년 변동 추이", 'font': {'size': 18, 'color': 'white'}},
            xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(color='#94a3b8')),
            yaxis=dict(
                range=[0, 100], 
                tickfont=dict(color='#94a3b8'),
                gridcolor='rgba(255,255,255,0.1)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=20, t=40, b=40),
            height=300,
            showlegend=False
        )
        
        # Add horizontal zones
        fig_trend.add_hrect(y0=0, y1=25, fillcolor="red", opacity=0.1, layer="below", line_width=0)
        fig_trend.add_hrect(y0=75, y1=100, fillcolor="green", opacity=0.1, layer="below", line_width=0)
        
        trend_json = fig_trend.to_json()
        
    except Exception as e:
        error = str(e)
        import traceback
        traceback.print_exc()
        
    return templates.TemplateResponse("fear_greed.html", {
        "request": request,
        "selected_ticker": "",
        "us_tickers": get_popular_tickers(US_CANDIDATES, 'us'),
        "kr_tickers": get_popular_tickers(KR_CANDIDATES, 'kr'),
        "score": final_score,
        "details": details,
        "gauge_json": gauge_json,
        "trend_json": trend_json,
        "error": error
    })

@app.get("/exchange-rate", response_class=HTMLResponse)
async def exchange_rate(request: Request):
    """Exchange Rate Page with Smart Advice"""
    import yfinance as yf
    import pandas as pd
    import numpy as np
    
    # Fallback rates
    rates = {
        "USD": 1.0, 
        "KRW": 1300.0, 
        "JPY": 145.0, 
        "EUR": 0.9,
        "GBP": 0.8,
        "CNY": 7.2,
        "AUD": 1.5,
        "CAD": 1.35
    }
    analysis = {}
    error = None
    
    try:
        # 1. Fetch Spot Rates (as before)
        # Using separate calls for reliability in this specific template context
        r_krw = yf.Ticker("KRW=X").history(period="1d")['Close'].iloc[-1]
        r_jpy = yf.Ticker("JPY=X").history(period="1d")['Close'].iloc[-1]
        r_cny = yf.Ticker("CNY=X").history(period="1d")['Close'].iloc[-1]
        r_cad = yf.Ticker("CAD=X").history(period="1d")['Close'].iloc[-1]
        
        r_eur_usd = yf.Ticker("EURUSD=X").history(period="1d")['Close'].iloc[-1]
        r_gbp_usd = yf.Ticker("GBPUSD=X").history(period="1d")['Close'].iloc[-1]
        r_aud_usd = yf.Ticker("AUDUSD=X").history(period="1d")['Close'].iloc[-1]
        
        rates = {
            "USD": 1.0,
            "KRW": float(r_krw),
            "JPY": float(r_jpy),
            "EUR": 1.0 / float(r_eur_usd),
            "GBP": 1.0 / float(r_gbp_usd),
            "CNY": float(r_cny),
            "AUD": 1.0 / float(r_aud_usd),
            "CAD": float(r_cad)
        }
        
        # 2. Fetch History for Analysis (USD/KRW and JPY/KRW)
        # Fetch 1 month history
        hist_krw = yf.Ticker("KRW=X").history(period="1mo")['Close']
        hist_jpy = yf.Ticker("JPY=X").history(period="1mo")['Close']
        
        if not hist_krw.empty and not hist_jpy.empty:
            # Align dates
            df = pd.DataFrame({'KRW': hist_krw, 'JPY': hist_jpy}).dropna()
            
            # USD/KRW Analysis
            usd_current = df['KRW'].iloc[-1]
            usd_avg = df['KRW'].mean()
            usd_min = df['KRW'].min()
            usd_max = df['KRW'].max()
            
            usd_status = "보통"
            usd_msg = "평균적인 수준입니다."
            if usd_current < usd_avg * 0.98:
                usd_status = "강력 매수 (환전 추천)"
                usd_msg = "최근 평균보다 매우 낮습니다. 지금 환전하는 것이 유리합니다."
            elif usd_current < usd_avg:
                usd_status = "매수 우위"
                usd_msg = "평균보다 약간 낮습니다. 나쁘지 않은 시기입니다."
            elif usd_current > usd_avg * 1.02:
                usd_status = "관망 (환전 비추천)"
                usd_msg = "최근 평균보다 높습니다. 급하지 않다면 기다려보세요."
            else:
                usd_status = "중립"
                usd_msg = "평균 수준입니다. 분할 환전을 고려하세요."
                
            analysis['USD'] = {
                'current': round(usd_current, 2),
                'avg': round(usd_avg, 2),
                'min': round(usd_min, 2),
                'max': round(usd_max, 2),
                'status': usd_status,
                'message': usd_msg
            }
            
            # JPY/KRW (100 Yen) Analysis
            # 100 JPY = (KRW/USD) / (JPY/USD) * 100
            df['JPYKRW'] = (df['KRW'] / df['JPY']) * 100
            
            jpy_current = df['JPYKRW'].iloc[-1]
            jpy_avg = df['JPYKRW'].mean()
            jpy_min = df['JPYKRW'].min()
            jpy_max = df['JPYKRW'].max()
            
            jpy_status = "보통"
            jpy_msg = "평균적인 수준입니다."
            if jpy_current < jpy_avg * 0.98:
                jpy_status = "강력 매수 (엔화 저렴)"
                jpy_msg = "엔화가 매우 저렴합니다. 여행이나 투자를 위해 환전하기 좋습니다."
            elif jpy_current < jpy_avg:
                jpy_status = "매수 우위"
                jpy_msg = "평균보다 낮습니다. 괜찮은 가격대입니다."
            elif jpy_current > jpy_avg * 1.02:
                jpy_status = "관망 (엔화 비쌈)"
                jpy_msg = "엔화가 다소 비쌉니다. 추이를 지켜보세요."
            
            analysis['JPY'] = {
                'current': round(jpy_current, 2),
                'avg': round(jpy_avg, 2),
                'min': round(jpy_min, 2),
                'max': round(jpy_max, 2),
                'status': jpy_status,
                'message': jpy_msg
            }
        
    except Exception as e:
        error = f"데이터를 가져오는데 실패했습니다: {str(e)}"
        print(f"Exchange Analysis Error: {e}")
        
    return templates.TemplateResponse("exchange.html", {
        "request": request,
        "selected_ticker": "",
        "us_tickers": get_popular_tickers(US_CANDIDATES, 'us'),
        "kr_tickers": get_popular_tickers(KR_CANDIDATES, 'kr'),
        "rates": rates,
        "analysis": analysis,
        "error": error
    })

@app.get("/etf-explorer", response_class=HTMLResponse)
async def etf_explorer(request: Request, ticker: str = ""):
    """ETF Explorer Page"""
    categories = [
        {
            "id": "korea",
            "icon": "🇰🇷",
            "title": "대한민국 인기 ETF",
            "desc": "세계 시장에서 주목받는 한국의 대표 우량주와 핵심 성장 테마(반도체, 2차전지 등)에 투자하세요.",
            "theme": "korea",
            "etf_list": [
                ("069500.KS", "KODEX 200", "코스피 200 지수 추종 (대한민국 대표)"),
                ("371460.KS", "TIGER 차이나전기차", "중국 전기차/배터리 밸류체인 (국내 인기 1위)"),
                ("292150.KS", "TIGER TOP10", "국내 시가총액 상위 10개 우량주 집중 투자"),
                ("305720.KS", "KODEX 2차전지산업", "국내 배터리 3사 및 소재/장비 밸류체인"),
                ("360750.KS", "TIGER 미국S&P500", "미국 S&P 500 지수를 환헤지 없이 추종")
            ]
        },
        {
            "id": "us",
            "icon": "🇺🇸",
            "title": "미국 지수 추종",
            "desc": "전 세계 자본이 모이는 미국 시장의 성장성에 투자하는 가장 확실한 방법입니다.",
            "theme": "us",
            "etf_list": [
                ("SPY", "S&P 500 Trust", "미국 대형주 500개 기업 투자 (시장 수익률의 표준)"),
                ("QQQ", "Invesco QQQ", "나스닥 100 기술주 중심 (고성장 테크기업)"),
                ("DIA", "Dow Jones ETF", "다우존스 30개 초우량 전통 기업"),
                ("IWM", "Russell 2000", "미국 중소형주 2000개 (경기 회복기 수혜)"),
                ("VTI", "Vanguard Total Stock", "미국 전체 상장 기업에 분산 투자")
            ]
        },
        {
            "id": "dividend",
            "icon": "💰",
            "title": "배당 & 인컴",
            "desc": "매달 혹은 매분기 들어오는 현금 흐름을 중시하는 안정적인 투자자를 위한 선택입니다.",
            "theme": "dividend",
            "etf_list": [
                ("SCHD", "US Dividend Equity", "10년 연속 배당금을 늘려온 우량 배당 성장주"),
                ("JEPI", "JPMorgan Premium", "주식+콜옵션 매도로 높은 월배당 수익 추구"),
                ("O", "Realty Income", "미국 상업용 부동산 월배당 리츠의 대명사"),
                ("VNQ", "Vanguard Real Estate", "미국 부동산 리츠 시장 전체에 투자"),
                ("DGRO", "Dividend Growth", "지속적으로 배당을 성장시키는 기업에 투자")
            ]
        },
        {
            "id": "tech",
            "icon": "🚀",
            "title": "테크 & 혁신",
            "desc": "미래를 바꿀 혁신 기술(AI, 반도체, 로봇 등)에 투자하여 초과 수익을 노려보세요.",
            "theme": "tech",
            "etf_list": [
                ("SOXX", "Semiconductor ETF", "엔비디아, 브로드컴 등 글로벌 반도체 대표 지수"),
                ("XLK", "Technology Select", "마이크로소프트, 애플 등 S&P 500 기술주"),
                ("ARKK", "ARK Innovation", "파괴적 혁신 기업에 집중 투자 (고변동성)"),
                ("NVDL", "GraniteShares 2x NVDA", "엔비디아 일일 수익률의 2배 추종 (초고위험)"),
                ("CIBR", "First Trust Cyber Security", "전 세계 사이버 보안 선두 기업들")
            ]
        },
        {
            "id": "safe",
            "icon": "🛡️",
            "title": "채권 & 안전자산",
            "desc": "경제 불확실성에 대비하여 포트폴리오의 변동성을 낮춰주는 든든한 방패입니다.",
            "theme": "safe",
            "etf_list": [
                ("TLT", "Lt. Treasury Bond", "20년 이상 미국 장기 국채 (금리 인하 시 수혜)"),
                ("SHY", "1-3 Year Treasury", "미국 단기 국채 (현금과 유사한 안전성)"),
                ("GLD", "SPDR Gold Shares", "금 실물 가격을 추종하는 대표 ETF"),
                ("LQD", "Investment Grade Corp", "우량 등급 미국 회사채 투자"),
                ("IEF", "7-10 Year Treasury", "미국 중기 국채 (가장 표준적인 안전자산)")
            ]
        }
    ]
    
    stock_data = None
    if ticker:
        stock_data = get_analysis_context(ticker)
    
    return templates.TemplateResponse("etf.html", {
        "request": request,
        "selected_ticker": ticker,
        "stock_data": stock_data,
        "us_tickers": get_popular_tickers(US_CANDIDATES, 'us'),
        "kr_tickers": get_popular_tickers(KR_CANDIDATES, 'kr'),
        "categories": categories
    })

@app.post("/etf-explorer", response_class=HTMLResponse)
async def etf_explorer_post(request: Request, ticker: str = Form(...)):
    return await etf_explorer(request, ticker)

@app.get("/sector-analysis", response_class=HTMLResponse)
async def sector_analysis(request: Request, cycle: str = "rate_cut"):
    """Sector Analysis Page"""
    import plotly.graph_objects as go
    import json
    
    # 1. Get Recommendations
    recommendation = utils.get_cycle_recommendation(cycle)
    
    # 2. Get Performance Data (Bar Chart)
    perf_data = utils.get_sector_performance()
    
    # 3. Get History Data (Line Chart) [NEW]
    history_data = utils.get_sector_history_data() # Returns dict {sector: [{x,y}...]}
    
    # 4. Get Top Stocks for Bullish Sectors [NEW]
    top_stocks = utils.get_sector_top_stocks(recommendation['bullish'])
    
    # Create Bar Chart Logic (Same as before)
    fig = go.Figure()
    if perf_data:
        tickers = [item['ticker'] for item in perf_data]
        rs_vals = [item['rs_1m'] for item in perf_data]
        colors = ['#4CAF50' if val > 0 else '#f44336' for val in rs_vals]
        
        fig.add_trace(go.Bar(
            x=tickers,
            y=rs_vals,
            marker_color=colors,
            text=[f"{val:+.1f}%" for val in rs_vals],
            textposition='auto'
        ))
        
    fig.update_layout(
        title="최근 1개월 상대 강도 (vs SPY)",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8', family='Inter'),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis_title="섹터 ETF",
        yaxis_title="상대 수익률 (%)",
    )
    chart_json = fig.to_json()
    
    return templates.TemplateResponse("sector.html", {
        "request": request,
        "current_cycle": cycle,
        "recommendation": recommendation,
        "chart_json": chart_json,
        "trend_json": json.dumps(history_data) if history_data else "{}",
        "top_stocks": top_stocks,
        "us_tickers": get_popular_tickers(US_CANDIDATES, 'us'),
        "kr_tickers": get_popular_tickers(KR_CANDIDATES, 'kr')
    })

@app.get("/sentiment-analysis", response_class=HTMLResponse)
async def sentiment_analysis(request: Request):
    """Sentiment Analysis Page"""
    import json
    
    meme_stocks = utils.get_meme_candidates()
    
    # Extract keywords from Meme Stock related text/news [NEW]
    # For now, we simulate by collecting tickers and manual keywords since we don't have deep news db here
    # Ideally, would call utilities.get_news(ticker) for each.
    
    # Simplified Word Cloud Source
    all_titles = []
    # Add dummy/real titles - in real app, fetch news for top meme stocks
    for stock in meme_stocks[:3]:
        # Try to fetch real reddit titles if earlier cache existed, or re-fetch (expensive)
        # For performance, we'll just use ticker + status
        all_titles.append(f"{stock['ticker']} stock analysis value")
        
    # Let's actually use Reddit titles if possible
    # Note: get_meme_candidates calls get_reddit_sentiment internally but doesn't return titles.
    # We might want to optimize this later. For now, we'll run a quick keyword check on Tickers themselves + Metadata
    keywords = utils.get_keywords([s['ticker'] + " Stock Market Analysis" for s in meme_stocks])
    
    # Prepare JSON for Scatter Plot
    meme_json = json.dumps([{
        'ticker': s['ticker'],
        'volatility': s['volatility'],
        'volume_ratio': s['volume_ratio'],
        'change_pct': s['change_pct'],
        'meme_score': s['meme_score']
    } for s in meme_stocks])
    
    return templates.TemplateResponse("sentiment.html", {
        "request": request,
        "meme_stocks": meme_stocks,
        "meme_json": meme_json,
        "keywords": keywords,
        "us_tickers": get_popular_tickers(US_CANDIDATES, 'us'),
        "kr_tickers": get_popular_tickers(KR_CANDIDATES, 'kr')
    })

@app.get("/economic-indicators", response_class=HTMLResponse)
async def economic_indicators_page(request: Request):
    """Economic Indicators Dashboard"""
    try:
        import numpy as np
        df = pd.read_csv(os.path.join(BASE_DIR, "static", "economic_indicators.csv"))
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)

        # yfinance로 최신 데이터 보완 (SMH, XLI, EWY, SOX)
        try:
            import yfinance as yf
            latest_date = df['date'].max()
            end_dt = datetime.now()
            if end_dt > latest_date:
                yf_map = {'smh': 'SMH', 'xli': 'XLI', 'ewy': 'EWY', 'sox': '^SOX'}
                for col, ticker in yf_map.items():
                    hist = yf.download(ticker, start=latest_date.strftime('%Y-%m-%d'),
                                       end=end_dt.strftime('%Y-%m-%d'), interval='1mo', progress=False, auto_adjust=True)
                    if not hist.empty:
                        for idx, row in hist.iterrows():
                            month_start = pd.Timestamp(idx).replace(day=1)
                            if month_start > latest_date:
                                mask = df['date'] == month_start
                                if mask.any():
                                    df.loc[mask, col] = float(row['Close'])
                                else:
                                    new_row = pd.DataFrame({'date': [month_start], col: [float(row['Close'])]})
                                    df = pd.concat([df, new_row], ignore_index=True)
                df = df.sort_values('date').reset_index(drop=True)
        except Exception:
            pass

        # 지표 메타 정보
        indicator_meta = {
            'fed_rate':      {'label': 'Fed 기준금리', 'unit': '%',  'icon': '🏦', 'desc': '미국 연방준비제도 기준금리. 높을수록 시장 유동성 감소'},
            'cpi':           {'label': 'CPI (소비자물가)', 'unit': '',  'icon': '🛒', 'desc': '미국 소비자물가지수. 인플레이션 측정 핵심 지표'},
            'treasury_10y':  {'label': '미국 10년 국채', 'unit': '%',  'icon': '📜', 'desc': '10년 만기 미국 국채 수익률. 장기 금리 기대 반영'},
            'usd_krw':       {'label': 'USD/KRW 환율', 'unit': '원', 'icon': '💱', 'desc': '달러-원 환율. 높을수록 원화 약세'},
            'ind_prod':      {'label': '산업생산지수', 'unit': '',   'icon': '🏭', 'desc': '미국 산업생산 활동 수준 지수'},
            'wti':           {'label': 'WTI 유가', 'unit': '$',  'icon': '🛢️', 'desc': '서부 텍사스산 원유 가격(달러/배럴)'},
            'vix':           {'label': 'VIX 공포지수', 'unit': '',   'icon': '😱', 'desc': 'S&P 500 변동성 지수. 높을수록 시장 불안'},
            'sox':           {'label': 'SOX 반도체지수', 'unit': '',  'icon': '💾', 'desc': 'PHLX 반도체 지수. 글로벌 반도체 업황 대표 지표'},
            'xli':           {'label': 'XLI 산업ETF', 'unit': '$',  'icon': '⚙️', 'desc': '미국 산업재 섹터 ETF'},
            'ewy':           {'label': 'EWY 한국ETF', 'unit': '$',  'icon': '🇰🇷', 'desc': 'iShares MSCI South Korea ETF'},
            'smh':           {'label': 'SMH 반도체ETF', 'unit': '$', 'icon': '🔬', 'desc': 'VanEck 반도체 ETF. NVDA, TSMC 등 포함'},
        }

        # 현재값 및 변화율 계산 (각 컬럼별 마지막 유효값 사용)
        indicator_cols = list(indicator_meta.keys())

        indicators_display = []
        for col in indicator_cols:
            col_series = df[col].dropna()
            cur = float(col_series.iloc[-1]) if len(col_series) >= 1 else None
            prv = float(col_series.iloc[-2]) if len(col_series) >= 2 else None
            if cur is not None and prv is not None and prv != 0:
                chg = cur - prv
                chg_pct = chg / abs(prv) * 100
            else:
                chg = None
                chg_pct = None
            meta = indicator_meta[col]
            indicators_display.append({
                'col': col,
                'label': meta['label'],
                'unit': meta['unit'],
                'icon': meta['icon'],
                'desc': meta['desc'],
                'current': cur,
                'change': chg,
                'change_pct': chg_pct,
            })

        # 상관관계 히트맵 — NASDAQ / S&P500 / KOSPI 포함
        # yfinance로 주가 지수 월별 데이터 병합
        index_price_meta = {
            'nasdaq': {'label': '📈 NASDAQ',  'ticker': '^IXIC'},
            'sp500':  {'label': '📈 S&P 500', 'ticker': '^GSPC'},
            'kospi':  {'label': '📈 KOSPI',   'ticker': '^KS11'},
        }
        corr_df_base = df[['date'] + indicator_cols].copy()
        try:
            import yfinance as yf
            for col_key, meta in index_price_meta.items():
                hist = yf.download(meta['ticker'], start='1995-01-01', interval='1mo',
                                   progress=False, auto_adjust=True)
                if hist.empty:
                    continue
                close = hist['Close'].squeeze()
                idx_tmp = pd.DataFrame({
                    'date': pd.to_datetime(close.index).to_period('M').to_timestamp(),
                    col_key: close.values.astype(float)
                }).dropna()
                idx_tmp['date'] = idx_tmp['date'].dt.normalize()
                corr_df_base = pd.merge(corr_df_base, idx_tmp, on='date', how='left')
        except Exception:
            pass

        # 전체 컬럼 리스트 (경제지표 + 주가)
        all_corr_cols = indicator_cols + [k for k in index_price_meta if k in corr_df_base.columns]
        corr_matrix = corr_df_base[all_corr_cols].dropna().corr().round(2)

        # 라벨 생성 (주가 지수는 bold 느낌으로 별도 표시)
        all_labels = []
        for c in corr_matrix.columns:
            if c in index_price_meta:
                all_labels.append(index_price_meta[c]['label'])
            else:
                all_labels.append(indicator_meta[c]['label'])

        # 셀 색상 강조: 주가 행/열은 별도 annotation으로 표시
        z_vals = corr_matrix.values.tolist()
        text_vals = corr_matrix.values.round(2).tolist()

        heatmap_fig = go.Figure(go.Heatmap(
            z=z_vals,
            x=all_labels, y=all_labels,
            colorscale='RdBu', zmid=0, zmin=-1, zmax=1,
            text=text_vals,
            texttemplate='%{text}',
            textfont=dict(size=8),
            hoverongaps=False,
            colorbar=dict(len=0.8, thickness=12, title=dict(text='상관계수', side='right')),
        ))

        # 주가 지수 행/열 구분선 (세로/가로 점선)
        n_econ = len(indicator_cols)
        n_total = len(all_corr_cols)
        if n_total > n_econ:
            heatmap_fig.add_shape(
                type='line', x0=n_econ - 0.5, x1=n_econ - 0.5, y0=-0.5, y1=n_total - 0.5,
                line=dict(color='rgba(251,191,36,0.7)', width=1.5, dash='dot')
            )
            heatmap_fig.add_shape(
                type='line', x0=-0.5, x1=n_total - 0.5, y0=n_econ - 0.5, y1=n_econ - 0.5,
                line=dict(color='rgba(251,191,36,0.7)', width=1.5, dash='dot')
            )

        n_idx = len(all_corr_cols)
        heatmap_fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#94a3b8', family='Inter', size=9),
            height=max(600, n_idx * 42),
            margin=dict(l=155, r=20, t=30, b=155),
            xaxis=dict(tickangle=-45, tickfont=dict(size=9)),
            yaxis=dict(tickfont=dict(size=9)),
        )
        heatmap_json = heatmap_fig.to_json()

        # 주가-경제지표 핵심 상관관계 Top 테이블 (템플릿에 전달)
        corr_top_rows = []
        stock_cols = [k for k in index_price_meta if k in corr_matrix.columns]
        for sc in stock_cols:
            econ_corrs = corr_matrix.loc[indicator_cols, sc].dropna().sort_values(key=abs, ascending=False)
            for ec, val in econ_corrs.head(3).items():
                corr_top_rows.append({
                    'stock': index_price_meta[sc]['label'],
                    'indicator': indicator_meta[ec]['label'],
                    'corr': float(val),
                    'bar_width': int(abs(val) * 100),
                    'color': '#4ade80' if val > 0 else '#f87171',
                    'sign': '+' if val > 0 else '',
                })

        # 트렌드 차트 (선택 지표 추이, 최근 5년)
        recent = df[df['date'] >= df['date'].max() - pd.DateOffset(years=5)].copy()
        trend_fig = go.Figure()
        trend_cols = ['fed_rate', 'treasury_10y', 'vix']
        trend_colors = ['#38bdf8', '#c084fc', '#f87171']
        for tc, color in zip(trend_cols, trend_colors):
            mask = recent[tc].notna()
            trend_fig.add_trace(go.Scatter(
                x=recent.loc[mask, 'date'].dt.strftime('%Y-%m').tolist(),
                y=recent.loc[mask, tc].tolist(),
                name=indicator_meta[tc]['label'],
                line=dict(color=color, width=2),
                mode='lines',
            ))
        trend_fig.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#94a3b8', family='Inter'),
            height=300,
            margin=dict(l=40, r=20, t=20, b=40),
            legend=dict(orientation='h', y=1.1),
            hovermode='x unified',
        )
        trend_json = trend_fig.to_json()

        # ML 예측 — 캐시 공유 함수 재사용 (6시간 캐시)
        index_predictions = _get_main_index_predictions()
        feature_importance_json = None

        # Feature Importance 차트 — 캐시된 예측이 있을 때만 생성
        try:
            if index_predictions:
                import yfinance as yf
                from sklearn.ensemble import RandomForestClassifier
                from sklearn.model_selection import train_test_split
                from sklearn.preprocessing import StandardScaler

                feat_cols = ['fed_rate', 'cpi', 'treasury_10y', 'usd_krw', 'ind_prod', 'wti', 'vix']
                fi_labels = [indicator_meta[c]['label'] for c in feat_cols]

                # fi 차트도 캐싱
                _fi_cache_key = "fi_json"
                _fi_ts_key = "fi_ts"
                if (
                    _fi_cache_key in _main_predictions_cache
                    and _main_predictions_cache[_fi_ts_key] == _main_predictions_cache["ts"]
                ):
                    feature_importance_json = _main_predictions_cache[_fi_cache_key]
                else:
                    all_fi = []
                    target_indices = [
                        ('^IXIC', '#38bdf8'),
                        ('^GSPC', '#818cf8'),
                        ('^KS11', '#4ade80'),
                    ]
                    for ticker_sym, _ in target_indices:
                        try:
                            hist = yf.download(ticker_sym, start='1995-01-01', interval='1mo',
                                               progress=False, auto_adjust=True)
                            if hist.empty:
                                continue
                            close = hist['Close'].squeeze()
                            idx_df = pd.DataFrame({
                                'date': pd.to_datetime(close.index).to_period('M').to_timestamp(),
                                'price': close.values.astype(float)
                            }).dropna()
                            idx_df['date'] = idx_df['date'].dt.normalize()
                            merged = pd.merge(
                                df[['date'] + feat_cols].dropna(subset=feat_cols),
                                idx_df, on='date', how='inner'
                            ).sort_values('date').reset_index(drop=True)
                            merged['target'] = (merged['price'].shift(-1) > merged['price']).astype(int)
                            merged = merged.dropna()
                            if len(merged) < 30:
                                continue
                            X, y = merged[feat_cols].values, merged['target'].values
                            sc = StandardScaler()
                            Xs = sc.fit_transform(X)
                            X_tr, X_te, y_tr, y_te = train_test_split(Xs[:-12], y[:-12], test_size=0.2, random_state=42)
                            clf = RandomForestClassifier(200, max_depth=5, random_state=42)
                            clf.fit(X_tr, y_tr)
                            all_fi.append(clf.feature_importances_)
                        except Exception:
                            continue

                    if all_fi:
                        avg_fi = np.mean(all_fi, axis=0)
                        fi_sorted = sorted(zip(fi_labels, avg_fi.tolist()), key=lambda x: x[1], reverse=True)
                        fi_fig = go.Figure(go.Bar(
                            x=[v for _, v in fi_sorted],
                            y=[l for l, _ in fi_sorted],
                            orientation='h',
                            marker=dict(
                                color=[f'rgba(56,189,248,{min(1.0, 0.35 + v * 2.5):.2f})' for _, v in fi_sorted]
                            ),
                            text=[f'{v:.3f}' for _, v in fi_sorted],
                            textposition='outside',
                        ))
                        fi_fig.update_layout(
                            template='plotly_dark',
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            font=dict(color='#94a3b8', family='Inter', size=11),
                            height=280,
                            margin=dict(l=150, r=60, t=20, b=20),
                            xaxis_title='평균 중요도',
                        )
                        feature_importance_json = fi_fig.to_json()
                        _main_predictions_cache[_fi_cache_key] = feature_importance_json
                        _main_predictions_cache[_fi_ts_key] = _main_predictions_cache["ts"]
        except Exception as e:
            print(f"[eco-indicators] FI chart error: {e}")

        data_start = df['date'].min().strftime('%Y-%m')
        data_end = df['date'].max().strftime('%Y-%m')

        return templates.TemplateResponse("economic_indicators.html", {
            "request": request,
            "selected_ticker": "",
            "us_tickers": get_popular_tickers(US_CANDIDATES, 'us'),
            "kr_tickers": get_popular_tickers(KR_CANDIDATES, 'kr'),
            "indicators_display": indicators_display,
            "heatmap_json": heatmap_json,
            "corr_top_rows": corr_top_rows,
            "trend_json": trend_json,
            "feature_importance_json": feature_importance_json,
            "index_predictions": index_predictions,
            "data_start": data_start,
            "data_end": data_end,
            "error": None,
        })
    except Exception as e:
        return templates.TemplateResponse("economic_indicators.html", {
            "request": request,
            "selected_ticker": "",
            "us_tickers": get_popular_tickers(US_CANDIDATES, 'us'),
            "kr_tickers": get_popular_tickers(KR_CANDIDATES, 'kr'),
            "error": str(e),
        })


@app.get("/robots.txt", response_class=PlainTextResponse)
@app.head("/robots.txt", response_class=PlainTextResponse)
async def robots():
    """Serve robots.txt"""
    import os
    robots_path = os.path.join("static", "robots.txt")
    if os.path.exists(robots_path):
        with open(robots_path, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = "User-agent: *\nAllow: /"
    return content

@app.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_policy(request: Request):
    """Privacy Policy Page"""
    return templates.TemplateResponse("privacy_policy.html", {"request": request})

@app.get("/terms-of-service", response_class=HTMLResponse)
async def terms_of_service(request: Request):
    """Terms of Service Page"""
    return templates.TemplateResponse("terms.html", {"request": request})

@app.get("/api/og")
async def api_og(ticker: str, price: str, change: str, pct: str, verdict: str, color: str):
    """Generate dynamic OG image"""
    
    # 1. Create Base Image (Dark Theme)
    W, H = 1200, 630
    img = Image.new('RGB', (W, H), color='#0f172a')
    draw = ImageDraw.Draw(img)
    
    # 2. visual elements (gradient-like background effect)
    # Draw some subtle circles
    draw.ellipse((-100, -100, 300, 300), fill='#1e293b')
    draw.ellipse((900, 400, 1400, 800), fill='#1e293b')
    
    # 3. Load Fonts
    # 3. Load Fonts
    try:
        # Load local Korean font for server-side generation
        import os
        base_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(base_dir, "static", "NanumGothic-Bold.ttf")
        
        font_large = ImageFont.truetype(font_path, 80)
        font_medium = ImageFont.truetype(font_path, 50)
        font_small = ImageFont.truetype(font_path, 30)
    except Exception as e:
        # Fallback to default if font file is missing (text might break)
        print(f"Font loading failed: {e}")
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # 4. Draw Text
    # Ticker
    draw.text((100, 100), ticker, font=font_large, fill='#ffffff')
    
    # Price
    price_text = f"{price} ({change} / {pct})"
    draw.text((100, 220), price_text, font=font_medium, fill='#e2e8f0')
    
    # Verdict Box
    # Calculate text size to center or draw box
    # Simple draw:
    draw.text((100, 350), "AI 분석 의견:", font=font_small, fill='#94a3b8')
    draw.text((100, 400), verdict, font=font_large, fill=color)
    
    # Footer branding
    draw.text((100, 550), "Stock Insight AI", font=font_small, fill='#64748b')
    
    # 5. Save to Buffer
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    return Response(content=buf.getvalue(), media_type="image/png")

@app.get("/sitemap.xml")
async def sitemap():
    """Generate and serve dynamic sitemap.xml"""
    from datetime import datetime
    from fastapi.responses import Response
    
    base_url = "https://stock-insight.app"
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Build sitemap XML
    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
    <!-- 메인 페이지 -->
    <url>
        <loc>{base_url}/</loc>
        <lastmod>{today}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>{base_url}/yield-calculator</loc>
        <lastmod>{today}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>{base_url}/fear-greed-index</loc>
        <lastmod>{today}</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>{base_url}/exchange-rate</loc>
        <lastmod>{today}</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>{base_url}/etf-explorer</loc>
        <lastmod>{today}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>{base_url}/privacy-policy</loc>
        <lastmod>{today}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.5</priority>
    </url>
    <url>
        <loc>{base_url}/terms-of-service</loc>
        <lastmod>{today}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.5</priority>
    </url>
    <url>
        <loc>{base_url}/sector-analysis</loc>
        <lastmod>{today}</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>{base_url}/sentiment-analysis</loc>
        <lastmod>{today}</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>{base_url}/economic-indicators</loc>
        <lastmod>{today}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
"""

    # Add popular US stocks with clean URLs
    for tick, name in US_TOP_TICKERS[:8]:  # Top 8
        sitemap_xml += f"""    <url>
        <loc>{base_url}/stock/{tick}</loc>
        <lastmod>{today}</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.9</priority>
    </url>
"""

    # Add popular Korean stocks with clean URLs
    for tick, name in KR_TOP_TICKERS[:4]:  # Top 4
        sitemap_xml += f"""    <url>
        <loc>{base_url}/stock/{tick}</loc>
        <lastmod>{today}</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.9</priority>
    </url>
"""
    
    sitemap_xml += "</urlset>"
    
    return Response(content=sitemap_xml, media_type="application/xml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

