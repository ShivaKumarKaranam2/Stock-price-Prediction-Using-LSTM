# =======================
# File: screener.py
# =======================
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import google.generativeai as genai
import json
import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup

# ✅ Gemini API Key
genai.configure(api_key="AIzaSyDXP7hms2jkswxBZhMh8TTXO_dlAavq6ko")

# ✅ Get HTML using Selenium
def get_rendered_html_selenium(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.get(url)
    driver.implicitly_wait(5)
    html = driver.page_source
    driver.quit()
    return html

# ✅ Gemini-based Metric Extractor
def extract_metrics_from_html(html, symbol):
    prompt = f"""
You are a financial data extractor. From the Yahoo Finance HTML page for {symbol}, extract all key metrics visible in the summary section.

Format output in JSON like:
{{
  "Previous Close": "...",
  "Open": "...",
  "Bid": "...",
  "Ask": "...",
  "Day’s Range": "...",
  "52 Week Range": "...",
  "Volume": "...",
  "Avg. Volume": "...",
  "Market Cap": "...",
  "PE Ratio (TTM)": "...",
  "EPS (TTM)": "...",
  "Earnings Date": "...",
  "Dividend & Yield": "...",
  "Ex-Dividend Date": "..."
}}

Don’t guess data. HTML content:
----
{html[:18000]}
"""
    model = genai.GenerativeModel("gemma-3n-e4b-it")
    response = model.generate_content(prompt)
    try:
        json_start = response.text.find("{")
        json_data = response.text[json_start:].split("}```")[0].strip()
        return json.loads(json_data)
    except Exception as e:
        print("⚠️ Could not parse JSON:", e)
        print(response.text)
        return {}

# ✅ Overview Data
def scrape_overview(symbol: str) -> dict:
    url = f"https://finance.yahoo.com/quote/{symbol}"
    html = get_rendered_html_selenium(url)
    return extract_metrics_from_html(html, symbol=symbol)

# ✅ Analyst Data
def scrape_analysis(symbol: str) -> dict:
    url = f"https://finance.yahoo.com/quote/{symbol}/analysis"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    data = {}
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) == 2:
                key = cols[0].text.strip()
                val = cols[1].text.strip()
                if key and val:
                    data[key] = val
    return data

# ✅ Financials
def scrape_financials(symbol: str) -> pd.DataFrame:
    try:
        fin = yf.Ticker(symbol).financials
        return fin
    except:
        return pd.DataFrame()

# ✅ Main Fetcher
def get_screener_data(symbol: str) -> tuple:
    overview = scrape_overview(symbol)
    analysis = scrape_analysis(symbol)
    financial_df = scrape_financials(symbol)
    return overview, analysis, financial_df

# ✅ LLM Prompt Builder
def build_investment_decision_prompt(
    symbol: str,
    overview_data: dict,
    technical_indicators: dict,
) -> str:
    return f"""
You are a financial investment advisor with expertise in stock market analysis and forecasting.

Your task is to analyze the stock ** ({symbol})** and provide a detailed investment recommendation based on:

🎯 Your tasks:
1. Determine whether the stock is currently **undervalued**, **overvalued**, or **fairly priced**.
2. Identify short-term (next 7 days) and medium-term (30 days) trends based on both LSTM predictions and technical indicators.
3. Assess the sentiment and recent news impact (positive/neutral/negative).
4. Finally, give a **detailed recommendation** for each of the following traders:
   - Conservative Investor (risk-averse, long-term)
   - Swing Trader (technical-based, medium-term)
   - Day Trader (short-term, volatility-based)

📌 Output Format:
```json
{{
  "ValuationStatus": "...",
  "ShortTermTrend": "...",
  "MediumTermForecast": "...",
  "SentimentImpact": "...",
  "Recommendations": {{
    "ConservativeInvestor": "...",
    "SwingTrader": "...",
    "DayTrader": "..."
  }}
}}
```"""

