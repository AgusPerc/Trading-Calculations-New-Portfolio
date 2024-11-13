import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Set page config
st.set_page_config(
    page_title="Trading Strategy Dashboard",
    layout="centered",  # Changed to centered for better mobile view
    initial_sidebar_state="collapsed"  # Default collapsed on mobile
)

# Custom CSS for mobile responsiveness
st.markdown("""
    <style>
    .stPlotlyChart {
        width: 100%;
        min-width: 300px;
    }
    .st-emotion-cache-1r6slb0 {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

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
st.title("Trading Strategy Metrics")
st.markdown("---")

# Key metrics - Stacked vertically for mobile
st.metric(
    label="Initial Portfolio",
    value=f"${initial_portfolio:,.2f} USD",
    delta=None
)

st.metric(
    label="Risk Per Trade",
    value=f"${risk_amount:,.2f} USD",
    delta=f"{risk_percentage}%"
)

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
    fig.update_layout(height=200)  # Reduced height for mobile
    return fig

# Display gauges vertically for mobile
st.plotly_chart(create_gauge(best_case, "Best Case"), use_container_width=True)
st.plotly_chart(create_gauge(normal_case, "Normal Case"), use_container_width=True)
st.plotly_chart(create_gauge(worst_case, "Worst Case"), use_container_width=True)

# Portfolio projection with linear growth
st.markdown("---")
st.subheader("Portfolio Projection")

# Create monthly projection for different scenarios (linear)
months = range(1, 13)
monthly_best = initial_portfolio * (best_case/100)
monthly_normal = initial_portfolio * (normal_case/100)
monthly_worst = initial_portfolio * (worst_case/100)

best_case_proj = [initial_portfolio + (monthly_best * m) for m in months]
normal_case_proj = [initial_portfolio + (monthly_normal * m) for m in months]
worst_case_proj = [initial_portfolio + (monthly_worst * m) for m in months]

fig = go.Figure()
fig.add_trace(go.Scatter(x=list(months), y=best_case_proj, name="Best Case", line=dict(color="green")))
fig.add_trace(go.Scatter(x=list(months), y=normal_case_proj, name="Normal Case", line=dict(color="blue")))
fig.add_trace(go.Scatter(x=list(months), y=worst_case_proj, name="Worst Case", line=dict(color="red")))

fig.update_layout(
    title="12-Month Portfolio Projection (Linear)",
    xaxis_title="Months",
    yaxis_title="Portfolio Value (USD)",
    hovermode="x unified",
    height=400  # Adjusted height for mobile
)
st.plotly_chart(fig, use_container_width=True)

# Risk Analysis
st.markdown("---")
st.subheader("Portfolio Risk Analysis")

st.info(f"Maximum Potential Loss (Based on Max DD): ${max_loss:,.2f} USD")
st.metric(
    label="Maximum Number of Simultaneous Trades",
    value=f"{int(max_trades)}",
    help="Based on risk per trade"
)
    
st.success(f"Remaining Portfolio After Max DD: ${remaining_portfolio:,.2f} USD")
st.metric(
    label="Average Trade Size",
    value=f"${initial_portfolio/max_trades:,.2f} USD",
    help="Suggested position size based on risk parameters"
)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <i>Note: All calculations are based on provided estimates and actual results may vary. 
    Past performance does not guarantee future results.</i>
</div>
""", unsafe_allow_html=True)
