# -*- coding: utf-8 -*-
"""Trial P3-11 of PREREGISTRATION_PEAD_SHARADAR_2026-09-13.md. Writes Data/results/pead_*.csv.
Every window, sample bound and gate is the pre-registration's.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from eventstudies import firm  # noqa: E402

P2 = os.path.join(os.path.dirname(HERE), "Project2 Investment Strategy")
OUT = os.path.join(HERE, "Data", "results")
EVENT_START, EVENT_END = "2013-01-02", "2026-06-01"
HALF_SPLIT = "2020-01-01"
HOLD = (2, 60)


def membership_intervals(events_path):
    """Per ticker, list of [start, end] membership intervals from Sharadar's add/remove events
    and the current list. A 'removed' with no prior 'added' starts at the data start; an 'added'
    with no later 'removed' runs to the end; current tickers with no events are members throughout."""
    e = pd.read_csv(events_path, parse_dates=["date"])
    start, end = pd.Timestamp("2010-01-01"), pd.Timestamp("2099-12-31")
    current = set(e.loc[e["action"] == "current", "ticker"])
    ev = e[e["action"].isin(["added", "removed"])].sort_values(["ticker", "date"])
    iv = {}
    for t, g in ev.groupby("ticker"):
        opens = []; cur = None
        for r in g.itertuples():
            if r.action == "added":
                cur = r.date
            else:
                opens.append((start if cur is None else cur, r.date)); cur = None
        if cur is not None:
            opens.append((cur, end))
        iv[t] = opens
    for t in current:
        if t not in iv:
            iv[t] = [(start, end)]
        elif iv[t] and iv[t][-1][1] != end and not any(b == end for a, b in iv[t]):
            iv[t].append((iv[t][-1][1], end))   # currently a member but last event was a removal (re-add missing): treated as member since that removal
    return iv


def is_member(iv, ticker, date):
    return any(a <= date <= b for a, b in iv.get(ticker, []))


def main():
    os.makedirs(OUT, exist_ok=True)
    fund = pd.read_csv(os.path.join(P2, "reporting", "sharadar_cache", "us_fundamentals.csv"),
                       usecols=["ticker", "date", "reportperiod", "epsdil"], parse_dates=["date", "reportperiod"])
    prices = pd.read_csv(os.path.join(P2, "reporting", "sharadar_cache", "us_master_universe_prices.csv"), index_col=0, parse_dates=True).sort_index()
    spy = pd.read_csv(os.path.join(HERE, "Data", "SPY_daily_adjclose.csv"), index_col=0, parse_dates=True)["close"].sort_index()
    returns = prices.pct_change(fill_method=None)
    market = spy.pct_change().reindex(returns.index)

    s = firm.sue_seasonal_random_walk(fund)
    s = s[s["sue"].notna() & (s["date"] >= EVENT_START) & (s["date"] <= EVENT_END) & s["ticker"].isin(returns.columns)].copy()
    iv = membership_intervals(os.path.join(P2, "archive", "sharadar_sp500_full_history.csv"))
    s["member"] = [is_member(iv, t, d) for t, d in zip(s["ticker"], s["date"])]
    s["fq"] = s["date"].dt.to_period("Q")
    s["event_id"] = np.arange(len(s))
    print(f"events with SUE in window: {len(s)}; members on filing date: {int(s['member'].sum())}")

    results = {}
    for label, sub in [("gated", s[s["member"]].copy()), ("ungated", s.copy())]:
        sub["decile"] = sub.groupby("fq")["sue"].transform(lambda x: pd.qcut(x.rank(method="first"), 10, labels=False) + 1)
        pan = firm.abnormal_returns(returns, market, sub[["event_id", "ticker", "date"]], est_window=(-250, -31), min_est=120, event_window=(-30, 60))
        dec = sub.set_index("event_id")["decile"].reindex(pan.ar.index)
        rows = []
        for d in range(1, 11):
            m = dec == d
            rows.append({"decile": d, "n": int(m.sum()),
                         **{f"car_m30_m1": firm.bmp_test(pan, (-30, -1), m)["mean_car"], "t_m30_m1": firm.bmp_test(pan, (-30, -1), m)["t_bmp"],
                            "car_0_1": firm.bmp_test(pan, (0, 1), m)["mean_car"], "t_0_1": firm.bmp_test(pan, (0, 1), m)["t_bmp"],
                            "car_2_60": firm.bmp_test(pan, (2, 60), m)["mean_car"], "t_2_60": firm.bmp_test(pan, (2, 60), m)["t_bmp"]}})
        tab = pd.DataFrame(rows).set_index("decile")
        # D10 - D1 on standardized CARs, Welch t
        def d10_d1(window):
            c = firm.car(pan, window); L = window[1] - window[0] + 1
            sc = (c / (pan.sigma * np.sqrt(L)))
            a, b = sc[dec == 10].dropna(), sc[dec == 1].dropna()
            ca, cb = c[dec == 10].dropna(), c[dec == 1].dropna()
            t = (a.mean() - b.mean()) / np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
            return {"diff_car": float(ca.mean() - cb.mean()), "t_welch_scar": float(t), "n10": len(a), "n1": len(b)}
        diffs = {w: d10_d1(w) for w in [(-30, -1), (0, 1), (2, 60)]}
        # calendar-time long D10 / short D1
        ev = pan.events.set_index("event_id"); w = pd.Series(0.0, index=ev.index)
        w[dec == 10] = 1.0; w[dec == 1] = -1.0
        ev2 = ev.reset_index()
        ct = firm.calendar_time_portfolio(returns, ev2, HOLD, weights=w.reindex(ev2["event_id"]).set_axis(ev2.index))
        x = pd.DataFrame({"mkt": market})
        full = firm.newey_west_alpha(ct, x); h1 = firm.newey_west_alpha(ct[ct.index < HALF_SPLIT], x); h2 = firm.newey_west_alpha(ct[ct.index >= HALF_SPLIT], x)
        wl = pd.Series(0.0, index=ev.index); wl[dec == 10] = 1.0
        ctl = firm.calendar_time_portfolio(returns, ev2, HOLD, weights=wl.reindex(ev2["event_id"]).set_axis(ev2.index))
        long_only = firm.newey_west_alpha(ctl, x)
        from math import erf, sqrt
        p_one = 1 - 0.5 * (1 + erf(full["t"] / sqrt(2)))
        results[label] = dict(tab=tab, diffs=diffs, ct=ct, full=full, h1=h1, h2=h2, long_only=long_only, p_one=p_one,
                              n_used=len(pan.ar), dropped=pan.dropped["reason"].value_counts().to_dict())
        tab.to_csv(os.path.join(OUT, f"pead_deciles_{label}.csv"))
        ct.rename("ls_ret").to_csv(os.path.join(OUT, f"pead_calendar_time_{label}.csv"))

    g = results["gated"]
    legible = g["diffs"][(-30, -1)]["diff_car"] > 0 and g["diffs"][(-30, -1)]["t_welch_scar"] > 3
    passes = (g["p_one"] < 0.025) and (g["h1"]["alpha"] > 0) and (g["h2"]["alpha"] > 0)
    summary = []
    for label, r in results.items():
        summary.append(dict(sample=label, n_events=r["n_used"], d10_d1_car_m30_m1=r["diffs"][(-30, -1)]["diff_car"], t_m30_m1=r["diffs"][(-30, -1)]["t_welch_scar"],
                            d10_d1_car_0_1=r["diffs"][(0, 1)]["diff_car"], t_0_1=r["diffs"][(0, 1)]["t_welch_scar"],
                            d10_d1_car_2_60=r["diffs"][(2, 60)]["diff_car"], t_2_60=r["diffs"][(2, 60)]["t_welch_scar"],
                            ct_alpha_daily=r["full"]["alpha"], ct_alpha_annual=r["full"]["alpha"] * 252, ct_t_nw=r["full"]["t"], ct_p_one_sided=r["p_one"],
                            ct_alpha_h1_annual=r["h1"]["alpha"] * 252, ct_t_h1=r["h1"]["t"], ct_alpha_h2_annual=r["h2"]["alpha"] * 252, ct_t_h2=r["h2"]["t"],
                            long_only_d10_alpha_annual=r["long_only"]["alpha"] * 252, long_only_t=r["long_only"]["t"], dropped=str(r["dropped"])))
    sdf = pd.DataFrame(summary); sdf["legibility"] = ["PASS" if legible else "FAIL"] * 2; sdf["P3-11"] = [("PASS" if passes else "fail") if legible else "uninterpretable"] * 2
    sdf.to_csv(os.path.join(OUT, "pead_summary.csv"), index=False)
    pd.set_option("display.width", 250)
    for label, r in results.items():
        print(f"\n[{label}] deciles (mean CAR, BMP t):\n", r["tab"].round(4).to_string())
    print("\n", sdf.round(4).T.to_string())


if __name__ == "__main__":
    main()
