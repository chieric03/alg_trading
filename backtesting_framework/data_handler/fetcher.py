import yfinance as yf
import pandas as pd

def fetch_data(ticker: str, start_date: str, end_date: str, interval: str = '1d') -> pd.DataFrame:
    """
    Fetches historical market data using yfinance.

    Args:
        ticker (str): The ticker symbol to fetch (e.g., 'NQ=F', 'AAPL').
        start_date (str): The start date in 'YYYY-MM-DD' format.
        end_date (str): The end date in 'YYYY-MM-DD' format.
        interval (str): The data interval (e.g., '1m', '15m', '1h', '1d').

    Returns:
        pd.DataFrame: A pandas DataFrame containing the OHLCV data,
                      with columns potentially lowercased and multi-level headers flattened.
                      Returns an empty DataFrame if download fails.
    """
    try:
        print(f"Fetching {ticker} data from {start_date} to {end_date} ({interval})...")
        df = yf.download(ticker, start=start_date, end=end_date, interval=interval, progress=False)

        if df.empty:
            print(f"No data found for {ticker} in the specified range.")
            return df

        # Handle potential multi-level columns returned by yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            print("Flattened multi-level columns.")

        # Ensure standard column names (lowercase)
        df.columns = [col.lower() for col in df.columns]
        # Rename 'adj close' if it exists
        if 'adj close' in df.columns:
            df = df.rename(columns={'adj close': 'adj_close'})

        print(f"Successfully fetched {len(df)} rows of data.")
        return df

    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

if __name__ == '__main__':
    # Example usage:
    ticker_symbol = 'NQ=F'
    start = '2025-04-01'
    end = '2025-04-08'
    interval_period = '15m'

    data = fetch_data(ticker_symbol, start, end, interval_period)

    if not data.empty:
        print("\nFetched Data Sample:")
        print(data.head())
        print("\nData Info:")
        data.info()
    else:
        print("\nFailed to fetch data.")
