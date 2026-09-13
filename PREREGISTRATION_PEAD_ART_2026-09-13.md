# Pre-registration: post-earnings-announcement drift on ART, Global Developed 1997–2012

**Written 2026-09-13, before any number was computed. Trial P3-12 here and trial #12 of the
shared ART budget (`ClaudeCode/ART_TRIAL_BUDGET.md`). NOT RUN: ARTData is `RECOVERY_PENDING`
(the SQL service account `.\sqlsvc` has no stored SMB credential for `\\192.168.0.25`); the
script `run_pead_art.py` is written and will be run once, unchanged, when the database is
back.** Henrik: "run the pead on ART". His instruction is the written decision the ART budget
requires for a trial in a new family (earnings surprise), spending the 12th of 20 with the
warning line at 13.

## 1. Why ART for this and not Sharadar

The Sharadar trial (P3-11) could only date the 10-Q filing. ART's `IbesDataActualsPit` dates
the **announcement** (`RptDate`, the day IBES recorded the actual), covers Europe, America and
Asia from the 1990s, and is survivorship-free by construction. This is the sample on which the
literature's PEAD lived. It contains the two bear markets Project2's data lacks.

## 2. Data — fixed (schema from `Project1/InvestmentLibrary/art_pit.py`, verified live 2026-08-31)

- **Events:** `IbesDataActualsPit`, `Measure='EPS'`, `PerType='Q'`, one row per
  (StockId, PerDate) = the **earliest `RptDate`** (first-known vintage; later restatements are
  dropped, `get_pit_actuals` convention). Event date = `RptDate`. Sample: `RptDate` from
  **1997-01-02** (one year of quarterly history for the scale, and the 1996 factor-panel start)
  to **2012-12-31** (day +60 must exist before the 2013-04-08 price end).
- **Universe gate:** the stock is a member of **Global Developed** on `RptDate`
  (`UniversesEntry` with `Date_ <= RptDate < ToDate`). Region from `AllStocks.RegionId`
  (2 Asia, 3 Europe, 4 America), reported per region.
- **Prices:** `PriceData.TotRet` (total-return index), `DeletedAt IS NULL`, daily simple returns
  from consecutive `TotRet` levels; a return whose absolute value exceeds 100% is set to NaN
  (the known >100% weekly prints; `art-pit-database` memory). Loaded once per stock set and
  cached to `Data/art_cache/` (gitignored).
- **Market:** the equal-weighted mean daily return of the event stocks **in the same region**,
  computed from the same panel. No index series is used.

## 3. Surprise and deciles — fixed, identical in form to P3-11

SUE (seasonal random walk): surprise = Actual − Actual of the PerDate 350–380 days earlier for
the same StockId and the same `Currency`; scale = standard deviation of the previous eight
surprises (at least six). Deciles of SUE **within each calendar quarter of `RptDate`,
globally** (not per region); region is a reporting split, not a ranking universe.

## 4. Abnormal returns — the P3-11 lesson applied

**Market-adjusted returns (`model="market_adjusted"`): AR = r − r_market(region).** No fitted
intercept, for the reason recorded in `firm.abnormal_returns`: on earnings-sorted firms the
estimation-window intercept manufactures a multi-point "reversal". Sigma for BMP statistics
still comes from [−250, −31] (at least 120 paired days). Event window [−30, +60]. Day 0 = the
first trading day on or after `RptDate`.

## 5. Legibility check — recorded, not a trial

**CAR[0, +1], decile 10 minus decile 1, positive with plain t > 3** (market-adjusted). An
announcement-dated study must show the announcement. If it does not, `RptDate` is not the
announcement date in this table and P3-12 is reported as **uninterpretable** and still counted.

## 6. P3-12 hypothesis, statistic, gate — fixed and binding

**Hypothesis:** after the announcement, the top SUE decile keeps outperforming the bottom decile.

**Primary statistic:** calendar-time portfolio long decile 10 / short decile 1, each event held
days **+2 through +60**, equal weight per event, dollar-neutral, gross exposure 1; daily return
regressed on the equal-weighted market of the panel (all regions) with Newey–West t, 5 lags,
1997–2012.

**Gate: one-sided p < 0.025 (t > 1.96) AND alpha positive in both halves, 1997–2004 and
2005–2012.**

Reported, not gated: mean market-adjusted CAR[−30,−1], [0,+1], [+2,+60] by decile with t;
D10 − D1 CAR[+2,+60] with a Welch t; the same by region (Europe / America / Asia) and by
half; the long-only decile-10 alpha; event counts and drop reasons; the BMP t on
market-adjusted SCARs for completeness.

**No second holding window, no other surprise definition, no other universe, no per-region
gate after seeing the data.** A region that "works on its own" is a new trial.

## 7. Expected outcomes, stated before running

- **Legibility: passes.** D10 − D1 CAR[0,+1] between +2 and +5 points, t far above 3.
- **P3-12: passes.** This is the one event study in the catalogue where the prior is on the
  side of the effect: 1997–2012, announcement-dated, mid- and large-cap global names in the
  era before PEAD decayed in the US. Expected D10 − D1 CAR[+2,+60] between +1.5 and +3.5
  points; calendar-time alpha t between 2.5 and 5; positive in both halves; strongest in
  America and Europe, weakest in Asia. Probability of a pass, in my judgement, about 60%,
  which is far above the project's usual prior and is stated so that it can be scored.
- If it fails, the likely reason is the seasonal-random-walk surprise (analyst-relative surprise
  is what most of the post-2000 evidence uses) or gross-return drift that a 10 bp one-way cost
  at two rebalances per event would not survive. Costs are reported after the gate, never as
  part of it.

## 8. What a pass would mean

A gross, cost-free, announcement-dated drift in 1997–2012 data. The next steps would be, in
order: the real-fill cost model of `Project1/REAL_TRADES.md` applied to two trades per event;
a check against ART's own alpha ranks (`Revision` composite) to see whether ART already traded
this; and a forward record. Not capital.

## 9. Budget

Project3 trial P3-12 and ART trial #12. After it, 12 of 20 ART trials are spent and the next
one is the warning line, at which the correction arithmetic is re-run before anything else.
