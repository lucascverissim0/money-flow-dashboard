import sys
import os
from pathlib import Path

# Ensure the repo root is in the Python path
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

import pandas as pd
import yfinance as yf

import config  # uses the config.py at repo root


def get_all_tickers_from_universe(universe: dict) -> list:
    """Flatten UNIVERSE dict into a simple list of tickers."""
    tickers = []
    for group in universe.values():
        for ticker in group.keys():
            tickers.append(ticker)
    return tickers


def download_universe_prices(tickers, start_date, end_date=None) -> pd.DataFrame:
    """
    Download OHLCV data for all tickers using yfinance and return a tidy DataFrame.

    Columns: date, ticker, open, high, low, close, adj_close, volume
    """
    print(f"Downloading price data for: {tickers}")

    data = yf.download(
        tickers=tickers,
        start=start_date,
        end=end_date,
        auto_adjust=False,
        progress=True,
        group_by="ticker",
    )

    # yfinance returns a multi-index column structure when multiple tickers
    records = []
    for ticker in tickers:
        if ticker not in data.columns.levels[0]:
            print(f"WARNING: No data returned for ticker {ticker}")
            continue

        df_t = data[ticker].copy()
        df_t["ticker"] = ticker
        df_t = df_t.reset_index()  # date becomes a column
        df_t.columns = [c.lower().replace(" ", "_") for c in df_t.columns]
        # Standardize names
        df_t = df_t.rename(columns={"adj_close": "adj_close"})
        records.append(df_t)

    if not records:
        print("ERROR: No data downloaded for any ticker.")
        sys.exit(1)

    prices = pd.concat(records, ignore_index=True)
    prices = prices.rename(columns={"index": "date"}) if "index" in prices.columns else prices
    prices = prices.sort_values(["ticker", "date"])

    return prices


def download_vix(start_date, end_date=None) -> pd.DataFrame:
    """
    Download VIX index from yfinance (^VIX) and return tidy DataFrame.

    Columns: date, ticker, open, high, low, close, adj_close, volume
    """
    print("Downloading VIX (^VIX)...")

    vix = yf.download(
        "^VIX",
        start=start_date,
        end=end_date,
        auto_adjust=False,
        progress=True,
    )

    if vix.empty:
        print("WARNING: No VIX data downloaded.")
        return pd.DataFrame()

    vix = vix.reset_index()
    vix.columns = [c.lower().replace(" ", "_") for c in vix.columns]
    vix["ticker"] = "^VIX"
    vix = vix.sort_values("date")

    return vix


def main():
    # Ensure data/raw exists
    raw_dir = config.DATA_DIR / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    # 1) Get tickers from UNIVERSE in config.py
    tickers = get_all_tickers_from_universe(config.UNIVERSE)

    # 2) Download universe prices
    prices = download_universe_prices(
        tickers=tickers,
        start_date=config.START_DATE,
        end_date=config.END_DATE,
    )

    prices_path = raw_dir / "prices.parquet"
    prices.to_parquet(prices_path)
    print(f"Saved prices to {prices_path}")

    # 3) Download VIX
    vix = download_vix(
        start_date=config.START_DATE,
        end_date=config.END_DATE,
    )

    if not vix.empty:
        vix_path = raw_dir / "vix.parquet"
        vix.to_parquet(vix_path)
        print(f"Saved VIX to {vix_path}")
    else:
        print("No VIX file written (empty data).")

    print("Pipeline step 1 (data download) completed.")


if __name__ == "__main__":
    main()
