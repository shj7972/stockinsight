"""
Reality Gap Score Engine
========================
주가 모멘텀과 펀더멘털 모멘텀의 괴리를 측정해 저평가/과열 종목을 발굴합니다.

- 매일 아침 GHA에서 실행되어 static/reality_gap.json 스냅샷 생성
- 웹(/reality-gap)은 이 JSON만 읽어서 렌더 (실시간 API 호출 없음)

Score 산식 (v1):
    price_momentum = 20일 수익률(0.6) + 60일 수익률(0.4)   → 섹터 내 Z-score
    fund_momentum  = 매출YoY(0.4) + 영업이익YoY(0.3) + 마진개선(0.15) + FCF축적(0.15)  → 섹터 내 Z-score
    gap_score      = clamp( (fund_z - price_z) * 스케일, -100 ~ +100 )

    +50 이상: Positive Gap (주가↓ + 펀더멘털↑) → 저평가 후보
    -50 이하: Negative Gap (주가↑ + 펀더멘털↓) → 과열 경계
"""

import os
import json
import math
import time
import logging
import warnings
from datetime import datetime

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
yf_logger = logging.getLogger('yfinance')
yf_logger.disabled = True

import yfinance as yf

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, "static", "reality_gap.json")

# 유니버스 재사용 (stock_discovery_manager의 US/KR 정의)
try:
    from stock_discovery_manager import US_UNIVERSE, KR_UNIVERSE
except ImportError:
    US_UNIVERSE, KR_UNIVERSE = [], []

# ── 가중치 (v1 고정) ─────────────────────────────────────────────────────
W_P20, W_P60 = 0.6, 0.4          # 가격 모멘텀 내부 가중치
W_REV, W_OI, W_MARGIN, W_FCF = 0.4, 0.3, 0.15, 0.15  # 펀더멘털 내부 가중치

# 펀더멘털 YoY 계산 시 분모가 지나치게 작은 케이스 방지 (초기기업 왜곡)
# yfinance 재무제표는 원화 표기(원 단위). 30조가 아니라 300억 = 3e10
MIN_BASE_REVENUE = 30_000_000_000         # 300억원 (KR)
MIN_BASE_US = 30_000_000                  # 3백만 달러 (US)

# Z-score → 점수 변환 스케일
SCORE_SCALE = 40.0
CLIP_LIMIT = 100.0

# Positive/Negative Gap 판정 임계 (score 기준) — 실측 분포 기반 ±35
POSITIVE_GAP_LINE = 35
NEGATIVE_GAP_LINE = -35

# 결과 유지 기간
HISTORY_MAX = 30      # 최근 30일 히스토리 보관


# ── 펀더멘털 추출 ─────────────────────────────────────────────────────────
def _safe_yoy(curr, base, min_base):
    """YoY(%) 계산. 분모 작거나 None이면 None."""
    if curr is None or base is None or pd.isna(curr) or pd.isna(base):
        return None
    try:
        if abs(base) < min_base:
            return None
        return float((curr - base) / abs(base) * 100)
    except (ZeroDivisionError, TypeError):
        return None


def fetch_fundamentals(ticker: str, market: str) -> dict:
    """yfinance로 펀더멘털 모멘텀 원시값 수집. 종목당 ~1~2초."""
    min_base = MIN_BASE_US if market == "US" else MIN_BASE_REVENUE
    out = {
        "rev_yoy": None, "op_yoy": None, "margin_chg": None,
        "fcf_growth": None, "rev_growth_info": None, "earn_growth_info": None,
        "gross_margin": None, "peg": None,
    }
    try:
        t = yf.Ticker(ticker)
        info = t.info
        out["rev_growth_info"] = _pct(info.get("revenueGrowth"))
        out["earn_growth_info"] = _pct(info.get("earningsGrowth"))
        out["gross_margin"] = _pct(info.get("grossMargins"))
        out["peg"] = _plain(info.get("pegRatio"))

        fin = t.quarterly_income_stmt
        if fin is None or fin.empty:
            return out

        # Total Revenue YoY (최근 분기 vs 4분기 전)
        rev_row = _find_row(fin, ["Total Revenue", "Revenues"])
        if rev_row:
            rev = fin.loc[rev_row].dropna()
            if len(rev) >= 5:
                out["rev_yoy"] = _safe_yoy(rev.iloc[0], rev.iloc[4], min_base)

        # Operating Income YoY
        op_row = _find_row(fin, ["Operating Income"])
        if op_row:
            oi = fin.loc[op_row].dropna()
            if len(oi) >= 5:
                # 음→양 전환 보정: 분모 음수 방지 (절대값 사용)
                out["op_yoy"] = _safe_yoy(oi.iloc[0], oi.iloc[4], min_base)

        # Gross Margin 전분기 대비 변화
        try:
            cr = _find_row(fin, ["Gross Profit"])
            if cr and rev_row:
                gross = fin.loc[cr].dropna()
                if len(gross) >= 2 and len(rev) >= 2 and rev.iloc[0] != 0 and rev.iloc[1] != 0:
                    m0 = gross.iloc[0] / rev.iloc[0]
                    m1 = gross.iloc[1] / rev.iloc[1]
                    out["margin_chg"] = float((m0 - m1) * 100)   # %p 변화
        except Exception:
            pass

        # FCF 트렌드 (최근 4분기 FCF 합 vs 이전 4분기)
        try:
            cf = yf.Ticker(ticker).quarterly_cashflow
            fc_row = _find_row(cf, ["Free Cash Flow"])
            if fc_row:
                fcf = cf.loc[fc_row].dropna()
                if len(fcf) >= 8:
                    recent = fcf.iloc[:4].sum()
                    prev = fcf.iloc[4:8].sum()
                    if abs(prev) > min_base:
                        out["fcf_growth"] = float((recent - prev) / abs(prev) * 100)
        except Exception:
            pass
    except Exception as e:
        logger.debug(f"{ticker} fundamentals 실패: {e}")
    return out


def fetch_price_momentum(ticker: str) -> dict:
    """20일/60일 수익률."""
    out = {"p20": None, "p60": None, "last": None}
    try:
        t = yf.Ticker(ticker)
        h = t.history(period="75d")
        if h is None or h.empty:
            return out
        close = h["Close"].dropna()
        if len(close) < 21:
            return out
        last = float(close.iloc[-1])
        out["last"] = last
        out["p20"] = float((last / close.iloc[-21] - 1) * 100) if len(close) > 20 else None
        if len(close) > 60:
            out["p60"] = float((last / close.iloc[-61] - 1) * 100)
    except Exception as e:
        logger.debug(f"{ticker} price 실패: {e}")
    return out


# ── 유틸 ───────────────────────────────────────────────────────────────────
def _find_row(df: pd.DataFrame, keywords: list):
    for kw in keywords:
        matches = [i for i in df.index if kw in str(i)]
        if matches:
            return matches[0]
    return None


def _pct(x):
    """info 값(0~1) → %로. None 가능. 극단값(|x|>1000%)은 None 처리 (초기기업 왜곡 방지)."""
    try:
        if x is None or pd.isna(x):
            return None
        v = float(x) * 100
        if abs(v) > 1000:
            return None
        return v
    except (TypeError, ValueError):
        return None


def _plain(x):
    try:
        if x is None or pd.isna(x):
            return None
        return float(x)
    except (TypeError, ValueError):
        return None


def _safe_wei_sum(parts: list, weights: list) -> float:
    """None이 아닌 항목만 가중치 재정규화해서 합산. 모두 None이면 None."""
    valid_w, valid_v = [], []
    for v, w in zip(parts, weights):
        if v is not None and not (isinstance(v, float) and (math.isnan(v) or math.isinf(v))):
            # 영업이익 YoY 음→양 전환 보정 (전기 음, 현재 양이면 가중 2배)
            valid_w.append(w * 2 if v is not None and v > 200 else w)
            valid_v.append(min(max(v, -300), 300))   # 발산 억제 clip
    if not valid_v:
        return None
    # 각 항목을 tanh로 squashing 후 합산 (±300%라도 안정적으로 ±1 근처)
    squashed = [math.tanh(v / 100) for v in valid_v]
    return sum(w * s for s, w in zip(squashed, valid_w)) / sum(valid_w)   # -1 ~ +1


# ── 종목 단위 계산 ─────────────────────────────────────────────────────────
def rank_by_value(data: list, key: str, higher_better: bool = True):
    """list[dict] → 섹터 내 순위 계산 (None 제외)."""
    vals = [d[key] for d in data if d[key] is not None]
    if not vals:
        return {}
    sorted_vals = sorted(set(vals), reverse=higher_better)
    return {d["ticker"]: (sorted_vals.index(d[key]) + 1) / len(sorted_vals) for d in data if d[key] is not None}


def compute_stock(ticker: str, name: str, sector: str, market: str):
    """단일 종목 Reality Gap 원시 계산. 실패 시 None."""
    f = fetch_fundamentals(ticker, market)
    p = fetch_price_momentum(ticker)
    if p["last"] is None:
        return None
    if all(v is None for v in [f["rev_yoy"], f["op_yoy"], f["margin_chg"], f["fcf_growth"], f["rev_growth_info"]]):
        return None

    # 펀더멘털 모멘텀 (-1 ~ +1)
    fund_raw = _safe_wei_sum(
        [f["rev_yoy"], f["op_yoy"], f["margin_chg"] or 0, f["fcf_growth"], f["rev_growth_info"] or 0],
        [W_REV, W_OI, W_MARGIN, W_FCF, W_REV * 0.5],   # info 기반 값 보조 가중
    )
    # 가격 모멘텀 (-1 ~ +1, tanh squash)
    p20 = p["p20"] if p["p20"] is not None else 0
    p60 = p["p60"] if p["p60"] is not None else 0
    price_raw = (W_P20 * math.tanh(p20 / 25) + W_P60 * math.tanh(p60 / 40)) / (W_P20 + W_P60)

    # Gap = 펀더멘털 강세 − 가격 강세
    if fund_raw is None:
        return None
    gap = fund_raw - price_raw   # -2 ~ +2 범위
    score = max(-CLIP_LIMIT, min(CLIP_LIMIT, round(gap * SCORE_SCALE * 1.28, 1)))   # ±100 클리핑

    if score >= POSITIVE_GAP_LINE:
        label = "positive_gap"     # 저평가 후보
    elif score <= NEGATIVE_GAP_LINE:
        label = "negative_gap"     # 과열 경계
    else:
        label = "aligned"

    return {
        "ticker": ticker,
        "name": name,
        "sector": sector,
        "market": market,
        "price": p["last"],
        "p20": p["p20"],
        "p60": p["p60"],
        "price_raw": round(price_raw, 3),
        "fund_raw": round(fund_raw, 3),
        "score": score,
        "label": label,
        # 원시 펀더멘털 (표 표시용)
        "rev_yoy": _r1(f["rev_yoy"]),
        "op_yoy": _r1(f["op_yoy"]),
        "margin_chg": _r1(f["margin_chg"]),
        "fcf_growth": _r1(f["fcf_growth"]),
        "peg": _r1(f["peg"]),
    }


def _r1(x):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return None
    return round(float(x), 1)


# ── 전체 실행 ─────────────────────────────────────────────────────────────
def run(update_history: bool = True) -> dict:
    """유니버스 전체 계산 → static/reality_gap.json 저장."""
    universe = [(t, n, s, "US") for t, n, s in US_UNIVERSE] + \
               [(t, n, s, "KR") for t, n, s in KR_UNIVERSE]
    logger.info(f"Reality Gap 계산 시작: {len(universe)}종")

    results = []
    t0 = time.time()
    for ticker, name, sector, market in universe:
        r = compute_stock(ticker, name, sector, market)
        if r:
            results.append(r)
        time.sleep(0.2)   # rate limit 배려

    # 섹터 내 순위 추가 (산점도/표에서 상대 비교용)
    try:
        price_rank = rank_by_value(results, "price_raw", higher_better=True)
        fund_rank = rank_by_value(results, "fund_raw", higher_better=True)
        for r in results:
            r["price_rank_pct"] = round(price_rank.get(r["ticker"], 0.5) * 100, 1)
            r["fund_rank_pct"] = round(fund_rank.get(r["ticker"], 0.5) * 100, 1)
    except Exception as e:
        logger.debug(f"rank 실패: {e}")

    results.sort(key=lambda x: x["score"], reverse=True)

    # 히스토리 누적 (최근 30일)
    today = datetime.now().strftime("%Y-%m-%d")
    history = []
    prev = None
    if OUTPUT_FILE and os.path.exists(OUTPUT_FILE) and update_history:
        try:
            prev = json.load(open(OUTPUT_FILE, encoding="utf-8"))
            history = prev.get("history", [])
        except Exception:
            pass
    summary_today = {
        "date": today,
        "positive_count": sum(1 for r in results if r["label"] == "positive_gap"),
        "negative_count": sum(1 for r in results if r["label"] == "negative_gap"),
        "avg_score": round(sum(r["score"] for r in results) / max(1, len(results)), 1),
    }
    history = [h for h in history if h["date"] != today][:HISTORY_MAX - 1]
    history.insert(0, summary_today)

    output = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "generated_at_kst": datetime.now().strftime("%Y-%m-%d %H:%M KST"),
        "total_stocks": len(results),
        "thresholds": {
            "positive_gap": POSITIVE_GAP_LINE,
            "negative_gap": NEGATIVE_GAP_LINE,
        },
        "summary": summary_today,
        "history": history,
        "stocks": results,
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=1)
    logger.info(f"Reality Gap 완료: {len(results)}종, {time.time()-t0:.1f}초, positive={summary_today['positive_count']}, negative={summary_today['negative_count']}")
    return output


if __name__ == "__main__":
    out = run()
    pos = [s for s in out["stocks"] if s["label"] == "positive_gap"][:5]
    neg = [s for s in out["stocks"] if s["label"] == "negative_gap"][:5]
    print("\n=== Positive Gap TOP 5 (주가↓+펀더멘털↑ = 저평가 후보) ===")
    for s in pos:
        print(f"{s['name']} ({s['ticker']}) score={s['score']:+.0f} — 펀더멘털 {s['fund_raw']:+.2f} / 가격 {s['price_raw']:+.2f}")
    print("\n=== Negative Gap TOP 5 (주가↑+펀더멘털↓ = 과열 경계) ===")
    for s in neg:
        print(f"{s['name']} ({s['ticker']}) score={s['score']:+.0f} — 펀더멘털 {s['fund_raw']:+.2f} / 가격 {s['price_raw']:+.2f}")