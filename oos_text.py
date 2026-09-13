# -*- coding: utf-8 -*-
"""The September out-of-sample paragraph, generated from Data/results/september_oos*.csv.
Shared by build_article.py and build_linkedin.py so the two texts carry the same numbers."""
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "Data", "results")


def oos_text():
    oos = pd.concat([pd.read_csv(os.path.join(RES, "september_oos.csv")), pd.read_csv(os.path.join(RES, "september_oos2.csv"))])
    T = {r["trial"]: r for r in oos.to_dict("records") if str(r["trial"]).startswith("P3")}
    R = {r["series"]: r for r in oos.to_dict("records") if r["trial"] == "report"}
    parts = []
    for key, name, us in [("P3-8", "MSCI World since 1972", "report: S&P 500 on the MSCI World window"),
                          ("P3-9", "the FTSE 100 since 1984", "report: S&P 500 on the FTSE window"),
                          ("P3-10", "the Nikkei 225 since 1965", "report: S&P 500 on the Nikkei window"),
                          ("P3-7", "the STOXX 600, which Yahoo only carries from 2004", "report: S&P 500 on the STOXX window")]:
        r = T[key]; u = R[us]
        verdict = "passes" if r["passes_gate"] == "PASS" else "fails"
        parts.append(f"{name}: {100 * r['diff']:+.1f} points, t {r['t']:.2f}, p {r['p_one_sided']:.3f}, {verdict}"
                     f" (the S&P 500 on the same window: {100 * u['diff']:+.1f}, p {u['p_one_sided']:.3f})")
    halves = sum(int(T[k]["diff_half1"] < 0) + int(T[k]["diff_half2"] < 0) for k in ("P3-7", "P3-9", "P3-10"))
    return ("; ".join(parts) + ". The MSCI World pass is the S&P 500 again, since two-thirds of that index is American and "
            "the two rows on the same window agree to a hundredth of a point. The three indices with no American stocks "
            f"all have a negative September, in {halves} of their six half-samples, at roughly two-thirds of the American "
            "size, and none of them clears the gate on its own. Pooling them would be a test chosen after seeing the data, "
            "so it was not run. The record reads: September is a robust feature of the US index; abroad it has the same "
            "sign, a smaller size, and no single market can confirm it.")


OOS_TEXT = oos_text()
