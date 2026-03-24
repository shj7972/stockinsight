"""
AI 주가 방향 예측 사전 계산 스크립트
경제지표 CSV를 읽어 RandomForest 모델로 다음 달 NASDAQ·S&P500·KOSPI 방향을 예측하고
static/predictions.json 에 저장합니다.

실행:
    python update_predictions.py
"""

import json
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "static", "economic_indicators.csv")
OUT_PATH = os.path.join(BASE_DIR, "static", "predictions.json")


def compute_predictions() -> list:
    if not os.path.exists(CSV_PATH):
        print(f"ERROR: {CSV_PATH} not found")
        return []

    df = pd.read_csv(CSV_PATH)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)

    rate_cols = ['fed_rate', 'treasury_10y', 'vix']
    trend_cols = ['cpi', 'usd_krw', 'wti', 'ind_prod']
    feat_cols = rate_cols + [f'{c}_yoy' for c in trend_cols]

    for c in rate_cols + trend_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    for c in trend_cols:
        df[f'{c}_yoy'] = df[c].pct_change(periods=12, fill_method=None) * 100

    target_indices = [
        ('^IXIC', 'NASDAQ',  '#38bdf8'),
        ('^GSPC', 'S&P 500', '#818cf8'),
        ('^KS11', 'KOSPI',   '#4ade80'),
    ]

    results = []
    for ticker_sym, name, color in target_indices:
        try:
            hist = yf.download(ticker_sym, start='1995-01-01', interval='1mo',
                               progress=False, auto_adjust=True)
            if hist.empty:
                print(f"WARN: no data for {ticker_sym}")
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
            merged = merged.iloc[:-1].dropna(subset=feat_cols + ['target'])

            if len(merged) < 60:
                print(f"WARN: insufficient data for {name} ({len(merged)} rows)")
                continue

            econ_latest = df[['date'] + feat_cols].dropna(subset=feat_cols).iloc[[-1]]

            X_train = merged[feat_cols].values
            y_train = merged['target'].values

            sc = StandardScaler()
            X_train_s = sc.fit_transform(X_train)
            X_latest_s = sc.transform(econ_latest[feat_cols].values)

            rf = RandomForestClassifier(
                n_estimators=200,
                max_depth=4,
                min_samples_leaf=5,
                random_state=42,
                class_weight='balanced'
            )
            rf.fit(X_train_s, y_train)

            proba = rf.predict_proba(X_latest_s)[0]
            p_up = float(proba[1])

            if p_up >= 0.5:
                final_dir = 1
                confidence = p_up * 100
            else:
                final_dir = 0
                confidence = (1 - p_up) * 100

            results.append({
                'ticker': ticker_sym,
                'name': name,
                'color': color,
                'direction': '상승' if final_dir == 1 else '하락',
                'direction_icon': '📈' if final_dir == 1 else '📉',
                'direction_color': '#4ade80' if final_dir == 1 else '#f87171',
                'confidence': round(float(confidence), 1),
                'data_months': int(len(merged)),
            })
            print(f"  {name}: {'상승' if final_dir == 1 else '하락'} (신뢰도 {confidence:.1f}%)")
        except Exception as e:
            print(f"ERROR [{name}]: {e}")
            continue

    return results


def main():
    print("AI 주가 방향 예측 계산 시작...")
    predictions = compute_predictions()

    if not predictions:
        print("ERROR: 예측 결과 없음 — 기존 파일 유지")
        sys.exit(1)

    output = {
        "updated_at": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
        "predictions": predictions,
    }

    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"저장 완료: {OUT_PATH} ({len(predictions)}개 지수)")


if __name__ == '__main__':
    main()
