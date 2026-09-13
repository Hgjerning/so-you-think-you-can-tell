# -*- coding: utf-8 -*-
"""Tests for eventstudies.core -- every guard is proved by making it fail first.

Run either way:

    python tests/test_core.py            # no pytest needed
    python -m pytest tests/ -q           # if pytest is installed

Tolerances are written down BEFORE the numbers are looked at (see each docstring).
"""
import os
import sys
import traceback

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from eventstudies import core  # noqa: E402


def _synthetic_prices(n_days=6000, seed=0, drift=0.0003, vol=0.01):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("1990-01-01", periods=n_days)
    r = rng.normal(drift, vol, n_days)
    return pd.Series(100 * np.cumprod(1 + r), index=idx, name="close")


def test_election_day_rule():
    """Known dates: 1928-11-06, 2000-11-07, 2016-11-08, 2020-11-03, 2024-11-05; midterm 2022-11-08."""
    assert core.us_election_day(1928) == pd.Timestamp("1928-11-06")
    assert core.us_election_day(2000) == pd.Timestamp("2000-11-07")
    assert core.us_election_day(2016) == pd.Timestamp("2016-11-08")
    assert core.us_election_day(2020) == pd.Timestamp("2020-11-03")
    assert core.us_election_day(2024) == pd.Timestamp("2024-11-05")
    assert core.us_election_day(2022) == pd.Timestamp("2022-11-08")
    assert list(core.us_election_dates(2018, 2024, "midterm").index) == [2018, 2022]
    assert list(core.us_election_dates(2018, 2024, "presidential").index) == [2020, 2024]


def test_alignment_is_by_index_never_backwards():
    """A Saturday event maps to the following Monday; an event on a trading day maps to
    itself; an event after the last trading day is -1. Removing a trading day from the
    index must shift the mapped position by exactly one, never keep a stale position."""
    p = _synthetic_prices(300)
    sat = pd.Timestamp("1990-03-03")  # Saturday
    assert sat.weekday() == 5
    pos = core.align_dates([sat, pd.Timestamp("1990-03-05"), pd.Timestamp("2050-01-01")], p.index)
    assert p.index[pos[0]] == pd.Timestamp("1990-03-05")
    assert pos[0] == pos[1]
    assert pos[2] == -1
    p2 = p.drop(pd.Timestamp("1990-03-05"))
    pos2 = core.align_dates([sat], p2.index)
    assert p2.index[pos2[0]] == pd.Timestamp("1990-03-06")


def test_window_return_convention():
    """ret[a,b] = P[p+b]/P[p+a-1] - 1 by hand on a tiny series; a window that runs off
    the end is NaN, not truncated."""
    idx = pd.bdate_range("2020-01-01", periods=10)
    p = pd.Series(np.arange(1, 11, dtype=float), index=idx)
    r = core.window_returns(p, [idx[4]], (1, 3))
    assert abs(r.iloc[0] - (p.iloc[7] / p.iloc[4] - 1)) < 1e-12
    r0 = core.window_returns(p, [idx[4]], (0, 0))
    assert abs(r0.iloc[0] - (p.iloc[4] / p.iloc[3] - 1)) < 1e-12
    r_off = core.window_returns(p, [idx[8]], (1, 3))
    assert np.isnan(r_off.iloc[0])
    paths = core.event_paths(p, [idx[4]], pre=2, post=2)
    assert list(paths.columns) == [-2, -1, 0, 1, 2]
    assert abs(paths.iloc[0][2] - (p.iloc[6] / p.iloc[1] - 1)) < 1e-12


def test_placebo_null_rejection_rate():
    """GUARD: on a pure random walk with drift, random 'events' must NOT look special.
    Tolerance fixed before running: over 300 studies of 25 events each, the two-sided
    placebo p < 0.05 rate must lie in [0.02, 0.09] (binomial 2 s.d. around 0.05 is
    about +-0.025; the band is wider to keep the test from flapping)."""
    p = _synthetic_prices(8000, seed=1)
    rng = np.random.default_rng(7)
    pool = np.arange(100, len(p) - 100)
    plc = core.placebo_window_means(p, 25, (1, 60), n_draws=3000, seed=3)
    rejects = 0
    n_studies = 300
    for _ in range(n_studies):
        ev = p.index[rng.choice(pool, 25, replace=False)]
        obs = core.window_returns(p, ev, (1, 60)).mean()
        if core.placebo_pvalue(obs, plc) < 0.05:
            rejects += 1
    rate = rejects / n_studies
    assert 0.02 <= rate <= 0.09, f"null rejection rate {rate:.3f} outside [0.02, 0.09]"


def test_placebo_detects_injected_effect_and_drift_alone_does_not_fool_it():
    """Two halves of one guard. (1) Inject +4% spread over days +1..+20 after 25 events on
    a driftless walk: placebo p must be < 0.01. (2) On a walk with strong positive drift
    and NO injected effect, the raw mean post-event return is clearly positive but the
    placebo p must be > 0.05 -- the test must not credit unconditional drift to the
    event. Both were run first with the placebo centred at zero instead of at its mean,
    and (2) then failed, which is why placebo_pvalue centres on the placebo mean."""
    rng = np.random.default_rng(11)
    n = 6000
    idx = pd.bdate_range("1990-01-01", periods=n)
    r = rng.normal(0.0, 0.01, n)
    ev_pos = np.sort(rng.choice(np.arange(200, n - 200), 25, replace=False))
    for p0 in ev_pos:
        r[p0 + 1: p0 + 21] += 0.04 / 20
    p = pd.Series(100 * np.cumprod(1 + r), index=idx)
    obs = core.window_returns(p, idx[ev_pos], (1, 20)).mean()
    plc = core.placebo_window_means(p, 25, (1, 20), n_draws=4000, seed=5)
    assert core.placebo_pvalue(obs, plc) < 0.01

    # (2) as a RATE over 200 random event sets, not a single draw: the first version of
    # this test used one draw and failed on a 3-sigma event set (p 0.0027) while the
    # rate over 200 sets was 0.075 -- a single draw cannot distinguish a bug from luck.
    # Tolerance fixed before re-running: rejection rate in [0.02, 0.10].
    p_drift = _synthetic_prices(6000, seed=2, drift=0.0008, vol=0.008)
    plc2 = core.placebo_window_means(p_drift, 25, (1, 60), n_draws=4000, seed=5)
    assert plc2.mean() > 0.02, "drift sample should show a large unconditional 60-day return"
    rejects = 0
    for s in range(200):
        rs = np.random.default_rng(s)
        ev = p_drift.index[np.sort(rs.choice(np.arange(200, 5800), 25, replace=False))]
        obs2 = core.window_returns(p_drift, ev, (1, 60)).mean()
        if core.placebo_pvalue(obs2, plc2) < 0.05:
            rejects += 1
    rate = rejects / 200
    assert 0.02 <= rate <= 0.10, f"drift-only rejection rate {rate:.3f} outside [0.02, 0.10]"


def test_permutation_diff_null_and_signal():
    rng = np.random.default_rng(3)
    v = pd.Series(rng.normal(0, 1, 40))
    g = pd.Series(["D"] * 20 + ["R"] * 20)
    out = core.permutation_diff(v, g, "D", "R", n_perm=2000, seed=1)
    assert out["p"] > 0.05
    v2 = v.copy(); v2[:20] += 2.0
    out2 = core.permutation_diff(v2, g, "D", "R", n_perm=2000, seed=1)
    assert out2["p"] < 0.01 and out2["diff"] > 1.5


def test_sell_in_may_rows_are_non_overlapping_and_complete():
    """Winter y = Nov y..Apr y+1, summer y = May..Oct y; a year with a missing month is
    dropped rather than filled; the last incomplete winter is dropped."""
    idx = pd.date_range("2000-01-31", "2005-06-30", freq="ME")
    m = pd.Series(0.01, index=idx)
    tab = core.sell_in_may_table(m)
    assert list(tab.index) == [2000, 2001, 2002, 2003, 2004]
    assert abs(tab.loc[2000, "summer"] - (1.01 ** 6 - 1)) < 1e-12
    assert abs(tab.loc[2000, "winter"] - (1.01 ** 6 - 1)) < 1e-12
    m2 = m.drop(pd.Timestamp("2002-07-31"))
    assert 2002 not in core.sell_in_may_table(m2).index


def test_calendar_month_table_shape_and_bonferroni_flag():
    rng = np.random.default_rng(4)
    idx = pd.date_range("1950-01-31", "2020-12-31", freq="ME")
    m = pd.Series(rng.normal(0.005, 0.04, len(idx)), index=idx)
    tab = core.calendar_month_table(m)
    assert list(tab.index) == list(range(1, 13)) and not tab["bonferroni12"].any()
    m2 = m.copy(); m2[m2.index.month == 9] -= 0.05
    assert core.calendar_month_table(m2).loc[9, "bonferroni12"]


if __name__ == "__main__":
    tests = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for name, fn in tests:
        try:
            fn(); print(f"PASS {name}")
        except Exception:
            failed += 1; print(f"FAIL {name}"); traceback.print_exc()
    print(f"{len(tests) - failed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
