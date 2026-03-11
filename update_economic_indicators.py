"""
경제지표 CSV 자동 업데이트 스크립트
- FRED API: fed_rate (FEDFUNDS), cpi (CPIAUCSL), ind_prod (INDPRO)
- yfinance: treasury_10y (^TNX), usd_krw (KRW=X), wti (CL=F),
            vix (^VIX), sox (^SOX), xli (XLI), ewy (EWY), smh (SMH)

Usage:
    python update_economic_indicators.py
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import datetime

import logging
yf_logger = logging.getLogger('yfinance')
yf_logger.disabled = True

# Fix encoding for Windows (cp949 can't handle emoji)
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "static", "economic_indicators.csv")

# ── FRED API helpers ──────────────────────────────────────────────────
FRED_API_KEY = os.environ.get("FRED_API_KEY", "")

FRED_SERIES = {
    "fed_rate": "FEDFUNDS",
    "cpi": "CPIAUCSL",
    "ind_prod": "INDPRO",
}

# ── yfinance ticker → CSV column mapping ─────────────────────────────
YF_TICKERS = {
    "treasury_10y": "^TNX",
    "usd_krw": "KRW=X",
    "wti": "CL=F",
    "vix": "^VIX",
    "sox": "^SOX",
    "xli": "XLI",
    "ewy": "EWY",
    "smh": "SMH",
}


def fetch_fred_series(series_id: str, start_date: str, end_date: str) -> pd.Series:
    """Fetch monthly data from FRED API, return Series indexed by YYYY-MM-01."""
    import requests

    if not FRED_API_KEY:
        print(f"  ⚠ FRED_API_KEY not set, skipping {series_id}")
        return pd.Series(dtype=float)

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": start_date,
        "observation_end": end_date,
        "frequency": "m",  # monthly
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        obs = data.get("observations", [])
        records = {}
        for o in obs:
            if o["value"] == ".":
                continue
            dt = pd.Timestamp(o["date"]).strftime("%Y-%m-01")
            records[dt] = float(o["value"])
        return pd.Series(records, dtype=float)
    except Exception as e:
        print(f"  ✗ FRED {series_id} error: {e}")
        return pd.Series(dtype=float)


def fetch_yf_monthly(tickers: dict, start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch monthly average close prices from yfinance."""
    import yfinance as yf

    result = pd.DataFrame()
    ticker_list = list(tickers.values())
    col_names = list(tickers.keys())

    try:
        # Download all at once for efficiency
        raw = yf.download(
            " ".join(ticker_list),
            start=start_date,
            end=end_date,
            progress=False,
            auto_adjust=True,
        )

        if raw.empty:
            print("  ✗ yfinance returned empty data")
            return result

        # Extract Close prices
        if "Close" in raw.columns or (hasattr(raw.columns, 'levels') and 'Close' in raw.columns.get_level_values(0)):
            close = raw["Close"] if len(ticker_list) > 1 else raw[["Close"]]
        else:
            close = raw

        # If single ticker, column name is 'Close' instead of ticker
        if len(ticker_list) == 1:
            close.columns = [col_names[0]]
        else:
            # Map yfinance column names to our column names
            rename_map = {}
            for col_name, yf_ticker in zip(col_names, ticker_list):
                rename_map[yf_ticker] = col_name
            close = close.rename(columns=rename_map)

        # Resample to monthly average
        close.index = pd.to_datetime(close.index)
        monthly = close.resample("MS").mean()  # MS = month start

        # ^TNX is in basis-points-like (e.g. 425 = 4.25%), need no conversion
        # Actually ^TNX returns values like 4.25 directly, no conversion needed

        result = monthly

    except Exception as e:
        print(f"  ✗ yfinance error: {e}")

    return result


def main():
    print("=" * 60)
    print("📊 경제지표 CSV 업데이트 시작")
    print(f"   시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. Read existing CSV
    if not os.path.exists(CSV_PATH):
        print(f"✗ CSV not found: {CSV_PATH}")
        sys.exit(1)

    df = pd.read_csv(CSV_PATH)
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    print(f"\n📄 기존 CSV: {len(df)} rows, last date = {df['date'].iloc[-1]}")

    # 2. Determine date range to fetch
    last_date = pd.Timestamp(df["date"].iloc[-1])
    today = pd.Timestamp.now()

    # We need data from the last row (to backfill) up to the last *completed* month
    # A month is "completed" if we're past its last day
    if today.day >= 1:
        # Last completed month
        last_completed = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    else:
        last_completed = today.replace(day=1)

    # Start from 2 months before the last CSV date (to ensure backfill coverage)
    fetch_start = (last_date - pd.DateOffset(months=2)).strftime("%Y-%m-%d")
    fetch_end = (last_completed + pd.DateOffset(months=1)).strftime("%Y-%m-%d")

    print(f"\n🔍 수집 범위: {fetch_start} ~ {fetch_end}")
    print(f"   마지막 완료된 월: {last_completed.strftime('%Y-%m-01')}")

    # 3. Fetch FRED data
    print("\n── FRED API 데이터 수집 ──")
    fred_data = {}
    for col, series_id in FRED_SERIES.items():
        print(f"  📥 {col} ({series_id})...", end=" ")
        s = fetch_fred_series(series_id, fetch_start, fetch_end)
        fred_data[col] = s
        if not s.empty:
            print(f"✓ {len(s)} months (latest: {s.index[-1]} = {s.iloc[-1]:.2f})")
        else:
            print("✗ no data")
        time.sleep(0.5)  # Rate limit courtesy

    # 4. Fetch yfinance data
    print("\n── yfinance 데이터 수집 ──")
    yf_monthly = fetch_yf_monthly(YF_TICKERS, fetch_start, fetch_end)
    if not yf_monthly.empty:
        print(f"  ✓ {len(yf_monthly)} months fetched")
        for col in yf_monthly.columns:
            latest = yf_monthly[col].dropna()
            if not latest.empty:
                print(f"    {col}: latest = {latest.index[-1].strftime('%Y-%m-01')} = {latest.iloc[-1]:.2f}")
    else:
        print("  ✗ no data")

    # 5. Update existing rows (backfill missing values)
    print("\n── 기존 행 빈 값 보완 ──")
    updated_cells = 0

    all_cols = list(FRED_SERIES.keys()) + list(YF_TICKERS.keys())

    for idx, row in df.iterrows():
        row_date = row["date"]
        row_date_key = pd.Timestamp(row_date).strftime("%Y-%m-01")

        for col in all_cols:
            current_val = row.get(col)
            if pd.isna(current_val) or current_val == "":
                new_val = None

                # Check FRED data
                if col in fred_data and row_date_key in fred_data[col].index:
                    new_val = fred_data[col][row_date_key]

                # Check yfinance data
                if col in YF_TICKERS and not yf_monthly.empty:
                    ts_key = pd.Timestamp(row_date_key)
                    if col in yf_monthly.columns and ts_key in yf_monthly.index:
                        v = yf_monthly.loc[ts_key, col]
                        if not pd.isna(v):
                            new_val = v

                if new_val is not None:
                    df.at[idx, col] = round(new_val, 2)
                    updated_cells += 1

    print(f"  ✓ {updated_cells} cells backfilled")

    # 6. Add new month rows
    print("\n── 새로운 월 데이터 추가 ──")
    new_rows = 0
    existing_dates = set(df["date"].tolist())

    # Generate list of months that should exist
    check_date = last_date + pd.DateOffset(months=1)
    while check_date <= last_completed:
        date_str = check_date.strftime("%Y-%m-%d")
        date_key = check_date.strftime("%Y-%m-01")

        if date_str not in existing_dates:
            new_row = {"date": date_str}

            # Fill from FRED
            for col in FRED_SERIES:
                if date_key in fred_data.get(col, pd.Series()).index:
                    new_row[col] = round(fred_data[col][date_key], 2)

            # Fill from yfinance
            if not yf_monthly.empty:
                ts_key = pd.Timestamp(date_key)
                for col in YF_TICKERS:
                    if col in yf_monthly.columns and ts_key in yf_monthly.index:
                        v = yf_monthly.loc[ts_key, col]
                        if not pd.isna(v):
                            new_row[col] = round(float(v), 2)

            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            new_rows += 1
            print(f"  + {date_str}: {', '.join(f'{k}={v}' for k, v in new_row.items() if k != 'date' and pd.notna(v))}")

        check_date = check_date + pd.DateOffset(months=1)

    if new_rows == 0:
        print("  (새로운 완료된 월 없음)")

    # 7. Save CSV
    # Ensure column order matches original
    col_order = ["date", "fed_rate", "cpi", "treasury_10y", "usd_krw",
                 "ind_prod", "wti", "vix", "sox", "xli", "ewy", "smh"]
    for c in col_order:
        if c not in df.columns:
            df[c] = np.nan

    df = df[col_order]
    df.to_csv(CSV_PATH, index=False)

    print(f"\n{'=' * 60}")
    print(f"✅ 완료! CSV 저장: {len(df)} rows")
    print(f"   Backfilled: {updated_cells} cells")
    print(f"   New rows: {new_rows}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
