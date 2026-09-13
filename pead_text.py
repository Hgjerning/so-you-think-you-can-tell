# -*- coding: utf-8 -*-
"""Earnings-surprise section (P3-11 Sharadar, P3-12 ART) and the trials 7–12 ledger, generated
from Data/results/. Shared by build_article.py and build_linkedin.py."""
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "Data", "results")


def _pct(x, d=1):
    return f"{100 * x:+.{d}f}"


def load():
    sh = pd.read_csv(os.path.join(RES, "pead_summary.csv")).set_index("sample").loc["gated"]
    shd = pd.read_csv(os.path.join(RES, "pead_diag_market_adjusted.csv")).set_index("window")
    art = pd.read_csv(os.path.join(RES, "pead_art_summary.csv")).set_index("scope")
    dec = pd.read_csv(os.path.join(RES, "pead_art_deciles.csv")).set_index("decile")
    return sh, shd, art, dec


def paragraphs():
    sh, shd, art, dec = load()
    a = art.loc["ALL"]
    p1 = ("Post-earnings-announcement drift has the longest paper trail of any event effect: after a good "
          "earnings surprise the stock keeps rising for weeks, after a bad one it keeps falling. Two data sets, "
          "two pre-registered trials, the P3-11 and P3-12 of the ledger.")
    p2 = (f"The first used Sharadar's point-in-time S&P 500 from 2013, {int(sh['n_events']):,} filings by members on the day. "
          "Sharadar dates the 10-Q filing, a median 36 days after the quarter ends and weeks after the press release, so this "
          "could only ever be a post-filing test. The surprise is the seasonal random walk: this quarter's EPS minus the same "
          "quarter a year earlier, scaled by the firm's own history, in deciles by quarter. A calendar-time book long the top "
          f"decile and short the bottom from day +2 to +60 earned {_pct(sh['ct_alpha_annual'])}% a year with a Newey–West t of "
          f"{sh['ct_t_nw']:.2f}. Market-adjusted, the top decile beat the bottom by {_pct(shd.loc['[-30,-1]', 'D10_minus_D1'])} points in the month "
          f"before the filing (t {shd.loc['[-30,-1]', 't_plain']:.1f}, the press release is in there) and by {_pct(shd.loc['[2,60]', 'D10_minus_D1'])} points "
          f"in the three months after it (t {shd.loc['[2,60]', 't_plain']:.1f}). Fail, as predicted.")
    p3 = (f"The second used ART, my own 1997–2012 database: {int(a['n_events']):,} quarterly announcements dated by IBES on the day they "
          "were made, every stock a member of the developed-market universe on that day, Europe, America and Asia. This is the "
          "sample the literature's drift lived on, and it is the one trial in the project where I wrote down a pass as the "
          "expected outcome, at about sixty percent.")
    p4 = (f"The announcement is unmistakable: the top surprise decile beats the bottom by {_pct(a['d10_d1_0_1'])} points on the two announcement "
          f"days, t {a['t_0_1']:.0f}, and by {_pct(a['d10_d1_-30_-1'])} points in the month before, which is analysts and leakage. The drift after it is "
          f"{_pct(a['d10_d1_2_60'])} points over the next three months, t {a['t_2_60']:.1f}. The calendar-time long-short book earns "
          f"{_pct(a['ct_alpha_annual'])}% a year, t {a['ct_t_nw']:.2f}, one-sided p {a['ct_p_one_sided']:.3f} against a gate of 0.025. "
          f"Every decile drifts down against the equal-weight market, between {_pct(dec['car2_60'].max())} and {_pct(dec['car2_60'].min())} points, "
          f"so a long-only book of good surprises loses {_pct(-a['long_only_d10_alpha_annual'])}% a year (t {a['long_only_t']:.1f}) and only the spread is positive. "
          f"Asia on its own shows {_pct(art.loc['Asia', 'd10_d1_2_60'])} points with t {art.loc['Asia', 't_2_60']:.1f}; that is recorded as seen and not tested, "
          "because a region picked after the data is a new trial. Fail. My sixty percent was wrong.")
    p5 = ("Two harness bugs surfaced on the way and are worth more than the verdict. On Sharadar, the textbook market model fits an "
          "intercept on the prior year; on firms sorted by earnings changes that intercept runs from minus ten to plus ten percent a "
          "year across the deciles, and sixty days of it manufactures a four-point reversal that is not in the returns. On ART, the "
          "price panel spans three regional calendars, so a US stock is missing on Tokyo-only days; a naive return calculation then "
          "also loses the day after every gap, and a strict cumulative-return rule wiped out almost every American drift window. "
          "Both were fixed before the corrected numbers were seen, both are guarded by tests that manufacture the bug on synthetic "
          "data, and in both cases the corrected verdict was the same as the flawed one. That last part is luck, not design.")
    return [p1, p2, p3, p4, p5]


def chart_rows():
    _, _, _, dec = load()
    return [{"decile": int(d), "car01": float(r["car0_1"]), "car260": float(r["car2_60"])} for d, r in dec.iterrows()]


def ledger2_rows():
    """Trials P3-7 .. P3-12 for the article's second ledger table."""
    s1 = pd.read_csv(os.path.join(RES, "september_oos.csv")); s2 = pd.read_csv(os.path.join(RES, "september_oos2.csv"))
    sep = pd.concat([s1, s2]); sep = sep[sep["trial"].astype(str).str.startswith("P3")].set_index("trial")
    sh, _, art, _ = load(); a = art.loc["ALL"]
    rows = []
    names = {"P3-7": "September, STOXX Europe 600 (2004–2026)", "P3-8": "September, MSCI World (1972–2026)",
             "P3-9": "September, FTSE 100 (1984–2026)", "P3-10": "September, Nikkei 225 (1965–2026)"}
    for t in ["P3-7", "P3-8", "P3-9", "P3-10"]:
        r = sep.loc[t]
        rows.append(dict(trial=t, hypothesis=names[t], n=int(r["n_sep"]), observed=f"{100 * r['diff']:+.1f} pts/mo",
                         p=f"{r['p_one_sided']:.3f}", verdict="PASS" if r["passes_gate"] == "PASS" else "fail", call="right"))
    rows.append(dict(trial="P3-11", hypothesis="Post-filing earnings drift, Sharadar PIT S&P 500 (2013–2026)", n=int(sh["n_events"]),
                     observed=f"{100 * sh['ct_alpha_annual']:+.1f}%/yr, t {sh['ct_t_nw']:.2f}", p=f"{sh['ct_p_one_sided']:.3f}", verdict="fail", call="right"))
    rows.append(dict(trial="P3-12", hypothesis="Post-announcement earnings drift, ART Global Developed (1997–2012)", n=int(a["n_events"]),
                     observed=f"{100 * a['ct_alpha_annual']:+.1f}%/yr, t {a['ct_t_nw']:.2f}", p=f"{a['ct_p_one_sided']:.3f}", verdict="fail", call="WRONG"))
    return rows


PEAD_PARAGRAPHS = paragraphs()
PEAD_CHART = chart_rows()
LEDGER2 = ledger2_rows()
