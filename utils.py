# =======================
# File: utils.py
# =======================
import plotly.graph_objects as go
import pandas as pd
import numpy as np

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

