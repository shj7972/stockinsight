import streamlit as st

def show():
    st.markdown("""
        <div class="glass-panel" style="padding: 1.25rem; margin-bottom: 2rem;">
            <h3 style="margin: 0; font-size: 1.5rem; display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 2rem;">🧮</span> 주식 수익률 계산기
            </h3>
            <p style="color: #94a3b8; margin-top: 0.5rem;">매수/매도 금액과 수수료를 입력하여 예상 수익을 계산해보세요.</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 📥 매수 정보")
        buy_price = st.number_input("매수 단가 (원/$)", min_value=0.0, value=10000.0, step=100.0, format="%.2f")
        quantity = st.number_input("수량 (주)", min_value=1, value=10, step=1)
        
    with col2:
        st.markdown("### 📤 매도(현재) 정보")
        sell_price = st.number_input("매도/현재 단가 (원/$)", min_value=0.0, value=12000.0, step=100.0, format="%.2f")
        fee_rate = st.number_input("거래 수수료율 (%)", min_value=0.0, value=0.015, step=0.001, format="%.3f")
        # tax_rate = st.number_input("세금 (%)", min_value=0.0, value=0.25, step=0.01) # Optional, keep simple for now

    st.markdown("---")

    if st.button("계산하기", type="primary", use_container_width=True):
        # Calculation Logic
        total_buy = buy_price * quantity
        total_sell_gross = sell_price * quantity
        
        # Fees (usually calculated on both buy and sell, or just sell depending on market. Let's assume on "transaction" total value involved if simple, but usually:
        # Buy Fee = Total Buy * Fee Rate / 100
        # Sell Fee = Total Sell * Fee Rate / 100
        # Let's simplify: User inputs "Total effective fee rate for round trip" or just apply to sell?
        # Standard: Commission on both. But let's assume the user puts in the ROUND TRIP fee or just one way.
        # Let's verify standard calc.
        # Often: Buy Fee (0.xxx%) + Sell Fee (0.xxx%) + Sell Tax (0.xx%).
        # Let's apply fee to both buy and sell amounts separately.
        
        buy_fee = total_buy * (fee_rate / 100)
        sell_fee = total_sell_gross * (fee_rate / 100)
        total_fee = buy_fee + sell_fee
        
        total_buy_cost = total_buy + buy_fee
        total_sell_net = total_sell_gross - sell_fee
        
        net_profit = total_sell_net - total_buy_cost
        roi = (net_profit / total_buy_cost) * 100 if total_buy_cost > 0 else 0

        # Display Results
        st.markdown("### 📊 계산 결과")
        
        r_col1, r_col2, r_col3 = st.columns(3)
        
        r_col1.metric("총 매수 금액 (수수료 포함)", f"{total_buy_cost:,.0f}")
        r_col2.metric("총 평가 금액 (수수료 제외)", f"{total_sell_net:,.0f}")
        
        roi_color = "normal" if net_profit >= 0 else "inverse"
        r_col3.metric("최종 손익", f"{net_profit:+,.0f}", f"{roi:+.2f}%", delta_color=roi_color)

        st.markdown(f"""
            <div class="glass-panel" style="padding: 1rem; margin-top: 1rem; font-size: 0.9rem; color: #cbd5e1;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>순수 매수금:</span>
                    <span>{total_buy:,.0f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span>순수 평가금:</span>
                    <span>{total_sell_gross:,.0f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; border-top: 1px solid #334155; padding-top: 0.5rem;">
                    <span>총 수수료:</span>
                    <span style="color: #fca5a5;">-{total_fee:,.0f}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

