# -*- coding: utf-8 -*-
"""Index-level event studies with placebo inference.

Written 2026-09-13 for Project3 Event Driven Strategies. The events here are few (25 US presidential
elections, 24 midterms, one Sell-in-May observation per year), so the usual cross-sectional
t-statistics of firm-level event studies have nothing to stand on. Every test in this module
is therefore judged against a PLACEBO distribution: the same statistic computed on the same
number of randomly placed windows drawn from the same price history. That is what removes
the market's unconditional drift from a "stocks rise after X" claim -- stocks rise after
most things.

Conventions
-----------
* ``prices`` is a Series of index closes on a DatetimeIndex of trading days, ascending.
* Day 0 of an event is the first trading day ON OR AFTER the event date
  (`align_dates`, searchsorted side='left'). An election day is a trading day and its
  result is known after the close, so a post-election window starts at +1.
* A window (a, b) in trading days is the return from the close of day a-1 to the close
  of day b, inclusive of both a and b:  P[p+b] / P[p+a-1] - 1.
* Alignment is by index, never by position in a list of dates.
* No function here fetches data or decides a verdict.
"""
from __future__ import annotations

from typing import Iterable, Optional, Tuple

import numpy as np
import pandas as pd


# ----------------------------------------------------------------------------- calendar

def us_election_day(year: int) -> pd.Timestamp:
    """First Tuesday after the first Monday of November (US federal elections since 1845)."""
    nov1 = pd.Timestamp(year=year, month=11, day=1)
    first_monday = nov1 + pd.Timedelta(days=(7 - nov1.weekday()) % 7)
    return first_monday + pd.Timedelta(days=1)


def us_election_dates(start_year: int, end_year: int, kind: str = "presidential") -> pd.Series:
    """kind='presidential' -> years divisible by 4; 'midterm' -> even years not divisible by 4."""
    if kind == "presidential":
        years = [y for y in range(start_year, end_year + 1) if y % 4 == 0]
    elif kind == "midterm":
        years = [y for y in range(start_year, end_year + 1) if y % 2 == 0 and y % 4 != 0]
    else:
        raise ValueError("kind must be 'presidential' or 'midterm'")
    return pd.Series([us_election_day(y) for y in years], index=pd.Index(years, name="year"), name="date")


# ----------------------------------------------------------------------------- alignment

def align_dates(event_dates: Iterable, index: pd.DatetimeIndex) -> np.ndarray:
    """Position of the first trading day on or after each event date; -1 if beyond the end."""
    idx = pd.DatetimeIndex(index)
    if not idx.is_monotonic_increasing:
        raise ValueError("index must be ascending")
    d = pd.to_datetime(pd.Series(list(event_dates))).to_numpy(dtype="datetime64[ns]")
    pos = idx.searchsorted(d, side="left")
    return np.where(pos >= len(idx), -1, pos)


def _window_return_at(P: np.ndarray, pos: np.ndarray, a: int, b: int) -> np.ndarray:
    """Return from close[pos+a-1] to close[pos+b]; NaN where the window does not fit."""
    T = len(P)
    lo, hi = pos + a - 1, pos + b
    ok = (pos >= 0) & (lo >= 0) & (hi < T)
    out = np.full(len(pos), np.nan)
    out[ok] = P[hi[ok]] / P[lo[ok]] - 1.0
    return out


def window_returns(prices: pd.Series, event_dates: Iterable, window: Tuple[int, int]) -> pd.Series:
    """Per-event return over ``window`` (see module conventions). Index = the event dates."""
    a, b = window
    dates = pd.to_datetime(pd.Series(list(event_dates)))
    pos = align_dates(dates, prices.index)
    r = _window_return_at(prices.to_numpy(dtype=float), pos, a, b)
    return pd.Series(r, index=pd.DatetimeIndex(dates), name=f"ret[{a},{b}]")


def event_paths(prices: pd.Series, event_dates: Iterable, pre: int, post: int) -> pd.DataFrame:
    """Cumulative return path per event, columns = relative trading days -pre..post,
    base = close of day -pre-1 (so the path is comparable across events). NaN where the
    window does not fit inside the data."""
    P = prices.to_numpy(dtype=float)
    dates = pd.to_datetime(pd.Series(list(event_dates)))
    pos = align_dates(dates, prices.index)
    rel = np.arange(-pre, post + 1)
    rows = []
    for p in pos:
        base = p - pre - 1
        if p < 0 or base < 0 or p + post >= len(P):
            rows.append(np.full(len(rel), np.nan)); continue
        rows.append(P[p - pre: p + post + 1] / P[base] - 1.0)
    return pd.DataFrame(np.array(rows).reshape(len(pos), len(rel)), index=pd.DatetimeIndex(dates), columns=rel)


# ----------------------------------------------------------------------------- placebo inference

def placebo_window_means(prices: pd.Series, n_events: int, window: Tuple[int, int],
                         n_draws: int = 10000, seed: int = 42,
                         positions_pool: Optional[np.ndarray] = None) -> np.ndarray:
    """Distribution of the MEAN window return over ``n_events`` randomly placed events.

    Positions are drawn uniformly (with replacement) from every trading day at which the
    window fits, or from ``positions_pool`` when given (e.g. only Novembers, to test an
    election effect against same-season placebos). Deterministic under ``seed``."""
    a, b = window
    P = prices.to_numpy(dtype=float)
    T = len(P)
    if positions_pool is None:
        pool = np.arange(max(1 - a, 0), T - b)
    else:
        pool = np.asarray(positions_pool)
        pool = pool[(pool + a - 1 >= 0) & (pool + b < T)]
    if len(pool) == 0:
        raise ValueError("no trading day fits the window")
    rng = np.random.default_rng(seed)
    draws = rng.choice(pool, size=(n_draws, n_events), replace=True)
    r = P[draws + b] / P[draws + a - 1] - 1.0
    return r.mean(axis=1)


def placebo_path_band(prices: pd.Series, n_events: int, pre: int, post: int,
                      n_draws: int = 2000, seed: int = 42,
                      quantiles: Tuple[float, ...] = (0.05, 0.10, 0.50, 0.90, 0.95)) -> pd.DataFrame:
    """Quantiles, per relative day, of the MEAN path over ``n_events`` random events. This
    is the band an event-path chart should carry: the band of averages, not of single
    events, and drawn from unconditional history rather than from the events themselves."""
    P = prices.to_numpy(dtype=float)
    T = len(P)
    pool = np.arange(pre + 1, T - post)
    rng = np.random.default_rng(seed)
    draws = rng.choice(pool, size=(n_draws, n_events), replace=True)
    rel = np.arange(-pre, post + 1)
    means = np.empty((n_draws, len(rel)))
    for k, d in enumerate(rel):
        means[:, k] = (P[draws + d] / P[draws - pre - 1] - 1.0).mean(axis=1)
    q = np.quantile(means, quantiles, axis=0)
    return pd.DataFrame(q.T, index=rel, columns=[f"q{int(round(x * 100)):02d}" for x in quantiles])


def placebo_pvalue(observed: float, placebo: np.ndarray, alternative: str = "two-sided") -> float:
    """Share of placebo draws at least as extreme as the observed statistic, measured
    around the placebo MEAN (so the test asks 'is this unusual relative to the
    unconditional drift', not 'is it different from zero'). Add-one correction."""
    p = np.asarray(placebo, dtype=float)
    c = p.mean()
    if alternative == "two-sided":
        k = np.sum(np.abs(p - c) >= abs(observed - c))
    elif alternative == "greater":
        k = np.sum((p - c) >= (observed - c))
    elif alternative == "less":
        k = np.sum((p - c) <= (observed - c))
    else:
        raise ValueError("alternative must be two-sided, greater or less")
    return float((k + 1) / (len(p) + 1))


def permutation_diff(values: pd.Series, labels: pd.Series, group_a, group_b,
                     n_perm: int = 10000, seed: int = 42) -> dict:
    """Difference of means (group_a - group_b) with a two-sided permutation p-value over
    label shuffles. NaN values are dropped first."""
    df = pd.DataFrame({"v": values, "g": labels}).dropna()
    df = df[df["g"].isin([group_a, group_b])]
    v = df["v"].to_numpy(dtype=float); g = df["g"].to_numpy()
    na, nb = int((g == group_a).sum()), int((g == group_b).sum())
    if na == 0 or nb == 0:
        return {"diff": np.nan, "p": np.nan, "n_a": na, "n_b": nb}
    obs = v[g == group_a].mean() - v[g == group_b].mean()
    rng = np.random.default_rng(seed)
    cnt = 0
    for _ in range(n_perm):
        perm = rng.permutation(v)
        d = perm[:na].mean() - perm[na:].mean()
        if abs(d) >= abs(obs):
            cnt += 1
    return {"diff": float(obs), "p": float((cnt + 1) / (n_perm + 1)), "n_a": na, "n_b": nb,
            "mean_a": float(v[g == group_a].mean()), "mean_b": float(v[g == group_b].mean())}


# ----------------------------------------------------------------------------- calendar effects

def monthly_returns(prices: pd.Series) -> pd.Series:
    """Month-end to month-end simple returns from daily closes (the first month is dropped)."""
    m = prices.resample("ME").last().dropna()
    return m.pct_change().dropna().rename("ret_m")


def welch_t(x: np.ndarray, y: np.ndarray) -> Tuple[float, float, float]:
    """Welch's t for mean(x) - mean(y); returns (diff, t, dof)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    nx, ny = len(x), len(y)
    vx, vy = x.var(ddof=1) / nx, y.var(ddof=1) / ny
    t = (x.mean() - y.mean()) / np.sqrt(vx + vy)
    dof = (vx + vy) ** 2 / (vx ** 2 / (nx - 1) + vy ** 2 / (ny - 1))
    return float(x.mean() - y.mean()), float(t), float(dof)


def calendar_month_table(monthly: pd.Series) -> pd.DataFrame:
    """Per calendar month: n, mean, mean of the other eleven, Welch t of the difference,
    two-sided p (normal approximation, dof > 60 throughout), and the Bonferroni-12 flag."""
    from math import erf, sqrt
    rows = []
    for m in range(1, 13):
        x = monthly[monthly.index.month == m].to_numpy()
        y = monthly[monthly.index.month != m].to_numpy()
        diff, t, dof = welch_t(x, y)
        p = 2 * (1 - 0.5 * (1 + erf(abs(t) / sqrt(2))))
        rows.append({"month": m, "n": len(x), "mean": x.mean(), "mean_other": y.mean(),
                     "diff": diff, "t": t, "p": p, "bonferroni12": p < 0.05 / 12})
    return pd.DataFrame(rows).set_index("month")


def sell_in_may_table(monthly: pd.Series) -> pd.DataFrame:
    """One row per calendar year y: summer = May..Oct of y (compounded), winter = Nov y ..
    Apr y+1 (compounded), diff = winter - summer. Years missing any month are dropped, so
    the rows are non-overlapping and a paired t on ``diff`` is valid."""
    g = (1 + monthly)
    rows = []
    years = sorted(set(monthly.index.year))
    for y in years:
        s = g[(g.index.year == y) & (g.index.month >= 5) & (g.index.month <= 10)]
        w = pd.concat([g[(g.index.year == y) & (g.index.month >= 11)],
                       g[(g.index.year == y + 1) & (g.index.month <= 4)]])
        if len(s) != 6 or len(w) != 6:
            continue
        rows.append({"year": y, "summer": s.prod() - 1, "winter": w.prod() - 1})
    df = pd.DataFrame(rows).set_index("year")
    df["diff"] = df["winter"] - df["summer"]
    return df


def paired_t(diff: pd.Series) -> dict:
    d = pd.Series(diff).dropna().to_numpy(dtype=float)
    n = len(d)
    if n < 3:
        return {"n": n, "mean": np.nan, "t": np.nan}
    return {"n": n, "mean": float(d.mean()), "t": float(d.mean() / (d.std(ddof=1) / np.sqrt(n)))}
