# Project3 trial ledger

**Opened 2026-09-13 at 0 trials.** Project2 spent 24 tests on 2012–2026 before anyone counted
(`ClaudeCode/ART_TRIAL_BUDGET.md`); this ledger exists so that Project3 counts from the first
one. The rules are the ART budget's: every pre-registered hypothesis that decides something is a
trial whether it passes or fails; a harness-bug re-run is the same trial; inventories and
legibility checks are not trials; **the row is added before the run.** Any Project3 test that
reads ART data goes in the ART budget as well, not instead.

Bonferroni is applied inside each pre-registration (its trial count), and the running total
below is what a later reader corrects against.

| # | date | hypothesis | spec | outcome |
|---|---|---|---|---|
| P3-1 | 2026-09-13 | Presidential elections followed by an unusual 60-day S&P 500 return | `PREREGISTRATION_US_POLITICAL_AND_CALENDAR_2026-09-13.md` | **failed** — +2.2% vs placebo +1.9%, p 0.89 |
| P3-2 | 2026-09-13 | Post-election 60-day return differs by winner's party | same | **failed** — D −1.6 pts vs R, p 0.62 |
| P3-3 | 2026-09-13 | The 60 days into a presidential election are unusual | same | **failed** — +1.2% vs placebo +2.0%, p 0.69 |
| P3-4 | 2026-09-13 | Midterm elections followed by an unusual 90-day return | same | **failed the 0.0083 gate, suggestive** — +7.6% vs placebo +2.9%, p 0.039 |
| P3-5 | 2026-09-13 | Some calendar month has an unusual mean return (Bonferroni 12, both halves) | same | **passed** — September −1.9 pts/month, t −3.24, p 0.0012, same sign both halves |
| P3-6 | 2026-09-13 | Sell in May holds on the post-publication sample 2003–2025 | same | **failed** — +1.6 pts/yr, t 0.62, p 0.54 |

| P3-7 | 2026-09-13 | September below the other eleven months, STOXX Europe 600, 2004–2026 (22 Septembers) | `PREREGISTRATION_SEPTEMBER_OOS_2026-09-13.md` | **failed** — −0.7 pts, t −0.81, one-sided p 0.21; first half positive; (S&P on the same 2004+ window: −1.3 pts, p 0.10, also weak) |
| P3-8 | 2026-09-13 | September below the other eleven months, MSCI World, 1972–2026 (54 Septembers, ~2/3 US) | same | **passed** — −1.8 pts, t −2.72, one-sided p 0.004, both halves negative; near-identical to the S&P on the same window (−1.8, t −2.82), i.e. mostly the same evidence |

| P3-9 | 2026-09-13 | September below the other eleven months, FTSE 100, 1984–2026 (43 Septembers) | `PREREGISTRATION_SEPTEMBER_OOS2_2026-09-13.md` | **failed, narrowly** — −1.5 pts, t −1.85, one-sided p 0.035 (gate 0.025), both halves negative (−2.3 / −0.7); S&P on the same window −1.9, p 0.007 |
| P3-10 | 2026-09-13 | September below the other eleven months, Nikkei 225, 1965–2026 (62 Septembers) | same | **failed** — −1.1 pts, t −1.61, one-sided p 0.056, both halves negative (−1.5 / −0.8); S&P on the same window −1.5, p 0.008 |

| P3-11 | 2026-09-13 | Post-filing earnings drift: top SUE decile beats bottom decile from day +2 to +60 after the 10-Q filing, PIT S&P 500, Sharadar 2013–2026 (calendar-time alpha vs SPY) | `PREREGISTRATION_PEAD_SHARADAR_2026-09-13.md` | **failed** on the primary statistic — long-short calendar-time alpha +0.6%/yr, NW t 0.41, one-sided p 0.34; halves −0.5% / +1.5%. The pre-registered legibility check (market-model CAR[−30,−1]) failed for an ESTIMATOR reason (intercept bias by decile, diagnosed after the run, `diag_pead_estimator.py`); market-adjusted returns read correctly (+2.4 pts, t 9.1) and give a drift of +0.4 pts, t 1.1 — same verdict |

| P3-12 | 2026-09-13 | Post-earnings-announcement drift on ART, Global Developed 1997–2012: top SUE decile beats bottom from day +2 to +60 after the IBES announcement date (calendar-time alpha vs EW market) — **also ART budget trial #12** | `PREREGISTRATION_PEAD_ART_2026-09-13.md` | **failed** — run 2026-09-13; three harness corrections, same trial (RegionId is on UniversesEntry; returns on each stock's own calendar, the union-calendar bug had erased 99.9% of American drift windows; CAR coverage rule 90%). Corrected: 136,822 announcement-dated events; legibility PASS (D10−D1 CAR[0,+1] +2.9 pts, t 28.9); **calendar-time long-short alpha +2.7%/yr, NW t 1.42, one-sided p 0.077 (gate 0.025)**; halves +0.8% (t 0.26) / +5.4% (t 2.13); D10−D1 CAR[+2,+60] +0.5 pts (t 1.8); long-only decile 10 alpha −7.9%/yr (t −3.1). First execution under the bug: alpha +2.2%, t 1.09 — same verdict. My "pass, ~60%" was wrong. Seen, not tested: Asia +2.3 pts (t 3.4) and 2005–2012 +0.7 (t 2.6) — a per-region or per-half claim is a new trial |

**Spent: 12 (rows added before running). Warning line: 13. Review at 20.**

Not counted: the PEAD legibility check (CAR[−30,−1] by SUE decile must read the right way),
which decides whether P3-11 is interpretable, not whether anything works — same footing as the
ART closed-book check.

## Not counted, and why

- The filing-lag inventory on Sharadar (`CANDIDATES.md`, PEAD section): a coverage look that
  decided which event date is available, not whether any strategy works.
- The synthetic-data tests in `tests/test_core.py`: correctness of the machinery.
- Charts and descriptive tables listed as "reported, not gated" in a pre-registration: they
  are attached to the trial that produced them and do not add to the count.
