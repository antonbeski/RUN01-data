"""
RUN01 — api/index.py
Flask API wrapping finvizfinance. Deployed on Vercel as a serverless
function; all /api/* requests are rewritten to this file (see vercel.json).
"""

import pandas as pd
from flask import Flask, jsonify

from finvizfinance.quote import finvizfinance, Statements
from finvizfinance.screener.overview import Overview
from finvizfinance.news import News
from finvizfinance.insider import Insider
from finvizfinance.calendar import Calendar
from finvizfinance.group.overview import Overview as GroupOverview
from finvizfinance.forex import Forex
from finvizfinance.crypto import Crypto

app = Flask(__name__)


def df_to_records(df):
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return []
    return df.fillna("").astype(str).to_dict(orient="records")


def safe(func, *args, **kwargs):
    try:
        return func(*args, **kwargs), None
    except Exception as e:
        return None, str(e)


def fetch_fundamentals_robust(stock):
    try:
        return stock.ticker_fundament()
    except Exception:
        pass
    try:
        soup = stock.soup
        if soup is None:
            return None
        marker_labels = {"P/E", "Market Cap", "EPS (ttm)", "Shs Outstand"}
        table = next(
            (t for t in soup.find_all("table")
             if marker_labels & {td.get_text(strip=True) for td in t.find_all("td")}),
            None,
        )
        if table is None:
            return None
        info = {}
        company_tag = soup.find("h2", class_="quote-header_ticker-wrapper_company")
        if company_tag:
            info["Company"] = company_tag.text.strip()
        links_container = soup.find("div", class_="quote-links")
        if links_container:
            links = links_container.find_all("a")
            for key, idx in [("Sector", 0), ("Industry", 1), ("Country", 2), ("Exchange", 3)]:
                if len(links) > idx:
                    info[key] = links[idx].text.strip()
        for row in table.find_all("tr"):
            cols = [td.get_text(strip=True) for td in row.find_all("td")]
            for i in range(0, len(cols) - 1, 2):
                if cols[i]:
                    info[cols[i]] = cols[i + 1]
        return info if len(info) > len(marker_labels) else None
    except Exception:
        return None


@app.route("/api/ticker/<ticker>")
def api_ticker(ticker):
    ticker = ticker.upper()
    result = {"ticker": ticker, "sections": {}, "errors": []}

    stock, err = safe(finvizfinance, ticker)
    if err:
        result["errors"].append(err)
    if stock is None or not getattr(stock, "flag", True):
        result["errors"].append(f"Ticker '{ticker}' not found on finviz.")
        return jsonify(result), 404

    val, err = safe(fetch_fundamentals_robust, stock)
    result["sections"]["fundamentals"] = val or {}
    if err: result["errors"].append(err)

    val, err = safe(stock.ticker_description)
    result["sections"]["description"] = (val or "").strip()
    if err: result["errors"].append(err)

    val, err = safe(stock.ticker_peer)
    result["sections"]["peers"] = val or []
    if err: result["errors"].append(err)

    val, err = safe(stock.ticker_etf_holders)
    result["sections"]["etf_holders"] = val or []
    if err: result["errors"].append(err)

    val, err = safe(stock.ticker_outer_ratings)
    result["sections"]["ratings"] = df_to_records(val)
    if err: result["errors"].append(err)

    val, err = safe(stock.ticker_inside_trader)
    result["sections"]["insider"] = df_to_records(val)
    if err: result["errors"].append(err)

    val, err = safe(stock.ticker_news)
    result["sections"]["news"] = df_to_records(val)
    if err: result["errors"].append(err)

    val, err = safe(stock.ticker_charts, "daily", "advanced", "", True)
    result["sections"]["chart_url"] = val or ""
    if err: result["errors"].append(err)

    statements = {}
    for code, name in [("I", "income"), ("B", "balance"), ("C", "cashflow")]:
        val, err = safe(Statements().get_statements, ticker, code, "A")
        statements[name] = df_to_records(val)
        if err: result["errors"].append(err)
    result["sections"]["statements"] = statements

    return jsonify(result)


@app.route("/api/market/<ticker>")
def api_market(ticker):
    ticker = ticker.upper()
    result = {"sections": {}, "errors": []}

    val, err = safe(Overview().compare, ticker, ["Sector", "Industry"])
    result["sections"]["sector_peers"] = df_to_records(val)
    if err: result["errors"].append(err)

    val, err = safe(GroupOverview().screener_view, "Sector")
    result["sections"]["sector_performance"] = df_to_records(val)
    if err: result["errors"].append(err)

    val, err = safe(lambda: News().get_news())
    result["sections"]["market_news"] = (
        {k: df_to_records(df) for k, df in val.items()} if isinstance(val, dict) else {}
    )
    if err: result["errors"].append(err)

    val, err = safe(lambda: Calendar().calendar())
    result["sections"]["calendar"] = df_to_records(val)
    if err: result["errors"].append(err)

    val, err = safe(lambda: Insider(option="latest").get_insider())
    result["sections"]["insider_market"] = df_to_records(val)
    if err: result["errors"].append(err)

    val, err = safe(lambda: Forex().performance())
    result["sections"]["forex"] = df_to_records(val)
    if err: result["errors"].append(err)

    val, err = safe(lambda: Crypto().performance())
    result["sections"]["crypto"] = df_to_records(val)
    if err: result["errors"].append(err)

    return jsonify(result)
