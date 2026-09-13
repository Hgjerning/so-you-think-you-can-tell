# -*- coding: utf-8 -*-
"""Trials P3-7 and P3-8 of PREREGISTRATION_SEPTEMBER_OOS_2026-09-13.md: September vs the other
eleven months on STOXX Europe 600 and MSCI World. Writes Data/results/september_oos.csv.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from eventstudies import core  # noqa: E402

OUT = os.path.join(HERE, "Data", "results")
LAST_MONTH = "2026-08-31"
GATE = 0.025


def one_sided_p(t, dof):
    try:
        from scipy import stats
        return float(stats.t.cdf(t, dof))          # P(T <= t): small when t is very negative
    except Exception:
        from math import erf, sqrt
        return float(0.5 * (1 + erf(t / sqrt(2))))


def load(name):
    s = pd.read_csv(os.path.join(HERE, "Data", name), index_col=0, parse_dates=True)["close"].sort_index()
    return s[s.index <= LAST_MONTH]


def september_row(label, monthly):
    x = monthly[monthly.index.month == 9].to_numpy(); y = monthly[monthly.index.month != 9].to_numpy()
    diff, t, dof = core.welch_t(x, y)
    years = sorted(set(monthly.index.year)); mid = years[len(years) // 2]
    h1, h2 = monthly[monthly.index.year < mid], monthly[monthly.index.year >= mid]
    d1 = h1[h1.index.month == 9].mean() - h1[h1.index.month != 9].mean()
    d2 = h2[h2.index.month == 9].mean() - h2[h2.index.month != 9].mean()
    p = one_sided_p(t, dof)
    return dict(series=label, months=len(monthly), n_sep=len(x), first=str(monthly.index.min().date()), last=str(monthly.index.max().date()),
                sep_mean=x.mean(), other_mean=y.mean(), diff=diff, t=t, dof=dof, p_one_sided=p, split_year=mid,
                diff_half1=d1, diff_half2=d2, both_negative=bool(d1 < 0 and d2 < 0))


def main():
    stoxx, world, spx = load("STOXX_daily_close.csv"), load("990100_USD_STRD_daily_close.csv"), load("GSPC_daily_close.csv")
    m_stoxx, m_world, m_spx = core.monthly_returns(stoxx), core.monthly_returns(world), core.monthly_returns(spx)
    rows = []
    r7 = september_row("P3-7 STOXX Europe 600", m_stoxx); r7["trial"] = "P3-7"; rows.append(r7)
    r8 = september_row("P3-8 MSCI World (USD)", m_world); r8["trial"] = "P3-8"; rows.append(r8)
    rows.append({**september_row("report: S&P 500 on the STOXX window", m_spx[m_spx.index >= m_stoxx.index.min()]), "trial": "report"})
    rows.append({**september_row("report: S&P 500 on the MSCI World window", m_spx[m_spx.index >= m_world.index.min()]), "trial": "report"})
    df = pd.DataFrame(rows)
    df["passes_gate"] = np.where(df["trial"].str.startswith("P3"), np.where((df["p_one_sided"] < GATE) & df["both_negative"], "PASS", "fail"), "")
    df.to_csv(os.path.join(OUT, "september_oos.csv"), index=False)
    for label, m in [("STOXX Europe 600", m_stoxx), ("MSCI World", m_world)]:
        tab = core.calendar_month_table(m)
        tab.to_csv(os.path.join(OUT, f"calendar_months_{label.split()[0].lower()}.csv"))
        print(f"\n{label}: twelve-month table (two-sided p, for the record)\n", tab[["n", "mean", "diff", "t", "p"]].round(4).to_string())
    pd.set_option("display.width", 250)
    print("\n", df[["trial", "series", "n_sep", "first", "last", "sep_mean", "other_mean", "diff", "t", "p_one_sided", "diff_half1", "diff_half2", "both_negative", "passes_gate"]].round(4).to_string(index=False))


if __name__ == "__main__":
    main()
