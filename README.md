# Cross-Asset Money Flow Dashboard & Model

This repository tracks **where capital is flowing across major indexes and assets** (equities, metals, crypto, etc.) and builds **predictive models** on top of those flows.

The idea is simple:

- If **SPY is bleeding capital**, where is that money (or volume) going instead — **gold (XAU)? silver (XAG)? BTC? other equity indices?**
- Can we use **cross-asset flows + volatility metrics (VIX, etc.)** to estimate the **probability that prices go up or down** over the next X days?

The project is built around a **single data pipeline script** and separate scripts for visualization and modeling.

---

## Goals

### 1. Visualize cross-asset flows

- Track **money/volume flow** into and out of:
  - Major equity index ETFs (e.g., SPY, QQQ, IWM, …)
  - Precious metals (XAU, XAG, …)
  - Crypto (BTC, ETH, …)
- Approximate "where money is going" using:
  - Changes in **market cap** (when possible)
  - Changes in **notional traded** (price × volume) as a proxy
- Build clear visualizations such as:
  - “SPY lost \$X (proxy) this month — which assets gained?”
  - “Top daily inflow and outflow assets in the universe”

### 2. Predict price direction using flows

- Use money/volume flow features to model:
  - Probability that an asset’s price is **higher/lower in N days**
- Incorporate additional signals:
  - **VIX** (and later other volatility / risk indicators)
  - Rolling returns, volatility, correlations, etc.
- Train and evaluate models (initially simple; can evolve to more complex ML).

---

## Approach

You can’t literally see “\$800M left SPY and went into BTC” from public data.

Instead, this repo builds **systematic proxies**:

- **Market cap change**  
  `market_cap ≈ close_price × shares_outstanding` (where available)  
  `Δ market_cap` ≈ net capital flow proxy
- **Notional traded**  
  `notional_traded = close_price × volume`  
  `Δ notional_traded` and its share of universe flows
- **Relative flows**  
  For each day, compute the **share of total universe flow** captured by each asset.
- **Volatility context**  
  Add VIX and other metrics to see flows in risk-on vs risk-off regimes.

These features feed into:

- Visual dashboards (money flow maps, rankings)
- Prediction models (e.g. future 5d / 20d returns)

---

## Repository Structure

Planned structure:

```text
.
├─ README.md
├─ requirements.txt
├─ data/
│  ├─ raw/         # Raw downloads from APIs (e.g. yfinance)
│  ├─ interim/     # Intermediate processed files
│  └─ processed/   # Final, modeling-ready datasets
├─ notebooks/
│  ├─ 01_exploratory_flows.ipynb
│  └─ 02_model_sandbox.ipynb
├─ scripts/
│  ├─ run_pipeline.py        # SINGLE end-to-end data pipeline
│  ├─ visualize_flows.py     # CLI/plots to explore money flows
│  ├─ train_model.py         # Train prediction models
│  └─ score_model.py         # Apply models to latest data
└─ moneyflow/
   ├─ __init__.py
   ├─ config.py              # Universe, paths, common settings
   ├─ data_sources.py        # Download data (prices, VIX, etc.)
   ├─ features.py            # Flow calculations & features
   ├─ labeling.py            # Future-return labels for modeling
   └─ viz.py                 # Plotting utilities
