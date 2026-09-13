# -*- coding: utf-8 -*-
"""Run the six pre-registered trials of PREREGISTRATION_US_POLITICAL_AND_CALENDAR_2026-09-13.md
and write every number to Data/results/. Nothing here chooses a window: every window,
seed and sample is the pre-registration's.

    python run_political_calendar_studies.py
"""
import os
import sys
from math import erf, sqrt

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from eventstudies import core  # noqa: E402

OUT = os.path.join(HERE, "Data", "results")
os.makedirs(OUT, exist_ok=True)
SEED, DRAWS = 42, 10000
GATE = 0.05 / 6


def norm_p(t):
    return 2 * (1 - 0.5 * (1 + erf(abs(t) / sqrt(2))))


def t_p(t, dof):
    """Two-sided p from the t-distribution (scipy if present, else normal approximation)."""
    try:
        from scipy import stats
        return float(2 * stats.t.sf(abs(t), dof))
    except Exception:
        return norm_p(t)


def main():
    prices = pd.read_csv(os.path.join(HERE, "Data", "GSPC_daily_close.csv"), index_col=0, parse_dates=True)["close"]
    prices = prices.sort_index()
    pres = core.us_election_dates(1928, 2024, "presidential")
    mid = core.us_election_dates(1930, 2022, "midterm")
    parties = pd.read_csv(os.path.join(HERE, "Data", "us_presidential_elections.csv")).set_index("year")
    summary = []

    # ---- P3-1 presidential post [+1,+60]
    r_post = core.window_returns(prices, pres.values, (1, 60))
    r_post.index = pres.index
    plc = core.placebo_window_means(prices, len(r_post.dropna()), (1, 60), DRAWS, SEED)
    p1 = core.placebo_pvalue(r_post.mean(), plc)
    summary.append(dict(trial="P3-1", hypothesis="presidential post [+1,+60] vs placebo", n=int(r_post.notna().sum()),
                        statistic=r_post.mean(), placebo_mean=plc.mean(), placebo_sd=plc.std(), p=p1))

    # ---- P3-2 party difference
    lab = parties["winner_party"].reindex(r_post.index)
    pd2 = core.permutation_diff(r_post, lab, "D", "R", DRAWS, SEED)
    summary.append(dict(trial="P3-2", hypothesis="post [+1,+60] Democrat - Republican winner", n=pd2["n_a"] + pd2["n_b"],
                        statistic=pd2["diff"], placebo_mean=0.0, placebo_sd=np.nan, p=pd2["p"],
                        note=f"D mean {pd2['mean_a']:.4f} (n {pd2['n_a']}), R mean {pd2['mean_b']:.4f} (n {pd2['n_b']})"))
    keep = ~r_post.index.isin([2000, 2020])
    pd2x = core.permutation_diff(r_post[keep], lab[keep], "D", "R", DRAWS, SEED)
    summary.append(dict(trial="P3-2 (report)", hypothesis="same, excluding 2000 and 2020", n=pd2x["n_a"] + pd2x["n_b"],
                        statistic=pd2x["diff"], placebo_mean=0.0, placebo_sd=np.nan, p=pd2x["p"]))

    # ---- P3-3 presidential pre [-60,0]
    r_pre = core.window_returns(prices, pres.values, (-60, 0)); r_pre.index = pres.index
    plc = core.placebo_window_means(prices, len(r_pre.dropna()), (-60, 0), DRAWS, SEED)
    p3 = core.placebo_pvalue(r_pre.mean(), plc)
    summary.append(dict(trial="P3-3", hypothesis="presidential pre [-60,0] vs placebo", n=int(r_pre.notna().sum()),
                        statistic=r_pre.mean(), placebo_mean=plc.mean(), placebo_sd=plc.std(), p=p3))
    inc = parties["incumbent_party"].reindex(r_pre.index)
    pdi = core.permutation_diff(r_pre, inc, "D", "R", DRAWS, SEED)
    summary.append(dict(trial="P3-3 (report)", hypothesis="pre [-60,0] Democrat - Republican INCUMBENT", n=pdi["n_a"] + pdi["n_b"],
                        statistic=pdi["diff"], placebo_mean=0.0, placebo_sd=np.nan, p=pdi["p"]))

    # ---- P3-4 midterm post [+1,+90]
    r_mid = core.window_returns(prices, mid.values, (1, 90)); r_mid.index = mid.index
    plc = core.placebo_window_means(prices, len(r_mid.dropna()), (1, 90), DRAWS, SEED)
    p4 = core.placebo_pvalue(r_mid.mean(), plc)
    summary.append(dict(trial="P3-4", hypothesis="midterm post [+1,+90] vs placebo, 1930-2022", n=int(r_mid.notna().sum()),
                        statistic=r_mid.mean(), placebo_mean=plc.mean(), placebo_sd=plc.std(), p=p4))
    r_mid74 = r_mid[r_mid.index >= 1974]
    plc74 = core.placebo_window_means(prices, len(r_mid74), (1, 90), DRAWS, SEED)
    summary.append(dict(trial="P3-4 (report)", hypothesis="midterm post [+1,+90], Goldman window 1974-2022", n=len(r_mid74),
                        statistic=r_mid74.mean(), placebo_mean=plc74.mean(), placebo_sd=plc74.std(),
                        p=core.placebo_pvalue(r_mid74.mean(), plc74)))

    # ---- P3-5 calendar months
    monthly = core.monthly_returns(prices)
    tab = core.calendar_month_table(monthly)
    h1, h2 = monthly[monthly.index.year <= 1976], monthly[monthly.index.year >= 1977]
    t1, t2 = core.calendar_month_table(h1), core.calendar_month_table(h2)
    tab["diff_1928_1976"] = t1["diff"]; tab["diff_1977_2026"] = t2["diff"]
    tab["same_sign_halves"] = np.sign(t1["diff"]) == np.sign(t2["diff"])
    tab["passes_gate"] = tab["bonferroni12"] & tab["same_sign_halves"]
    tab.to_csv(os.path.join(OUT, "calendar_months.csv"))
    best = tab["p"].idxmin()
    summary.append(dict(trial="P3-5", hypothesis="any calendar month unusual (Bonferroni 12 + same sign in both halves)",
                        n=len(monthly), statistic=tab.loc[best, "diff"], placebo_mean=np.nan, placebo_sd=np.nan,
                        p=tab.loc[best, "p"], note=f"most extreme month {best}, passes_gate={bool(tab.loc[best, 'passes_gate'])}; "
                        f"months clearing Bonferroni: {list(tab.index[tab['bonferroni12']])}; passing gate: {list(tab.index[tab['passes_gate']])}"))

    # ---- P3-6 sell in May
    sim = core.sell_in_may_table(monthly)
    sim.to_csv(os.path.join(OUT, "sell_in_may_by_year.csv"))
    for label, sub, gated in [("2003-2025 (post-publication, GATE)", sim[(sim.index >= 2003) & (sim.index <= 2025)], True),
                              ("1928-2025 full", sim, False), ("1950-2025", sim[sim.index >= 1950], False),
                              ("1928-2002 pre-publication", sim[sim.index <= 2002], False)]:
        pt = core.paired_t(sub["diff"])
        summary.append(dict(trial="P3-6" if gated else "P3-6 (report)", hypothesis=f"Sell in May winter - summer, {label}",
                            n=pt["n"], statistic=pt["mean"], placebo_mean=0.0, placebo_sd=np.nan, p=t_p(pt["t"], pt["n"] - 1),
                            note=f"t {pt['t']:.2f}; winter mean {sub['winter'].mean():.4f}, summer mean {sub['summer'].mean():.4f}, share winter>summer {(sub['diff'] > 0).mean():.2f}"))

    # ---- reported: presidential cycle by year and party
    yearly = prices.resample("YE").last().pct_change().dropna()
    rows = []
    for y, pr in parties["winner_party"].items():
        for k in range(1, 5):
            yr = y + k
            if pd.Timestamp(year=yr, month=12, day=31) in yearly.index or yr < 2026:
                v = yearly[yearly.index.year == yr]
                if len(v):
                    rows.append(dict(election=y, party=pr, cycle_year=k, year=yr, ret=float(v.iloc[0])))
    cyc = pd.DataFrame(rows)
    cyc.to_csv(os.path.join(OUT, "presidential_cycle_years.csv"), index=False)
    cyc_tab = cyc.groupby(["cycle_year", "party"])["ret"].agg(["mean", "median", "count"]).unstack("party")
    cyc_tab.to_csv(os.path.join(OUT, "presidential_cycle_summary.csv"))

    # ---- paths and placebo bands for the charts
    PRE, POST = 90, 90
    paths_p = core.event_paths(prices, pres.values, PRE, POST); paths_p.index = pres.index
    paths_m = core.event_paths(prices, mid.values, PRE, POST); paths_m.index = mid.index
    paths_p.to_csv(os.path.join(OUT, "paths_presidential.csv")); paths_m.to_csv(os.path.join(OUT, "paths_midterm.csv"))
    core.placebo_path_band(prices, len(paths_p), PRE, POST, 2000, SEED).to_csv(os.path.join(OUT, "band_presidential_n25.csv"))
    core.placebo_path_band(prices, len(paths_m), PRE, POST, 2000, SEED).to_csv(os.path.join(OUT, "band_midterm_n24.csv"))
    nD, nR = int((lab == "D").sum()), int((lab == "R").sum())
    core.placebo_path_band(prices, nD, PRE, POST, 2000, SEED).to_csv(os.path.join(OUT, f"band_presidential_n{nD}.csv"))
    core.placebo_path_band(prices, nR, PRE, POST, 2000, SEED).to_csv(os.path.join(OUT, f"band_presidential_n{nR}.csv"))
    paths_m[paths_m.index >= 1974].to_csv(os.path.join(OUT, "paths_midterm_1974.csv"))
    core.placebo_path_band(prices, int((paths_m.index >= 1974).sum()), PRE, POST, 2000, SEED).to_csv(os.path.join(OUT, "band_midterm_1974.csv"))
    # per-event window returns for the record
    pd.DataFrame({"post_1_60": r_post, "pre_m60_0": r_pre, "winner_party": lab, "incumbent_party": inc}).to_csv(os.path.join(OUT, "presidential_windows.csv"))
    r_mid.rename("post_1_90").to_csv(os.path.join(OUT, "midterm_windows.csv"))
    # monthly seasonal path: average cumulative price return by calendar month (for the chart)
    mon = monthly.groupby(monthly.index.month).agg(["mean", "median", "std", "count"])
    mon.to_csv(os.path.join(OUT, "monthly_by_calendar_month.csv"))

    s = pd.DataFrame(summary)
    s["passes_gate"] = np.where(s["trial"].str.contains("report"), "", np.where(s["p"] < GATE, "PASS", "fail"))
    s.to_csv(os.path.join(OUT, "summary.csv"), index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 120)
    print(s.to_string(index=False))
    print("\ncalendar months:\n", tab[["n", "mean", "diff", "t", "p", "bonferroni12", "diff_1928_1976", "diff_1977_2026", "passes_gate"]].round(4).to_string())
    print("\npresidential cycle (mean annual price return by cycle year and party):\n", cyc_tab.round(4).to_string())


if __name__ == "__main__":
    main()
