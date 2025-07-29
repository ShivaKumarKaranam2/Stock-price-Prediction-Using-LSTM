

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

def scrape_analysis(symbol: str) -> dict:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # Analyst-like metrics derived from info
        analysis = {
            "Revenue Estimate - Current Qtr": info.get("revenueEstimate"),
            "Revenue Estimate - Next Qtr": info.get("revenueEstimateNextQuarter"),
            "EPS Trend - Current Qtr": info.get("epsCurrentQuarter"),
            "EPS Trend - Current Year": info.get("epsForward"),
            "Year Ago EPS": info.get("epsTrailingTwelveMonths"),
            "Sales Growth (year/est)": f"{info.get('revenueGrowth', 0) * 100:.2f}%" if info.get("revenueGrowth") else None,
            "Current Estimate": info.get("earningsEstimate"),
            "Up Last 7 Days": info.get("earningsEstimateUpLast7Days"),
            "Up Last 30 Days": info.get("earningsEstimateUpLast30Days"),
            "Current Qtr": f"{info.get('earningsQuarterGrowth', 0) * 100:.2f}%" if info.get("earningsQuarterGrowth") else None,
            "Next Qtr": f"{info.get('earningsNextQuarterGrowth', 0) * 100:.2f}%" if info.get("earningsNextQuarterGrowth") else None,
            "Current Year": f"{info.get('earningsGrowth', 0) * 100:.2f}%" if info.get("earningsGrowth") else None,
            "Next Year": f"{info.get('earningsNextYearGrowth', 0) * 100:.2f}%" if info.get("earningsNextYearGrowth") else None
        }

        # Clean: remove None or missing values
        analysis = {k: v for k, v in analysis.items() if v is not None}

        return analysis

    except Exception as e:
        return {"error": f"Failed to fetch analyst data: {str(e)}"}


def scrape_financials(symbol: str) -> pd.DataFrame:
    try:
        return yf.Ticker(symbol).financials
    except:
        return pd.DataFrame()

# ✅ Final API to use in app
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





