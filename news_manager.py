import feedparser
import requests
from bs4 import BeautifulSoup
import openai
import os
import json
import random
import time
from datetime import datetime
from deep_translator import GoogleTranslator

# File to store cached news
NEWS_DATA_FILE = "static/news_data.json"

# RSS Feeds
# RSS Feeds - Using Search Query for reliability
FEEDS = {
    "domestic": "https://news.google.com/rss/search?q=economy+finance+korea&hl=ko&gl=KR&ceid=KR%3Ako",
    "global": "https://news.google.com/rss/search?q=US+stock+market+economy&hl=en-US&gl=US&ceid=US%3Aen"
}

def clean_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.extract()
    return soup.get_text()[:2000] # Limit char count for token saving

def summarize_with_ai(title, content):
    """
    Uses OpenAI to summarize the news and analyze sentiment.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "summary": ["AI 요약 기능을 사용하려면 API 키가 필요합니다.", "OpenAI API 키를 설정해주세요.", "기사 원문을 참고하세요."],
            "sentiment": "Neutral",
            "score": 0
        }

    client = openai.OpenAI(api_key=api_key)
    
    prompt = f"""
    You are a financial news analyst. 
    Analyze the following news article:
    Title: {title}
    Content: {content}

    Task:
    1. Summarize the key points in exactly 3 bullet points in Korean. Each point must be under 50 characters.
    2. Analyze the sentiment (POSITIVE, NEGATIVE, NEUTRAL) regarding the market/economy.

    Output format (JSON):
    {{
        "summary": ["Point 1", "Point 2", "Point 3"],
        "sentiment": "POSITIVE", 
        "sentiment_score": 0.8  (Range -1.0 to 1.0)
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
        return {
            "summary": result.get("summary", ["요약 실패"]),
            "sentiment": result.get("sentiment", "Neutral"),
            "score": result.get("sentiment_score", 0)
        }
    except Exception as e:
        print(f"AI Error: {e}")
        return {
            "summary": ["AI 요약 생성 중 오류 발생.", "잠시 후 다시 시도해주세요.", "원문을 확인하세요."],
            "sentiment": "Neutral",
            "score": 0
        }

def fetch_rss_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        return response.content
    except Exception as e:
        print(f"Fetch Error {url}: {e}")
        return None

def fetch_and_process_news():
    # Check if data exists and is fresh (e.g. < 50 mins old)
    if os.path.exists(NEWS_DATA_FILE):
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(NEWS_DATA_FILE))
        time_diff = datetime.now() - file_mod_time
        if time_diff.total_seconds() < 50 * 60:  # 50 minutes
            print(f"[{datetime.now()}] News data is fresh (updated {int(time_diff.total_seconds() // 60)} mins ago). Skipping.")
            return

    print(f"[{datetime.now()}] Starting News Crawl...")
    
    all_news = []
    
    # 1. Fetch Domestic (Top 3)
    try:
        content = fetch_rss_content(FEEDS["domestic"])
        if content:
            feed = feedparser.parse(content)
            for entry in feed.entries[:3]:
                # Call to clean_html
                cleaned_desc = clean_html(entry.description)
                
                # AI Processing
                ai_result = summarize_with_ai(entry.title, cleaned_desc)
                
                all_news.append({
                    "title": entry.title,
                    "link": entry.link,
                    "publisher": entry.source.title if hasattr(entry, 'source') else "Google News",
                    "summary": ai_result['summary'],
                    "sentiment": ai_result['sentiment'],
                    "sentiment_score": ai_result['score'],
                    "type": "국내"
                })
    except Exception as e:
        print(f"Domestic News Error: {e}")

    # 2. Fetch Global (Top 3)
    try:
        content = fetch_rss_content(FEEDS["global"])
        if content:
            feed = feedparser.parse(content)
            for entry in feed.entries[:3]:
                # Translate Title
                try:
                    translated_title = GoogleTranslator(source='auto', target='ko').translate(entry.title)
                except:
                    translated_title = entry.title

                cleaned_desc = clean_html(entry.description)
                ai_result = summarize_with_ai(entry.title, cleaned_desc)
                
                all_news.append({
                    "title": translated_title,
                    "original_title": entry.title,
                    "link": entry.link,
                    "publisher": entry.source.title if hasattr(entry, 'source') else "Global News",
                    "summary": ai_result['summary'],
                    "sentiment": ai_result['sentiment'],
                    "sentiment_score": ai_result['score'],
                    "type": "해외"
                })
    except Exception as e:
        print(f"Global News Error: {e}")

    # Save to JSON
    with open(NEWS_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=2)
    
    print(f"[{datetime.now()}] News Updated: {len(all_news)} items.")

def get_latest_news():
    # Check if file exists
    if not os.path.exists(NEWS_DATA_FILE):
        return []
    
    try:
        with open(NEWS_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def update_news_now(force=False):
    """
    Manually triggers a news update.
    If force is True, it will bypass the 50-minute freshness check.
    """
    # Check if data exists and is fresh (e.g. < 50 mins old)
    if not force and os.path.exists(NEWS_DATA_FILE):
        file_mod_time = datetime.fromtimestamp(os.path.getmtime(NEWS_DATA_FILE))
        time_diff = datetime.now() - file_mod_time
        if time_diff.total_seconds() < 50 * 60:  # 50 minutes
            print(f"[{datetime.now()}] News data is fresh (updated {int(time_diff.total_seconds() // 60)} mins ago). Skipping.")
            return

    fetch_and_process_news()
