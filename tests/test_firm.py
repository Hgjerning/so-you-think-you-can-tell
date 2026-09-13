# -*- coding: utf-8 -*-
"""Tests for eventstudies.firm on synthetic data. Run: python tests/test_firm.py"""
import os
import sys
import traceback

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from eventstudies import firm  # noqa: E402


def _panel(n_days=1500, n_tk=40, seed=0, beta=1.0, ivol=0.015):
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2015-01-01", periods=n_days)
    m = pd.Series(rng.normal(0.0003, 0.01, n_days), index=idx, name="mkt")
    R = beta * m.to_numpy()[:, None] + rng.normal(0, ivol, (n_days, n_tk))
    return pd.DataFrame(R, index=idx, columns=[f"T{i}" for i in range(n_tk)]), m


def test_car_recovers_injected_effect_and_null_is_null():
    """Inject +3% on day +1 for 200 events: mean CAR[1,1] within 3% ± 0.5%, BMP t > 8.
    With nothing injected, |t_BMP| < 3 on CAR[2,60] (a loose null bound for one draw)."""
    ret, m = _panel(); rng = np.random.default_rng(1)
    ev = pd.DataFrame({"event_id": range(200), "ticker": rng.choice(ret.columns, 200), "date": ret.index[rng.integers(300, 1400, 200)]})
    ret2 = ret.copy()
    for r in ev.itertuples():
        p = ret.index.get_loc(r.date); ret2.iloc[p + 1, ret.columns.get_loc(r.ticker)] += 0.03
    pan = firm.abnormal_returns(ret2, m, ev)
    b = firm.bmp_test(pan, (1, 1)); assert abs(b["mean_car"] - 0.03) < 0.005 and b["t_bmp"] > 8, b
    pan0 = firm.abnormal_returns(ret, m, ev); b0 = firm.bmp_test(pan0, (2, 60)); assert abs(b0["t_bmp"]) < 3, b0


def test_intercept_bias_on_sorted_sample_and_market_adjusted_fix():
    """GUARD from P3-11: give half the tickers a +60%/yr drift that covers the whole estimation
    window and stops before the event window. The market model must then show a large spurious
    NEGATIVE CAR[2,60] for the drifting group (59 days of the extrapolated intercept, about
    −14 pts); market-adjusted returns must not. Tolerances fixed before running: market-model
    D_drift − D_flat < −8 pts; market-adjusted |D_drift − D_flat| < 1.5 pts. Idiosyncratic
    volatility is set low (0.2%/day) because the 400 events sit in a 33-day span, so their
    windows overlap and the effective sample is the 60 tickers, not the 400 events: at the
    default 1.5%/day the noise on the difference was ~3 pts and the second version of this
    test failed on noise (+4.5 pts) with the code correct. The first version used a +15%/yr
    drift half-covering the estimation window and could not tell bias from noise at all."""
    ret, m = _panel(n_days=1200, n_tk=60, seed=5, ivol=0.002); rng = np.random.default_rng(6)
    drift_cols = ret.columns[:30]
    ret.loc[ret.index[:1000], drift_cols] += 0.60 / 252          # drift only BEFORE the events
    dates = ret.index[rng.integers(998, 1031, 400)]               # est window inside the drift, event window outside
    ev = pd.DataFrame({"event_id": range(400), "ticker": rng.choice(ret.columns, 400), "date": dates})
    grp = ev["ticker"].isin(drift_cols).to_numpy()
    for model, lo, hi in [("market", -np.inf, -0.08), ("market_adjusted", -0.015, 0.015)]:
        pan = firm.abnormal_returns(ret, m, ev, model=model)
        c = firm.car(pan, (2, 60)); g = pd.Series(grp, index=ev["event_id"]).reindex(c.index)
        d = c[g].mean() - c[~g].mean()
        assert lo <= d <= hi, (model, d)


def test_returns_on_own_calendar_keep_the_return_across_a_gap():
    """GUARD from P3-12: a stock with prices 100, NaN, 110 on a three-day union calendar must
    have return NaN on day 2 and +10% on day 3. panel.pct_change() gives NaN on BOTH days,
    which is the bug that emptied the American CAR windows."""
    idx = pd.bdate_range("2020-01-01", periods=3)
    panel = pd.DataFrame({"A": [100.0, np.nan, 110.0], "B": [50.0, 55.0, 55.0]}, index=idx)
    r = firm.returns_on_own_calendar(panel)
    assert np.isnan(r["A"].iloc[1]) and abs(r["A"].iloc[2] - 0.10) < 1e-12
    assert abs(r["B"].iloc[1] - 0.10) < 1e-12 and r["B"].iloc[2] == 0.0
    naive = panel.pct_change(fill_method=None)
    assert np.isnan(naive["A"].iloc[2])   # the bug, demonstrated


def test_car_min_coverage():
    """With min_coverage, a window with one NaN day (of 59) is summed over the rest; a window
    with 20% NaN days is NaN; without it, any NaN day gives NaN."""
    ret, m = _panel(n_tk=2, ivol=0.001); ret[:] = 0.001
    ev = pd.DataFrame({"event_id": [0, 1], "ticker": ["T0", "T1"], "date": [ret.index[600]] * 2})
    ret.iloc[605, 0] = np.nan                       # one gap day for T0
    ret.iloc[602:614, 1] = np.nan                   # 12 gap days for T1 (20% of 59)
    pan = firm.abnormal_returns(ret, m, ev, model="market_adjusted")
    strict = firm.car(pan, (2, 60)); loose = firm.car(pan, (2, 60), 0.9)
    assert np.isnan(strict.loc[0]) and np.isnan(strict.loc[1])
    assert not np.isnan(loose.loc[0]) and np.isnan(loose.loc[1])


def test_estimation_window_never_overlaps_event_window():
    ret, m = _panel()
    ev = pd.DataFrame({"event_id": [0], "ticker": ["T0"], "date": [ret.index[500]]})
    try:
        firm.abnormal_returns(ret, m, ev, est_window=(-250, -10), event_window=(-30, 60)); raise AssertionError("overlap accepted")
    except ValueError:
        pass


def test_calendar_time_portfolio_no_lookahead_and_signs():
    """A return placed at day +1 must not enter a [2,60] portfolio; one at +2 must. A short
    weight flips the sign."""
    ret, m = _panel(n_tk=3); ret[:] = 0.0
    d = ret.index[600]; p = 600
    ret.iloc[p + 1, 0] = 0.10; ret.iloc[p + 2, 0] = 0.05
    ev = pd.DataFrame({"event_id": [0], "ticker": ["T0"], "date": [d]})
    ct = firm.calendar_time_portfolio(ret, ev, (2, 60))
    assert np.isnan(ct.iloc[p + 1]) and abs(ct.iloc[p + 2] - 0.05) < 1e-12
    ct2 = firm.calendar_time_portfolio(ret, ev, (2, 60), weights=pd.Series([-1.0]))
    assert abs(ct2.iloc[p + 2] + 0.05) < 1e-12


def test_newey_west_alpha_detects_drift():
    rng = np.random.default_rng(3); idx = pd.bdate_range("2015-01-01", periods=2000)
    y = pd.Series(rng.normal(0.0005, 0.01, 2000), index=idx)
    out = firm.newey_west_alpha(y); assert out["t"] > 1.5 and abs(out["alpha"] - 0.0005) < 0.0007
    y0 = pd.Series(rng.normal(0.0, 0.01, 2000), index=idx); assert abs(firm.newey_west_alpha(y0)["t"]) < 3


def test_sue_matches_four_quarters_back_and_uses_only_prior_history():
    """EPS grows by 1 per quarter: surprise = 4 everywhere once a match exists; SUE is NaN
    until 6 prior surprises exist and the scale is built from the PRIOR surprises only."""
    rp = pd.date_range("2010-03-31", periods=20, freq="QE")
    f = pd.DataFrame({"ticker": "A", "reportperiod": rp, "date": rp + pd.Timedelta(days=35), "epsdil": np.arange(20, dtype=float)})
    f.loc[19, "epsdil"] = 100.0  # a shock in the last quarter must not enter its own scale
    s = firm.sue_seasonal_random_walk(f)
    assert np.isnan(s.loc[3, "surprise"]) and s.loc[4, "surprise"] == 4.0
    assert np.isnan(s.loc[9, "sue"])  # only 6 prior surprises exist from index 4..9 -> at index 10
    prev = s.loc[4:9, "surprise"]; assert prev.std(ddof=1) == 0  # constant -> no scale -> NaN
    # make the history vary so a scale exists, then check the shock uses prior scale only
    # (first version of this test had eight identical prior surprises, so the scale was zero and
    # SUE correctly NaN -- the test data was wrong, not the code)
    f2 = f.copy(); f2["epsdil"] = np.array([0, 0, 0, 0, 1, 2, 1, 3, 2, 5, 1, 6, 4, 6, 3, 8, 5, 9, 4, 100], dtype=float)
    s2 = firm.sue_seasonal_random_walk(f2)
    assert not np.isnan(s2.loc[19, "sue"]) and s2.loc[19, "sue"] > 20
    # dedupe keeps the first filing per period
    f3 = pd.concat([f2, f2.iloc[[5]].assign(date=f2.loc[5, "date"] + pd.Timedelta(days=200), epsdil=99.0)])
    s3 = firm.sue_seasonal_random_walk(f3); assert (s3["ticker"] == "A").sum() == 20 and s3.loc[5, "epsdil"] == 2.0


if __name__ == "__main__":
    tests = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    for name, fn in tests:
        try:
            fn(); print(f"PASS {name}")
        except Exception:
            failed += 1; print(f"FAIL {name}"); traceback.print_exc()
    print(f"{len(tests) - failed} passed, {failed} failed"); sys.exit(1 if failed else 0)
