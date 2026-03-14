import streamlit as st

def show():
    st.markdown("""
        <div class="glass-panel" style="padding: 1.25rem; margin-bottom: 2rem;">
            <h3 style="margin: 0; font-size: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 2rem;">🔭</span> ETF 탐험가
            </h3>
            <p style="color: #94a3b8; margin-top: 0.5rem;">
                인기 있는 ETF를 테마별로 살펴보고 즉시 분석해보세요.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # ETF Categories
    categories = {
        "🇰🇷 대한민국 인기 ETF": [
            ("069500.KS", "KODEX 200", "코스피 200 지수 추종"),
            ("229200.KS", "KODEX 코스닥150", "국내 코스닥 대표 지수"),
            ("459580.KS", "KODEX CD금리액티브", "금리형 액티브 ETF (안전자산)"),
            ("381170.KS", "TIGER 미국테크TOP10", "미국 빅테크 우량주 TOP 10"),
            ("465320.KS", "TIGER 미국테크TOP10+10%프리미엄", "빅테크 투자 + 월배당")
        ],
        "🇺🇸 미국 지수 추종": [
            ("SPY", "S&P 500 Trust", "미국 대형주 500개 기업 투자"),
            ("QQQ", "Invesco QQQ", "나스닥 100 기술주 중심"),
            ("DIA", "Dow Jones ETF", "다우존스 30개 우량 기업"),
            ("IWM", "Russell 2000", "미국 중소형주 2000개")
        ],
        "💰 배당 & 인컴": [
            ("SCHD", "US Dividend Equity", "안정적인 배당 성장주"),
            ("JEPI", "JPMorgan Premium", "커버드콜 고배당 전략"),
            ("O", "Realty Income", "월배당 리츠 대장주"),
            ("VNQ", "Vanguard Real Estate", "미국 부동산 리츠 종합")
        ],
        "🚀 테크 & 혁신": [
            ("SOXX", "Semiconductor ETF", "필라델피아 반도체 지수"),
            ("XLK", "Technology Select", "마이크로소프트, 애플 등 기술주"),
            ("ARKK", "ARK Innovation", "파괴적 혁신 기업 투자"),
            ("NVDL", "GraniteShares 2x NVDA", "엔비디아 2배 레버리지 (고위험)")
        ],
        "🛡️ 채권 & 안전자산": [
            ("TLT", "20+ Year Treasury", "미국 장기 국채"),
            ("SHY", "1-3 Year Treasury", "미국 단기 국채 (현금성)"),
            ("GLD", "SPDR Gold Shares", "금 현물 투자"),
            ("LQD", "Investment Grade Corp", "투자등급 회사채")
        ]
    }
    
    for category, etfs in categories.items():
        st.markdown(f"### {category}")
        
        cols = st.columns(2)
        for idx, (ticker, name, desc) in enumerate(etfs):
            col = cols[idx % 2]
            with col:
                # Card-like styling using container
                with st.container():
                    st.markdown(f"""
                        <div style="
                            background: rgba(255, 255, 255, 0.03);
                            border: 1px solid rgba(255, 255, 255, 0.1);
                            border-radius: 12px;
                            padding: 1rem;
                            margin-bottom: 1rem;
                            transition: all 0.2s;
                        ">
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                                <span style="font-weight: bold; font-size: 1.2rem; color: #38bdf8;">{ticker}</span>
                                <span style="font-size: 0.9rem; color: #e2e8f0; background: rgba(56, 189, 248, 0.2); padding: 0.2rem 0.6rem; border-radius: 99px;">ETF</span>
                            </div>
                            <div style="font-weight: 500; font-size: 1rem; margin-bottom: 0.3rem;">{name}</div>
                            <div style="font-size: 0.85rem; color: #94a3b8; margin-bottom: 0.8rem; height: 2.5rem; overflow: hidden; text-overflow: ellipsis;">{desc}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"🔎 {ticker} 분석하기", key=f"btn_{ticker}", use_container_width=True):
                        st.session_state.selected_ticker = ticker
                        st.session_state.menu_nav = "대시보드" # This key must match app.py radio key
                        st.rerun()
        
        st.markdown("<div style='margin-bottom: 1.5rem'></div>", unsafe_allow_html=True)
