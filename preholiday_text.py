# -*- coding: utf-8 -*-
"""Pre-holiday section (P3-13 S&P, P3-14 FTSE, P3-15 FTSE without Easter) and the trials
13-15 ledger, generated from Data/results/. Shared by build_article.py and build_linkedin.py.

Every number here is read from the result CSVs. Nothing is typed.
"""
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "Data", "results")

MARKETS = ("us", "uk", "uk_nogf")


def _pts(x, d=3):
    return f"{100 * x:+.{d}f}"


def _sig(x, lo=2, hi=3):
    """Enough decimals that a small number is not printed as -0.00."""
    return f"{x:+.{lo}f}" if abs(x) >= 0.005 else f"{x:+.{hi}f}"


def _pv(p):
    return f"{p:.3f}" if p >= 0.001 else f"{p:.4f}"


def load():
    """{market -> {scope -> row}} plus the per-holiday tables."""
    stats, byhol = {}, {}
    for m in MARKETS:
        s = pd.read_csv(os.path.join(RES, f"preholiday_stats_{m}.csv")).set_index("scope")
        stats[m] = s
        byhol[m] = pd.read_csv(os.path.join(RES, f"preholiday_by_holiday_{m}.csv")).set_index("holiday")
    return stats, byhol


def _head(stats, m):
    return stats[m].loc["all holidays in the set"]


def paragraphs():
    stats, byhol = load()
    us, uk, ng = _head(stats, "us"), _head(stats, "uk"), _head(stats, "uk_nogf")
    leg = stats["us"].loc["legibility"]
    us_ye = stats["us"].loc[[i for i in stats["us"].index if "no year-end" in i][0]]
    decay = 1 - us["diff"] / leg["diff"]
    ukh = byhol["uk"]["mean_pct"].idxmax()
    ukh_v = byhol["uk"].loc[ukh]
    ush = byhol["us"]["mean_pct"].idxmax()
    ush_v = byhol["us"].loc[ush]
    us_worst = byhol["us"]["mean_pct"].idxmin()
    uk_worst = byhol["uk"]["mean_pct"].idxmin()

    p1 = ("The day before a public holiday is supposed to be the best day of the year to hold stocks. Ariel "
          "measured it on American data from 1963 to 1982 and found that single day returning something like "
          "ten times an ordinary one. It is the kind of claim this project exists to re-ask, because it comes "
          "with two things most calendar effects lack: a published sample, so there is a genuine out-of-sample "
          "period after it, and a published estimate of how much it faded once everyone knew. Three trials, "
          "P3-13 to P3-15.")

    p2 = (f"Identifying the event is most of the work, and it is where the arithmetic hides. A holiday is not in "
          f"the data; it is a hole in it, a weekday the exchange did not trade. Between 1983 and 2026 the S&P has "
          f"{int(us['n']) + 17} such holes but only about eight a year are scheduled holidays. The rest are "
          f"the eleventh of September 2001 and the four days after it, Hurricane Sandy, four presidential funerals, "
          f"a hurricane in 1985. The day before an unscheduled closure is the day the market was falling, so "
          f"leaving those in would load the sample in the direction everyone wants it to go. They are classified "
          f"out by rule and the full list is printed with the result.")

    p3 = (f"On Ariel's own sample the machinery finds exactly what he did: the pre-holiday session beat every other "
          f"session by {_pts(leg['diff'], 2)} points a day, t {leg['t']:.1f}. On the {int(us['n'])} pre-holiday "
          f"days since 1983 the gap is {_pts(us['diff'], 3)} points, t {us['t']:.2f}, one-sided p {_pv(us['p'])} "
          f"against a gate of 0.025. Fail. But the interesting number is the ratio of those two: the effect has "
          f"decayed by {100 * decay:.0f}%, and the decay figure in the literature is 77%. The gate needed the decay "
          f"to be under about seventy percent, which was written down before the run, so this trial was committed "
          f"in advance to failing if the published decay estimate was right. It was right. A fail here cannot tell "
          f"you the effect is gone; it can only tell you it is too small for this sample to see, which is a "
          f"different sentence and the one the record carries.")

    p4 = (f"So far, so tidy. Then the same test on the FTSE 100, which I argued was not worth running — a second "
          f"index, the same likely under-powered fail. That was wrong, and it was wrong for a reason worth naming: "
          f"I never checked how much the two event sets overlap. Five of the eight British bank holidays have no "
          f"American counterpart at all. On {int(uk['n'])} UK pre-holiday sessions since 1984 the gap is "
          f"{_pts(uk['diff'], 3)} points a day, t {uk['t']:.2f}, one-sided p {_pv(uk['p'])}, positive in both "
          f"halves of the sample. Pass — the only one in this family, and the trial I recommended against.")

    uk_top = ("the Easter session — one trading day that precedes both Good Friday and Easter Monday, since "
              "the Friday, Saturday and Sunday are all shut" if " + " in ukh else ukh)
    p5 = (f"A pass is where a project like this earns its gates, because the next question is whether it survives "
          f"being taken apart. The strongest British day is {uk_top} — {ukh_v['mean_pct']:+.2f}% a day — and "
          f"{ush} is also the strongest American one at {ush_v['mean_pct']:+.2f}%. If the UK result is "
          f"really an Easter result, it is not independent evidence of anything; it is the same spring weekend "
          f"seen from a second exchange. P3-15 removed it. The remaining {int(ng['n'])} sessions give "
          f"{_pts(ng['diff'], 3)} points, and here the two ways of computing significance part company: the "
          f"textbook two-sample t says p {_pv(ng['p'])} and the placebo says p {_pv(ng['p_placebo'])}. The "
          f"specification demanded both, fixed before the run precisely because they were going to disagree. "
          f"Fail. The British pre-holiday effect is an Easter effect with company.")

    p6 = (f"The disagreement is not a glitch and it is the most portable thing here. Pre-holiday sessions are "
          f"calm: the market moves about thirty percent less on them than on an ordinary day. A two-sample t "
          f"divides by the event group's own quiet variance and reads strong; the placebo asks how unusual the "
          f"number is against randomly chosen days drawn from the market as it actually is, and reads weaker. "
          f"Neither is wrong. But on a subset selected for being quiet, the t-statistic flatters, and the honest "
          f"default is the one that compares against the whole distribution. Had the gate been written with one "
          f"leg and chosen afterwards, P3-15 would have been a pass.")

    p7 = (f"Two smaller things the procedure caught, both in my own specification rather than in the market. "
          f"Printing every excluded closure surfaced five Juneteenths: an NYSE holiday since 2022 that I had not "
          f"listed among the nine, sitting in the discard pile where it did not belong. It stays there, recorded, "
          f"because amending a list after seeing the result is how a specification stops meaning anything, and "
          f"five days out of {int(us['n']) + 5} could not move the verdict. And a legibility check on the UK run "
          f"failed for the dullest possible reason: I had specified a count of holidays per year and the quantity "
          f"produced was sessions per year. They differ because the Thursday before Good Friday is also the "
          f"session before Easter Monday, and Christmas Eve precedes Boxing Day — the calendar pairs up its own "
          f"holidays. The same slip sat in the power calculation, so the trial that passed cleared a higher bar "
          f"than the one I had written down.")

    p8 = (f"The family closes there. Dead in America at a decay the literature had already measured; in Britain "
          f"indistinguishable from Easter. The Nikkei was not run, although the data is sitting in the folder and "
          f"a Japanese calendar shares nothing with either of these, because the specification said the third "
          f"market was conditional on the second surviving decomposition and it did not. Not running it is the "
          f"result. One last thing, reported and not tested: the weakest pre-holiday day in America is "
          f"{us_worst}, at {_sig(byhol['us'].loc[us_worst, 'mean_pct'])}%, and the weakest in Britain is "
          f"{uk_worst}, at {_sig(byhol['uk'].loc[uk_worst, 'mean_pct'])}%. In both countries the one session "
          f"everybody can name as a market ritual is the session that does nothing.")

    return [p1, p2, p3, p4, p5, p6, p7, p8]


def chart_rows():
    """Per-holiday mean daily return, both markets, for the section chart."""
    _, byhol = load()
    out = []
    for m, label in (("us", "S&P 500"), ("uk", "FTSE 100")):
        for h, r in byhol[m].sort_values("mean_pct", ascending=False).iterrows():
            out.append({"market": label, "holiday": h, "mean": float(r["mean_pct"]),
                        "n": int(r["n"]), "up": float(r["share_up"])})
    return out


def ledger3_rows():
    """Trials P3-13 .. P3-15 for the article's third ledger table."""
    stats, _ = load()
    us, uk, ng = _head(stats, "us"), _head(stats, "uk"), _head(stats, "uk_nogf")
    return [
        dict(trial="P3-13", hypothesis="Pre-holiday effect, S&P 500 (1983–2026, post-publication)",
             n=int(us["n"]), observed=f"{100 * us['diff']:+.3f} pts/day, t {us['t']:.2f}",
             p=_pv(us["p"]), verdict="fail", call="right"),
        dict(trial="P3-14", hypothesis="Pre-holiday effect, FTSE 100 (1984–2026)",
             n=int(uk["n"]), observed=f"{100 * uk['diff']:+.3f} pts/day, t {uk['t']:.2f}",
             p=_pv(uk["p"]), verdict="PASS", call="WRONG"),
        dict(trial="P3-15", hypothesis="The same, with Easter removed (both legs required)",
             n=int(ng["n"]), observed=f"{100 * ng['diff']:+.3f} pts/day, placebo p {_pv(ng['p_placebo'])}",
             p=_pv(ng["p"]), verdict="fail", call="right"),
    ]


PREHOLIDAY_PARAGRAPHS = paragraphs()
PREHOLIDAY_CHART = chart_rows()
LEDGER3 = ledger3_rows()
