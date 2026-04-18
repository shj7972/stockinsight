#!/usr/bin/env python3
"""
Weekly Newsletter Sender — Stock Insight AI
============================================
매주 월요일 GitHub Actions에서 실행됩니다.
static/newsletter_subscribers.json 의 구독자에게
주간 시장 요약 이메일을 발송합니다.

필요한 환경 변수 (GitHub Secrets):
  RESEND_API_KEY   - Resend API 키 (resend.com 에서 발급)
  NEWSLETTER_FROM  - 발신 이메일 (기본: newsletter@stock-insight.app)
                     Resend 대시보드에서 도메인 인증 필요
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUBSCRIBERS_FILE = os.path.join(BASE_DIR, "static", "newsletter_subscribers.json")
PICKS_FILE       = os.path.join(BASE_DIR, "static", "stock_picks.json")
NEWS_FILE        = os.path.join(BASE_DIR, "static", "news_data.json")

RESEND_API_KEY   = os.environ.get("RESEND_API_KEY", "")
FROM_EMAIL       = os.environ.get("NEWSLETTER_FROM", "newsletter@stock-insight.app")
SITE_URL         = "https://stock-insight.app"


# ── 데이터 로드 ────────────────────────────────────────────────────────────────

def load_subscribers() -> list[dict]:
    if not os.path.exists(SUBSCRIBERS_FILE):
        return []
    with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
        subs = json.load(f)
    return [s for s in subs if s.get("active", True)]


def load_picks() -> dict:
    if not os.path.exists(PICKS_FILE):
        return {}
    with open(PICKS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_news() -> list[dict]:
    if not os.path.exists(NEWS_FILE):
        return []
    with open(NEWS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ── 이메일 본문 생성 ──────────────────────────────────────────────────────────

def _pick_row(pick: dict) -> str:
    rp = pick.get("return_pct")
    rp_html = ""
    if rp is not None:
        color = "#4ade80" if rp >= 0 else "#f87171"
        rp_html = f'<span style="color:{color};font-weight:700;">{rp:+.2f}%</span>'
    ticker_clean = pick["ticker"].replace(".KS", "").replace(".KQ", "")
    flag = "🇺🇸" if pick.get("market") == "US" else "🇰🇷"
    return (
        f'<tr style="border-bottom:1px solid #1e293b;">'
        f'<td style="padding:8px 10px;color:#94a3b8;">{flag}</td>'
        f'<td style="padding:8px 10px;">'
        f'<a href="{SITE_URL}/stock/{pick["ticker"]}" style="color:#38bdf8;text-decoration:none;font-weight:600;">'
        f'{ticker_clean}</a></td>'
        f'<td style="padding:8px 10px;color:#94a3b8;">{pick["name"]}</td>'
        f'<td style="padding:8px 10px;text-align:right;">{rp_html if rp_html else "<span style=\"color:#475569;\">집계중</span>"}</td>'
        f'</tr>'
    )


def build_email_html(subscriber_email: str) -> str:
    today    = datetime.now().strftime("%Y년 %m월 %d일")
    week_str = datetime.now().strftime("%Y년 %m월 %d일")

    # ── 종목 발굴 픽 ──
    picks_data   = load_picks()
    picks_history = picks_data.get("picks_history", [])
    latest_picks = picks_history[0] if picks_history else {}
    us_picks     = latest_picks.get("us_picks", [])[:3]
    kr_picks     = latest_picks.get("kr_picks", [])[:3]
    picks_date   = latest_picks.get("date", today)

    picks_rows = "".join(_pick_row(p) for p in (us_picks + kr_picks))
    picks_section = ""
    if picks_rows:
        picks_section = f"""
        <div style="margin-bottom:28px;">
            <h2 style="font-size:16px;font-weight:700;color:#e2e8f0;margin:0 0 12px 0;
                border-left:3px solid #38bdf8;padding-left:10px;">
                🔍 이번 주 AI 종목 발굴 ({picks_date})
            </h2>
            <table style="width:100%;border-collapse:collapse;font-size:13px;">
                <thead>
                    <tr style="color:#475569;font-size:11px;">
                        <th style="padding:6px 10px;text-align:left;"></th>
                        <th style="padding:6px 10px;text-align:left;">티커</th>
                        <th style="padding:6px 10px;text-align:left;">종목명</th>
                        <th style="padding:6px 10px;text-align:right;">수익률</th>
                    </tr>
                </thead>
                <tbody>{picks_rows}</tbody>
            </table>
            <p style="margin:10px 0 0;font-size:11px;color:#475569;">
                * 수익률은 추천 시점 대비 현재가 기준입니다.
                <a href="{SITE_URL}/stock-discovery" style="color:#38bdf8;">전체 성과 보기 →</a>
            </p>
        </div>
        """

    # ── 뉴스 상위 3개 ──
    news_items = load_news()[:3]
    news_rows = ""
    for item in news_items:
        title   = item.get("title", "")
        link    = item.get("link", "#")
        source  = item.get("source", "")
        sentiment = item.get("sentiment_label", "")
        s_color = "#4ade80" if "긍정" in sentiment or "positive" in sentiment.lower() else \
                  "#f87171" if "부정" in sentiment or "negative" in sentiment.lower() else "#94a3b8"
        news_rows += (
            f'<li style="margin-bottom:10px;padding-bottom:10px;border-bottom:1px solid #1e293b;">'
            f'<a href="{link}" style="color:#e2e8f0;text-decoration:none;font-size:13px;font-weight:500;"'
            f' target="_blank">{title}</a>'
            f'<div style="margin-top:4px;font-size:11px;color:#475569;">'
            f'{source} &nbsp;·&nbsp; <span style="color:{s_color};">{sentiment}</span></div>'
            f'</li>'
        )
    news_section = ""
    if news_rows:
        news_section = f"""
        <div style="margin-bottom:28px;">
            <h2 style="font-size:16px;font-weight:700;color:#e2e8f0;margin:0 0 12px 0;
                border-left:3px solid #818cf8;padding-left:10px;">
                📰 이번 주 주요 뉴스
            </h2>
            <ul style="list-style:none;margin:0;padding:0;">{news_rows}</ul>
            <p style="margin:10px 0 0;font-size:11px;color:#475569;">
                <a href="{SITE_URL}" style="color:#38bdf8;">더 많은 뉴스 보기 →</a>
            </p>
        </div>
        """

    # ── 일일 리포트 링크 ──
    today_iso = datetime.now().strftime("%Y-%m-%d")
    report_section = f"""
    <div style="margin-bottom:28px;padding:16px;background:#0f172a;border-radius:12px;border:1px solid #1e293b;">
        <h2 style="font-size:15px;font-weight:700;color:#e2e8f0;margin:0 0 8px 0;">📋 오늘의 AI 시장 리포트</h2>
        <p style="color:#64748b;font-size:13px;margin:0 0 12px 0;">
            {today} 기준 주요 지수, 공포·탐욕 지수, 섹터 동향을 한눈에 확인하세요.
        </p>
        <a href="{SITE_URL}/daily-report/{today_iso}"
           style="display:inline-block;padding:8px 20px;background:linear-gradient(135deg,#3b82f6,#8b5cf6);
           color:white;border-radius:8px;text-decoration:none;font-size:13px;font-weight:600;">
            리포트 보기 →
        </a>
    </div>
    """

    # ── 전체 HTML 조립 ──
    unsubscribe_note = f'<p style="color:#334155;font-size:11px;margin:0;">수신을 원하지 않으시면 <a href="mailto:{FROM_EMAIL}?subject=unsubscribe&body={subscriber_email}" style="color:#475569;">수신 거부</a>해 주세요.</p>'

    return f"""<!DOCTYPE html>
<html lang="ko">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Stock Insight AI 주간 인사이트</title></head>
<body style="margin:0;padding:0;background:#020917;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
<div style="max-width:600px;margin:0 auto;padding:20px;">

    <!-- 헤더 -->
    <div style="text-align:center;padding:28px 20px 20px;margin-bottom:24px;
        background:linear-gradient(135deg,rgba(56,189,248,0.08),rgba(139,92,246,0.08));
        border:1px solid rgba(56,189,248,0.15);border-radius:16px;">
        <div style="font-size:32px;margin-bottom:8px;">📈</div>
        <h1 style="margin:0 0 6px;font-size:22px;font-weight:800;
            background:linear-gradient(90deg,#38bdf8,#a78bfa);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            background-clip:text;">Stock Insight AI</h1>
        <p style="color:#64748b;font-size:13px;margin:0;">주간 투자 인사이트 · {week_str}</p>
    </div>

    <!-- 본문 -->
    <div style="background:#0f1629;border:1px solid #1e293b;border-radius:16px;padding:24px;margin-bottom:16px;">
        {picks_section}
        {news_section}
        {report_section}
    </div>

    <!-- 바로가기 버튼 -->
    <div style="display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap;">
        <a href="{SITE_URL}/stock-discovery" style="flex:1;min-width:120px;display:block;padding:10px;text-align:center;
            background:#0f1629;border:1px solid #1e293b;border-radius:10px;
            color:#38bdf8;text-decoration:none;font-size:12px;font-weight:600;">🔍 종목 발굴</a>
        <a href="{SITE_URL}/fear-greed-index" style="flex:1;min-width:120px;display:block;padding:10px;text-align:center;
            background:#0f1629;border:1px solid #1e293b;border-radius:10px;
            color:#818cf8;text-decoration:none;font-size:12px;font-weight:600;">😨 공포·탐욕</a>
        <a href="{SITE_URL}/blog" style="flex:1;min-width:120px;display:block;padding:10px;text-align:center;
            background:#0f1629;border:1px solid #1e293b;border-radius:10px;
            color:#4ade80;text-decoration:none;font-size:12px;font-weight:600;">📝 블로그</a>
        <a href="{SITE_URL}/etf-explorer" style="flex:1;min-width:120px;display:block;padding:10px;text-align:center;
            background:#0f1629;border:1px solid #1e293b;border-radius:10px;
            color:#fbbf24;text-decoration:none;font-size:12px;font-weight:600;">🔭 ETF 탐험가</a>
    </div>

    <!-- 푸터 -->
    <div style="text-align:center;padding:16px;color:#334155;font-size:11px;">
        <p style="margin:0 0 6px;">
            <a href="{SITE_URL}" style="color:#475569;text-decoration:none;">stock-insight.app</a>
            &nbsp;·&nbsp;
            <a href="{SITE_URL}/privacy-policy" style="color:#475569;text-decoration:none;">개인정보처리방침</a>
        </p>
        {unsubscribe_note}
        <p style="color:#1e293b;font-size:10px;margin:8px 0 0;">
            ⚠️ 본 뉴스레터의 내용은 투자 권유가 아닙니다. 모든 투자 결정은 본인 판단으로 하시기 바랍니다.
        </p>
    </div>
</div>
</body>
</html>"""


# ── Resend API 발송 ───────────────────────────────────────────────────────────

def send_email(to: str, subject: str, html: str) -> bool:
    """Resend API로 단일 이메일을 발송합니다. 성공 시 True 반환."""
    payload = json.dumps({
        "from":    FROM_EMAIL,
        "to":      [to],
        "subject": subject,
        "html":    html,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type":  "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status in (200, 201)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"  [HTTP {e.code}] {body[:200]}")
        return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


# ── 메인 ─────────────────────────────────────────────────────────────────────

def main():
    if not RESEND_API_KEY:
        print("ERROR: RESEND_API_KEY 환경 변수가 설정되지 않았습니다.")
        print("  resend.com 에서 API 키를 발급 받고 GitHub Secrets에 RESEND_API_KEY 로 등록하세요.")
        sys.exit(1)

    subscribers = load_subscribers()
    if not subscribers:
        print("구독자가 없습니다. 종료합니다.")
        return

    today_iso = datetime.now().strftime("%Y-%m-%d")
    subject   = f"📈 Stock Insight AI 주간 인사이트 — {datetime.now().strftime('%m월 %d일')}"

    print(f"[{today_iso}] 뉴스레터 발송 시작 — {len(subscribers)}명")

    success, fail = 0, 0
    for sub in subscribers:
        email = sub.get("email", "")
        if not email:
            continue
        html = build_email_html(email)
        ok   = send_email(email, subject, html)
        if ok:
            success += 1
            print(f"  ✓ {email}")
        else:
            fail += 1
            print(f"  ✗ {email} (실패)")
        time.sleep(0.3)  # Resend rate limit 여유

    print(f"\n완료: 성공 {success}개 / 실패 {fail}개 / 전체 {len(subscribers)}개")
    if fail > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
