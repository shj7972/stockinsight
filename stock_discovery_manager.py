"""
Stock Discovery Manager — AI 앙상블 종목 발굴
================================================
매일 아침 8시 (KST) GitHub Actions에서 실행되어
US 3종목 + KR 3종목을 추천하고 static/stock_picks.json에 저장합니다.

모델 앙상블:
  1. RandomForest (RF)
  2. XGBoost (XGB) — 없을 경우 GradientBoosting으로 대체
  3. MLP (Multi-Layer Perceptron)
  4. Pseudo-LSTM (시계열 Lag Feature 기반 Deep MLP)

기술적 지표: RSI, MACD, 볼린저밴드, 거래량비율, 모멘텀, MA 괴리율
섹터 로테이션: 11개 섹터 ETF 1개월 수익률 기반 Z-score
"""

import os
import json
import time
import logging
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import requests
import yfinance as yf

try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

logger = logging.getLogger(__name__)

# ── 파일 경로 ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PICKS_FILE = os.path.join(BASE_DIR, "static", "stock_picks.json")
GITHUB_PICKS_URL = "https://raw.githubusercontent.com/shj7972/stockinsight/master/static/stock_picks.json"

PICKS_MAX_DAYS = 7   # 최대 보관 일수
CACHE_TTL = 30 * 60  # 캐시 TTL (30분)

# ── 종목 유니버스 ────────────────────────────────────────────────────────────
# (ticker, 표시명, 섹터)
US_UNIVERSE = [
    # Technology
    ("AAPL",  "Apple",          "Technology"),
    ("MSFT",  "Microsoft",      "Technology"),
    ("NVDA",  "NVIDIA",         "Technology"),
    ("AMD",   "AMD",            "Technology"),
    ("INTC",  "Intel",          "Technology"),
    ("AVGO",  "Broadcom",       "Technology"),
    ("QCOM",  "Qualcomm",       "Technology"),
    ("TXN",   "Texas Instr.",   "Technology"),
    ("ADBE",  "Adobe",          "Technology"),
    ("CRM",   "Salesforce",     "Technology"),
    ("ORCL",  "Oracle",         "Technology"),
    # Communication / Consumer Discretionary
    ("GOOGL", "Alphabet",       "Communication Services"),
    ("META",  "Meta",           "Communication Services"),
    ("NFLX",  "Netflix",        "Communication Services"),
    ("DIS",   "Disney",         "Communication Services"),
    ("AMZN",  "Amazon",         "Consumer Discretionary"),
    ("TSLA",  "Tesla",          "Consumer Discretionary"),
    ("NKE",   "Nike",           "Consumer Discretionary"),
    ("MCD",   "McDonald's",     "Consumer Discretionary"),
    # Healthcare
    ("UNH",   "UnitedHealth",   "Healthcare"),
    ("JNJ",   "J&J",           "Healthcare"),
    ("ABBV",  "AbbVie",         "Healthcare"),
    ("MRK",   "Merck",          "Healthcare"),
    ("PFE",   "Pfizer",         "Healthcare"),
    ("LLY",   "Eli Lilly",      "Healthcare"),
    # Financials
    ("JPM",   "JPMorgan",       "Financials"),
    ("BAC",   "BofA",          "Financials"),
    ("GS",    "Goldman Sachs",  "Financials"),
    ("V",     "Visa",           "Financials"),
    ("MA",    "Mastercard",     "Financials"),
    # Energy
    ("XOM",   "ExxonMobil",     "Energy"),
    ("CVX",   "Chevron",        "Energy"),
    # Consumer Staples
    ("WMT",   "Walmart",        "Consumer Staples"),
    ("COST",  "Costco",         "Consumer Staples"),
    ("PG",    "P&G",            "Consumer Staples"),
    ("KO",    "Coca-Cola",      "Consumer Staples"),
    # Industrials
    ("CAT",   "Caterpillar",    "Industrials"),
    ("HON",   "Honeywell",      "Industrials"),
    ("BA",    "Boeing",         "Industrials"),
    # Materials / Real Estate / Utilities
    ("FCX",   "Freeport",       "Materials"),
    ("AMT",   "Amer. Tower",    "Real Estate"),
    ("NEE",   "NextEra Energy", "Utilities"),
]

KR_UNIVERSE = [
    # KOSPI — Technology / Semiconductor
    ("005930.KS", "삼성전자",       "Technology"),
    ("000660.KS", "SK하이닉스",    "Technology"),
    ("066570.KS", "LG전자",        "Technology"),
    ("009150.KS", "삼성전기",      "Technology"),
    ("034220.KS", "LG디스플레이",  "Technology"),
    # KOSPI — Chemicals / Battery
    ("051910.KS", "LG화학",        "Materials"),
    ("096770.KS", "SK이노베이션",   "Energy"),
    ("003670.KS", "포스코퓨처엠",  "Materials"),
    # KOSPI — Auto
    ("005380.KS", "현대차",        "Consumer Discretionary"),
    ("000270.KS", "기아",          "Consumer Discretionary"),
    ("012330.KS", "현대모비스",    "Consumer Discretionary"),
    # KOSPI — Healthcare / Bio
    ("207940.KS", "삼성바이오로직스", "Healthcare"),
    ("068270.KS", "셀트리온",      "Healthcare"),
    # KOSPI — Finance
    ("105560.KS", "KB금융",        "Financials"),
    ("055550.KS", "신한지주",      "Financials"),
    ("086790.KS", "하나금융지주",  "Financials"),
    # KOSPI — Communication / Platform
    ("035420.KS", "NAVER",         "Communication Services"),
    ("035720.KS", "카카오",        "Communication Services"),
    # KOSPI — Industrials
    ("028260.KS", "삼성물산",      "Industrials"),
    ("034730.KS", "SK",            "Industrials"),
    ("011200.KS", "HMM",           "Industrials"),
    # KOSPI — Consumer Staples
    ("097950.KS", "CJ제일제당",    "Consumer Staples"),
    # KOSDAQ — Secondary market (more volatile, high opportunity)
    ("247540.KQ", "에코프로비엠",  "Materials"),
    ("086520.KQ", "에코프로",      "Materials"),
    ("196170.KQ", "알테오젠",      "Healthcare"),
    ("145020.KQ", "휴젤",          "Healthcare"),
]

# ── 섹터 ETF (Z-score 기반 섹터 로테이션) ────────────────────────────────────
SECTOR_ETFS = {
    "Technology":              "XLK",
    "Healthcare":              "XLV",
    "Financials":              "XLF",
    "Energy":                  "XLE",
    "Consumer Discretionary":  "XLY",
    "Consumer Staples":        "XLP",
    "Industrials":             "XLI",
    "Materials":               "XLB",
    "Utilities":               "XLU",
    "Real Estate":             "XLRE",
    "Communication Services":  "XLC",
}

# ── 피처 컬럼 정의 ────────────────────────────────────────────────────────────
FEATURE_COLS = [
    "rsi", "macd_hist", "macd_cross",
    "bb_pos", "bb_width",
    "vol_ratio", "vol_trend",
    "mom5", "mom20", "mom60",
    "above_ma50", "dist_ma50", "dist_ma200",
    "atr_ratio",
    # Lag (LSTM-style temporal features)
    "rsi_lag1", "rsi_lag2", "rsi_lag3", "rsi_lag5",
    "macd_lag1", "macd_lag2", "macd_lag3", "macd_lag5",
    "vol_lag1",  "vol_lag2",  "vol_lag3",  "vol_lag5",
]
LAG_COLS = [c for c in FEATURE_COLS if "lag" in c]

# ── 캐시 ─────────────────────────────────────────────────────────────────────
_picks_cache = {"data": None, "ts": 0}


# ═══════════════════════════════════════════════════════════════════════════════
# 피처 계산
# ═══════════════════════════════════════════════════════════════════════════════

def _calc_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-9)
    return 100 - (100 / (1 + rs))


def _calc_features(df: pd.DataFrame) -> pd.DataFrame:
    """OHLCV DataFrame → 피처 DataFrame"""
    close  = df["Close"].astype(float)
    volume = df["Volume"].astype(float)
    high   = df["High"].astype(float)
    low    = df["Low"].astype(float)

    out = df.copy()

    # RSI
    out["rsi"] = _calc_rsi(close)

    # MACD
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    out["macd_hist"]  = ((macd_line - signal_line) / close.replace(0, 1e-9)).clip(-0.1, 0.1)
    out["macd_cross"] = (macd_line > signal_line).astype(int)

    # 볼린저밴드
    sma20 = close.rolling(20).mean()
    std20 = close.rolling(20).std()
    upper = sma20 + 2 * std20
    lower_band = sma20 - 2 * std20
    band_width = (upper - lower_band).replace(0, 1e-9)
    out["bb_pos"]   = ((close - lower_band) / band_width).clip(0, 1)
    out["bb_width"] = (band_width / sma20.replace(0, 1e-9)).clip(0, 0.5)

    # 거래량
    vol_ma20 = volume.rolling(20).mean().replace(0, 1e-9)
    out["vol_ratio"] = (volume / vol_ma20).clip(0, 10)
    out["vol_trend"] = (volume.rolling(5).mean() / vol_ma20).clip(0, 5)

    # 모멘텀
    out["mom5"]  = close.pct_change(5).clip(-0.3, 0.3)
    out["mom20"] = close.pct_change(20).clip(-0.5, 0.5)
    out["mom60"] = close.pct_change(60).clip(-0.7, 0.7)

    # 이동평균 괴리율
    ma50  = close.rolling(50).mean().replace(0, 1e-9)
    ma200 = close.rolling(200).mean().replace(0, 1e-9)
    out["above_ma50"]  = (close > ma50).astype(float)
    out["dist_ma50"]   = (close / ma50 - 1).clip(-0.5, 0.5)
    out["dist_ma200"]  = (close / ma200 - 1).clip(-0.5, 0.5)

    # ATR (변동성)
    hl = high - low
    hc = (high - close.shift()).abs()
    lc = (low  - close.shift()).abs()
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    out["atr_ratio"] = (atr / close.replace(0, 1e-9)).clip(0, 0.2)

    # Lag 피처 (LSTM-style)
    for lag in [1, 2, 3, 5]:
        out[f"rsi_lag{lag}"]  = out["rsi"].shift(lag)
        out[f"macd_lag{lag}"] = out["macd_hist"].shift(lag)
        out[f"vol_lag{lag}"]  = out["vol_ratio"].shift(lag)

    return out


# ═══════════════════════════════════════════════════════════════════════════════
# 섹터 Z-score
# ═══════════════════════════════════════════════════════════════════════════════

def _get_sector_zscores() -> dict:
    """11개 섹터 ETF 1개월 수익률 기반 Z-score 반환 {섹터명: z값}"""
    try:
        etfs = list(SECTOR_ETFS.values())
        raw = yf.download(etfs, period="3mo", auto_adjust=True, progress=False)
        close = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw

        if len(close) < 20:
            return {}

        ret_1m = close.iloc[-1] / close.iloc[-20] - 1
        mean_r = ret_1m.mean()
        std_r  = ret_1m.std() if ret_1m.std() > 0 else 1.0
        zscores = ((ret_1m - mean_r) / std_r).to_dict()

        etf_to_sector = {v: k for k, v in SECTOR_ETFS.items()}
        return {etf_to_sector.get(etf, etf): float(z) for etf, z in zscores.items()}
    except Exception as e:
        logger.warning(f"Sector Z-score 계산 실패: {e}")
        return {}


# ═══════════════════════════════════════════════════════════════════════════════
# ML 앙상블 예측
# ═══════════════════════════════════════════════════════════════════════════════

def _train_predict(df: pd.DataFrame) -> tuple[float, dict]:
    """
    주어진 OHLCV DataFrame에 대해 앙상블 예측을 수행합니다.
    반환: (ensemble_score 0~1, {model_name: score} 딕셔너리)
    """
    df_feat = _calc_features(df.copy())

    # 타겟: 5일 선행 수익률 > 1.5%
    df_feat["target"] = (df_feat["Close"].shift(-5) / df_feat["Close"] - 1 > 0.015).astype(int)
    df_feat = df_feat.dropna(subset=FEATURE_COLS + ["target"])

    if len(df_feat) < 120:
        return 0.5, {}

    # 마지막 5일은 타겟이 미확정이므로 훈련에서 제외
    train = df_feat.iloc[:-5]
    latest_row = df_feat.iloc[-1:]

    X_tr = train[FEATURE_COLS].values
    y_tr = train["target"].values
    X_te = latest_row[FEATURE_COLS].values

    pos_count = int(y_tr.sum())
    neg_count = len(y_tr) - pos_count
    if pos_count < 15 or neg_count < 15:
        return 0.5, {}

    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.neural_network import MLPClassifier
    from sklearn.preprocessing import StandardScaler

    scaler = StandardScaler()
    X_tr_s = scaler.fit_transform(X_tr)
    X_te_s = scaler.transform(X_te)

    model_scores = {}

    # 1. Random Forest
    try:
        rf = RandomForestClassifier(
            n_estimators=100, max_depth=6, min_samples_leaf=5,
            class_weight="balanced", random_state=42, n_jobs=-1
        )
        rf.fit(X_tr_s, y_tr)
        model_scores["rf"] = float(rf.predict_proba(X_te_s)[0][1])
    except Exception:
        pass

    # 2. XGBoost (없으면 GradientBoosting)
    try:
        if HAS_XGB:
            xgb = XGBClassifier(
                n_estimators=100, max_depth=4, learning_rate=0.1,
                eval_metric="logloss", random_state=42, verbosity=0
            )
        else:
            xgb = GradientBoostingClassifier(
                n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42
            )
        xgb.fit(X_tr_s, y_tr)
        model_scores["xgb"] = float(xgb.predict_proba(X_te_s)[0][1])
    except Exception:
        pass

    # 3. MLP
    try:
        mlp = MLPClassifier(
            hidden_layer_sizes=(64, 32), max_iter=300,
            early_stopping=True, random_state=42
        )
        mlp.fit(X_tr_s, y_tr)
        model_scores["mlp"] = float(mlp.predict_proba(X_te_s)[0][1])
    except Exception:
        pass

    # 4. Pseudo-LSTM (Lag 피처 전용 Deep MLP — 시계열 패턴 학습)
    try:
        X_lag_tr = train[LAG_COLS].values
        X_lag_te = latest_row[LAG_COLS].values
        lag_scaler = StandardScaler()
        X_lag_tr_s = lag_scaler.fit_transform(X_lag_tr)
        X_lag_te_s = lag_scaler.transform(X_lag_te)
        lstm_mlp = MLPClassifier(
            hidden_layer_sizes=(48, 32, 16), max_iter=300,
            early_stopping=True, random_state=42
        )
        lstm_mlp.fit(X_lag_tr_s, y_tr)
        model_scores["lstm"] = float(lstm_mlp.predict_proba(X_lag_te_s)[0][1])
    except Exception:
        pass

    if not model_scores:
        return 0.5, {}

    ensemble = float(np.mean(list(model_scores.values())))
    return round(ensemble, 4), {k: round(v, 4) for k, v in model_scores.items()}


# ═══════════════════════════════════════════════════════════════════════════════
# 신호 요약 텍스트
# ═══════════════════════════════════════════════════════════════════════════════

def _signal_summary(rsi, macd_hist, bb_pos, vol_ratio, sector_z) -> str:
    parts = []
    if rsi < 30:
        parts.append("RSI 강한 과매도")
    elif rsi < 40:
        parts.append("RSI 과매도 진입")
    elif rsi < 50:
        parts.append("RSI 중립~반등")

    if macd_hist > 0:
        parts.append("MACD 골든크로스")
    elif macd_hist > -0.002:
        parts.append("MACD 반등 임박")

    if bb_pos < 0.2:
        parts.append("볼린저 하단 근접")
    elif bb_pos < 0.35:
        parts.append("볼린저 하단 탈출")

    if vol_ratio > 2.0:
        parts.append(f"거래량 급증 ×{vol_ratio:.1f}")
    elif vol_ratio > 1.4:
        parts.append("거래량 증가세")

    if sector_z > 1.0:
        parts.append(f"섹터 모멘텀 상위 (Z={sector_z:+.1f})")
    elif sector_z > 0.3:
        parts.append(f"섹터 양호 (Z={sector_z:+.1f})")

    return " · ".join(parts) if parts else "복합 기술적 신호"


# ═══════════════════════════════════════════════════════════════════════════════
# 종목 스크리닝
# ═══════════════════════════════════════════════════════════════════════════════

def _screen_stocks(universe: list, sector_zscores: dict, market: str) -> list:
    """주어진 유니버스를 스크리닝해서 상위 3종목 반환."""
    results = []
    tickers = [t for t, _, _ in universe]
    ticker_meta = {t: (n, s) for t, n, s in universe}

    # 배치 다운로드
    try:
        raw = yf.download(tickers, period="2y", auto_adjust=True, progress=False)
    except Exception as e:
        logger.error(f"Batch download failed ({market}): {e}")
        return []

    # MultiIndex 여부에 따라 처리
    if isinstance(raw.columns, pd.MultiIndex):
        # columns: (Price, Ticker)
        close_all  = raw["Close"]
        high_all   = raw["High"]
        low_all    = raw["Low"]
        volume_all = raw["Volume"]
    else:
        # 단일 티커인 경우 (유니버스 크기 1 — 거의 없음)
        t = tickers[0]
        close_all  = pd.DataFrame({t: raw["Close"]})
        high_all   = pd.DataFrame({t: raw["High"]})
        low_all    = pd.DataFrame({t: raw["Low"]})
        volume_all = pd.DataFrame({t: raw["Volume"]})

    for ticker in tickers:
        try:
            if ticker not in close_all.columns:
                continue

            c = close_all[ticker].dropna()
            if len(c) < 180:
                continue

            idx = c.index
            df_stock = pd.DataFrame({
                "Close":  c,
                "High":   high_all[ticker].reindex(idx),
                "Low":    low_all[ticker].reindex(idx),
                "Volume": volume_all[ticker].reindex(idx).fillna(0),
            }).dropna()

            if len(df_stock) < 180:
                continue

            # 최신 피처 계산 (빠른 체크)
            feat = _calc_features(df_stock.copy())
            feat = feat.dropna(subset=["rsi", "macd_hist", "bb_pos", "vol_ratio"])
            if len(feat) < 5:
                continue

            latest = feat.iloc[-1]
            rsi      = float(latest["rsi"])
            macd_h   = float(latest["macd_hist"])
            bb_pos   = float(latest["bb_pos"])
            vol_r    = float(latest["vol_ratio"])
            entry_px = float(latest["Close"])

            # 과매수 / 고점 근처 필터링
            if rsi > 72:
                continue
            if bb_pos > 0.88:
                continue

            name, sector = ticker_meta[ticker]
            sector_z = sector_zscores.get(sector, 0.0)

            # ML 앙상블 예측
            ensemble_score, model_scores = _train_predict(df_stock)

            # 최종 점수: 70% ML + 30% 섹터 Z-score (정규화)
            sector_norm = max(-2.0, min(2.0, sector_z)) / 2.0  # → -1 ~ +1
            final_score = 0.70 * ensemble_score + 0.30 * (sector_norm + 1.0) / 2.0

            results.append({
                "ticker":         ticker,
                "name":           name,
                "market":         market,
                "sector":         sector,
                "entry_price":    round(entry_px, 2),
                "rsi":            round(rsi, 1),
                "bb_pos":         round(bb_pos * 100, 1),
                "vol_ratio":      round(vol_r, 2),
                "macd_positive":  macd_h >= 0,
                "sector_zscore":  round(sector_z, 2),
                "ensemble_score": ensemble_score,
                "model_scores":   model_scores,
                "final_score":    round(final_score, 4),
                "signal_summary": _signal_summary(rsi, macd_h, bb_pos, vol_r, sector_z),
                "current_price":  None,
                "return_pct":     None,
            })

        except Exception as e:
            logger.debug(f"{ticker} 스크리닝 실패: {e}")

    # 점수 내림차순 정렬
    results.sort(key=lambda x: x["final_score"], reverse=True)

    # 섹터 다변화: 섹터당 1종목만 포함
    seen_sectors: set = set()
    diversified = []
    remainder = []
    for r in results:
        if r["sector"] not in seen_sectors:
            diversified.append(r)
            seen_sectors.add(r["sector"])
        else:
            remainder.append(r)

    top = diversified[:3]
    if len(top) < 3:
        top.extend(remainder[:3 - len(top)])

    return top[:3]


# ═══════════════════════════════════════════════════════════════════════════════
# 데이터 영속성
# ═══════════════════════════════════════════════════════════════════════════════

def _load_history() -> list:
    if not os.path.exists(PICKS_FILE):
        return []
    try:
        with open(PICKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("picks_history", [])
    except Exception:
        return []


def _save_history(history: list):
    os.makedirs(os.path.dirname(PICKS_FILE), exist_ok=True)
    with open(PICKS_FILE, "w", encoding="utf-8") as f:
        json.dump({"picks_history": history}, f, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
# 수익률 업데이트
# ═══════════════════════════════════════════════════════════════════════════════

def _update_returns(history: list) -> list:
    """표시 시점의 현재가를 가져와 수익률을 업데이트합니다."""
    all_tickers = set()
    for entry in history:
        for pick in entry.get("us_picks", []) + entry.get("kr_picks", []):
            all_tickers.add(pick["ticker"])

    if not all_tickers:
        return history

    prices: dict = {}
    try:
        raw = yf.download(list(all_tickers), period="5d", auto_adjust=True, progress=False)
        close = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw
        if isinstance(close, pd.DataFrame):
            # 티커별 마지막 유효값 사용 (US/KR 거래시간 차이로 인한 NaN 방지)
            latest = close.apply(lambda col: col.dropna().iloc[-1] if col.dropna().shape[0] > 0 else None)
            prices = {t: float(v) for t, v in latest.items() if v is not None and not pd.isna(v)}
        else:
            t = list(all_tickers)[0]
            prices = {t: float(close.dropna().iloc[-1])}
    except Exception as e:
        logger.warning(f"수익률 업데이트 실패: {e}")

    for entry in history:
        for pick in entry.get("us_picks", []) + entry.get("kr_picks", []):
            t = pick["ticker"]
            ep = pick.get("entry_price", 0)
            if t in prices and ep > 0:
                cur = prices[t]
                pick["current_price"] = round(cur, 2)
                pick["return_pct"] = round((cur - ep) / ep * 100, 2)

    return history


# ═══════════════════════════════════════════════════════════════════════════════
# 공개 API
# ═══════════════════════════════════════════════════════════════════════════════

def generate_daily_picks() -> dict:
    """
    전체 스크리닝 파이프라인을 실행하고 결과를 JSON에 저장합니다.
    GitHub Actions에서 매일 8시 KST에 호출됩니다.
    """
    logger.info("종목 발굴 스크리닝 시작...")

    sector_zscores = _get_sector_zscores()
    logger.info(f"섹터 Z-score 계산 완료: {len(sector_zscores)}개 섹터")

    us_picks = _screen_stocks(US_UNIVERSE, sector_zscores, "US")
    logger.info(f"US 스크리닝 완료: {len(us_picks)}개 선정")

    kr_picks = _screen_stocks(KR_UNIVERSE, sector_zscores, "KR")
    logger.info(f"KR 스크리닝 완료: {len(kr_picks)}개 선정")

    today = datetime.now().strftime("%Y-%m-%d")
    new_entry = {
        "date":          today,
        "generated_at":  datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "sector_top3":   sorted(sector_zscores.items(), key=lambda x: x[1], reverse=True)[:3],
        "us_picks":      us_picks,
        "kr_picks":      kr_picks,
    }

    history = _load_history()
    history = [h for h in history if h["date"] != today]  # 오늘치 중복 제거
    history.insert(0, new_entry)
    history = history[:PICKS_MAX_DAYS]

    _save_history(history)

    _picks_cache["data"] = None  # 캐시 무효화
    _picks_cache["ts"] = 0

    logger.info("종목 발굴 완료 및 저장됨.")
    return new_entry


def get_latest_picks() -> dict:
    """
    현재가 + 수익률이 업데이트된 picks_history를 반환합니다.
    우선순위: 1) 인메모리 캐시  2) GitHub raw  3) 로컬 파일
    """
    now = time.time()

    # 1. 캐시 확인
    if _picks_cache["data"] and (now - _picks_cache["ts"]) < CACHE_TTL:
        return _picks_cache["data"]

    # 2. GitHub raw URL에서 최신 데이터 시도
    history = []
    try:
        resp = requests.get(GITHUB_PICKS_URL, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            history = data.get("picks_history", [])
            logger.debug(f"GitHub에서 picks 로드 ({len(history)}일치)")
    except Exception as e:
        logger.debug(f"GitHub picks fetch 실패: {e}")

    # 3. 로컬 파일 폴백
    if not history:
        history = _load_history()

    if not history:
        return {"picks_history": []}

    # 수익률 업데이트 (최근 5일치만)
    history = _update_returns(history[:5])

    result = {"picks_history": history}
    _picks_cache["data"] = result
    _picks_cache["ts"] = now
    return result
