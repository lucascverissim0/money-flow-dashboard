import sys
from pathlib import Path

# Ensure repo root is on PATH
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import pandas as pd
import numpy as np
import config


def compute_flow_features(prices: pd.DataFrame, vix: pd.DataFrame) -> pd.DataFrame:
    """
    Build notional-traded flow features and merge VIX.
    """

    # ---- 1) Ensure datetime sorted
    prices["date"] = pd.to_datetime(prices["date"])
    vix["date"] = pd.to_datetime(vix["date"])

    prices = prices.sort_values(["ticker", "date"])
    vix = vix.sort_values("date")

    # ---- 2) Compute notional traded proxy
    prices["notional_traded"] = prices["close"] * prices["volume"]

    # ---- 3) Lagged notional and delta
    prices["notional_lag"] = prices.groupby("ticker")["notional_traded"].shift(1)
    prices["d_notional"] = prices["notional_traded"] - prices["notional_lag"]

    # ---- 4) Daily universe sum of flows
    daily_total = (
        prices.groupby("date")["d_notional"]
        .sum()
        .rename("d_notional_universe")
        .reset_index()
    )

    prices = prices.merge(daily_total, on="date", how="left")

    # ---- 5) Flow share (% of universe flow)
    prices["flow_share"] = prices["d_notional"] / prices["d_notional_universe"]

    # ---- 6) Rolling z-score of flow per asset
    prices["flow_z"] = (
        prices.groupby("ticker")["d_notional"]
        .transform(lambda s: (s - s.rolling(60).mean()) / s.rolling(60).std())
    )

    # ---- 7) Add VIX
    prices = prices.merge(vix[["date", "close"]].rename(columns={"close": "vix"}), on="date", how="left")

    return prices


def main():
    raw_dir = config.DATA_DIR / "raw"
    processed_dir = config.DATA_DIR / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    # ---- Load input files
    prices = pd.read_parquet(raw_dir / "prices.parquet")
    vix = pd.read_parquet(raw_dir / "vix.parquet")

    # ---- Compute features
    print("Building flow features…")
    df = compute_flow_features(prices, vix)

    # ---- Save output
    out_path = processed_dir / "flows.parquet"
    df.to_parquet(out_path)

    print(f"DONE. Saved flow feature dataset to:\n  {out_path}")


if __name__ == "__main__":
    main()
