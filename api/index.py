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

PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>RUN01</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap" rel="stylesheet" />
<style>
  :root{
    --bg:#0a0a0a;
    --fg:#e8e8e8;
    --dim:#8a8a8a;
    --line:#3a3a3a;
    --hi:#ffffff;
  }
  *{box-sizing:border-box;}
  html,body{
    margin:0; padding:0;
    background:var(--bg);
    color:var(--fg);
    font-family:"SF Mono","SFMono-Regular","JetBrains Mono","IBM Plex Mono","Courier New",monospace;
    font-weight:400;
    font-size:13px;
    line-height:1.5;
  }
  body{ padding:24px 18px 60px; }
  ::selection{ background:var(--fg); color:var(--bg); }

  a{ color:var(--fg); text-decoration:underline; }
  a:hover{ color:var(--hi); }

  .ascii-title{
    white-space:pre;
    font-family:"Roboto Mono",monospace;
    font-size:11px;
    line-height:1.15;
    color:var(--fg);
    margin-bottom:6px;
    overflow-x:auto;
  }
  .subtitle{ color:var(--dim); margin-bottom:20px; }

  .prompt-row{
    display:flex; align-items:center; gap:8px;
    border:1px solid var(--line);
    padding:10px 12px;
    margin-bottom:8px;
    flex-wrap:wrap;
  }
  .prompt-label{ color:var(--dim); white-space:nowrap; }
  input[type=text]{
    background:transparent;
    border:none;
    outline:none;
    color:var(--hi);
    font-family:inherit;
    font-size:13px;
    flex:1;
    min-width:120px;
    caret-color:var(--hi);
  }
  .cursor{
    display:inline-block; width:8px; height:15px;
    background:var(--hi);
    animation:blink 1s steps(1) infinite;
    vertical-align:-3px;
  }
  @keyframes blink{ 50%{ opacity:0; } }

  .btn{
    background:transparent;
    border:1px solid var(--fg);
    color:var(--fg);
    font-family:inherit;
    font-size:12px;
    padding:6px 14px;
    cursor:pointer;
    text-transform:uppercase;
    letter-spacing:0.05em;
  }
  .btn:hover{ background:var(--fg); color:var(--bg); }
  .btn:disabled{ opacity:0.35; cursor:default; background:transparent; color:var(--fg); }

  .toggle-row{
    display:flex; align-items:center; gap:8px;
    color:var(--dim); font-size:12px;
  }
  .toggle-row input{ accent-color:var(--fg); }

  .controls{
    display:flex; align-items:center; gap:16px; flex-wrap:wrap;
    margin-bottom:20px;
  }

  .status{
    color:var(--dim);
    margin:10px 0 20px;
    min-height:18px;
    white-space:pre-wrap;
  }
  .status.error{ color:var(--hi); }

  .section{
    border:1px solid var(--line);
    margin-bottom:18px;
  }
  .section-head{
    display:flex; justify-content:space-between; align-items:center;
    padding:8px 12px;
    border-bottom:1px solid var(--line);
    cursor:pointer;
    user-select:none;
  }
  .section-head:hover{ background:#111; }
  .section-head .num{ color:var(--dim); margin-right:8px; }
  .section-head .chev{ color:var(--dim); }
  .section-body{ padding:14px 16px; overflow-x:auto; }
  .section-body.collapsed{ display:none; }

  .kv-grid{
    display:grid;
    grid-template-columns:repeat(auto-fill,minmax(260px,1fr));
    gap:4px 20px;
  }
  .kv-item{
    display:flex; justify-content:space-between; gap:10px;
    border-bottom:1px dashed var(--line);
    padding:3px 0;
  }
  .kv-key{ color:var(--dim); }
  .kv-val{ color:var(--hi); text-align:right; }

  .desc-text{ color:var(--fg); max-width:900px; }

  table{ border-collapse:collapse; width:100%; font-size:12px; }
  th,td{
    border:1px solid var(--line);
    padding:5px 9px;
    text-align:left;
    white-space:nowrap;
  }
  th{ color:var(--hi); background:#111; text-transform:uppercase; font-size:11px; letter-spacing:0.03em; }
  tr:hover td{ background:#111; }

  .empty{ color:var(--dim); font-style:italic; }

  .chip-row{ display:flex; flex-wrap:wrap; gap:6px; }
  .chip{
    border:1px solid var(--line);
    padding:2px 8px;
    color:var(--fg);
    font-size:12px;
  }

  .divider{ border:none; border-top:1px solid var(--line); margin:26px 0; }

  footer{ color:var(--dim); margin-top:30px; font-size:11px; }

  ::-webkit-scrollbar{ height:8px; width:8px; }
  ::-webkit-scrollbar-track{ background:var(--bg); }
  ::-webkit-scrollbar-thumb{ background:var(--line); }
</style>
</head>
<body>

<div class="ascii-title">╦═╗╦ ╦╔╗╔╔═╗╦
╠╦╝║ ║║║║║ ║║
╩╚═╚═╝╝╚╝╚═╝╩╩</div>
<div class="subtitle">RUN01 — full stock data terminal, powered by finvizfinance</div>

<div class="prompt-row">
  <span class="prompt-label">user@run01:~$ fetch</span>
  <input type="text" id="tickerInput" value="AAPL" autocomplete="off" spellcheck="false" />
  <span class="cursor"></span>
  <button class="btn" id="runBtn">Run</button>
</div>

<div class="controls">
  <label class="toggle-row">
    <input type="checkbox" id="marketToggle" />
    include market-wide extras (sector perf, news, calendar, insider, forex, crypto — slower)
  </label>
</div>

<div class="status" id="status">idle. enter a ticker and hit run.</div>

<div id="output"></div>

<footer>RUN01 &nbsp;|&nbsp; backend: flask + finvizfinance &nbsp;|&nbsp; data source: finviz.com</footer>

<script>
const API_BASE = "";
const statusEl = document.getElementById("status");
const outputEl = document.getElementById("output");
const runBtn = document.getElementById("runBtn");
const tickerInput = document.getElementById("tickerInput");
const marketToggle = document.getElementById("marketToggle");

function setStatus(text, isError=false){
  statusEl.textContent = text;
  statusEl.classList.toggle("error", isError);
}

function el(tag, attrs={}, children=[]){
  const e = document.createElement(tag);
  for(const k in attrs){
    if(k === "class") e.className = attrs[k];
    else if(k === "text") e.textContent = attrs[k];
    else if(k === "html") e.innerHTML = attrs[k];
    else e.setAttribute(k, attrs[k]);
  }
  (Array.isArray(children) ? children : [children]).forEach(c => c && e.appendChild(c));
  return e;
}

function sectionShell(num, title){
  const body = el("div", {class:"section-body"});
  const head = el("div", {class:"section-head"}, [
    el("span", {}, [
      el("span", {class:"num", text: num + "."}),
      el("span", {text: title})
    ]),
    el("span", {class:"chev", text:"[-]"})
  ]);
  head.addEventListener("click", () => {
    body.classList.toggle("collapsed");
    head.querySelector(".chev").textContent = body.classList.contains("collapsed") ? "[+]" : "[-]";
  });
  const section = el("div", {class:"section"}, [head, body]);
  return {section, body};
}

function emptyNote(msg="no data returned"){
  return el("div", {class:"empty", text: msg});
}

function renderKV(container, dict){
  if(!dict || Object.keys(dict).length === 0){ container.appendChild(emptyNote()); return; }
  const grid = el("div", {class:"kv-grid"});
  Object.entries(dict).forEach(([k,v]) => {
    grid.appendChild(el("div", {class:"kv-item"}, [
      el("span", {class:"kv-key", text:k}),
      el("span", {class:"kv-val", text: (v===null||v===undefined||v==="") ? "—" : String(v)})
    ]));
  });
  container.appendChild(grid);
}

function renderList(container, list){
  if(!list || list.length === 0){ container.appendChild(emptyNote()); return; }
  const row = el("div", {class:"chip-row"});
  list.forEach(item => row.appendChild(el("span", {class:"chip", text:item})));
  container.appendChild(row);
}

function renderTable(container, records, maxRows=null){
  if(!records || records.length === 0){ container.appendChild(emptyNote()); return; }
  const rows = maxRows ? records.slice(0, maxRows) : records;
  const cols = Object.keys(rows[0]);
  const table = el("table");
  const thead = el("thead", {}, [el("tr", {}, cols.map(c => el("th", {text:c})))]);
  const tbody = el("tbody", {}, rows.map(r => el("tr", {}, cols.map(c => el("td", {text: r[c] ?? ""})))));
  table.appendChild(thead);
  table.appendChild(tbody);
  container.appendChild(table);
  if(maxRows && records.length > maxRows){
    container.appendChild(el("div", {class:"empty", text:`… ${records.length - maxRows} more rows not shown`}));
  }
}

function renderText(container, text){
  if(!text){ container.appendChild(emptyNote()); return; }
  container.appendChild(el("div", {class:"desc-text", text}));
}

function renderErrors(errors){
  if(!errors || errors.length === 0) return null;
  const box = el("div", {class:"section"});
  const head = el("div", {class:"section-head"}, el("span", {text:"⚠ fetch warnings"}));
  const body = el("div", {class:"section-body"});
  errors.forEach(e => body.appendChild(el("div", {class:"empty", text:"• " + e})));
  box.appendChild(head); box.appendChild(body);
  return box;
}

async function runFetch(){
  const ticker = tickerInput.value.trim().toUpperCase();
  if(!ticker){ setStatus("enter a ticker symbol first.", true); return; }
  const includeMarket = marketToggle.checked;

  runBtn.disabled = true;
  outputEl.innerHTML = "";
  setStatus(`▓▓▓ fetching ${ticker} from finviz... ▓▓▓`);

  try{
    const res = await fetch(`${API_BASE}/api/ticker/${ticker}`);
    const data = await res.json();

    if(!res.ok){
      setStatus(`error: ${(data.errors || ["ticker not found"]).join(" | ")}`, true);
      runBtn.disabled = false;
      return;
    }

    const s = data.sections;

    let n = 1;
    let sec;

    sec = sectionShell(n++, "FUNDAMENTALS / OVERVIEW SNAPSHOT");
    renderKV(sec.body, s.fundamentals);
    outputEl.appendChild(sec.section);

    sec = sectionShell(n++, "BUSINESS DESCRIPTION");
    renderText(sec.body, s.description);
    outputEl.appendChild(sec.section);

    sec = sectionShell(n++, "PEER TICKERS");
    renderList(sec.body, s.peers);
    outputEl.appendChild(sec.section);

    sec = sectionShell(n++, "HELD BY ETFs");
    renderList(sec.body, s.etf_holders);
    outputEl.appendChild(sec.section);

    sec = sectionShell(n++, "ANALYST RATINGS / PRICE TARGETS");
    renderTable(sec.body, s.ratings, 20);
    outputEl.appendChild(sec.section);

    sec = sectionShell(n++, "INSIDER TRADING (THIS TICKER)");
    renderTable(sec.body, s.insider, 20);
    outputEl.appendChild(sec.section);

    sec = sectionShell(n++, "LATEST NEWS & PRESS RELEASES");
    renderTable(sec.body, s.news, 15);
    outputEl.appendChild(sec.section);

    sec = sectionShell(n++, "TECHNICAL CHART");
    if(s.chart_url){
      sec.body.appendChild(el("a", {href:s.chart_url, target:"_blank", text:s.chart_url}));
    } else {
      sec.body.appendChild(emptyNote("unavailable"));
    }
    outputEl.appendChild(sec.section);

    sec = sectionShell(n++, "FINANCIAL STATEMENTS — INCOME (ANNUAL)");
    renderTable(sec.body, s.statements?.income, 12);
    outputEl.appendChild(sec.section);

    sec = sectionShell(n++, "FINANCIAL STATEMENTS — BALANCE SHEET (ANNUAL)");
    renderTable(sec.body, s.statements?.balance, 12);
    outputEl.appendChild(sec.section);

    sec = sectionShell(n++, "FINANCIAL STATEMENTS — CASH FLOW (ANNUAL)");
    renderTable(sec.body, s.statements?.cashflow, 12);
    outputEl.appendChild(sec.section);

    const errBox = renderErrors(data.errors);
    if(errBox) outputEl.appendChild(errBox);

    if(includeMarket){
      setStatus(`▓▓▓ ${ticker} loaded. fetching market-wide extras... ▓▓▓`);
      outputEl.appendChild(el("hr", {class:"divider"}));
      outputEl.appendChild(el("div", {class:"ascii-title", text:"MARKET-WIDE EXTRAS", style:""}));

      const mres = await fetch(`${API_BASE}/api/market/${ticker}`);
      const mdata = await mres.json();
      const ms = mdata.sections;

      sec = sectionShell(n++, "SCREENER — PEERS IN SAME SECTOR/INDUSTRY");
      renderTable(sec.body, ms.sector_peers, 20);
      outputEl.appendChild(sec.section);

      sec = sectionShell(n++, "SECTOR PERFORMANCE (ALL SECTORS)");
      renderTable(sec.body, ms.sector_performance);
      outputEl.appendChild(sec.section);

      sec = sectionShell(n++, "GENERAL MARKET NEWS");
      if(ms.market_news && Object.keys(ms.market_news).length){
        Object.entries(ms.market_news).forEach(([k, records]) => {
          sec.body.appendChild(el("div", {class:"kv-key", text: k.toUpperCase(), style:"margin:10px 0 6px;"}));
          renderTable(sec.body, records, 10);
        });
      } else {
        sec.body.appendChild(emptyNote());
      }
      outputEl.appendChild(sec.section);

      sec = sectionShell(n++, "ECONOMIC CALENDAR");
      renderTable(sec.body, ms.calendar, 20);
      outputEl.appendChild(sec.section);

      sec = sectionShell(n++, "INSIDER TRADING (MARKET-WIDE, LATEST)");
      renderTable(sec.body, ms.insider_market, 20);
      outputEl.appendChild(sec.section);

      sec = sectionShell(n++, "FOREX PERFORMANCE");
      renderTable(sec.body, ms.forex);
      outputEl.appendChild(sec.section);

      sec = sectionShell(n++, "CRYPTO PERFORMANCE");
      renderTable(sec.body, ms.crypto, 20);
      outputEl.appendChild(sec.section);

      const merrBox = renderErrors(mdata.errors);
      if(merrBox) outputEl.appendChild(merrBox);
    }

    setStatus(`done. ${ticker} report generated at ${new Date().toLocaleTimeString()}.`);
  } catch(e){
    setStatus("fatal error: " + e.message, true);
  } finally {
    runBtn.disabled = false;
  }
}

runBtn.addEventListener("click", runFetch);
tickerInput.addEventListener("keydown", (e) => { if(e.key === "Enter") runFetch(); });
</script>
</body>
</html>
"""


@app.route("/")
def home():
    return PAGE_HTML


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
