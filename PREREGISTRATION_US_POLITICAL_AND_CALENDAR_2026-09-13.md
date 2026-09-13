# Pre-registration: US election events and calendar effects on the S&P 500

**Written 2026-09-13, before any of the numbers below were computed. Committed before running.**
Trials P3-1 to P3-6 of `TRIAL_LEDGER.md`. Requested by Henrik on 2026-09-13: "US president
election pre/post dem/rep", "the calendar effect — monthly and the classical sell in May", and
charts "similar to" the Goldman Sachs midterm exhibit (S&P 500 around midterm elections since
1974, median/average with a 10th–90th percentile band).

## 1. Data — fixed

- **Prices:** S&P 500 index daily close, Yahoo `^GSPC`, 1927-12-30 to 2026-09-11, 24,791 days,
  `Data/GSPC_daily_close.csv`. **Price index, no dividends.** Every number below is a price
  return. This understates all windows by roughly the dividend yield pro rata and cannot
  create a seasonal or event pattern by itself, except that dividend yields were much higher
  before 1960 (4–6%), which matters for the size of the Sell-in-May difference, not its sign.
- **Presidential elections:** 25, 1928–2024, election day = first Tuesday after the first
  Monday of November (computed, tested against six known dates). Winner and winner's party
  from `Data/us_presidential_elections.csv` (hand-entered from public record). Two elections
  are flagged because the winner was not knowable on day +1: 2000 (resolved 2000-12-12) and
  2020 (called 2020-11-07). They stay in the main sample because the question is "what did the
  market do after a Democrat/Republican won", not "what could a trader have done".
- **Midterm elections:** 24, 1930–2022, same date rule.
- **Monthly returns:** month-end to month-end from the daily closes, 1928-01 to 2026-08
  (1,184 months).

## 2. Method — fixed (`eventstudies/core.py`, tests in `tests/test_core.py`)

- Day 0 = the first trading day on or after the event date. Election day is a trading day
  and the result arrives after the close, so **post windows start at +1** and pre windows end
  at 0. A window (a, b) is the return from the close of day a−1 to the close of day b.
- **Placebo inference for every event test.** The statistic is the mean window return over
  the N events. Its null distribution is the same mean over N randomly placed windows drawn
  uniformly from the whole 1927–2026 history, 10,000 draws, seed 42. The p-value counts
  draws at least as far from the placebo mean as the observed value (two-sided). This is what
  removes the market's unconditional drift from the claim: the S&P 500 rose in 60 trading
  days after most things.
- **Party comparisons:** permutation test on the difference of means, 10,000 label shuffles,
  seed 42, two-sided.
- **Calendar months:** Welch t of month m against the other eleven, two-sided normal p.
- **Sell in May:** per calendar year y, summer = May–Oct of y compounded, winter = Nov y to
  Apr y+1 compounded, paired difference winter − summer; t on the non-overlapping annual
  differences (Bouman and Jacobsen 2002 construction).
- **Charts** (`Data/results/…`): mean and median event path from −pre to +post with the
  5th/95th and 10th/90th percentile band of the MEAN path over N placebo events. The Goldman
  chart's band is the spread of single elections around their average; it says how variable
  elections are, not whether the average is unusual. The placebo band answers the second
  question and is the one drawn here; the single-event spread is also reported.

## 3. The six trials and their gates — fixed and binding

Bonferroni over the six trials in this document: **a trial passes at two-sided p < 0.0083**
(0.05/6). p between 0.0083 and 0.05 is recorded as "suggestive, fails the gate", and is a fail.

| # | hypothesis | statistic | gate |
|---|---|---|---|
| P3-1 | Presidential elections are followed by an unusual 60-day return | mean ret[+1,+60] over 25 elections vs placebo | p < 0.0083 |
| P3-2 | The post-election return differs by winner's party | mean ret[+1,+60], Democrat − Republican, permutation | p < 0.0083 |
| P3-3 | The 60 days into a presidential election are unusual ("sideways") | mean ret[−60,0] vs placebo | p < 0.0083 |
| P3-4 | Midterm elections are followed by an unusual 90-day return (the Goldman exhibit) | mean ret[+1,+90] over 24 midterms vs placebo | p < 0.0083 |
| P3-5 | Some calendar month has an unusual mean return | 12 Welch tests, 1928–2026 | any month with p < 0.0042 (Bonferroni 12 inside the family) AND the same sign of the difference in both halves, 1928–1976 and 1977–2026 |
| P3-6 | Sell in May: Nov–Apr beats May–Oct | paired t on annual differences, **post-publication sample 2003–2025** (Bouman & Jacobsen, AER Dec 2002) | two-sided p < 0.0083 (t-distribution) |

Reported beside the gated numbers, not gated: the same statistics on the full sample and on
1950+, the presidential-cycle year 1–4 returns by party, the pre-election window by
INCUMBENT party (the only party label knowable before the election), P3-2 excluding 2000 and
2020, the single-election spread, and the Goldman window (midterms since 1974) as a
replication of their exhibit.

**No second window, no other index, no other event definition after seeing the data.** A
result that "looks interesting at +30 instead of +60" is a new trial and goes in the ledger
first.

## 4. Expected outcomes, stated before running

My expectation, for the record and to be scored:

- P3-1 fail, p > 0.2. The average post-election rally is the market's average drift.
- P3-2 fail. Twenty-five observations split roughly 13/12 cannot resolve a party difference
  of the size anyone claims (a few percent) against a 60-day standard deviation of ~8%.
- P3-3 fail. "Sideways ahead of the election" will be a mean near the placebo mean with a
  wide spread.
- P3-4 fail at the gate, possibly suggestive (p 0.02–0.2). The post-midterm rally is the most
  repeated of these claims and the 1974-onward window in the Goldman chart is a selected
  start; 24 events since 1930 will be less clean.
- P3-5 fail. September's negative mean is the most durable month effect in the literature and
  may clear Bonferroni on the full sample; I expect it to fail the both-halves condition or the
  threshold, and January to fail outright for a large-cap price index.
- P3-6 fail on the post-publication sample (t around 1). The full-sample t will be above 2,
  which is why the gate is the post-publication sample.

Henrik's expectation: to be added by him before the run if he wishes; otherwise "not stated".

## 5. What a pass would and would not mean

A pass is one clean p-value on a price index with no costs, no timing rule and no
implementation. It would justify a pre-registered forward test and nothing else. A fail closes
the hypothesis as stated for this project; the numbers still go in the README because a
recorded null is the product.
