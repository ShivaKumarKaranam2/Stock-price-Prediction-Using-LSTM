# =======================
# File: utils.py
# =======================
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# Format currency to ₹ Cr
def humanize_cr(value: float) -> str:
    if not value or np.isnan(value):
        return "₹0"
    cr = value / 1e7  # Convert to Crores
    return f"₹{cr:,.0f} Cr"

# Compute Moving Averages, RSI, MACD
def compute_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.set_index('Date', inplace=True)
    
    # Moving Averages
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['MA50'] = df['Close'].rolling(window=50).mean()
    
    # RSI (14)
    delta = df['Close'].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    roll_up = up.rolling(14).mean()
    roll_down = down.rolling(14).mean()
    rs = roll_up / (roll_down + 1e-9)
    df['RSI'] = 100.0 - (100.0 / (1.0 + rs))

    # MACD
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

    df.reset_index(inplace=True)
    return df

# Moving Averages Plot
def plot_ma_chart(df_ta: pd.DataFrame):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_ta['Date'], y=df_ta['Close'], name='Close Price'))
    if 'MA20' in df_ta:
        fig.add_trace(go.Scatter(x=df_ta['Date'], y=df_ta['MA20'], name='MA20'))
    if 'MA50' in df_ta:
        fig.add_trace(go.Scatter(x=df_ta['Date'], y=df_ta['MA50'], name='MA50'))
    fig.update_layout(title='Moving Averages', xaxis_title='Date', yaxis_title='Price')
    return fig

# RSI Chart
def plot_rsi_chart(df_ta: pd.DataFrame):
    fig = go.Figure()
    if 'RSI' in df_ta:
        fig.add_trace(go.Scatter(x=df_ta['Date'], y=df_ta['RSI'], name='RSI'))
        fig.add_hline(y=70, line_dash='dash', line_color='red')
        fig.add_hline(y=30, line_dash='dash', line_color='green')
    fig.update_layout(title='RSI (14)', xaxis_title='Date', yaxis_title='RSI')
    return fig

# MACD Chart
def plot_macd_chart(df_ta: pd.DataFrame):
    fig = go.Figure()
    if 'MACD' in df_ta and 'Signal' in df_ta:
        fig.add_trace(go.Scatter(x=df_ta['Date'], y=df_ta['MACD'], name='MACD'))
        fig.add_trace(go.Scatter(x=df_ta['Date'], y=df_ta['Signal'], name='Signal'))
        fig.add_hline(y=0, line_dash='dash', line_color='gray')
    fig.update_layout(title='MACD', xaxis_title='Date', yaxis_title='Value')
    return fig

# EPS Trend Chart
def plot_eps_chart(financials: pd.DataFrame):
    fig = go.Figure()
    try:
        if financials is None or financials.empty:
            return fig
        if 'Net Income' in financials.index and 'Basic Shares Outstanding' in financials.index:
            eps_series = financials.loc['Net Income'] / financials.loc['Basic Shares Outstanding']
        elif 'Basic EPS' in financials.index:
            eps_series = financials.loc['Basic EPS']
        else:
            return fig
        eps_series = eps_series.sort_index()
        eps_series.index = pd.to_datetime(eps_series.index, errors='coerce')
        eps_series = eps_series.dropna()
        fig.add_trace(go.Scatter(x=eps_series.index, y=eps_series.values, mode='lines+markers', name='EPS'))
        fig.update_layout(title='EPS Trend', xaxis_title='Period', yaxis_title='EPS')
        return fig
    except Exception:
        return fig

# Shareholding Pattern Pie Chart
def plot_shareholding_pie(data: dict):
    labels = list(data.keys())
    values = list(data.values())
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4)])
    fig.update_layout(title='Shareholding Pattern')
    return fig
