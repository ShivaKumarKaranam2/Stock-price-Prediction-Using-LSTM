# 📈 Stock Price Prediction using LSTM

Welcome to the **Stock Price Prediction App**, powered by **Streamlit** and deployed on **Hugging Face Spaces**.

This app predicts the future **closing prices** of any stock using a deep learning model (**LSTM - Long Short-Term Memory**). It allows you to interactively fetch, visualize, and forecast stock trends with a user-friendly interface.

🔗 **Live App**: [Click to Open](https://huggingface.co/spaces/Shiva-k22/Stock-price-prediction-uisng-LSTM)

---

## 🚀 Features

✅ Predict stock prices using a pre-trained LSTM model  
✅ Visualize historical trends and future forecasts  
✅ Download both historical and predicted data as CSV  
✅ Customize prediction duration (1–30 days)  
✅ Clean and interactive Streamlit UI

---

## 🧠 Model Details

- **Type**: LSTM (Long Short-Term Memory)
- **Framework**: TensorFlow / Keras
- **Trained On**: Only the `Close` price of historical stock data
- **Sequence Length**: 100 days
- **Output**: Predicted `Close` prices for next *n* days

---

## 🛠 Built With

| Library        | Purpose                           |
|----------------|-----------------------------------|
| `streamlit`    | Web UI                            |
| `yfinance`     | Fetching stock data               |
| `tensorflow`   | LSTM Model Prediction             |
| `scikit-learn` | Data Scaling (MinMaxScaler)       |
| `matplotlib`   | Plotting graphs                   |
| `pandas`       | Data handling                     |
| `numpy`        | Numerical operations              |

---

## 📁 How to Use (Locally)

```bash
# Clone the repo
git clone https://huggingface.co/spaces/Shiva-k22/Stock-price-prediction-uisng-LSTM
cd Stock-price-prediction-uisng-LSTM

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run stock_app.py

