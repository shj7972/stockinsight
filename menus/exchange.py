import streamlit as st
import yfinance as yf
import pandas as pd

def get_exchange_rates():
    try:
        # USD/KRW
        usd_krw_ticker = yf.Ticker("KRW=X")
        usd_krw = usd_krw_ticker.history(period="1d")['Close'].iloc[-1]
        
        # USD/JPY
        usd_jpy_ticker = yf.Ticker("JPY=X")
        usd_jpy = usd_jpy_ticker.history(period="1d")['Close'].iloc[-1]
        
        # EUR/USD (Note: EUR=X is usually USD/EUR or similar, but EURUSD=X is 1 EUR in USD)
        # Let's get EURUSD=X to be safe -> Value ~1.1 means 1 EUR = 1.1 USD.
        eur_usd_ticker = yf.Ticker("EURUSD=X")
        eur_usd = eur_usd_ticker.history(period="1d")['Close'].iloc[-1]
        
        return {
            "USD": 1.0,
            "KRW": usd_krw,
            "JPY": usd_jpy,
            "EUR": 1.0 / eur_usd # Store as 'per USD' to standardize. 1 USD = (1/1.1) EUR roughly.
        }
    except Exception as e:
        return None

def show():
    st.markdown("""
        <div class="glass-panel" style="padding: 1.25rem; margin-bottom: 2rem;">
            <h3 style="margin: 0; font-size: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 2rem;">💱</span> 환율 계산기
            </h3>
            <p style="color: #94a3b8; margin-top: 0.5rem;">실시간 환율 정보를 바탕으로 환전 금액을 계산합니다.</p>
        </div>
    """, unsafe_allow_html=True)

    with st.spinner("환율 정보 가져오는 중..."):
        rates = get_exchange_rates()

    if rates:
        col1, col2, col3 = st.columns([1, 0.2, 1])
        
        with col1:
            st.markdown("### 📤 보내는 금액")
            amount = st.number_input("금액", min_value=0.0, value=1.0, format="%.2f")
            from_curr = st.selectbox("통화 선택", ["USD", "KRW", "JPY", "EUR"], key="from_curr")
            
        with col2:
            st.markdown("<div style='height: 3rem;'></div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center; font-size: 2rem;'>➡️</div>", unsafe_allow_html=True)
            
        with col3:
            st.markdown("### 📥 받는 금액")
            to_curr = st.selectbox("통화 선택", ["KRW", "USD", "JPY", "EUR"], key="to_curr")
            
            # Conversion Logic
            # Base is USD
            # Amount * (1/Rate_From) * Rate_To
            # e.g. 1000 KRW -> USD: 1000 * (1/1300) * 1 = 0.76 USD.
            # e.g. 10 USD -> KRW: 10 * (1/1) * 1300 = 13000 KRW.
            
            if from_curr == "JPY":
                # JPY is usually quoted per 100 Yen in Korea, but here logic is standard math.
                # But note: stock market JPY rate is JPY per USD (~145).
                pass
            
            base_amount = amount / rates[from_curr]
            converted_amount = base_amount * rates[to_curr]
            
            # Display Result
            currency_symbols = {"USD": "$", "KRW": "₩", "JPY": "¥", "EUR": "€"}
            sym = currency_symbols.get(to_curr, "")
            
            st.markdown(f"""
                <div style="
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 12px;
                    padding: 1.5rem;
                    text-align: center;
                    margin-top: 2rem;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                ">
                    <div style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 0.5rem;">예상 환전 금액</div>
                    <div style="font-size: 2rem; font-weight: bold; color: #38bdf8;">
                        {sym} {converted_amount:,.2f}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        
        # Display Current Rates Panel
        st.markdown("### 🌏 주요 환율 정보 (1 USD 기준)")
        info_col1, info_col2, info_col3 = st.columns(3)
        
        info_col1.metric("USD / KRW", f"{rates['KRW']:,.2f} 원")
        info_col2.metric("USD / JPY", f"{rates['JPY']:,.2f} 엔")
        
        # EUR/USD is inverted for display usually "1 EUR = X USD"
        eur_usd_disp = 1.0 / rates['EUR']
        info_col3.metric("EUR / USD", f"{eur_usd_disp:,.4f} 달러")
        
    else:
        st.error("환율 정보를 가져오는데 실패했습니다.")
