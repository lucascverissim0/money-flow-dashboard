from pathlib import Path

# Base data directory (all scripts will write/read here)
DATA_DIR = Path("data")

# Asset universe: start small, we can expand later
UNIVERSE = {
    "indices": {
        "SPY": {
            "type": "etf_equity",
            "description": "S&P 500 ETF",
        },
        "QQQ": {
            "type": "etf_equity",
            "description": "Nasdaq 100 ETF",
        },
        "IWM": {
            "type": "etf_equity",
            "description": "Russell 2000 ETF",
        },
    },
    "metals": {
        "XAUUSD": {
            "type": "spot_fx",
            "description": "Gold vs USD",
        },
        "XAGUSD": {
            "type": "spot_fx",
            "description": "Silver vs USD",
        },
    },
    "crypto": {
        "BTC-USD": {
            "type": "crypto",
            "description": "Bitcoin vs USD",
        },
        "ETH-USD": {
            "type": "crypto",
            "description": "Ethereum vs USD",
        },
    },
}

# Date range for all data downloads
START_DATE = "2005-01-01"   # or later if you prefer
END_DATE = None             # None = up to latest available
