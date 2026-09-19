# -*- coding: utf-8 -*-
"""The pre-holiday effect -- P3-13 (US, ^GSPC) and P3-14 (UK, ^FTSE).

Runs exactly the specifications committed in PREREGISTRATION_PREHOLIDAY_2026-09-19.md
(commit 6074641) and PREREGISTRATION_PREHOLIDAY_FTSE_2026-09-19.md. Nothing here chooses a window, a sample or a gate; all of those are
fixed in that document and are repeated in the output so the two can be checked against
each other without opening both.

    python run_preholiday.py [US|UK]     # default US

Writes Data/results/preholiday_*_<market>.csv and prints the whole report.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from eventstudies import core  # noqa: E402

# --------------------------------------------------------------------------- fixed by the specs
OUT_DIR = os.path.join(HERE, "Data", "results")
GATE_P = 0.025                                           # one-sided, one trial each
N_DRAWS, SEED = 20000, 42

MARKETS = {
    # P3-13 -- PREREGISTRATION_PREHOLIDAY_2026-09-19.md (commit 6074641)
    "US": dict(
        trial="P3-13", index="^GSPC", calendar="US", price_file="GSPC_daily_close.csv",
        trial_start="1983-01-01", trial_end="2026-09-11",
        legib_start="1963-01-01", legib_end="1982-12-31",
        legib_note="Ariel 1990's own sample; NOT a trial", legib_min_t=3.0,
        half_split="2005-01-01",
        year_end=["Christmas Day", "New Year's Day"],
        tripwire=25,
        reserved="1928-01-03 -> 1962-12-31 is RESERVED by the pre-registration and is not read here.",
    ),
    # P3-14 -- PREREGISTRATION_PREHOLIDAY_FTSE_2026-09-19.md
    "UK": dict(
        trial="P3-14", index="^FTSE", calendar="UK", price_file="FTSE_daily_close.csv",
        trial_start="1984-01-03", trial_end="2026-09-11",
        legib_start=None, legib_end=None,
        legib_note="none -- the UK check is STRUCTURAL, see the exclusion list", legib_min_t=None,
        half_split="2005-01-01",
        # the UK clusters THREE of its eight holidays at the turn of the year
        year_end=["Christmas Day", "Boxing Day", "New Year's Day"],
        tripwire=25,
        reserved="the FTSE 100 series begins 1984-01-03; there is no earlier window to reserve.",
    ),
    # P3-15 -- PREREGISTRATION_PREHOLIDAY_NOGF_2026-09-19.md (commit 8beccb9)
    "UK_NOGF": dict(
        trial="P3-15", index="^FTSE", calendar="UK", price_file="FTSE_daily_close.csv",
        trial_start="1984-01-03", trial_end="2026-09-11",
        legib_start=None, legib_end=None,
        legib_note="none -- see P3-14; this is a subset of its event set", legib_min_t=None,
        half_split="2005-01-01",
        year_end=["Christmas Day", "Boxing Day", "New Year's Day"],
        tripwire=25,
        exclude=["Good Friday"],          # takes Easter Monday with it -- spec section 1
        both_legs=True,                   # spec section 2: Welch AND placebo must clear
        reserved="the FTSE 100 series begins 1984-01-03; there is no earlier window to reserve.",
    ),
}


def line(c="-", n=92):
    print(c * n)


def one_sided_greater(x: np.ndarray, y: np.ndarray) -> dict:
    """Welch t for mean(x) - mean(y) and the one-sided p that x is the larger."""
    diff, t, dof = core.welch_t(x, y)
    return {"n": len(x), "mean_x": float(np.mean(x)), "mean_y": float(np.mean(y)),
            "diff": diff, "t": t, "dof": dof, "p": float(stats.t.sf(t, dof))}


def report(tag: str, r: dict):
    print(f"  {tag:<34s} n {r['n']:>5d}   pre-holiday {r['mean_x']*100:+.4f}%   "
          f"other {r['mean_y']*100:+.4f}%   gap {r['diff']*100:+.4f} pts   "
          f"t {r['t']:+.2f}   one-sided p {r['p']:.4f}")


def build_events(prices: pd.Series, start: str, end: str, calendar: str):
    """Event days and the exclusion list, per section 2 of the pre-registration."""
    idx = prices.loc[start:end].index
    sched, unsched = core.scheduled_closures(idx, calendar=calendar)
    ev = core.preceding_sessions(idx, sched.index)
    ev = ev[(ev.index >= idx[0]) & (ev.index <= idx[-1])]
    # A session can precede two closures -- the Thursday before Good Friday also precedes
    # Easter Monday, because the Friday, Saturday and Sunday are all non-trading. Label it
    # with BOTH, or a per-holiday table silently credits one holiday with the other's day.
    pos = idx.searchsorted(pd.DatetimeIndex(sched.index), side="left") - 1
    owner = pd.Series(idx[pos], index=sched.index)
    combined = sched.groupby(owner).apply(lambda g: " + ".join(sorted(set(g))))
    holiday = combined.reindex(ev.index)
    return ev, holiday, unsched


def main(market="US"):
    M = MARKETS[market]
    TRIAL_START, TRIAL_END = M["trial_start"], M["trial_end"]
    LEGIB_START, LEGIB_END = M["legib_start"], M["legib_end"]
    HALF_SPLIT, YEAR_END = M["half_split"], M["year_end"]
    EXCLUSION_TRIPWIRE, CAL, RESERVED = M["tripwire"], M["calendar"], M["reserved"]
    os.makedirs(OUT_DIR, exist_ok=True)
    prices = pd.read_csv(os.path.join(HERE, "Data", M["price_file"]),
                         parse_dates=["date"]).set_index("date")["close"].sort_index()

    line("=")
    print(f"{M['trial']}  THE PRE-HOLIDAY EFFECT -- {market} ({M['index']}), {CAL} HOLIDAY CALENDAR")
    print(f"spec: {SPEC[market]} (committed before this run)")
    line("=")
    print(f"  series        {M['index']} daily close, {prices.index[0].date()} -> {prices.index[-1].date()}, "
          f"{len(prices):,} sessions")
    print(f"  trial sample  {TRIAL_START} -> {TRIAL_END}")
    print(f"  legibility    {LEGIB_START or '--'} -> {LEGIB_END or '--'}   ({M['legib_note']})")
    print(f"  {RESERVED}")
    print(f"  gate          one-sided p < {GATE_P} AND the gap positive in BOTH halves")

    # ---------------------------------------------------------------- event identification
    ev, holiday, unsched = build_events(prices, TRIAL_START, TRIAL_END, CAL)
    ev_all = ev                       # every pre-holiday session, before any spec exclusion
    n_before = len(ev)
    if M.get("exclude"):
        drop = holiday.map(lambda h: bool(set(str(h).split(" + ")) & set(M["exclude"])))
        ev, holiday = ev[~drop], holiday[~drop]
    print()
    line()
    print("SECTION 2 -- EVENT IDENTIFICATION")
    line()
    idx_t = prices.loc[TRIAL_START:TRIAL_END].index
    missing = pd.bdate_range(idx_t[0], idx_t[-1]).difference(idx_t)
    print(f"  weekdays absent from the index      {len(missing):>4d}   "
          f"({len(missing)/((idx_t[-1]-idx_t[0]).days/365.25):.1f} per year)")
    print(f"  classified as scheduled holidays    {len(missing)-len(unsched):>4d}")
    print(f"  UNSCHEDULED, excluded               {len(unsched):>4d}   (tripwire: > {EXCLUSION_TRIPWIRE} means the classifier is wrong)")
    print(f"  pre-holiday event sessions          {len(ev):>4d}   (after de-duplicating shared sessions)")
    if M.get("exclude"):
        print(f"  EXCLUDED by spec section 1          {n_before-len(ev):>4d}   "
              f"(label names {' or '.join(M['exclude'])}; {n_before} -> {len(ev)})")
    print()
    print("  the exclusion list in full -- the run is not reportable without it:")
    for d in unsched:
        print(f"    {d.date()}  {d.day_name()[:3]}")
    if len(unsched) > EXCLUSION_TRIPWIRE:
        print()
        print(f"  *** TRIPWIRE: {len(unsched)} unscheduled closures exceeds {EXCLUSION_TRIPWIRE}. Per the")
        print("      pre-registration this is a harness bug, not a market fact. FIX BEFORE READING ON.")

    # ---------------------------------------------------------------- the trial
    r_all = prices.pct_change()
    sample = r_all.loc[TRIAL_START:TRIAL_END].dropna()
    is_ev = sample.index.isin(ev.index)
    is_any_ev = sample.index.isin(ev_all.index)
    x, y = sample[is_ev].to_numpy(), sample[~is_any_ev].to_numpy()

    print()
    line()
    print("SECTION 3/4 -- THE TRIAL")
    line()
    n_holidays = len(core.HOLIDAY_CALENDARS[CAL](2024))
    main_res = one_sided_greater(x, y)
    report("all holidays in the set", main_res)

    # placebo cross-check, section 3
    obs = float(np.mean(x))
    placebo = core.placebo_window_means(prices.loc[TRIAL_START:TRIAL_END], len(x), (0, 0),
                                        n_draws=N_DRAWS, seed=SEED)
    p_plac = core.placebo_pvalue(obs, placebo, alternative="greater")
    main_res["p_placebo"] = p_plac        # the conservative leg; the article quotes it
    ratio = max(p_plac, main_res["p"]) / max(min(p_plac, main_res["p"]), 1e-12)
    print(f"  {'placebo cross-check':<34s} p {p_plac:.4f}   (Welch p {main_res['p']:.4f}, "
          f"ratio {ratio:.2f}{'  -- DISAGREE, investigate before reporting' if ratio > 2 else '  -- agree'})")

    # halves
    print()
    halves = {}
    h1 = f"half 1  {TRIAL_START[:4]}-2004"
    h2 = f"half 2  2005-{TRIAL_END[:4]}"
    for tag, lo, hi in [(h1, TRIAL_START, "2004-12-31"), (h2, HALF_SPLIT, TRIAL_END)]:
        s = r_all.loc[lo:hi].dropna()
        m = s.index.isin(ev.index)
        ma = s.index.isin(ev_all.index)
        halves[tag] = one_sided_greater(s[m].to_numpy(), s[~ma].to_numpy())
        report(tag, halves[tag])

    # ---------------------------------------------------------------- the overlap rule
    print()
    line()
    print("SECTION 4 -- THE PRE-COMMITTED OVERLAP RULE (reported, not a second gate)")
    line()
    # a label can name two holidays ("Boxing Day + Christmas Day"); the session is year-end
    # if ANY component is, or the overlap rule would quietly keep Christmas Eve in the set
    is_year_end = holiday.map(lambda h: bool(set(str(h).split(" + ")) & set(YEAR_END)))
    ev7 = ev[~is_year_end]
    is7 = sample.index.isin(ev7.index)
    seven = one_sided_greater(sample[is7].to_numpy(), sample[~is_any_ev].to_numpy())
    report(f"{n_holidays-len(YEAR_END)} holidays (no year-end)", seven)
    print(f"  removed {len(ev)-len(ev7)} year-end events ({', '.join(YEAR_END)})")

    # ---------------------------------------------------------------- diagnostics
    print()
    line()
    print("REPORTED, NOT GATED")
    line()
    per = []
    for name in sorted(set(holiday)):
        d = sample[sample.index.isin(ev[holiday == name].index)]
        per.append({"holiday": name, "n": len(d), "mean_pct": d.mean() * 100,
                    "median_pct": d.median() * 100, "share_up": (d > 0).mean()})
    per_df = pd.DataFrame(per).sort_values("mean_pct", ascending=False)
    print("  per holiday:")
    for _, q in per_df.iterrows():
        print(f"    {q['holiday']:<28s} n {int(q['n']):>3d}   mean {q['mean_pct']:+.4f}%   "
              f"median {q['median_pct']:+.4f}%   up {q['share_up']*100:.0f}%")

    dow = pd.DataFrame({
        "event_days": pd.Series(ev.index.day_name()).value_counts(),
        "all_days_mean_pct": sample.groupby(sample.index.day_name()).mean() * 100,
    })
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    print()
    print("  day-of-week (the event set is NOT a random draw from the week):")
    for d in order:
        n = int(dow["event_days"].get(d, 0))
        print(f"    {d:<10s} events {n:>3d}   all-day mean {dow['all_days_mean_pct'].get(d, np.nan):+.4f}%")

    # ---------------------------------------------------------------- legibility
    legib = None
    if LEGIB_START:
        ev_l, hol_l, unsched_l = build_events(prices, LEGIB_START, LEGIB_END, CAL)
        s_l = r_all.loc[LEGIB_START:LEGIB_END].dropna()
        m_l = s_l.index.isin(ev_l.index)
        legib = one_sided_greater(s_l[m_l].to_numpy(), s_l[~m_l].to_numpy())
        print()
        line()
        print(f"LEGIBILITY CHECK -- {LEGIB_START[:4]}-{LEGIB_END[:4]} ({M['legib_note']})")
        line()
        report(f"{LEGIB_START[:4]}-{LEGIB_END[:4]}", legib)
        print(f"  {len(unsched_l)} unscheduled closures excluded in this window")
        print(f"  pre-holiday mean is {legib['mean_x']/legib['mean_y']:.1f}x the ordinary day "
              f"(CANDIDATES.md records Ariel at ~10x)")
        print(f"  expectation stated before the run: t above {M['legib_min_t']}. "
              f"{'HOLDS' if legib['t'] > M['legib_min_t'] else 'DOES NOT HOLD -- event identification is suspect'}")
    else:
        print()
        line()
        print("STRUCTURAL LEGIBILITY CHECK -- no pre-publication window exists for this market")
        line()
        per_year = len(ev) / ((idx_t[-1] - idx_t[0]).days / 365.25)
        n_named = len(set(holiday))
        print(f"  scheduled holidays found per year   {per_year:.1f}   "
              f"(the calendar defines {len(core.HOLIDAY_CALENDARS[CAL](2024))})")
        print(f"  distinct holidays actually matched  {n_named}")
        print("  every ad-hoc closure must appear in the exclusion list above, not in the")
        print("  event set; check the known royal dates are there before reading the verdict.")

    # ---------------------------------------------------------------- verdict
    both_pos = halves[h1]["diff"] > 0 and halves[h2]["diff"] > 0
    both_legs = M.get("both_legs", False)
    welch_ok, plac_ok = main_res["p"] < GATE_P, p_plac < GATE_P
    passed = (welch_ok and plac_ok if both_legs else welch_ok) and both_pos
    print()
    line("=")
    print("VERDICT")
    line("=")
    print(f"  Welch   one-sided p {main_res['p']:.4f}  vs gate {GATE_P}   "
          f"{'PASS' if welch_ok else 'FAIL'}")
    if both_legs:
        print(f"  placebo one-sided p {p_plac:.4f}  vs gate {GATE_P}   "
              f"{'PASS' if plac_ok else 'FAIL'}   <- spec section 2 requires BOTH")
    print(f"  gap positive in both halves: {both_pos}                  "
          f"{'PASS' if both_pos else 'FAIL'}")
    print(f"  => {M['trial']} {'PASSES' if passed else 'FAILS'}")
    if passed:
        if seven["p"] > 0.10 or seven["diff"] < 0:
            print("  OVERLAP RULE FIRES: the non-year-end subset does not hold, so this pass is")
            print("  recorded as the TURN-OF-YEAR window. No general pre-holiday claim is made.")
        else:
            print("  the non-year-end subset holds, so the pass is not merely the turn-of-year window")
    else:
        # name the leg that actually bound, not the one that happened to be printed first
        if both_legs and not plac_ok:
            uncond_se = sample.std(ddof=1) / np.sqrt(len(x))
            need = stats.norm.isf(GATE_P) * uncond_se
            print(f"  the BINDING leg was the placebo: it needed a gap of {need*100:+.4f} pts "
                  f"on the unconditional sd; observed {main_res['diff']*100:+.4f} pts")
            print(f"  (Welch cleared at {main_res['p']:.4f} only because pre-holiday sessions are "
                  f"quieter -- sd {x.std(ddof=1)*100:.4f}% vs {y.std(ddof=1)*100:.4f}%)")
        else:
            need = stats.t.isf(GATE_P, main_res["dof"]) * (main_res["diff"] / main_res["t"])
            print(f"  the gap needed to clear the gate was {need*100:+.4f} pts; observed "
                  f"{main_res['diff']*100:+.4f} pts")

    # ---------------------------------------------------------------- artefacts
    per_df.to_csv(os.path.join(OUT_DIR, f"preholiday_by_holiday_{market.lower()}.csv"), index=False)
    pd.DataFrame({"event_session": ev.index, "closure": ev.values,
                  "holiday": holiday.values,
                  "ret": sample.reindex(ev.index).values}).to_csv(
        os.path.join(OUT_DIR, f"preholiday_events_{market.lower()}.csv"), index=False)
    pd.Series(unsched, name="unscheduled_closure").to_csv(
        os.path.join(OUT_DIR, f"preholiday_exclusions_{market.lower()}.csv"), index=False)
    pd.DataFrame([{"scope": k, **v} for k, v in
                  [("all holidays in the set", main_res), (f"{n_holidays-len(YEAR_END)} holidays, no year-end", seven),
                   (h1.strip(), halves[h1]), (h2.strip(), halves[h2])] +
                  ([("legibility", legib)] if legib else [])]).to_csv(
        os.path.join(OUT_DIR, f"preholiday_stats_{market.lower()}.csv"), index=False)
    print()
    print(f"  wrote 4 files to {OUT_DIR}")
    line("=")


SPEC = {"US": "PREREGISTRATION_PREHOLIDAY_2026-09-19.md",
        "UK": "PREREGISTRATION_PREHOLIDAY_FTSE_2026-09-19.md",
        "UK_NOGF": "PREREGISTRATION_PREHOLIDAY_NOGF_2026-09-19.md"}

if __name__ == "__main__":
    main(sys.argv[1].upper() if len(sys.argv) > 1 else "US")
