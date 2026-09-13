# -*- coding: utf-8 -*-
"""DIAGNOSTIC of the P3-11 estimator, not a trial. Run after run_pead_sharadar.py.

Question: is the −4 pt "reversal" in market-model CAR[+2,+60] by SUE decile a property of the
returns or of the estimator? The market model fits an intercept on [−250,−31]; firms sorted on
earnings changes have systematically different prior-year drift, so the intercept differs by
decile and 58 days of it is several points. Shows (a) the estimation-window alpha by decile,
(b) the same CARs with market-ADJUSTED returns (r − SPY, no estimation window).
Writes Data/results/pead_diag_alpha_by_decile.csv and pead_diag_market_adjusted.csv.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from eventstudies import firm  # noqa: E402
import run_pead_sharadar as R  # noqa: E402


def main():
    P2 = R.P2
    fund = pd.read_csv(os.path.join(P2, "reporting", "sharadar_cache", "us_fundamentals.csv"), usecols=["ticker", "date", "reportperiod", "epsdil"], parse_dates=["date", "reportperiod"])
    prices = pd.read_csv(os.path.join(P2, "reporting", "sharadar_cache", "us_master_universe_prices.csv"), index_col=0, parse_dates=True).sort_index()
    spy = pd.read_csv(os.path.join(HERE, "Data", "SPY_daily_adjclose.csv"), index_col=0, parse_dates=True)["close"].sort_index()
    returns = prices.pct_change(fill_method=None); market = spy.pct_change().reindex(returns.index)
    s = firm.sue_seasonal_random_walk(fund)
    s = s[s["sue"].notna() & (s["date"] >= R.EVENT_START) & (s["date"] <= R.EVENT_END) & s["ticker"].isin(returns.columns)].copy()
    iv = R.membership_intervals(os.path.join(P2, "archive", "sharadar_sp500_full_history.csv"))
    s = s[[R.is_member(iv, t, d) for t, d in zip(s["ticker"], s["date"])]].copy()
    s["fq"] = s["date"].dt.to_period("Q"); s["event_id"] = np.arange(len(s))
    s["decile"] = s.groupby("fq")["sue"].transform(lambda x: pd.qcut(x.rank(method="first"), 10, labels=False) + 1)
    pan = firm.abnormal_returns(returns, market, s[["event_id", "ticker", "date"]], (-250, -31), 120, (-30, 60))
    dec = s.set_index("event_id")["decile"].reindex(pan.ar.index)
    a = pd.DataFrame({"alpha_annualised": pan.alpha.groupby(dec).mean() * 252, "beta": pan.beta.groupby(dec).mean()})
    a.to_csv(os.path.join(R.OUT, "pead_diag_alpha_by_decile.csv"))
    pan_adj = firm.abnormal_returns(returns, market, s[["event_id", "ticker", "date"]], (-250, -31), 120, (-30, 60), model="market_adjusted")
    dec2 = s.set_index("event_id")["decile"].reindex(pan_adj.ar.index)
    rows = []
    for w in [(-30, -1), (0, 1), (2, 60)]:
        c = firm.car(pan_adj, w); g = c.groupby(dec2).mean()
        x, y = c[dec2 == 10].dropna(), c[dec2 == 1].dropna()
        t = (x.mean() - y.mean()) / np.sqrt(x.var(ddof=1) / len(x) + y.var(ddof=1) / len(y))
        rows.append({"window": f"[{w[0]},{w[1]}]", **{f"D{d}": g[d] for d in range(1, 11)}, "D10_minus_D1": x.mean() - y.mean(), "t_plain": t})
    m = pd.DataFrame(rows); m.to_csv(os.path.join(R.OUT, "pead_diag_market_adjusted.csv"), index=False)
    pd.set_option("display.width", 250)
    print(a.round(3).T.to_string()); print(m.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
