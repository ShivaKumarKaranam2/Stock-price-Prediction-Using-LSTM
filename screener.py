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

# ✅ Replaces Selenium – use requests to fetch HTML
def get_html_with_requests(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch HTML for {url}, Status: {response.status_code}")

# ✅ Extract Overview Metrics from HTML using Gemini
def extract_metrics_from_html(html, symbol):
    prompt = f"""
You are a financial data extractor. From the following Yahoo Finance HTML page for the stock symbol {symbol}, extract all the summary key-value metrics displayed to the user.

Your response should be a valid JSON object like:
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

Only include real data if available. Don’t make up values. HTML content is below:
----
{html[:18000]}
"""

    model = genai.GenerativeModel("gemma-3n-e4b-it")
    response = model.generate_content(prompt)

    try:
        json_match = re.search(r"{.*?}", response.text, re.DOTALL)
        if json_match:
            json_text = json_match.group(0)
            return json.loads(json_text)
        else:
            raise ValueError("No valid JSON found")
    except Exception as e:
        print("⚠️ Could not parse JSON:", e)
        print(response.text)
        return {}

# ✅ Extract Analysis Metrics
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

# ✅ Yahoo Finance Overview
def scrape_overview(symbol: str) -> dict:
    url = f"https://finance.yahoo.com/quote/{symbol}"
    html = get_html_with_requests(url)
    return extract_metrics_from_html(html, symbol)

# ✅ Yahoo Finance Analysis Tab
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

# ✅ Financials using yfinance
def scrape_financials(symbol: str) -> pd.DataFrame:
    try:
        fin = yf.Ticker(symbol).financials
        return fin
    except:
        return pd.DataFrame()

# ✅ Combine all screener info
def get_screener_data(symbol: str) -> tuple:
    overview = scrape_overview(symbol)
    analysis = scrape_analysis(symbol)
    financial_df = scrape_financials(symbol)
    return overview, analysis, financial_df

# ✅ Gemini Investment Advice Generator
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
