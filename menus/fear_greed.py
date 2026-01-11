import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

def get_market_data():
    try:
        # Fetch S&P 500 and VIX
        sp500 = yf.Ticker("^GSPC")
        vix = yf.Ticker("^VIX")
        
        # We need enough history for SMA 125
        sp500_hist = sp500.history(period="1y") 
        vix_hist = vix.history(period="5d")
        
        return sp500_hist, vix_hist
    except Exception:
        return None, None

def calculate_fear_greed(sp500_hist, vix_hist):
    if sp500_hist is None or sp500_hist.empty or vix_hist is None or vix_hist.empty:
        return None
    
    # 1. Market Momentum (S&P 500 vs 125-day SMA)
    # Weight: 40%
    current_price = sp500_hist['Close'].iloc[-1]
    sma_125 = sp500_hist['Close'].rolling(window=125).mean().iloc[-1]
    
    # Calculate diff pct
    momentum_pct = (current_price - sma_125) / sma_125
    # Normalize: Assuming +/- 10% is the typical extreme range
    # +10% -> 100 (Greed), -10% -> 0 (Fear), 0% -> 50 (Neutral)
    # Score = 50 + (momentum_pct * 100 * 2.5) -> 0.1 * 100 * 2.5 = 25 -> 75?
    # Let's map -0.1 to 0, +0.1 to 100.
    # Score = (momentum_pct + 0.1) / 0.2 * 100
    mom_score = ((momentum_pct + 0.1) / 0.2) * 100
    mom_score = max(0, min(100, mom_score))
    
    # 2. Market Volatility (VIX)
    # Weight: 40%
    # VIX 50-day average vs Current VIX? Or just raw VIX?
    # CNN uses VIX vs 50-day MA.
    # But let's simplify: Raw VIX mapping.
    # VIX 10 = Extreme Greed (Score 100), VIX 50 = Extreme Fear (Score 0)
    current_vix = vix_hist['Close'].iloc[-1]
    # Score = 100 - ((VIX - 10) / 40 * 100)
    vix_score = 100 - ((current_vix - 12) / (35 - 12) * 100) # Mapping 12-35 range
    vix_score = max(0, min(100, vix_score))
    
    # 3. Market Strength (RSI 14) of S&P 500
    # Weight: 20%
    delta = sp500_hist['Close'].diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1]
    # RSI 30 -> Fear (0), RSI 70 -> Greed (100)
    # Map 30-70 range to 0-100
    rsi_score = (current_rsi - 30) / (70 - 30) * 100
    rsi_score = max(0, min(100, rsi_score))
    
    # Weighted Average
    final_score = (mom_score * 0.4) + (vix_score * 0.4) + (rsi_score * 0.2)
    
    return int(final_score), {
        "Momentum Score": int(mom_score),
        "Volatility Score": int(vix_score),
        "Strength Score": int(rsi_score),
        "VIX": current_vix,
        "RSI": current_rsi
    }

def show():
    st.markdown("""
        <div class="glass-panel" style="padding: 1.25rem; margin-bottom: 2rem;">
            <h3 style="margin: 0; font-size: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 2rem;">😨</span> 공포 & 탐욕 지수 (Fear & Greed Index)
            </h3>
            <p style="color: #94a3b8; margin-top: 0.5rem;">
                시장 데이터를 기반으로 자체 분석한 현재 시장의 심리 상태입니다. (0: 극도의 공포 ~ 100: 극도의 탐욕)
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.spinner("시장 데이터 분석 중..."):
        sp500, vix = get_market_data()
        score, details = calculate_fear_greed(sp500, vix)
    
    if score is not None:
        # Determine Label and Color
        if score < 25:
            label = "Extreme Fear (극도의 공포)"
            color = "#ef4444"
        elif score < 45:
            label = "Fear (공포)"
            color = "#f97316"
        elif score < 55:
            label = "Neutral (중립)"
            color = "#eab308"
        elif score < 75:
            label = "Greed (탐욕)"
            color = "#84cc16"
        else:
            label = "Extreme Greed (극도의 탐욕)"
            color = "#22c55e"
            
        # Gauge Chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = score,
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
                    'value': score}
            }
        ))
        
        fig.update_layout(
            paper_bgcolor = "rgba(0,0,0,0)",
            font = {'color': "white", 'family': "Inter"},
            height = 400,
            margin = dict(l=30, r=30, t=50, b=30)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 🔍 상세 지표 분석")
        col1, col2, col3 = st.columns(3)
        
        col1.markdown(f"""
            <div class="glass-panel" style="padding: 1rem; text-align: center;">
                <div style="font-size: 0.9rem; color: #94a3b8;">시장 모멘텀 (S&P 500)</div>
                <div style="font-size: 1.5rem; font-weight: bold; margin-top: 0.5rem; color: #38bdf8;">{details['Momentum Score']}</div>
                <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.2rem;">추세 강도</div>
            </div>
        """, unsafe_allow_html=True)
        
        col2.markdown(f"""
            <div class="glass-panel" style="padding: 1rem; text-align: center;">
                <div style="font-size: 0.9rem; color: #94a3b8;">시장 변동성 (VIX)</div>
                <div style="font-size: 1.5rem; font-weight: bold; margin-top: 0.5rem; color: #38bdf8;">{details['Volatility Score']}</div>
                <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.2rem;">현재 VIX: {details['VIX']:.2f}</div>
            </div>
        """, unsafe_allow_html=True)
        
        col3.markdown(f"""
            <div class="glass-panel" style="padding: 1rem; text-align: center;">
                <div style="font-size: 0.9rem; color: #94a3b8;">매수 강도 (RSI)</div>
                <div style="font-size: 1.5rem; font-weight: bold; margin-top: 0.5rem; color: #38bdf8;">{details['Strength Score']}</div>
                <div style="font-size: 0.8rem; color: #64748b; margin-top: 0.2rem;">현재 RSI: {details['RSI']:.2f}</div>
            </div>
        """, unsafe_allow_html=True)
        
    else:
        st.error("시장 데이터를 불러오는데 실패했습니다. 잠시 후 다시 시도해주세요.")
