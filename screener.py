# =======================
# File: screener.py
# =======================

import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import json
import pandas as pd
import yfinance as yf
import re
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)


# ✅ Use requests to fetch raw HTML
def get_html_with_requests(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch HTML for {url}, Status: {response.status_code}")


# ✅ Replace Selenium with yfinance for Yahoo Overview
def scrape_overview(symbol: str) -> dict:
    ticker = yf.Ticker(symbol)
    info = ticker.info

    overview = {
        "Previous Close": info.get("previousClose", "N/A"),
        "Open": info.get("open", "N/A"),
        "Bid": f"{info.get('bid', 'N/A')} x {info.get('bidSize', 'N/A')}",
        "Ask": f"{info.get('ask', 'N/A')} x {info.get('askSize', 'N/A')}",
        "Day’s Range": f"{info.get('dayLow', 'N/A')} - {info.get('dayHigh', 'N/A')}",
        "52 Week Range": f"{info.get('fiftyTwoWeekLow', 'N/A')} - {info.get('fiftyTwoWeekHigh', 'N/A')}",
        "Volume": info.get("volume", "N/A"),
        "Avg. Volume": info.get("averageVolume", "N/A"),
        "Market Cap": info.get("marketCap", "N/A"),
        "PE Ratio (TTM)": info.get("trailingPE", "N/A"),
        "EPS (TTM)": info.get("trailingEps", "N/A"),
        "Earnings Date": str(info.get("earningsDate", "N/A")),
        "Dividend & Yield": f"{info.get('dividendRate', '0.00')} ({info.get('dividendYield', '0.00')})",
        "Ex-Dividend Date": str(info.get("exDividendDate", "N/A"))
    }

    return {k: str(v) if v is not None else "N/A" for k, v in overview.items()}


# ✅ Extract Analysis Page Text and Parse via Gemini
def scrape_analysis(symbol: str) -> dict:
    url = f"https://finance.yahoo.com/quote/{symbol}/analysis"
    html = get_html_with_requests(url)
    soup = BeautifulSoup(html, "html.parser")

    all_tables_text = ""
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = row.find_all(["th", "td"])
            row_text = " | ".join(cell.text.strip() for cell in cells)
            all_tables_text += row_text + "\n"

    if not all_tables_text.strip():
        print("⚠️ No analysis text found.")
        return {}

    return extract_analysis_from_html(all_tables_text, symbol)


def extract_analysis_from_html(text, symbol):
    prompt = f"""
You are a financial data extractor for stock analysis. From the table-like text below for the Yahoo Finance analysis page of {symbol}, extract a structured JSON object with the key metrics.

Expected Format:
{{
  "Revenue Estimate - Current Qtr": "...",
  "Revenue Estimate - Next Qtr": "...",
  "EPS Trend - Current Qtr": "...",
  "EPS Trend - Current Year": "...",
  ...
}}

Only extract what's present. Do not guess. Raw Text:
----
{text}
"""
    model = genai.GenerativeModel("gemma-3n-e4b-it")
    response = model.generate_content(prompt)

    try:
        json_match = re.search(r"{.*?}", response.text, re.DOTALL)
        if json_match:
            json_text = json_match.group(0)
            return json.loads(json_text)
        else:
            raise ValueError("No valid JSON found in Gemini output")
    except Exception as e:
        print("⚠️ Could not parse Gemini Analysis JSON:", e)
        print(response.text)
        return {}


# ✅ Financials using yfinance
def scrape_financials(symbol: str) -> pd.DataFrame:
    try:
        return yf.Ticker(symbol).financials
    except:
        return pd.DataFrame()


# ✅ Combined Function
def get_screener_data(symbol: str) -> tuple:
    overview = scrape_overview(symbol)
    analysis = scrape_analysis(symbol)
    financial_df = scrape_financials(symbol)
    return overview, analysis, financial_df


# ✅ Gemini Advice Builder
def build_investment_decision_prompt(symbol: str, overview: dict, predicted_price: float) -> str:
    prompt = f"""
You are a professional stock market advisor.

Analyze this stock and provide investment advice in the following format:
1. Investment Decision: Buy / Hold / Sell
2. Reasoning based on company metrics
3. Risk Factors
4. Final Recommendation Summary (one paragraph)

### Stock Symbol: {symbol}
### Predicted Price (Next Trading Day): ₹{predicted_price:.2f}

### Yahoo Finance Key Metrics (overview):
{json.dumps(overview, indent=2)}

Be precise and explain based only on the data provided. Don’t fabricate missing metrics.
"""
    model = genai.GenerativeModel("gemma-3n-e4b-it")
    response = model.generate_content(prompt)
    return response.text.strip()
