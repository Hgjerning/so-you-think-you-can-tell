# -*- coding: utf-8 -*-
"""Firm-level event studies: abnormal returns around dated events across many stocks.

Written 2026-09-13 for the PEAD study. Companion to core.py (index-level, placebo inference).
Here the cross-section is large (tens of thousands of filings), so the classic machinery
applies: market-model abnormal returns from an estimation window, cumulative abnormal returns
over event windows, the Boehmer–Musumeci–Poulsen (1991) standardized cross-sectional t, and a
calendar-time portfolio for long-horizon drift (Fama 1998), which is what handles overlapping
events and clustered dates.

Conventions
-----------
* ``returns``: wide DataFrame of simple daily returns, DatetimeIndex (ascending trading days)
  x ticker. ``market``: Series on the same index.
* ``events``: DataFrame with ``ticker``, ``date`` and an ``event_id`` column (unique).
* Day 0 = the first trading day on or after the event date (searchsorted, side='left'). A
  filing made after the close therefore has its first possible reaction on day +1.
* Windows are inclusive and in trading days; the estimation window must end before the
  event window starts, and the code refuses overlap.
* Alignment is by index; a ticker with missing days contributes NaN on those days and the
  estimation uses only the days it has.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np
import pandas as pd


@dataclass
class EventPanel:
    ar: pd.DataFrame        # event_id x relative day, abnormal return
    sigma: pd.Series        # residual std in the estimation window
    n_est: pd.Series
    alpha: pd.Series
    beta: pd.Series
    events: pd.DataFrame    # events used, with pos
    dropped: pd.DataFrame   # event_id, reason

    @property
    def rel_days(self) -> np.ndarray:
        return self.ar.columns.to_numpy()


def align_positions(dates, index: pd.DatetimeIndex) -> np.ndarray:
    idx = pd.DatetimeIndex(index)
    d = pd.to_datetime(pd.Series(list(dates))).to_numpy(dtype="datetime64[ns]")
    pos = idx.searchsorted(d, side="left")
    return np.where(pos >= len(idx), -1, pos)


def abnormal_returns(returns: pd.DataFrame, market: pd.Series, events: pd.DataFrame,
                     est_window: Tuple[int, int] = (-250, -31), min_est: int = 120,
                     event_window: Tuple[int, int] = (-30, 60), model: str = "market") -> EventPanel:
    """Abnormal returns for every event.

    model="market":          AR = r - (a + b m), a and b fitted on the estimation window.
    model="market_adjusted": AR = r - m (a = 0, b = 1); sigma still from the estimation window.

    LESSON (P3-11, 2026-09-13): on events SORTED BY A FUNDAMENTAL CHANGE, the fitted intercept
    a differs systematically by group (top SUE decile +9.5%/yr, bottom −10%/yr on the prior
    year), and over a 60-day window that intercept alone manufactures a 4-point "reversal"
    that is not in the returns. For windows longer than a few days on sorted samples use
    model="market_adjusted" or the calendar-time portfolio; keep "market" for short windows.
    """
    e0, e1 = est_window; w0, w1 = event_window
    if e1 >= w0:
        raise ValueError("estimation window overlaps event window")
    if model not in ("market", "market_adjusted"):
        raise ValueError("model must be 'market' or 'market_adjusted'")
    market = market.reindex(returns.index)
    idx = returns.index; T = len(idx)
    R = returns.to_numpy(dtype=float); M = market.to_numpy(dtype=float)
    col_of = {t: i for i, t in enumerate(returns.columns)}
    ev = events.copy(); ev["pos"] = align_positions(ev["date"], idx)
    rel = np.arange(w0, w1 + 1); L = len(rel)
    ar_rows, used, dropped, sig, nest, al, be = [], [], [], [], [], [], []
    for row in ev.itertuples(index=False):
        p = int(row.pos)
        if row.ticker not in col_of:
            dropped.append((row.event_id, "ticker not in returns")); continue
        if p < 0:
            dropped.append((row.event_id, "after last trading day")); continue
        j = col_of[row.ticker]
        lo, hi = max(p + e0, 0), p + e1
        if hi < lo + min_est:
            dropped.append((row.event_id, "estimation window too short")); continue
        r, m = R[lo:hi + 1, j], M[lo:hi + 1]
        ok = ~(np.isnan(r) | np.isnan(m)); n = int(ok.sum())
        if n < min_est:
            dropped.append((row.event_id, f"{n} est obs < {min_est}")); continue
        r, m = r[ok], m[ok]
        if model == "market":
            mbar = m.mean(); ss = float(((m - mbar) ** 2).sum())
            b = float(((m - mbar) * (r - r.mean())).sum() / ss) if ss > 0 else 0.0
            a = float(r.mean() - b * mbar)
        else:
            a, b = 0.0, 1.0
        resid = r - (a + b * m)
        s = float(np.sqrt((resid ** 2).sum() / max(n - 2, 1)))
        out = np.full(L, np.nan)
        a0, a1 = max(p + w0, 0), min(p + w1, T - 1)
        if a1 >= a0:
            k0 = a0 - (p + w0)
            out[k0:k0 + (a1 - a0 + 1)] = R[a0:a1 + 1, j] - (a + b * M[a0:a1 + 1])
        ar_rows.append(out); used.append(row.event_id); sig.append(s); nest.append(n); al.append(a); be.append(b)
    ar = pd.DataFrame(np.array(ar_rows).reshape(len(used), L), index=pd.Index(used, name="event_id"), columns=rel)
    ev_used = ev.set_index("event_id").loc[used].reset_index()
    return EventPanel(ar=ar, sigma=pd.Series(sig, index=ar.index), n_est=pd.Series(nest, index=ar.index),
                      alpha=pd.Series(al, index=ar.index), beta=pd.Series(be, index=ar.index),
                      events=ev_used, dropped=pd.DataFrame(dropped, columns=["event_id", "reason"]))


def returns_on_own_calendar(panel: pd.DataFrame) -> pd.DataFrame:
    """Simple returns per stock computed over THAT STOCK'S trading days, then placed back on
    the panel's (union) calendar; days the stock does not trade are NaN, and the return across
    such a gap is kept on the next day the stock trades.

    LESSON (P3-12, 2026-09-13): ART's price panel spans three regional calendars, so a US stock
    is NaN on Tokyo-only trading days. ``panel.pct_change()`` on that grid makes the return
    NaN on the gap day AND on the day after it (its previous price is NaN), silently deleting
    ~7% of every American stock's returns. Use this instead for any multi-calendar panel."""
    out = {}
    for c in panel.columns:
        s = panel[c].dropna()
        out[c] = s.pct_change()
    return pd.DataFrame(out).reindex(panel.index)


def car(panel: EventPanel, window: Tuple[int, int], min_coverage: Optional[float] = None) -> pd.Series:
    """CAR over an inclusive window. Default: NaN if any day inside the window is missing.
    With ``min_coverage`` (e.g. 0.9): the sum of the available days, NaN only when fewer than
    that share of the window's days carry an abnormal return — for panels on a union calendar
    where a stock's own holidays are NaN by construction (see returns_on_own_calendar)."""
    a, b = window
    cols = [d for d in panel.rel_days if a <= d <= b]
    if len(cols) != b - a + 1:
        raise ValueError("window outside the panel")
    block = panel.ar[cols]
    if min_coverage is None:
        return block.sum(axis=1, skipna=False).rename(f"CAR[{a},{b}]")
    cov = block.notna().mean(axis=1)
    return block.sum(axis=1, skipna=True).where(cov >= min_coverage).rename(f"CAR[{a},{b}]")


def bmp_test(panel: EventPanel, window: Tuple[int, int], mask: Optional[pd.Series] = None,
             min_coverage: Optional[float] = None) -> dict:
    """BMP (1991) t on standardized CARs, SCAR_i = CAR_i / (sigma_i * sqrt(L)). Robust to
    event-induced variance, not to cross-sectional correlation (use the calendar-time
    portfolio for that)."""
    a, b = window; L = b - a + 1
    c = car(panel, window, min_coverage)
    if mask is not None:
        c = c[mask.reindex(c.index).fillna(False).astype(bool)]
    s = (c / (panel.sigma.reindex(c.index) * np.sqrt(L))).dropna()
    n = len(s)
    if n < 3:
        return {"n": n, "mean_car": np.nan, "t_bmp": np.nan}
    return {"n": n, "mean_car": float(c.dropna().mean()), "t_bmp": float(s.mean() / (s.std(ddof=1) / np.sqrt(n)))}


def calendar_time_portfolio(returns: pd.DataFrame, events: pd.DataFrame, holding: Tuple[int, int],
                            weights: Optional[pd.Series] = None) -> pd.Series:
    """Daily return of an equal-weight (or ``weights``-signed) portfolio holding each event's
    ticker from relative day holding[0] through holding[1]. Long-short when weights carry
    signs: the result is sum(w r)/sum(|w|) per day. Days with nothing held are NaN.
    No look-ahead: a holding that starts at +2 contributes day +2's return first (tested)."""
    h0, h1 = holding
    idx = returns.index; T = len(idx)
    ev = events.copy(); ev["pos"] = align_positions(ev["date"], idx); ev = ev[ev["pos"] >= 0]
    w = pd.Series(1.0, index=ev.index) if weights is None else pd.Series(weights).reindex(ev.index).fillna(0.0)
    R = returns.to_numpy(dtype=float); col_of = {t: i for i, t in enumerate(returns.columns)}
    num = np.zeros(T); den = np.zeros(T)
    for row, wt in zip(ev.itertuples(index=False), w.to_numpy()):
        if row.ticker not in col_of or wt == 0:
            continue
        j = col_of[row.ticker]; lo, hi = row.pos + h0, min(row.pos + h1, T - 1)
        if lo > hi:
            continue
        r = R[lo:hi + 1, j]; ok = ~np.isnan(r)
        seg_n = num[lo:hi + 1]; seg_d = den[lo:hi + 1]
        seg_n[ok] += wt * r[ok]; seg_d[ok] += abs(wt)
    out = np.where(den > 0, num / np.where(den > 0, den, 1.0), np.nan)
    return pd.Series(out, index=idx, name=f"calendar_time[{h0},{h1}]")


def newey_west_alpha(y: pd.Series, x: Optional[pd.DataFrame] = None, lags: int = 5) -> dict:
    """OLS of y on a constant (and x) with Newey–West (Bartlett) errors. NaN rows dropped."""
    df = pd.DataFrame({"y": y})
    if x is not None:
        df = df.join(pd.DataFrame(x), how="left")
    df = df.dropna(); n = len(df)
    if n < 30:
        return {"alpha": np.nan, "t": np.nan, "n": n}
    Y = df["y"].to_numpy(dtype=float)
    X = np.column_stack([np.ones(n)] + [df[c].to_numpy(dtype=float) for c in df.columns if c != "y"])
    XtX_inv = np.linalg.pinv(X.T @ X); b = XtX_inv @ X.T @ Y; u = Y - X @ b
    Xu = X * u[:, None]; S = Xu.T @ Xu
    for l in range(1, lags + 1):
        G = Xu[l:].T @ Xu[:-l]; S += (1 - l / (lags + 1)) * (G + G.T)
    V = XtX_inv @ S @ XtX_inv; se = float(np.sqrt(max(V[0, 0], 0)))
    return {"alpha": float(b[0]), "t": float(b[0] / se) if se > 0 else np.nan, "n": n, "betas": [float(v) for v in b[1:]]}


def sue_seasonal_random_walk(fund: pd.DataFrame, eps_col: str = "epsdil", min_hist: int = 6, hist: int = 8) -> pd.DataFrame:
    """Standardized unexpected earnings, Bernard–Thomas seasonal random walk: for each
    (ticker, reportperiod), surprise = EPS - EPS four quarters earlier (matched by date, the
    record whose reportperiod is 350–380 days before), scaled by the standard deviation of the
    prior ``hist`` surprises (at least ``min_hist``). Uses only records filed before the
    event's own filing date: the scale is built from earlier reportperiods, whose filings
    precede this one. Returns fund with ``surprise`` and ``sue`` columns."""
    f = fund.sort_values(["ticker", "reportperiod", "date"]).drop_duplicates(["ticker", "reportperiod"], keep="first").copy()
    out = []
    for t, g in f.groupby("ticker", sort=False):
        g = g.reset_index(drop=True)
        rp = g["reportperiod"].to_numpy(dtype="datetime64[D]"); eps = g[eps_col].to_numpy(dtype=float)
        surprise = np.full(len(g), np.nan)
        for i in range(len(g)):
            lag = rp[i] - np.timedelta64(365, "D")
            k = np.where((rp >= lag - np.timedelta64(15, "D")) & (rp <= lag + np.timedelta64(15, "D")))[0]
            if len(k) and not np.isnan(eps[i]) and not np.isnan(eps[k[0]]):
                surprise[i] = eps[i] - eps[k[0]]
        sue = np.full(len(g), np.nan)
        for i in range(len(g)):
            prev = surprise[max(0, i - hist):i]; prev = prev[~np.isnan(prev)]
            if len(prev) >= min_hist and not np.isnan(surprise[i]) and prev.std(ddof=1) > 0:
                sue[i] = surprise[i] / prev.std(ddof=1)
        g["surprise"] = surprise; g["sue"] = sue; out.append(g)
    return pd.concat(out, ignore_index=True)
