import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import utils

def show():
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

    # Display Major Indices at the top with enhanced styling
    st.markdown("""
        <div class="glass-panel" style="padding: 1.25rem; margin-bottom: 1.5rem;">
            <h3 style="margin: 0; font-size: 1.25rem; display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.5rem;">📊</span> 실시간 글로벌 지수
            </h3>
        </div>
    """, unsafe_allow_html=True)

    with st.spinner('주요 지수를 불러오는 중...'):
        index_cols = st.columns(5)
        col_idx = 0
        
        for region, indices in MAJOR_INDICES.items():
            for ticker, name in indices:
                if col_idx < len(index_cols):
                    try:
                        current, change, change_pct = utils.get_index_data(ticker)
                        if current is not None:
                            delta_color = "normal" if change >= 0 else "inverse"
                            # 한국 지수는 정수로, 미국 지수는 소수점 2자리로 표시
                            if region == "한국":
                                current_str = f"{current:,.0f}"
                                change_str = f"{change:+.0f} ({change_pct:+.2f}%)"
                            else:
                                current_str = f"{current:,.2f}"
                                change_str = f"{change:+.2f} ({change_pct:+.2f}%)"
                            
                            index_cols[col_idx].metric(
                                name,
                                current_str,
                                change_str,
                                delta_color=delta_color
                            )
                        else:
                            index_cols[col_idx].metric(name, "N/A", "데이터 없음")
                    except Exception as e:
                        index_cols[col_idx].metric(name, "N/A", "오류")
                    col_idx += 1
        
        # Fill remaining columns if needed
        while col_idx < len(index_cols):
            index_cols[col_idx].empty()
            col_idx += 1

    st.markdown("<div style='margin: 1rem 0;'></div>", unsafe_allow_html=True)

    # Popular stock tickers
    US_TOP_TICKERS = [
        ("AAPL", "애플"),
        ("MSFT", "마이크로소프트"),
        ("GOOGL", "구글"),
        ("AMZN", "아마존"),
        ("TSLA", "테슬라"),
        ("META", "메타"),
        ("NVDA", "엔비디아"),
        ("JPM", "JP모건"),
        ("V", "비자"),
        ("JNJ", "존슨앤존슨")
    ]

    KR_TOP_TICKERS = [
        ("005930.KS", "삼성전자"),
        ("000660.KS", "SK하이닉스"),
        ("035420.KS", "NAVER"),
        ("051910.KS", "LG화학"),
        ("006400.KS", "삼성SDI"),
        ("035720.KS", "카카오"),
        ("207940.KS", "삼성바이오로직스"),
        ("028260.KS", "삼성물산"),
        ("005380.KS", "현대차"),
        ("105560.KS", "KB금융")
    ]

    # Initialize session state
    if 'selected_ticker' not in st.session_state:
        st.session_state.selected_ticker = "AAPL"

    # Sidebar for Dashboard
    with st.sidebar:
        st.markdown("### 🔍 종목 검색")
        
        # Ticker input with session state
        ticker_input = st.text_input("티커 또는 종목명 입력", value=st.session_state.selected_ticker).upper()
        if ticker_input != st.session_state.selected_ticker:
            st.session_state.selected_ticker = ticker_input
        
        # Use session state ticker
        ticker = st.session_state.selected_ticker
        
        st.markdown("---")
        
        # Add JavaScript for tooltips (only once)
        # Note: Since this is now inside a function that might be re-run, check if already injected? 
        # Actually st.markdown with script tag is fine, but maybe move to app.py?
        # Let's keep it here for now as it's specific to the ticker buttons.
        st.markdown("""
        <script>
        function addTooltips() {
            // Find all ticker buttons in sidebar
            const buttons = document.querySelectorAll('[data-testid="stSidebar"] button[kind="secondary"]');
            buttons.forEach(button => {
                // Skip if already has tooltip
                if (button.querySelector('.ticker-tooltip')) return;
                
                const buttonText = button.textContent.trim();
                if (buttonText) {
                    // Create tooltip element
                    const tooltip = document.createElement('div');
                    tooltip.className = 'ticker-tooltip';
                    tooltip.textContent = buttonText;
                    button.style.position = 'relative';
                    button.appendChild(tooltip);
                }
            });
        }
        
        // Run on page load
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', addTooltips);
        } else {
            addTooltips();
        }
        
        // Also run after Streamlit updates
        const observer = new MutationObserver(addTooltips);
        observer.observe(document.body, { childList: true, subtree: true });
        </script>
        <style>
        [data-testid="stSidebar"] button[kind="secondary"] {
            position: relative !important;
        }
        [data-testid="stSidebar"] button[kind="secondary"]:hover .ticker-tooltip {
            opacity: 1 !important;
            visibility: visible !important;
        }
        .ticker-tooltip {
            position: absolute !important;
            bottom: 100% !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            background-color: #1e2127 !important;
            color: #ffffff !important;
            padding: 0.5rem 0.75rem !important;
            border-radius: 4px !important;
            font-size: 0.8rem !important;
            white-space: nowrap !important;
            z-index: 10000 !important;
            margin-bottom: 5px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
            border: 1px solid #41444b !important;
            pointer-events: none !important;
            opacity: 0 !important;
            visibility: hidden !important;
            transition: opacity 0.2s, visibility 0.2s !important;
        }
        .ticker-tooltip::after {
            content: '' !important;
            position: absolute !important;
            top: 100% !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            border: 5px solid transparent !important;
            border-top-color: #1e2127 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # US Top 10
        st.markdown("### 🇺🇸 미국 주식 Top 10")
        cols_us = st.columns(2)
        for idx, (tick, name) in enumerate(US_TOP_TICKERS):
            col_idx = idx % 2
            button_label = f"{name} ({tick})"
            if cols_us[col_idx].button(button_label, key=f"us_{tick}", use_container_width=True):
                st.session_state.selected_ticker = tick
                st.rerun()
        
        st.markdown("---")
        
        # Korea Top 10
        st.markdown("### 🇰🇷 국내 주식 Top 10")
        cols_kr = st.columns(2)
        for idx, (tick, name) in enumerate(KR_TOP_TICKERS):
            col_idx = idx % 2
            button_label = f"{name} ({tick})"
            if cols_kr[col_idx].button(button_label, key=f"kr_{tick}", use_container_width=True):
                st.session_state.selected_ticker = tick
                st.rerun()
        
        st.markdown("---")
        with st.expander("💡 사용 팁"):
            st.info("미국 주식 티커 (예: AAPL, TSLA) 또는 한국 주식 코드 (예: 005930.KS)를 입력하세요.")

    if ticker:
        with st.spinner('데이터를 분석 중입니다...'):
            # Fetch Data
            history, info = utils.get_stock_data(ticker)
            news = utils.get_news(ticker)
            
            if history is None or history.empty:
                st.error(f"'{ticker}'에 대한 데이터를 찾을 수 없습니다. 티커를 확인해주세요.")
            else:
                # Process Data
                metrics_df = utils.calculate_metrics(history)
                sentiment_score, sentiment_details = utils.analyze_sentiment(news)
                verdict, advice_list = utils.generate_advice(metrics_df, sentiment_score)
                
                # Header Section with enhanced styling (removed redundant empty div)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    company_name = info.get('longName', ticker)
                    st.markdown(f"""
                        <h1 style="background: linear-gradient(135deg, #00d2ff 0%, #3a7bd5 50%, #8b5cf6 100%);
                                    -webkit-background-clip: text;
                                    -webkit-text-fill-color: transparent;
                                    background-clip: text;
                                    font-size: 2.5rem;
                                    font-weight: 700;
                                    margin-bottom: 0.5rem;">
                            {company_name} ({ticker})
                        </h1>
                    """, unsafe_allow_html=True)
                    
                    # Verdict Translation
                    verdict_map = {
                        "강력 매수 (Strong Buy) 🚀": "강력 매수 (Strong Buy) 🚀",
                        "매수 (Buy) ✅": "매수 (Buy) ✅",
                        "보류 (Hold) ✋": "보류 (Hold) ✋",
                        "매도 (Sell) ❌": "매도 (Sell) ❌",
                        "강력 매도 (Strong Sell) 📉": "강력 매도 (Strong Sell) 📉"
                    }
                    verdict_text = verdict_map.get(verdict, verdict)
                    # Verdict color based on recommendation
                    if "매수" in verdict_text or "Buy" in verdict_text:
                        verdict_color = "#4CAF50"
                    elif "매도" in verdict_text or "Sell" in verdict_text:
                        verdict_color = "#f44336"
                    else:
                        verdict_color = "#ff9800"
                    
                    st.markdown(f"""
                        <div class="verdict-wrapper" style="margin-top: 1rem;">
                            <span class="verdict-badge" style="
                                background: {verdict_color}22;
                                color: {verdict_color};
                                font-size: 1.1rem;
                                font-weight: 700;
                                padding: 0.6rem 1.2rem;
                                borderRadius: 100px;
                                border: 1px solid {verdict_color}44;
                                display: inline-block;
                            ">
                                {verdict_text}
                            </span>
                        </div>
                    """, unsafe_allow_html=True)
                with col2:
                    current_price = history['Close'].iloc[-1]
                    prev_price = history['Close'].iloc[-2]
                    delta = current_price - prev_price
                    
                    currency_symbol = "₩" if ticker.endswith(".KS") or ticker.endswith(".KQ") else "$"
                    st.metric("현재가", f"{currency_symbol}{current_price:,.2f}", f"{delta:,.2f}")

                # Main Content Tabs
                tab1, tab2, tab3, tab4 = st.tabs(["📊 차트 & 분석", "📋 재무 정보", "📰 뉴스 & 평판", "🤖 AI 조언"])

                with tab1:
                    # Interactive Chart
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                        vertical_spacing=0.03, subplot_titles=('Price & SMA', 'Volume'), 
                                        row_width=[0.2, 0.7])

                    # Candlestick
                    fig.add_trace(go.Candlestick(x=history.index,
                                    open=history['Open'],
                                    high=history['High'],
                                    low=history['Low'],
                                    close=history['Close'], 
                                    name='Price',
                                    increasing_line_color='#10b981', 
                                    decreasing_line_color='#ef4444'), row=1, col=1)
                    
                    # SMAs with modern colors
                    fig.add_trace(go.Scatter(x=history.index, y=metrics_df['sma_20'], line=dict(color='#38bdf8', width=1.5), name='SMA 20'), row=1, col=1)
                    fig.add_trace(go.Scatter(x=history.index, y=metrics_df['sma_50'], line=dict(color='#818cf8', width=1.5), name='SMA 50'), row=1, col=1)

                    # Volume with neutral color
                    fig.add_trace(go.Bar(x=history.index, y=history['Volume'], name='Volume', marker_color='#64748b', opacity=0.8), row=2, col=1)

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
                    
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                with tab2:
                    st.markdown("""
                        <div class="glass-panel" style="padding: 1.25rem; margin-bottom: 1.5rem;">
                            <h3 style="margin: 0; font-size: 1.25rem;">📝 기업 개요</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    summary = info.get('longBusinessSummary', '정보 없음')
                    if summary != '정보 없음':
                        with st.spinner('기업 개요를 번역 중입니다...'):
                            summary = utils.translate_text(summary)
                    
                    st.markdown(f"""
                        <div class="glass-panel" style="padding: 1.5rem; color: #cbd5e1; line-height: 1.8; font-size: 1rem; margin-bottom: 1.5rem;">
                            {summary}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    st.markdown("""
                        <div class="glass-panel" style="padding: 1.25rem; margin-bottom: 1.5rem;">
                            <h3 style="margin: 0; font-size: 1.25rem;">💎 주요 지표</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    col_m1, col_m2, col_m3 = st.columns(3)
                    col_m1.metric("시가총액", f"{info.get('marketCap', 0):,}")
                    col_m2.metric("PER", f"{info.get('trailingPE', 'N/A')}")
                    col_m3.metric("배당수익률", f"{info.get('dividendYield', 0) * 100:.2f}%" if info.get('dividendYield') else "N/A")

                with tab3:
                    st.markdown("""
                        <div class="glass-panel" style="padding: 1.25rem; margin-bottom: 1.5rem;">
                            <h3 style="margin: 0; font-size: 1.25rem;">🌍 실시간 뉴스 및 시장 심리</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if news and len(news) > 0:
                        st.markdown(f"""
                            <div class="glass-panel" style="padding: 1.25rem; margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <span style="color: #94a3b8; font-size: 0.9rem;">평균 감성 점수</span><br>
                                    <span style="color: #38bdf8; font-size: 1.5rem; font-weight: 700;">{sentiment_score:.2f}</span>
                                    <span style="color: #475569; font-size: 0.8rem;"> (-1.0 ~ 1.0)</span>
                                </div>
                                <div style="text-align: right;">
                                    <span style="color: #94a3b8; font-size: 0.9rem;">분석된 뉴스</span><br>
                                    <span style="color: #38bdf8; font-size: 1.5rem; font-weight: 700;">{len(sentiment_details)}</span>
                                    <span style="color: #475569; font-size: 0.8rem;"> 개</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if sentiment_details and len(sentiment_details) > 0:
                            # Translate all titles in advance for better performance
                            with st.spinner('뉴스 제목을 번역 중입니다...'):
                                translated_items = []
                                for item in sentiment_details[:5]:
                                    translated_title = utils.translate_text(item['title'])
                                    translated_items.append({
                                        **item,
                                        'translated_title': translated_title if translated_title else item['title']
                                    })
                            
                            # Display translated news items
                            for item in translated_items:
                                sentiment_icon = '🟢' if item['compound'] > 0.05 else '🔴' if item['compound'] < -0.05 else '⚪'
                                with st.expander(f"{sentiment_icon} {item['translated_title']}"):
                                    st.write(f"**출처:** {item['publisher']}")
                                    st.write(f"**감성 점수:** {item['compound']:.3f}")
                                    if item.get('link') and item['link'] != '#':
                                        st.markdown(f"[기사 읽기]({item['link']})")
                                    else:
                                        st.write("링크 없음")
                        else:
                            st.warning("뉴스는 수집되었지만 감성 분석 결과가 없습니다.")
                    else:
                        st.warning(f"'{ticker}'에 대한 최신 뉴스를 찾을 수 없습니다.")
                        st.info("뉴스가 없는 경우 감성 분석을 수행할 수 없습니다.")

                with tab4:
                    st.markdown("""
                        <div class="glass-panel" style="padding: 1.25rem; margin-bottom: 1.5rem;">
                            <h3 style="margin: 0; font-size: 1.25rem;">💡 AI 투자 전략 제안</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    for idx, advice in enumerate(advice_list):
                        # Determine color based on advice type
                        if "매수" in advice or "상승" in advice or "긍정" in advice:
                            border_color = "#4CAF50"
                            bg_color = "rgba(76, 175, 80, 0.1)"
                        elif "매도" in advice or "하락" in advice or "부정" in advice:
                            border_color = "#f44336"
                            bg_color = "rgba(244, 67, 54, 0.1)"
                        else:
                            border_color = "#ff9800"
                            bg_color = "rgba(255, 152, 0, 0.1)"
                        
                        st.markdown(f"""
                            <div style="
                                background: {bg_color};
                                border-left: 5px solid {border_color};
                                border-radius: 12px;
                                padding: 1.25rem 1.5rem;
                                margin-bottom: 1rem;
                                color: #f1f5f9;
                                line-height: 1.7;
                                font-size: 1rem;
                                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                            ">
                                {advice}
                            </div>
                        """, unsafe_allow_html=True)
