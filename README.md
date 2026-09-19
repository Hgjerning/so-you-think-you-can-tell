# Project3 Event Driven Strategies (renamed from "Project3 Event Studies" on 2026-09-13)

> **Current state:** see **STATE AS OF 2026-09-19** at the end of this file. The rest is the
> chronological record, newest last.

Event studies on dated events and calendar effects, judged against placebo windows drawn from
the same history. Opened 2026-09-13 at Henrik's request ("can we do a project3: eventstudies";
then "US president election pre/post dem/rep", "the calendar effect — monthly and the
classical sell in May", "search the net for other events", "similar graphs of different
events", "eps surprise / pead", and an article "So you think you can…" with an illustration).

Sibling projects: `Project1 Investment Strategy` (library, notebooks, the earlier calendar
strategies in `24.0` and the annual earnings-surprise null in `88.0`) and `Project2 Investment
Strategy` (QualityMom2; Sharadar and headline caches). Governance at the `ClaudeCode/` root:
`ART_TRIAL_BUDGET.md` for anything that reads ART; this project's own count in
`TRIAL_LEDGER.md`.

## Why placebo inference, and why this is not Project1's `24.0` again

`24.0` built turn-of-month, FOMC-day, payday and VIX-expiration *strategies* on SPY and
reported their Sharpe. A strategy Sharpe on a calendar rule answers "did being long on those
days make money", and being long the S&P 500 on almost any subset of days made money. The
question here is different and prior to it: **is the event window unusual relative to a window
of the same length opened on a random day?** That is the placebo test in `eventstudies/core.py`.
Only an event that passes it deserves a strategy.

## Layout

| file | what |
|---|---|
| `eventstudies/core.py` | election calendar, index alignment, window returns and paths, placebo means and path bands, permutation test, calendar-month table, Sell-in-May table, paired t |
| `tests/test_core.py` | 8 tests on synthetic data; every guard proved by making it fail (`python tests/test_core.py`, no pytest needed) |
| `PREREGISTRATION_US_POLITICAL_AND_CALENDAR_2026-09-13.md` | trials P3-1..P3-6, gates, and my predicted outcomes, committed before the run |
| `run_political_calendar_studies.py` | runs the six trials, writes `Data/results/` |
| `build_article.py` | renders `article/so_you_think_you_can_tell.html` from `Data/results/` — no number is typed in |
| `CANDIDATES.md` | the catalogue of further events, with data sources, feasibility and the PEAD data verdict |
| `TRIAL_LEDGER.md` | the count |
| `Data/GSPC_daily_close.csv` | Yahoo `^GSPC` daily close 1927-12-30 → 2026-09-11 (gitignored, regenerable — snippet below) |
| `Data/us_presidential_elections.csv` | winners and parties 1928–2024, hand-entered |

Interpreter: Project1's `.venv\Scripts\python.exe` (3.12, pandas 3.0, numpy 2.5, yfinance).

```python
import yfinance as yf, pandas as pd
c = yf.download("^GSPC", start="1927-01-01", auto_adjust=False, progress=False)["Close"].iloc[:, 0].dropna()
c.index = pd.to_datetime(c.index).tz_localize(None); c.rename("close").to_csv("Data/GSPC_daily_close.csv", index_label="date")
```

## 2026-09-13 — the six pre-registered trials, run once

Pre-registration committed at `a57ad6a` before the run. Gate: two-sided p < 0.0083 (0.05/6).
S&P 500 **price** index, no dividends, no costs. Placebo: 10,000 draws, seed 42.

| trial | hypothesis | n | observed | placebo mean (sd) | p | verdict | my call |
|---|---|---:|---:|---:|---:|---|---|
| P3-1 | presidential post [+1,+60] | 25 | +2.2% | +1.9% (1.9) | 0.887 | fail | right |
| P3-2 | post [+1,+60], Democrat − Republican winner | 13/12 | −1.6 pts (D +1.4%, R +3.0%) | — | 0.616 | fail | right |
| P3-3 | presidential pre [−60,0] | 25 | +1.2% | +2.0% (1.9) | 0.689 | fail | right |
| P3-4 | midterm post [+1,+90], 1930–2022 | 24 | +7.6% | +2.9% (2.3) | **0.039** | suggestive, fails gate | right |
| P3-5 | any calendar month, Bonferroni 12 + same sign in both halves | 1,185 months | **September −1.11%/mo vs +0.82% others; −1.9 pts, t −3.24** | — | **0.0012** | **PASS** | **wrong** (I predicted fail) |
| P3-6 | Sell in May, winter − summer, **2003–2025 post-publication** | 23 years | +1.6 pts/yr, t 0.62 | — | 0.540 | fail | right |

Reported, not gated:

- P3-2 excluding 2000 and 2020 (winner unknown at +1): −3.2 pts, p 0.31. Pre-election by
  incumbent party, D − R: +3.7 pts, p 0.21.
- P3-4 on Goldman's window 1974–2022: +8.5% on 13 midterms, placebo +2.9%, p 0.068.
- Calendar months: September is the only month below the unadjusted 5% line; January +0.6 pts,
  p 0.22; July +1.1 pts, p 0.06; February −0.8, p 0.07. September's gap is −2.1 pts in
  1928–1976 and −1.75 in 1977–2026.
- Sell in May: full 1928–2025 +2.7 pts, t 1.84; 1950–2025 +4.9 pts, t 3.25 (the quoted
  number; 1950 is the start that maximises it); 1928–2002 pre-publication +3.1 pts, t 1.73.
- Presidential cycle, mean annual price return by year of term, D / R: year 1 +12.9% / +0.7%,
  year 2 +3.7% / +3.6%, year 3 +15.4% / +12.2%, year 4 +10.8% / +2.2%. 13 and 12 per cell;
  year 1 under Republicans holds 1929, 1973, 2001, 2008.

**Score: five of six predictions right; the miss is the pass.** September clears both the
Bonferroni-12 line and the two-halves condition. It is one month, a price index, ~2 points, and
in print for decades; the next step is the same test on an index this project has not looked
at (`CANDIDATES.md` A, first row), not a trade.

**The article:** `article/so_you_think_you_can_tell.html`, built from the result CSVs, with
each event's path drawn against the placebo band of the mean of N random windows (the band the
Goldman midterm exhibit does not show; its band is the spread of single elections around their
own average). Published as an artifact (URL in the state block).

**Test harness note.** The drift guard in `tests/test_core.py` first ran as a single draw of
25 random events on a drifting walk and failed at p 0.0027; the rejection rate over 200 such
draws was 0.075 against 0.05 nominal. It is now a rate test with the tolerance [0.02, 0.10]
written before re-running. A single draw cannot tell a bug from a 3-sigma sample.

**LinkedIn package** (`build_linkedin.py` → `linkedin/`): `article_linkedin.txt` (1,300 words,
paste-ready, image placeholders where each PNG goes), `post.txt` (the feed post), `00_cover.png`
(1920×1080, the abstract prism/eclipse drawing), `01`–`05` the five charts as PNG, `06_ledger.png`
(the table as an image, since LinkedIn articles have no tables). Every number in the text comes
from `Data/results/`. The cover in the web article was redone in the same abstract form at
Henrik's request (no prism outline, no labels; white noise in, a spectrum out, one thread survives).

**Seen in the chart, not tested, and not to be chased without a ledger row:** the presidential
mean path runs above the placebo band between days −90 and −45. The pre-registered pre-window
was [−60, 0], which it fails. A [−90, −45] window would be a new trial chosen after seeing the
data; it is recorded here so that it is not "discovered" later.

## 2026-09-13, later — September out of sample (P3-7, P3-8)

Pre-registered at `594c24a` before running (`PREREGISTRATION_SEPTEMBER_OOS_2026-09-13.md`).
One-sided Welch t of September against the other eleven; gate p < 0.025 (Bonferroni 2) AND
negative in both halves. Price indices from Yahoo; STOXX 600 only reaches back to 2004 there.

| trial | index | Septembers | Sept mean | other months | gap | t | one-sided p | halves | verdict | my call |
|---|---|---:|---:|---:|---:|---:|---:|---|---|---|
| P3-7 | STOXX Europe 600, 2004–2026 | 22 | −0.19% | +0.51% | −0.7 pts | −0.81 | 0.21 | +0.1 / −1.5 | **fail** | right (fail), p above my 0.03–0.2 range |
| P3-8 | MSCI World (USD), 1972–2026 | 54 | −0.98% | +0.82% | −1.8 pts | −2.72 | **0.004** | −1.5 / −2.1 | **PASS** | right |
| report | S&P 500 on the STOXX window, 2004–2026 | 22 | −0.38% | +0.92% | −1.3 pts | −1.30 | 0.10 | +0.1 / −2.7 | — | — |
| report | S&P 500 on the MSCI World window, 1972–2026 | 54 | −0.91% | +0.91% | −1.8 pts | −2.82 | 0.003 | −1.4 / −2.2 | — | — |

**Reading.** The MSCI World pass is the S&P 500 pass again: the two rows on the same window are
within 0.01 points of each other, as a two-thirds-US index must be. It adds almost nothing to
P3-5. The clean out-of-sample, STOXX 600, has the right sign and no power: 22 observations,
and on that same 2004+ window even the S&P 500 only manages p 0.10, with a positive first
half. So the honest summary is: **September is a real feature of the long US record and of
the US-dominated world index; whether it is a feature of Europe, or of the last twenty years
anywhere, this data cannot say.** In the STOXX twelve-month table September is not even the
most negative month (June −1.5, August −1.3, both p ~0.07–0.10, none gated). Files:
`Data/results/september_oos.csv`, `calendar_months_stoxx.csv`, `calendar_months_msci.csv`.

Next, if wanted (each a new pre-registration): a long non-US series — FTSE 100 from 1984,
Nikkei 225 from 1965, DAX from 1959 — where a European or Japanese September can be tested
with 40–60 observations instead of 22.

## 2026-09-13, later still — September on FTSE 100 and Nikkei 225 (P3-9, P3-10)

Pre-registered at `c8bdbdc` before running (`PREREGISTRATION_SEPTEMBER_OOS2_2026-09-13.md`),
same statistic and gate as P3-7/P3-8: one-sided p < 0.025 AND negative in both halves.

| trial | index | Septembers | Sept mean | other months | gap | t | one-sided p | halves | verdict | my call |
|---|---|---:|---:|---:|---:|---:|---:|---|---|---|
| P3-9 | FTSE 100, 1984–2026 | 42 | −0.81% | +0.67% | −1.5 pts | −1.85 | 0.035 | −2.3 / −0.7 | **fail, narrowly** | right (predicted p 0.025–0.08) |
| P3-10 | Nikkei 225, 1965–2026 | 61 | −0.36% | +0.78% | −1.1 pts | −1.61 | 0.056 | −1.5 / −0.8 | **fail** | right (predicted p 0.05–0.3; gap a little larger than my −0.5 to −1) |
| report | S&P 500 on the FTSE window | 42 | −0.89% | +1.01% | −1.9 pts | −2.54 | 0.007 | −2.4 / −1.4 | — | — |
| report | S&P 500 on the Nikkei window | 61 | −0.64% | +0.82% | −1.5 pts | −2.49 | 0.008 | −1.4 / −1.6 | — | — |

**Reading, across all four out-of-sample series.** The sign is negative in every non-US index
(STOXX, FTSE, Nikkei) and in seven of their eight halves; the size is smaller than in the US
on the same windows (−1.5 vs −1.9 for the UK, −1.1 vs −1.5 for Japan, −0.7 vs −1.3 for
Europe since 2004), and no non-US series clears the gate on its own. Pooling them would be a
new test chosen after seeing the data and is not done. **The record therefore reads: September
is a robust feature of the US price index; abroad it has the same sign, about two-thirds of
the size, and does not reach significance in any single market.** In the FTSE table December
(+1.75, p 0.0006), April (+1.5) and June (−1.4) are all stronger than September; in the Nikkei
table nothing clears even the unadjusted 5% line. Files: `Data/results/september_oos2.csv`,
`calendar_months_ftse.csv`, `calendar_months_nikkei.csv`.

Both of my predicted verdicts were right (four of four on this round; six of eight overall,
the two misses both being September on the S&P 500 and MSCI World).

## 2026-09-13, evening — PEAD on Sharadar (P3-11), and an estimator lesson

Pre-registered at `17fd019` before running (`PREREGISTRATION_PEAD_SHARADAR_2026-09-13.md`).
Post-**filing** drift (Sharadar's date is the 10-Q, median 36 days after period end), PIT S&P 500
membership on the filing date, seasonal-random-walk SUE in deciles by filing quarter, 2013–2026.
26,409 gated filings (34,211 ungated). Primary statistic: calendar-time long decile 10 / short
decile 1, held days +2..+60, alpha vs SPY with Newey–West t; gate one-sided p < 0.025 and
positive in both halves.

| sample | events | LS alpha/yr | NW t | one-sided p | halves | long-only D10 alpha/yr (t) | verdict |
|---|---:|---:|---:|---:|---|---:|---|
| gated (PIT members) | 26,409 | +0.6% | 0.41 | 0.34 | −0.5% / +1.5% | +1.0% (0.6) | **fail** |
| ungated (master panel) | 34,211 | +1.9% | 1.29 | 0.10 | +1.4% / +2.4% | +3.8% (2.2) | reported: what the membership gate removes |

**My call: fail, right** (predicted alpha t between −0.5 and +1.5; got 0.41).

**The legibility check failed as pre-registered, and the reason is the estimator, not the
data.** Market-model CAR[−30,−1] for decile 10 minus decile 1 was +0.1 pts (t 0.8) instead of
the expected +3 to +7, and market-model CAR[+2,+60] showed a monotone 4-point "reversal"
(t −9.7) that the calendar-time portfolio does not see. Diagnosis (`diag_pead_estimator.py`,
run after and labelled as such): the estimation-window intercept runs from **−10%/yr in decile
1 to +9.5%/yr in decile 10** — firms sorted on earnings changes have had a year of opposite
drift — and 58 days of that intercept is ~4.5 points of expected return, which the market
model subtracts. With market-**adjusted** returns (r − SPY, no intercept) the same events give:

| window | D1 | D10 | D10 − D1 | t |
|---|---:|---:|---:|---:|
| [−30, −1] (contains the press release) | −1.3% | +1.0% | **+2.4 pts** | 9.1 |
| [0, +1] (filing days) | −0.6% | +0.2% | +0.8 pts | 6.6 |
| [+2, +60] (the drift) | −0.3% | +0.1% | **+0.4 pts** | 1.1 |

(`Data/results/pead_diag_market_adjusted.csv`, summed daily abnormal returns; an inline first
pass with compounded returns gave +0.6 pts, t 1.6 for the drift — same reading.) So the data
reads the right way, the surprise measure works, and the post-filing drift is under half a
point over three months with t near 1: the same verdict the calendar-time alpha gave.
**P3-11 is counted once and fails.** The legibility prediction ("passes, +3 to +7") was wrong
as pre-registered and, on the corrected measure, +2.4 is below my range: two misses on the
side detail, the verdict right.

**Harness lesson, applied:** `firm.abnormal_returns` now has `model="market_adjusted"`, the
docstring records why, and `tests/test_firm.py` has a guard that manufactures the bias on a
sorted synthetic sample and requires the market-adjusted variant not to show it. Any future
firm-level pre-registration with an event window longer than a few days uses market-adjusted
returns or the calendar-time portfolio for its legibility check; the market model with an
intercept stays for short windows only.

What was not done: no second holding window, no other surprise definition, no re-run of P3-11
under the corrected legibility check as a "harness fix" (the primary statistic was never
affected, so there is nothing to re-run). The ART leg (announcement-dated quarterly actuals,
1996–2013) remains the better sample and is still an ART-budget decision for Henrik.

## 2026-09-13, night — PEAD on ART pre-registered, blocked on the database (P3-12 / ART #12)

Henrik: "run the pead on ART". ARTData is `RECOVERY_PENDING`: the share `\\192.168.0.25`
answers from the user session and port 445 is open, but SQL Server runs as `.\sqlsvc`, which
has no stored SMB credential, so the 23 data files cannot be opened (same diagnosis as
2026-09-10). The fix is Henrik's to apply (a `cmdkey` run AS `sqlsvc` via a one-off scheduled
task, then `ALTER DATABASE ARTData SET ONLINE` or a service restart; recipe in the
`art-pit-database` memory and in the session log of 2026-09-13).

Pre-registration `PREREGISTRATION_PEAD_ART_2026-09-13.md` is written and committed with the
gate, the predictions (legibility passes; **P3-12 passes, ~60%**, the one study in the
catalogue with the prior on its side) and the P3-11 lesson applied (market-adjusted returns,
no fitted intercept). `run_pead_art.py` is written against the `art_pit.py` column names but
**has not executed against the live database**; a schema fix at run time is a harness
correction, any change to a window, gate, sample or surprise definition is not. Rows added in
both ledgers before running: Project3 P3-12 and ART #12 (**the next ART trial is the warning
line at 13**).

## 2026-09-13, 15:21–16:00 — ART back online; P3-12 run: FAIL, and a second harness lesson

**ART came back without the credential step.** The error log showed the 11:07 failure was OS
error 32 (files "in use by another process"), not access denied; Henrik's `schtasks` attempt
errored ("no mapping between account names and security IDs") and was unnecessary; a plain
`ALTER DATABASE ARTData SET ONLINE` from this session brought it up at 15:21. **Next time: try
SET ONLINE first.**

**First execution** hit one schema detail (`RegionId` is on `UniversesEntry`, not `AllStocks`)
and then ran to a fail — but three of the drift cells were NaN, and the diagnostic found a real
bug: the price panel's index is the union of the Asian, European and American calendars, so a
US stock is NaN on Tokyo-only days, `pct_change` on that grid also loses the return on the day
after each gap, and the all-days CAR rule then emptied **99.9% of American CAR[+2,+60]**. The
calendar-time alpha (which skips NaN days) had survived, minus the lost days. Corrections,
committed at `19e6e02` before the corrected numbers were seen and each guarded by a test:
`firm.returns_on_own_calendar` (per-stock returns on the stock's own trading days) and a 90%
coverage rule in `firm.car`. Same trial under the budget rule.

**Corrected result (136,822 events, 107k America / 19k Asia / 11k Europe — Europe and Asia
mostly report semi-annually, so few quarterly rows):**

| scope | events | D10−D1 CAR[−30,−1] | D10−D1 CAR[0,+1] | D10−D1 CAR[+2,+60] | t |
|---|---:|---:|---:|---:|---:|
| all | 136,822 | +4.2 pts (t 21.5) | **+2.9 pts (t 28.9)** | **+0.5 pts** | 1.8 |
| America | 107,365 | +4.4 | +3.1 | +0.3 | 1.1 |
| Asia | 18,635 | +2.9 | +1.6 | +2.3 | 3.4 |
| Europe | 10,822 | +3.3 | +2.3 | +0.1 | 0.2 |
| 1997–2004 | 52,378 | +6.1 | +2.3 | 0.0 | 0.0 |
| 2005–2012 | 84,444 | +2.9 | +3.3 | +0.7 | 2.6 |

| primary statistic (calendar-time long D10 / short D1, days +2..+60) | value |
|---|---:|
| alpha vs the equal-weight market, 1997–2012 | **+2.7%/yr, NW t 1.42, one-sided p 0.077** |
| gate | p < 0.025 and positive in both halves → **fail** |
| halves 1997–2004 / 2005–2012 | +0.8% (t 0.26) / +5.4% (t 2.13) |
| long-only decile 10 | −7.9%/yr (t −3.1) |
| under the calendar bug (first execution) | +2.2%/yr, t 1.09 — same verdict |

**Reading.** The announcement is unmistakable: three points between the top and bottom surprise
deciles on the announcement days, t 29, and four points in the month before (analysts and the
pre-announcement leak). The drift after it is half a point over three months, t 1.8 on the CARs
and 1.4 on the calendar-time alpha, and every decile drifts *down* against the equal-weight
market (−1.3 to −2.0 points), so the long-only top decile has negative alpha and only the
long-short spread is positive. **The pre-registered prediction was a pass at ~60%. It failed.**
Seen and not tested: Asia's +2.3 points (t 3.4) and the second half's +0.7 (t 2.6) — a
per-region or per-half claim is a new trial and would be chosen after seeing the data.

**Score, all twelve trials:** predictions right on 10 of 12; wrong on the two surprises in
opposite directions — September on the S&P 500 (predicted fail, passed) and PEAD on ART
(predicted pass, failed).

Files: `Data/results/pead_art_summary.csv`, `pead_art_deciles.csv`, `pead_art_calendar_time.csv`,
`pead_art_dropped.csv`, `pead_art_run_log.txt`; caches in `Data/art_cache/` (gitignored).

## 2026-09-19 — the pre-holiday family: P3-13, P3-14, P3-15 (12 -> 15 trials, past the warning line)

Ariel (1990) measured the pre-holiday effect on US 1963-1982, so 1983+ is post-publication and
`CANDIDATES.md` already carried a published decay estimate of 77%. Event = the last trading
session strictly before a **scheduled** exchange closure, recovered from the price series' own
gap structure (a closure is a weekday with no row). Each spec committed before its run, each
ledger row before that. `run_preholiday.py [US|UK|UK_NOGF]`, `preholiday_text.py`.

| trial | sample | n | gap/day | Welch | placebo | verdict | my call |
|---|---|---|---|---|---|---|---|
| P3-13 | S&P 500 1983-2026 | 373 | **+0.0745 pts** | t 1.61, p 0.0538 | 0.1058 | fail | right |
| P3-14 | FTSE 100 1984-2026 | 252 | **+0.1488 pts** | t 3.07, p 0.0012 | 0.0139 | **PASS** | **wrong** |
| P3-15 | FTSE, Easter removed | 209 | +0.1118 pts | t 2.11, p 0.0181 | **0.0710** | fail | right |

**P3-13.** Legibility on Ariel's own 1963-1982 sample passes (+0.2930 pts, t 5.79), so the
machinery finds the effect where it was published. **The decay is therefore 75%, against the
77% on record.** The power section, written before the run, said the gate needed decay under
~70% — so this trial was committed in advance to failing if the published figure was right. A
fail here cannot say the effect is gone, only that it is under this sample's resolution.

**P3-14.** I argued this trial was not worth running: a second index, the same under-powered
fail. That was wrong, and for a reason worth recording — I never checked the overlap. **Five of
the eight UK bank holidays have no US counterpart** (Easter Monday, Early May, Spring, Summer,
Boxing Day), so most of the event set is new. It passes, both halves positive.

**P3-15.** A decomposition of a result already seen, and section 0 of its spec says so: section
5 stated the expected numbers to two decimals and they landed to three. Good Friday is shared
with the US and was the strongest holiday in both markets, so the question was whether the UK
pass survives without it. **It does not.** The gate required *both* statistics — fixed before
the run, because the two were going to disagree on the verdict and leaving the choice open
would have been a lever. **The FTSE pre-holiday effect is an Easter effect with company.**
The Nikkei was not run: section 6 made a third market conditional on this surviving.

**Why the two statistics disagree, which is the portable part.** Pre-holiday sessions are calm
— sd 0.75% against 1.07% on ordinary days. Welch divides by the quieter event-group variance
and reads strong; the placebo compares against randomly drawn days from the market as it is,
and reads weaker. On a subset selected for being quiet the t-statistic flatters, and the
placebo is the conservative default. On a one-leg gate chosen after the fact, P3-15 passes.

**Two faults the procedure caught in the specification, not in the market.** Printing every
excluded closure surfaced five Juneteenths (an NYSE holiday since 2022, absent from my list of
nine); left in the discard pile and recorded, because amending a list after seeing the result
is how a spec stops meaning anything, and five days of 378 cannot move the verdict. And the UK
legibility check failed because I specified holidays per year while the harness produces
*sessions* per year: 85 of 337 closures share a preceding session, since the Thursday before
Good Friday also precedes Easter Monday and Christmas Eve precedes Boxing Day. The same slip
sat in the power calculation, so P3-14 cleared a higher bar than the one written down.

Machinery added to `eventstudies/core.py`: `easter_sunday`, `us_market_holiday_candidates`
(nine NYSE, MLK from 1998), `uk_market_holiday_candidates` (eight LSE; the UK substitutes
*forward*, the NYSE backward, and Christmas/Boxing cascade), `scheduled_closures(calendar=...)`
and `preceding_sessions`. 14 core tests, each proved by making it fail first.

Files: `Data/results/preholiday_{stats,by_holiday,events,exclusions}_{us,uk,uk_nogf}.csv`.

## STATE AS OF 2026-09-19

- **Trials:** 15 run (P3-1..P3-15), **3 passes** (September on the S&P 500 and, redundantly,
  MSCI World; the pre-holiday effect on the FTSE, which does not survive removing Easter),
  3 suggestive fails, 9 fails. **Past the warning line of 13; review at 20, five left.**
  ART budget untouched at 12 of 20. Predictions right on **12 of 15** — the three misses are
  September (predicted fail, passed), PEAD on ART (predicted pass, failed) and the FTSE
  pre-holiday trial (predicted fail, and I had argued against running it at all).
- **Firm-level machinery** now exists (`eventstudies/firm.py`, 6 tests) alongside the
  index-level placebo machinery (`core.py`, 8 tests).
- **Data:** S&P 500 1927–2026, MSCI World 1972–2026, STOXX 600 2004–2026, FTSE 100 1984–2026,
  Nikkei 225 1965–2026, all price indices from Yahoo.
- **The pre-holiday family is closed:** dead in the US at a measured 75% decay, and in the UK
  indistinguishable from an Easter effect. The Nikkei is deliberately not run.
- **September is closed for this project** unless a mechanism is proposed: five indices tested,
  sign consistent everywhere, gate cleared only where the US dominates.
- **Open next (not pre-registered):** post-midterm
  as a forward record (next observation 2026-11-03); PEAD on Sharadar as a *post-filing* drift
  study (the filing date is the 10-Q, median 36 days after period end — see `CANDIDATES.md` B),
  or on ART quarterly actuals when the NAS credential is restored (one ART trial, new family,
  needs a written decision).
- **Article artifact:** https://claude.ai/code/artifact/4834c924-cdf6-4376-88db-987a84193162
  (republish to the same URL from `article/so_you_think_you_can_tell.html`; never a new one).
- **Public copy (2026-09-13, on Henrik's yes):** `Hgjerning/so-you-think-you-can-tell` (public,
  `main`), GitHub Pages at https://hgjerning.github.io/so-you-think-you-can-tell/ serving
  `article/index.html` (the standalone build). Contents: article, pre-registrations, ledger,
  candidates, `Data/results/`, elections CSV, code, tests, LinkedIn package. Excluded: Yahoo
  price files, Sharadar caches, ART pulls, Henrik's PDF. To update: rebuild here, copy the same
  file set into a clone of the public repo, commit, push `main`. Licence not yet stated.
- **Repo:** `git@github.com:Hgjerning/Project3-event-driven-strategies.git` (private, `master`), created and
  first pushed 2026-09-13 on Henrik's word. Push only when he asks.
