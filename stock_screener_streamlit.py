import streamlit as st
import requests

API_KEY = st.secrets["FMP_API_KEY"]
BASE_URL = "https://financialmodelingprep.com/api/v3"
tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]

def get_financials(ticker):
    def get(endpoint):
        url = f"{BASE_URL}/{endpoint}/{ticker}?apikey={API_KEY}&limit=1"
        r = requests.get(url)
        return r.json()[0] if r.ok else {}

    income = get("income-statement")
    balance = get("balance-sheet-statement")
    profile = get("profile")

    ebit = income.get("ebit", 0)
    ca = balance.get("totalCurrentAssets", 0)
    ppe = balance.get("propertyPlantEquipmentNet", 0)
    leases = balance.get("capitalLeaseObligations", 0)
    lti = balance.get("longTermInvestments", 0)
    cl = balance.get("totalCurrentLiabilities", 0)
    cash = balance.get("cashAndCashEquivalents", 0)
    ltd = balance.get("longTermDebt", 0)
    ps = balance.get("preferredStock", 0)
    shares = profile.get("sharesOutstanding", 1)
    price = profile.get("price", 0)

    invested_cap = ca + ppe + leases + lti - cl - cash
    net_worth = invested_cap + cash - ltd - leases - ps
    market_cap = shares * price

    fm = market_cap / net_worth if net_worth else None
    roic = ebit / invested_cap if invested_cap else None

    return {
        "Ticker": ticker,
        "Faustmann Ratio": round(fm, 2) if fm else "N/A",
        "ROIC": round(roic, 2) if roic else "N/A",
        "Pass": fm and roic and fm <= 1 and roic >= 0.2
    }

st.title("📈 Stock Screener: Faustmann & ROIC")

results = [get_financials(t) for t in tickers]
for r in results:
    st.write(f"**{r['Ticker']}** — Faustmann: {r['Faustmann Ratio']}, ROIC: {r['ROIC']}, ✅ Pass: {r['Pass']}")
