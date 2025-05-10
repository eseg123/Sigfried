import streamlit as st
import requests

# Fetch S&P 500 tickers
def get_sp500_tickers():
    url = "https://financialmodelingprep.com/api/v3/sp500_constituent"
    response = requests.get(url)
    if response.status_code == 200:
        return [company['symbol'] for company in response.json()]
    else:
        st.error("Failed to fetch S&P 500 tickers.")
        return []

# Fetch financial data for a given ticker
def get_financial_data(ticker, api_key):
    url = f"https://financialmodelingprep.com/api/v3/ratios/{ticker}?apikey={api_key}&period=quarter"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            latest_data = data[0]  # Most recent quarter
            pb_ratio = latest_data.get('priceToBookRatio', None)
            roic = latest_data.get('returnOnInvestedCapital', None)
            return pb_ratio, roic
    return None, None

# Streamlit app
def main():
    st.title("S&P 500 Screener: P/B & ROIC")
    st.markdown("Screening S&P 500 stocks with P/B ratio between 0.5 and 2.0 and ROIC > 20%.")

    # Fetch tickers
    tickers = get_sp500_tickers()
    if not tickers:
        return

    # Fetch API key from Streamlit secrets
    api_key = st.secrets["FMP_API_KEY"]

    # Initialize results list
    results = []

    # Iterate through tickers and fetch financial data
    for ticker in tickers:
        pb_ratio, roic = get_financial_data(ticker, api_key)
        if pb_ratio and roic:
            if 0.5 <= pb_ratio <= 2.0 and roic > 20:
                results.append((ticker, pb_ratio, roic))

    # Display results
    if results:
        st.write(f"Found {len(results)} stocks matching criteria:")
        for ticker, pb_ratio, roic in results:
            st.write(f"**{ticker}** - P/B: {pb_ratio}, ROIC: {roic}%")
    else:
        st.write("No stocks found matching the criteria.")

if __name__ == "__main__":
    main()
