# Candidate event studies — what exists, what data it needs, what it would cost

**Written 2026-09-13.** A catalogue, not a pre-registration. Nothing here is a trial until it
has a row in `TRIAL_LEDGER.md` and a spec with a gate. The first six (US elections and the
calendar) are done: see `PREREGISTRATION_US_POLITICAL_AND_CALENDAR_2026-09-13.md` and the README.

## A. Index-level, from the S&P 500 series already in `Data/` (no new data)

| candidate | claim in circulation | what the placebo test would ask | notes |
|---|---|---|---|
| **September, out of sample** | done here: −1.9 pts/month, passes | the same test on an index this project has not looked at (STOXX 600 / MSCI World / Nikkei) | the natural next trial; the one pass of six |
| Post-midterm rally, forward | +7.6% at 90 days, p 0.04 (suggestive fail) | keep the row open; 2026-11-03 is the next observation | one observation every four years; a forward record, not a trial |
| Turn of the month | last day + first three days carry the month's return (Lakonishok–Smidt) | mean of the 4-day window vs placebo 4-day windows; **not** a strategy backtest | Project1 `24.0` built the SPY strategy version without a placebo test |
| Santa Claus rally | last 5 days of Dec + first 2 of Jan average +1.3% (Stock Trader's Almanac, since 1950) | 7-day window vs placebo; post-publication sample (the Almanac has printed it since 1972) | thin-market holiday period; pre-holiday effect literature (Ariel 1990) says most of it is the day before the holiday |
| Pre-holiday effect | the trading day before a market holiday returns ~10× a normal day (Ariel 1990, 1963–1982) | one-day window before each NYSE holiday vs placebo; **1983+ is the out-of-sample** | **REOPENED 2026-09-19. P3-13 failed on the S&P** (decay 75% against their 77%; surviving +0.075 pts, needed +0.091) **but P3-14 PASSED on the FTSE** — +0.1488 pts, t 3.07, p 0.0012, placebo p 0.0139, both halves positive, and stronger with the year-end removed. So the effect is not simply gone; it is gone *in the US*. **P3-15 then answered the next question: NO.** With the 43 Easter sessions removed the remaining 209 give +0.1118 pts, Welch p 0.0181 but placebo p 0.0710, and the spec required both — fails. **CLOSED.** The family reads: dead in the US (decay 75%, as published), and in the UK indistinguishable from an Easter effect. The Nikkei is not run; §6 of the NOGF spec made that conditional on a pass |
| FOMC announcement drift | the 24 hours into the FOMC statement carry most of the equity premium (Lucca–Moench 2015, 1994–2011) | [−1, 0] window on FOMC dates vs placebo; 2012+ is the out-of-sample | Project1 `24.0` has FOMC dates 1990–2023, gap after; Sharpe 0.51 there, no placebo; needs the dates extended to 2026 |
| Options expiration week | third-Friday week positive (Stivers–Sun) | 5-day window vs placebo | course material in the Quantra notebook; `24.0` did not build it |
| Quarter-end / window dressing | last days of the quarter up, first days down | two windows vs placebo | overlaps turn-of-month; would need both in one pre-registration to avoid double counting |
| Presidential cycle year 3 | third year of the term is the best (Hirsch) | annual return in year 3 vs placebo years | reported in the article (D +15.4%, R +12.2%); 24 observations, likely fails |
| Super Bowl / sports | decorative | no | listed to say no: no mechanism, and the placebo test would be an insult to the method |

## B. Firm-level, from data the other projects already hold

### EPS surprise and PEAD — Henrik's question of 2026-09-13: "do we have sufficient data?"

**Short answer: partly, and each source is compromised in a stated way.**

| source | what it has | what it lacks | verdict |
|---|---|---|---|
| **Sharadar** (`Project2/reporting/sharadar_cache/us_fundamentals.csv`, 44,816 ARQ rows, 814 tickers, 2010–2026, PIT S&P 500) | quarterly EPS with the **filing date** (`date`); enough for a seasonal-random-walk SUE (EPS − EPS four quarters earlier, scaled by its own history: the original Bernard–Thomas construction, no analysts needed) | **the filing date is the 10-Q, not the press release.** Inventory 2026-09-13: filing lag after period end is median 36 days, 5th–95th percentile 23–59 days. The press release is typically 1–3 weeks before the 10-Q, so the announcement reaction is *inside the pre-window* of a filing-dated study | a **post-filing drift** study is clean and buildable; an **announcement-window** study is not. 295 duplicated (ticker, period) rows must be reduced to the first filing (`first_filing_per_period` was drafted for this) |
| **ART** (`IbesDataActualsPit`, 591,613 quarterly EPS actuals 1996–2013, bitemporal) | announcement-dated actuals; the `InTime` column is the PIT stamp | **quarterly consensus does not exist anywhere in ART** (only annual FY1/FY2), found by Project1 `88.0`; ART is `RECOVERY_PENDING` today (NAS credential) | a quarterly-SUE PEAD on ART needs no consensus and is the best sample available (bear markets, no survivorship), **one ART trial**; the annual-surprise version was already tried (`88.0`, Sharpe −0.003, null) |
| Sharadar `/data/events` or an earnings-calendar vendor | actual announcement dates 2010+ | not fetched; unknown whether the proxy exposes it | the thing that would make the Sharadar leg an announcement study; check the endpoint before promising |

Cost if pursued: one Project3 trial per hypothesis; the ART leg also one ART-budget trial
(11 of 20 spent, at least 5 of the remaining 9 reserved for the value + profitability
family — a PEAD trial is a new family and needs a written decision first).

### Other firm-level events, data in hand

- **Index inclusion / exclusion:** Sharadar `/data/sp500` add/remove events 2010+ (the
  membership timeline Project2 already reconstructs). Classic result: +3–5% on announcement,
  decaying since 2000s. Placebo across non-event tickers on the same dates.
- **Dividend announcements / ex-dates:** Project2's dividend cache (`reporting/dividend_cache/`).
- **ART's own trades as events:** `PostTrades` 65,920 fills 2009–2013; "what does a stock do
  in the 20 days after ART bought it" is descriptive and already in `REAL_TRADES.md` (the
  signal paid at 3–4 weeks). Not a trial.
- **Headline corpus:** `Project2/pit_headlines/`, two weeks old; a sentiment event study is
  possible around 2029, not before.

## C. What the search turned up that is NOT worth a trial

Sources consulted 2026-09-13 (web search): CME Group on the January effect at midterms, a
2025 Finance Research Letters paper on cross-asset volatility around presidential and midterm
elections, Northern Trust and BlackRock midterm guides, IBKR on presidential-cycle seasonality,
Quantpedia's market-seasonality and January-effect pages, Jacobsen's Halloween-effect sector
paper, a Cogent Economics & Finance 2023 paper on witching days, the FPA Journal's Santa Claus
rally study, and McLean–Pontiff-style post-publication decay papers (average decay 25%; 77%
for the holiday anomaly). The pattern in every one: the effect is presented on a window that
starts where it looks best, with the spread of single events as the error band, and with no
comparison to a random window of the same length. The sell-side guides are the reason the
placebo band exists on the article page.
