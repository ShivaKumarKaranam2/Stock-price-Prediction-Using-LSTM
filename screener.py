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
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import yfinance as yf
import google.generativeai as genai
import re
import os
from dotenv import load_dotenv
import wikipedia

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Attempt Screener.in overview
def scrape_overview(symbol: str) -> dict:
    company = symbol.split(".")[0].lower()
    url = f"https://www.screener.in/company/{company}/"
    r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
    if r.status_code != 200:
        return None
    soup = BeautifulSoup(r.text, "html.parser")
    blocks = soup.select(".company-ratios .row .col")
    if not blocks:
        return None
    data = {}
    for b in blocks:
        data[b.select_one(".sub").get_text(strip=True)] = b.select_one(".number").get_text(strip=True)
    return data

# Web fallback: title + summary from Wikipedia
def fallback_overview(symbol: str) -> dict:
    try:
        company = symbol.split(".")[0]
        page = wikipedia.page(company)
        return {
            "Title": page.title,
            "Summary": page.summary[:500] + "..."
        }
    except Exception:
        return {"error": "Overview not available via fallback"}

# Financials via yfinance
def scrape_financials(symbol: str) -> pd.DataFrame:
    try:
        return yf.Ticker(symbol).financials
    except:
        return pd.DataFrame()

# Unified fetcher
def get_screener_data(symbol: str):
    ov = scrape_overview(symbol)
    if ov is None:
        ov = fallback_overview(symbol)
    fin = scrape_financials(symbol)
    return ov, {}, fin

# Gemini advice
def build_investment_decision_prompt(symbol: str, overview: dict, predicted_price: float) -> str:
    prompt = f"""
You are a smart stock advisor for Indian stocks.

Stock: {symbol}
Next‑day forecast closing price: ₹{predicted_price:.2f}

Available key data:
{json.dumps(overview, indent=2)}

Based only on this data, answer:
1. Investment Decision (Buy / Hold / Sell)
2. Reasoning
3. Risks
4. Final recommendation summary
"""
    resp = genai.GenerativeModel("gemma-3n-e4b-it").generate_content(prompt)
    return resp.text.strip()




