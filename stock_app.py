# =======================
# File: stock_app.py
# =======================
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import asyncio
import nest_asyncio

nest_asyncio.apply()


import datetime as dt
import matplotlib.pyplot as plt
from keras.models import load_model
from screener import  get_screener_data,build_investment_decision_prompt
from utils import plot_eps_chart
 


st.set_page_config(page_title="📈 Stock Price App", layout="wide")
tabs = st.tabs(["📉 LSTM Predictor", "📘 Stock Analyzer"])

# =====================================
# 📉 Tab 1: LSTM Predictor
# =====================================
with tabs[0]:
    st.title("📉 Stock Price Prediction using LSTM")
    model = load_model("C:/Users/karan/OneDrive/Documents/Stock price/stock_model.h5", compile=False)
    stock = st.sidebar.text_input("Enter Stock Symbol", value="RELIANCE.NS")
    start_date = st.sidebar.date_input("Start Date", dt.date(2010, 1, 1))
    end_date = dt.datetime.now()

    @st.cache_data
    def load_stock_data(symbol, start, end):
        df = yf.download(symbol, start=start, end=end)
        df = df.reset_index()
        return df

    df = load_stock_data(stock, start_date, end_date)
    if df.empty:
        st.warning("No data found for the given stock symbol.")
        st.stop()

    st.subheader(f"📄 Stock Data for {stock}")
    st.dataframe(df.tail())

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", csv, f"{stock}_data.csv", "text/csv")

    fig1, ax1 = plt.subplots(figsize=(12, 5))
    ax1.plot(df['Date'], df['Close'], label='Close Price', color='blue')
    ax1.set_title(f"{stock} Close Price from {start_date} to Today")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Close Price")
    ax1.legend()
    st.pyplot(fig1)

    features = ['Close']
    data = df[features]
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(data)

    train_size = int(len(scaled_data) * 0.70)
    test_data = scaled_data[train_size - 100:]
    close_index = features.index('Close')

    def create_sequences(data, seq_len=100, target_index=0):
        x, y = [], []
        for i in range(seq_len, len(data)):
            x.append(data[i-seq_len:i])
            y.append(data[i, target_index])
        return np.array(x), np.array(y)

    x_test, y_test = create_sequences(test_data, target_index=close_index)
    x_test = x_test.reshape((x_test.shape[0], x_test.shape[1], len(features)))

    predicted_prices = model.predict(x_test)
    predicted_prices = predicted_prices.reshape(-1, 1)

    pred_array = np.zeros((len(predicted_prices), len(features)))
    pred_array[:, close_index] = predicted_prices[:, 0]
    y_test_array = np.zeros((len(y_test), len(features)))
    y_test_array[:, close_index] = y_test

    predicted_prices_rescaled = scaler.inverse_transform(pred_array)[:, close_index]
    actual_prices_rescaled = scaler.inverse_transform(y_test_array)[:, close_index]

    st.subheader("📊 Latest Prediction")
    st.metric(label="Next-Day Predicted Close Price", value=f"${predicted_prices_rescaled[-1]:.2f}")

    fig2, ax2 = plt.subplots(figsize=(12, 5))
    ax2.plot(actual_prices_rescaled, label='Actual Price', color='green')
    ax2.plot(predicted_prices_rescaled, label='Predicted Price', color='red')
    ax2.set_title(f"{stock} Actual vs Predicted Prices")
    ax2.set_xlabel("Time")
    ax2.set_ylabel("Price")
    ax2.legend()
    st.pyplot(fig2)

    st.subheader("🔮 Predict Future Stock Prices")
    n_days = st.slider("Select number of future days to predict", min_value=1, max_value=30, value=7)
    future_input = scaled_data[-100:].reshape(1, 100, len(features))
    future_predictions = []
    for _ in range(n_days):
        pred = model.predict(future_input, verbose=0)[0][0]
        new_row = np.array([pred if i == close_index else future_input[0, -1, i] for i in range(future_input.shape[2])])
        next_input = np.vstack([future_input[0, 1:], new_row])
        future_input = np.expand_dims(next_input, axis=0)
        future_predictions.append(pred)

    future_array = np.zeros((n_days, len(features)))
    future_array[:, close_index] = future_predictions
    future_prices = scaler.inverse_transform(future_array)[:, close_index]

    future_dates = pd.date_range(start=df['Date'].iloc[-1] + pd.Timedelta(days=1), periods=n_days)
    future_df = pd.DataFrame({"Date": future_dates, "Predicted Close Price": future_prices})
    st.write("### 📅 Future Predicted Prices")
    st.dataframe(future_df)

    fig3, ax3 = plt.subplots(figsize=(10, 4))
    ax3.plot(future_df["Date"], future_df["Predicted Close Price"], marker='o', linestyle='--', color='purple')
    ax3.set_title(f"{stock} - Next {n_days} Days Predicted Close Prices")
    ax3.set_xlabel("Date")
    ax3.set_ylabel("Predicted Price")
    st.pyplot(fig3)

    csv_future = future_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv_future, f"{stock}_future_predictions.csv", "text/csv")


# 📘 Tab 2: Stock Analyzer (Enhanced)

with tabs[1]:
    st.title("📘 Stock Analyzer & AI Financial Advisor")

    if st.button("🔍 Analyze Stock"):
        with st.spinner("Fetching Stock Analysis & Advice..."):
            clean = stock.upper().split(".")[0] + ".NS"

            # ✅ Step 1: Scrape Screener Data
            overview, analysis, financial_df = get_screener_data(clean)

            # ✅ Step 2: Display Stock Overview
            st.subheader("📊 Stock Overview")
            if overview:
                st.json(overview)
            else:
                st.error("Failed to load overview data.")

            # ✅ Step 3: Analyst Forecasts
            if analysis:
                st.subheader("📊 Analyst Forecasts")
                for key, value in analysis.items():
                    st.markdown(f"- **{key}**: {value}")
            else:
                st.warning("❗ No analyst data found.")

            # ✅ Step 4: Financial Charts
            st.subheader("📈 Income Statement / Financials")
            if financial_df is not None and not financial_df.empty:
                st.plotly_chart(plot_eps_chart(financial_df), use_container_width=True)
            else:
                st.warning("Financials data unavailable.")

            # ✅ Step 5: Generate Investment Advice
            st.subheader("💡 AI Investment Advice (Gemini)")

            if overview and future_predictions:
                predicted_price = future_predictions[0]
                try:
                    advice_text = build_investment_decision_prompt(stock, overview, predicted_price)
                    st.success("Here’s what Gemini thinks:")
                    st.markdown(advice_text)

                    # ✅ Step 6: Download Button for Advice
                    st.download_button(
                        label="📥 Download Advice (.txt)",
                        data=advice_text,
                        file_name=f"{stock}_gemini_advice.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"Gemini API error: {e}")
            else:
                st.warning("Overview or predicted price missing. Advice generation skipped.")


            

            
   