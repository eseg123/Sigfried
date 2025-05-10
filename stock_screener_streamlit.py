import streamlit as st
import requests

# Your API key from Streamlit Secrets
API_KEY = st.secrets["FMP_API_KEY"]
BASE_URL = "https://financialmodelingprep.com/api/v3"
tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]

def safe_get(data, key):
    val = data.get(key)
    return val if isinstance(val, (int, float)) else 0

def get_financials(ticker):
    def fetch(endpoint):
        url = f"{BASE_URL}/{endpoint}/{ticker}?apikey={API_KEY}&limit=1"
        r = requests.get(url)
        return r.json()[0] if r.ok and r.json() else {}

    income = fetch("income-statement")
    balance = fetch("balance-sheet-statement")
    profile = fetch("profile")

    ebit = safe_get(income, "ebit")
    ca = safe_get(balance, "totalCurrentAssets")
    ppe = safe_get(balance, "propertyPlantEquipmentNet")
    leases = safe_get(balance, "capitalLeaseObligations")
    lti = safe_get(balance, "longTermInvestments")
    cl = safe_get(balance, "totalCurrentLiabilities")
    cash = safe_get(balance, "cashAndCashEquivalents")
    ltd = safe_get(balance, "longTermDebt")
    ps = safe_get(balance, "preferredStock")
    shares = safe_get(profile, "sharesOutstanding")
    price = safe_get(profile, "price")

    invested_cap = ca + ppe + leases + lti - cl - cash
    net_worth = invested_cap + cash - ltd - leases - ps
    market_cap = shares * price

    fm = market_cap / net_worth if net_worth else None
    roic = ebit / invested_cap if invested_cap else None

    return {
        "Ticker": ticker,
        "Faustmann Ratio": round(fm, 2) if fm is not None else "N/A",
        "ROIC": round(roic, 2) if roic is not None else "N/A",
        "Pass": (fm is not None and roic is not None and fm <= 1 and roic >= 0.2)
    }

# Streamlit Interface
st.title("📈 Stock Screener: Faustmann & ROIC")
st.markdown("Filters stocks based on **Faustmann Ratio ≤ 1** and **ROIC ≥ 0.2**")

results = [get_financials(t) for t in tickers]
for r in results:
    st.markdown(f"**{r['Ticker']}** — Faustmann: `{r['Faustmann Ratio']}`, ROIC: `{r['ROIC']}`")
    st.markdown(f"✅ Passes Criteria: {'Yes' if r['Pass'] else 'No'}")
    st.markdown("---")
