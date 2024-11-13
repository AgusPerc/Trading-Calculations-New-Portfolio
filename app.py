import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Set page config
st.set_page_config(
    page_title="Trading Strategy Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar controls
st.sidebar.title("Trading Parameters")

# Initial portfolio input
initial_portfolio = st.sidebar.number_input(
    "Initial Portfolio (USD)",
    min_value=1000,
    max_value=1000000,
    value=75000,
    step=1000,
    format="%d"
)

# Risk percentage input
risk_percentage = st.sidebar.slider(
    "Risk Per Trade (%)",
    min_value=0.5,
    max_value=5.0,
    value=2.0,
    step=0.1
)

# Max drawdown input
max_dd = st.sidebar.slider(
    "Estimated Max Drawdown (%)",
    min_value=5.0,
    max_value=50.0,
    value=32.6,
    step=0.1
)

# Return scenarios
st.sidebar.subheader("Monthly Return Scenarios")
best_case = st.sidebar.slider("Best Case Return (%)", 0, 100, 66)
normal_case = st.sidebar.slider("Normal Case Return (%)", 0, best_case, 32)
worst_case = st.sidebar.slider("Worst Case Return (%)", 0, normal_case, 21)

# Calculate derived values
risk_amount = initial_portfolio * (risk_percentage / 100)
max_loss = initial_portfolio * (max_dd / 100)
remaining_portfolio = initial_portfolio - max_loss
max_trades = initial_portfolio / risk_amount

# Main dashboard area
st.title("Trading Strategy Metrics Dashboard")
st.markdown("---")

# Key metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Initial Portfolio",
        value=f"${initial_portfolio:,.2f} USD",
        delta=None
    )

with col2:
    st.metric(
        label="Risk Per Trade",
        value=f"${risk_amount:,.2f} USD",
        delta=f"{risk_percentage}%"
    )

with col3:
    st.metric(
        label="Estimated Max Drawdown",
        value=f"{max_dd}%",
        delta=f"-${max_loss:,.2f} USD",
        delta_color="inverse"
    )

# Monthly return scenarios with gauge charts
st.markdown("---")
st.subheader("Monthly Return Scenarios")

def create_gauge(value, title):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, worst_case], 'color': "lightgray"},
                {'range': [worst_case, normal_case], 'color': "gray"},
                {'range': [normal_case, best_case], 'color': "lightblue"}
            ],
        }
    ))
    fig.update_layout(height=250)
    return fig

col1, col2, col3 = st.columns(3)

with col1:
    st.plotly_chart(
        create_gauge(best_case, "Best Case Scenario"),
        use_container_width=True
    )

with col2:
    st.plotly_chart(
        create_gauge(normal_case, "Normal Case Scenario"),
        use_container_width=True
    )

with col3:
    st.plotly_chart(
        create_gauge(worst_case, "Worst Case Scenario"),
        use_container_width=True
    )

# Portfolio projection
st.markdown("---")
st.subheader("Portfolio Projection")

# Create monthly projection for different scenarios
months = range(1, 13)
best_case_proj = [initial_portfolio * (1 + best_case/100)**m for m in months]
normal_case_proj = [initial_portfolio * (1 + normal_case/100)**m for m in months]
worst_case_proj = [initial_portfolio * (1 + worst_case/100)**m for m in months]

fig = go.Figure()
fig.add_trace(go.Scatter(x=list(months), y=best_case_proj, name="Best Case", line=dict(color="green")))
fig.add_trace(go.Scatter(x=list(months), y=normal_case_proj, name="Normal Case", line=dict(color="blue")))
fig.add_trace(go.Scatter(x=list(months), y=worst_case_proj, name="Worst Case", line=dict(color="red")))

fig.update_layout(
    title="12-Month Portfolio Projection",
    xaxis_title="Months",
    yaxis_title="Portfolio Value (USD)",
    hovermode="x unified"
)
st.plotly_chart(fig, use_container_width=True)

# Risk Analysis
st.markdown("---")
st.subheader("Portfolio Risk Analysis")

col1, col2 = st.columns(2)

with col1:
    st.info(f"Maximum Potential Loss (Based on Max DD): ${max_loss:,.2f} USD")
    st.metric(
        label="Maximum Number of Simultaneous Trades",
        value=f"{int(max_trades)}",
        help="Based on risk per trade"
    )
    
with col2:
    st.success(f"Remaining Portfolio After Max DD: ${remaining_portfolio:,.2f} USD")
    st.metric(
        label="Average Trade Size",
        value=f"${initial_portfolio/max_trades:,.2f} USD",
        help="Suggested position size based on risk parameters"
    )

# Position Calculator
st.markdown("---")
st.subheader("Position Size Calculator")

col1, col2, col3 = st.columns(3)

with col1:
    entry_price = st.number_input("Entry Price", min_value=0.01, value=100.0, step=0.01)
    
with col2:
    stop_loss = st.number_input("Stop Loss Price", min_value=0.01, value=95.0, step=0.01)
    
with col3:
    risk_per_trade = risk_amount
    position_size = abs(risk_per_trade / (entry_price - stop_loss))
    total_position_value = position_size * entry_price
    
    st.metric(
        label="Position Size (Units)",
        value=f"{position_size:.2f}",
        delta=f"Total Value: ${total_position_value:,.2f}"
    )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <i>Note: All calculations are based on provided estimates and actual results may vary. 
    Past performance does not guarantee future results.</i>
</div>
""", unsafe_allow_html=True)

# Cache the session state
if 'portfolio_history' not in st.session_state:
    st.session_state.portfolio_history = []