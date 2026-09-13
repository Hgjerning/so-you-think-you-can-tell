# Pre-registration: post-filing earnings drift on the point-in-time S&P 500 (Sharadar)

**Written 2026-09-13, before any number was computed. Committed before running. Trial P3-11.**
Henrik: "run the pead on sharadar". The data verdict of `CANDIDATES.md` §B applies: Sharadar's
`date` is the 10-Q/10-K **filing** date, a median 36 days after the period end and typically one
to three weeks after the earnings press release. So this is not the Bernard–Thomas announcement
study. It is the nearest thing the data supports honestly: **does the market keep drifting in the
direction of the earnings surprise after the filing that follows the announcement?**

## 1. Data — fixed (inventory 2026-09-13)

- **Fundamentals:** `Project2/reporting/sharadar_cache/us_fundamentals.csv`, dimension ARQ, 814
  tickers, 2010-01 → 2026-09. Point in time by `date` (filing date). Duplicate (ticker,
  reportperiod) rows reduced to the **first** filing (44,816 → 44,521). EPS field: `epsdil`
  (0.7% null). Quarter spacing is 87–98 days for 98% of rows, so "four quarters earlier" is
  matched by date, 350–380 days before.
- **Prices:** `Project2/reporting/sharadar_cache/us_master_universe_prices.csv`, Sharadar SEP
  adjusted close, 803 tickers, 2012-01-03 → 2026-09-11. Twenty fundamentals tickers have no
  price column and are dropped.
- **Market:** SPY total-return adjusted close (Yahoo, `Data/SPY_daily_adjclose.csv`).
- **Membership gate:** `Project2/archive/sharadar_sp500_full_history.csv` (667 add/remove
  events 2010-01-29 → 2026-08-28 plus the 503 current constituents). A filing counts only if
  the ticker was an S&P 500 member **on the filing date**, reconstructed from the events.
  Tickers with no events and not current are never members here and are excluded.
- **Event sample:** filings with `date` from **2013-01-02** (so a 250-day estimation window
  exists) to **2026-06-01** (so day +60 exists), with a defined SUE and membership on the day.

## 2. Surprise and deciles — fixed

- **SUE (seasonal random walk):** surprise = EPS − EPS of the report period 350–380 days
  earlier; SUE = surprise / standard deviation of the previous eight surprises (at least six).
  All inputs are earlier report periods, whose filings precede this one, so nothing is used
  before it was filed. No analyst data (Sharadar has none; ART's consensus is annual only).
- **Deciles:** SUE ranked into ten equal groups **within each calendar quarter of filing
  date**, so a quarter with generally good news does not fill the top decile.

## 3. Abnormal returns — fixed (`eventstudies/firm.py`, tests in `tests/test_firm.py`)

Market model on trading days [−250, −31] relative to day 0 (at least 120 paired
observations), day 0 = first trading day on or after the filing date. Abnormal returns on
[−30, +60]. CAR over inclusive windows, NaN if any day is missing.

## 4. Legibility check — recorded, not a trial, must pass for P3-11 to be readable

**CAR[−30, −1], decile 10 minus decile 1, must be positive with BMP t > 3.** The press
release sits inside this window for nearly every filing; if the top surprise decile has not
outperformed the bottom one in the month before the filing, the event date or the SUE is
broken and P3-11 is reported as **uninterpretable** (and still counted). This decides
whether the trial can be read, not whether anything works, on the same footing as the ART
closed-book check in `ART_TRIAL_BUDGET.md`.

## 5. P3-11 hypothesis, statistic, gate — fixed and binding

**Hypothesis:** after the filing, the top SUE decile continues to outperform the bottom decile.

**Primary statistic:** the **calendar-time portfolio** long decile 10 and short decile 1, each
event held from day **+2 through +60** (day 0 and +1 excluded so the filing-day reaction is not
in the drift), equal weight per event, dollar-neutral, gross exposure 1. Its daily return is
regressed on SPY's excess return (market model; constant = alpha) with Newey–West t, 5 lags,
over the full sample 2013–2026. This is the estimator that survives overlapping events and
clustered filing dates (Fama 1998).

**Gate:** alpha's **one-sided p < 0.025 (t > 1.96) AND alpha positive in both halves**,
2013-01 → 2019-12 and 2020-01 → 2026-08.

Reported, not gated: mean CAR[−30,−1], CAR[0,+1] and CAR[+2,+60] by decile with BMP t per
decile; the decile-10-minus-decile-1 CAR[+2,+60] with a Welch t on standardized CARs; the
long-only decile-10 calendar-time alpha; event counts and dropped-event reasons; the same
numbers without the membership gate (to show what survivorship-free gating costs).

**No second holding window, no other surprise definition, no other universe after seeing the
data.** A drift that "shows up at +2 to +20" is a new trial.

## 6. Expected outcomes, stated before running

- **Legibility: passes.** Decile 10 minus decile 1 CAR[−30,−1] between +3 and +7 points,
  BMP t well above 10. The announcement is in that window and SUE is a real surprise measure.
- **P3-11: fails.** Decile 10 minus decile 1 CAR[+2,+60] between −0.5 and +1.0 points;
  calendar-time alpha t between −0.5 and +1.5. Reasons: post-2012 S&P 500 constituents are
  the largest, most-covered stocks, where PEAD was already weak in the 2000s; the drift is
  measured from the filing, one to three weeks after the announcement, past the days where
  the literature finds most of it; and the seasonal-random-walk surprise is a coarse proxy
  for analyst-relative surprise.
- A pass would be the first firm-level event result in these projects and would go straight
  to a forward record (Project1's Saturday tracker pattern), not to capital.

## 7. Budget

One Project3 trial (P3-11). No ART data touched; the ART budget is unchanged at 11 of 20.
