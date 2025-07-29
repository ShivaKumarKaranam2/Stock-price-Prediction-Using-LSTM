# # =======================
# # File: screener.py
# # =======================
# import requests
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager
# import google.generativeai as genai
# import json
# import pandas as pd
# import yfinance as yf
# from bs4 import BeautifulSoup
# import re
# from dotenv import load_dotenv
# import os

# load_dotenv()  # 🔄 Loads environment variables from .env file

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# # ✅ Gemini API Key
# genai.configure(api_key="GEMINI_API_KEY")

# # ✅ Get HTML using Selenium
# def get_rendered_html_selenium(url):
#     options = Options()
#     options.add_argument("--headless")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--no-sandbox")
#     driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
#     driver.get(url)
#     driver.implicitly_wait(5)
#     html = driver.page_source
#     driver.quit()
#     return html


# def extract_metrics_from_html(html, symbol):
#     prompt = f"""
# You are a financial data extractor. From the following Yahoo Finance HTML page for the stock symbol {symbol}, extract all the summary key-value metrics displayed to the user.

# Your response should be a valid JSON object like:
# {{
#   "Previous Close": "...",
#   "Open": "...",
#   "Bid": "...",
#   "Ask": "...",
#   "Day’s Range": "...",
#   "52 Week Range": "...",
#   "Volume": "...",
#   "Avg. Volume": "...",
#   "Market Cap": "...",
#   "PE Ratio (TTM)": "...",
#   "EPS (TTM)": "...",
#   "Earnings Date": "...",
#   "Dividend & Yield": "...",
#   "Ex-Dividend Date": "..."
# }}

# Only include real data if available. Don’t make up values. HTML content is below:
# ----
# {html[:18000]}
# """

#     model = genai.GenerativeModel("gemma-3n-e4b-it")
#     response = model.generate_content(prompt)
#     try:
#         # Extract first valid JSON block using regex
#         json_match = re.search(r"{.*?}", response.text, re.DOTALL)
#         if json_match:
#             json_text = json_match.group(0)
#             return json.loads(json_text)
#         else:
#             raise ValueError("No valid JSON found")
#     except Exception as e:
#         print("⚠️ Could not parse JSON:", e)
#         print(response.text)
#         return {}


# # ✅ Overview Data
# def scrape_overview(symbol: str) -> dict:
#     url = f"https://finance.yahoo.com/quote/{symbol}"
#     html = get_rendered_html_selenium(url)
#     return extract_metrics_from_html(html, symbol=symbol)



# def extract_analysis_from_html(html, symbol):
#     prompt = f"""
# You are a financial data extractor for stock analysis. From the HTML content of the Yahoo Finance **Analysis** page for the stock symbol `{symbol}`, extract a structured JSON object summarizing the key analysis metrics.

# Format your response like this:
# {{
#   "Revenue Estimate - Current Qtr": "...",
#   "Revenue Estimate - Next Qtr": "...",
#   "EPS Trend - Current Qtr": "...",
#   "EPS Trend - Current Year": "...",
#   ...
# }}

# Only extract what is actually visible and avoid guessing. Here's the HTML:
# ----
# {html[:18000]}
# """
#     model = genai.GenerativeModel("gemma-3n-e4b-it")
#     response = model.generate_content(prompt)

#     try:
#         json_match = re.search(r"{.*?}", response.text, re.DOTALL)
#         if json_match:
#             json_text = json_match.group(0)
#             return json.loads(json_text)
#         else:
#             raise ValueError("No valid JSON found in Gemini output")
#     except Exception as e:
#         print("⚠️ Could not parse Gemini Analysis JSON:", e)
#         print(response.text)
#         return {}
# def scrape_analysis(symbol: str) -> dict:
#     url = f"https://finance.yahoo.com/quote/{symbol}/analysis"
#     html = get_rendered_html_selenium(url)
#     soup = BeautifulSoup(html, "html.parser")

#     # Collect clean visible text from analysis tables
#     all_tables_text = ""
#     for table in soup.find_all("table"):
#         for row in table.find_all("tr"):
#             cells = row.find_all(["th", "td"])
#             row_text = " | ".join(cell.text.strip() for cell in cells)
#             all_tables_text += row_text + "\n"

#     if not all_tables_text.strip():
#         print("⚠️ No visible text found in analysis tables.")
#         return {}

#     return extract_analysis_from_html(all_tables_text, symbol)



# def scrape_financials(symbol: str) -> pd.DataFrame:
#     try:
#         fin = yf.Ticker(symbol).financials
#         return fin
#     except:
#         return pd.DataFrame()


# def get_screener_data(symbol: str) -> tuple:
#     overview = scrape_overview(symbol)
#     analysis = scrape_analysis(symbol)
#     financial_df = scrape_financials(symbol)
#     return overview, analysis, financial_df

# # ✅ Generate AI Investment Advice using Gemini
# def build_investment_decision_prompt(symbol: str, overview: dict, predicted_price: float) -> str:

#     # Configure Gemini (You can place this once at top of the file too)
#     genai.configure(api_key="GEMINI_API_KEY")  # 🔁 Replace with your actual key if not done above

#     # Build prompt
#     prompt = f"""
#                 You are a professional stock market advisor.

#                 Analyze this stock and provide investment advice in the following format:
#                 1. Investment Decision: Buy / Hold / Sell
#                 2. Reasoning based on company metrics
#                 3. Risk Factors
#                 4. Final Recommendation Summary (one paragraph)

#                 ### Stock Symbol: {symbol}
#                 ### Predicted Price (Next Trading Day): ₹{predicted_price:.2f}

#                 ### Yahoo Finance Key Metrics (overview):
#                 {json.dumps(overview, indent=2)}

#                 Be precise and explain based only on the data provided. Don’t fabricate missing metrics.
#                 """

#     # Call Gemini Pro model
#     model = genai.GenerativeModel("gemma-3n-e4b-it")
#     response = model.generate_content(prompt)
#     return response.text.strip()
# =======================
# File: screener.py
# =======================
# Let's prepare working code for Indian stock analysis using Screener.in instead of Alpha Vantage.
# =======================
# File: screener.py
# =======================
# screener.py

import yfinance as yf
import google.generativeai as genai
import json
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# ✅ Fetch basic stock info using yfinance
def scrape_overview(symbol: str) -> dict:
    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        # Extract selected fields
        data = {
            "Symbol": symbol,
            "Current Price": info.get("currentPrice"),
            "Previous Close": info.get("previousClose"),
            "Open": info.get("open"),
            "Day Low": info.get("dayLow"),
            "Day High": info.get("dayHigh"),
            "52 Week Low": info.get("fiftyTwoWeekLow"),
            "52 Week High": info.get("fiftyTwoWeekHigh"),
            "Volume": info.get("volume"),
            "Market Cap": info.get("marketCap"),
            "PE Ratio": info.get("trailingPE"),
            "EPS": info.get("trailingEps"),
            "Dividend Yield": info.get("dividendYield"),
            "Sector": info.get("sector"),
            "Industry": info.get("industry"),
            "Website": info.get("website")
        }
        return {k: v for k, v in data.items() if v is not None}
    except Exception as e:
        return {"error": f"Failed to fetch data from yfinance: {str(e)}"}
# ✅ Extract limited analyst data from yfinance
def scrape_analysis(symbol: str) -> dict:
    try:
        ticker = yf.Ticker(symbol)
        cal = ticker.calendar.to_dict() if hasattr(ticker.calendar, 'to_dict') else {}
        earn = ticker.earnings

        if not cal and earn.empty:
            return {}

        analysis = {}
        
        # Extract data from calendar
        for key, val in cal.items():
            if len(val) > 0:
                analysis[key] = str(val[0])

        # Extract recent earnings
        if not earn.empty:
            recent = earn.iloc[-1]
            analysis["Earnings Year"] = str(recent.name)
            analysis["Revenue (Millions)"] = f"{recent['Revenue'] / 1e6:.2f}M"
            analysis["Earnings (Millions)"] = f"{recent['Earnings'] / 1e6:.2f}M"

        return analysis
    except Exception as e:
        return {"error": f"Failed to fetch analyst data: {str(e)}"}

def get_screener_data(symbol: str):
    overview = scrape_overview(symbol)
    analysis = scrape_analysis(symbol)  
    financials = scrape_financials(symbol)
    return overview, analysis, financials


# ✅ Gemini AI Investment Recommendation
def build_investment_decision_prompt(symbol: str, overview: dict, predicted_price: float) -> str:
    prompt = f"""
You are a professional Indian stock advisor.

Stock Symbol: {symbol}
Predicted Next Day Price: ₹{predicted_price:.2f}

Company Snapshot:
{json.dumps(overview, indent=2)}

Based only on this information, give:
1. Investment Decision: Buy / Hold / Sell
2. Reasoning
3. Risks
4. Final Summary
"""
    model = genai.GenerativeModel("gemma-3n-e4b-it")
    response = model.generate_content(prompt)
    return response.text.strip()





