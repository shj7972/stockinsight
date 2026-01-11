import streamlit as st
from menus import dashboard, yield_calc, fear_greed, exchange, etf

# Page Config
st.set_page_config(
    page_title="Stock Insight AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# SEO Meta Tags for Search Engines (including Naver)
st.markdown("""
    <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
    <meta name="googlebot" content="index, follow">
    <meta name="Yeti" content="index, follow">
    <meta name="NaverBot" content="index, follow">
    <meta name="description" content="Stock Insight AI - 실시간 주식 분석, AI 기반 투자 조언, 글로벌 지수 및 뉴스 감성 분석 플랫폼">
    <meta name="keywords" content="주식분석, AI투자, 주식차트, 투자조언, 주식뉴스, 감성분석, 실시간지수, 수익률계산기, 환율계산기, 공포탐욕지수">
    <meta property="og:title" content="Stock Insight AI - 스마트 투자 분석 플랫폼">
    <meta property="og:description" content="AI 기반 실시간 주식 분석 및 투자 조언 서비스">
    <meta property="og:type" content="website">
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    # Enhanced Logo Design
    st.markdown("""
        <div class="glass-panel" style="padding: 2rem 1rem; margin-bottom: 2rem; text-align: center;">
            <div style="font-size: 3.5rem; margin-bottom: 1rem;">📈</div>
            <h1 style="font-size: 1.8rem; margin: 0.5rem 0;">Stock Insight AI</h1>
            <div style="font-size: 0.75rem; color: #94a3b8; letter-spacing: 0.15em; text-transform: uppercase; font-weight: 500;">
                Smart Investment Intelligence
            </div>
            <div style="width: 40px; height: 3px; background: linear-gradient(90deg, #38bdf8, #818cf8); margin: 1.5rem auto 0; border-radius: 2px;"></div>
        </div>
    """, unsafe_allow_html=True)
    
    # Menu Selection
    st.markdown("### 📋 메뉴 선택")
    
    # Custom CSS for Radio Buttons (Simulated Tabs in Sidebar)
    st.markdown("""
    <style>
    .stRadio [role=radiogroup] {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 10px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    menu = st.radio(
        "이동할 메뉴를 선택하세요",
        ["대시보드", "수익률 계산기", "공포/탐욕 지수", "환율 계산기", "ETF 탐험가"],
        label_visibility="collapsed",
        key="menu_nav"
    )
    
    st.markdown("---")

# Navigation Logic
if menu == "대시보드":
    dashboard.show()
elif menu == "수익률 계산기":
    try:
        yield_calc.show()
    except AttributeError:
        st.info("수익률 계산기 메뉴 준비 중...")
elif menu == "공포/탐욕 지수":
    try:
        fear_greed.show()
    except AttributeError:
        st.info("공포/탐욕 지수 메뉴 준비 중...")
elif menu == "환율 계산기":
    try:
        exchange.show()
    except AttributeError:
        st.info("환율 계산기 메뉴 준비 중...")
elif menu == "ETF 탐험가":
    try:
        etf.show()
    except AttributeError:
        st.info("ETF 탐험가 메뉴 준비 중...")
