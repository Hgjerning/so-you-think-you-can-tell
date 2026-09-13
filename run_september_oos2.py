# -*- coding: utf-8 -*-
"""Trials P3-9 and P3-10 of PREREGISTRATION_SEPTEMBER_OOS2_2026-09-13.md: September vs the other
eleven months on FTSE 100 and Nikkei 225. Same statistic and gate as run_september_oos.py,
whose functions are reused unchanged. Writes Data/results/september_oos2.csv.
"""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from eventstudies import core  # noqa: E402
from run_september_oos import GATE, OUT, load, september_row  # noqa: E402


def main():
    ftse, n225, spx = load("FTSE_daily_close.csv"), load("N225_daily_close.csv"), load("GSPC_daily_close.csv")
    m_ftse, m_n225, m_spx = core.monthly_returns(ftse), core.monthly_returns(n225), core.monthly_returns(spx)
    rows = []
    r9 = september_row("P3-9 FTSE 100", m_ftse); r9["trial"] = "P3-9"; rows.append(r9)
    r10 = september_row("P3-10 Nikkei 225", m_n225); r10["trial"] = "P3-10"; rows.append(r10)
    rows.append({**september_row("report: S&P 500 on the FTSE window", m_spx[m_spx.index >= m_ftse.index.min()]), "trial": "report"})
    rows.append({**september_row("report: S&P 500 on the Nikkei window", m_spx[m_spx.index >= m_n225.index.min()]), "trial": "report"})
    df = pd.DataFrame(rows)
    df["passes_gate"] = np.where(df["trial"].str.startswith("P3"), np.where((df["p_one_sided"] < GATE) & df["both_negative"], "PASS", "fail"), "")
    df.to_csv(os.path.join(OUT, "september_oos2.csv"), index=False)
    for label, m in [("FTSE 100", m_ftse), ("Nikkei 225", m_n225)]:
        tab = core.calendar_month_table(m)
        tab.to_csv(os.path.join(OUT, f"calendar_months_{label.split()[0].lower()}.csv"))
        print(f"\n{label}: twelve-month table (two-sided p, for the record)\n", tab[["n", "mean", "diff", "t", "p"]].round(4).to_string())
    pd.set_option("display.width", 250)
    print("\n", df[["trial", "series", "n_sep", "first", "last", "sep_mean", "other_mean", "diff", "t", "p_one_sided", "diff_half1", "diff_half2", "both_negative", "passes_gate"]].round(4).to_string(index=False))


if __name__ == "__main__":
    main()
