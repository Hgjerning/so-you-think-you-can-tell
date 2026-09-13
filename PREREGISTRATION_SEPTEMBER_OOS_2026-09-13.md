# Pre-registration: September out of sample — STOXX Europe 600 and MSCI World

**Written 2026-09-13 after P3-5 passed on the S&P 500 (September −1.9 pts/month vs the other
eleven, t −3.24, same sign in both halves). Committed before running. Trials P3-7 and P3-8.**
Henrik: "run september on stoxx 600 and msci world".

## 1. Data — fixed (inventory 2026-09-13, Yahoo, price indices, no dividends)

| trial | index | symbol | daily history | Septembers | independence from P3-5 |
|---|---|---|---|---|---|
| P3-7 | STOXX Europe 600 | `^STOXX` | 2004-04-26 → 2026-09-11 | **22** (2004–2025) | clean: no US stocks; but short |
| P3-8 | MSCI World (USD, price) | `^990100-USD-STRD` | 1972-01-03 → 2026-09 | **54** (1972–2025) | partial: roughly 60–70% US weight throughout, so it re-uses most of the S&P 500 sample |

Yahoo does not carry the STOXX 600 back-history to 1987; the 2004 start is the data, not a
choice. Monthly returns are month-end to month-end from daily closes; the last month used is
2026-08. Files: `Data/STOXX_daily_close.csv`, `Data/990100_USD_STRD_daily_close.csv`.

## 2. Hypothesis and statistic — fixed

Directional replication of one pre-specified month: **September's mean monthly return is below
the mean of the other eleven months.** Welch t of September against the other eleven, **one-sided**
p from the t-distribution with Welch degrees of freedom. Halves: the sample split at its median
year (STOXX 2004–2014 / 2015–2026; MSCI World 1972–1998 / 1999–2026).

## 3. Gate — fixed and binding

Two trials, so Bonferroni inside this document: **a trial passes if one-sided p < 0.025 AND the
September gap is negative in both halves.** No other month is tested; if another month looks
more extreme in the twelve-month table, that is reported and is not a result.

Reported, not gated: the full twelve-month table for each index; the S&P 500 September gap on
exactly the same window as each index (2004-05 → 2026-08 and 1972-02 → 2026-08), so that
"different index" and "different period" can be told apart; the gap in each half.

## 4. Power, stated before running

Monthly standard deviation of these indices is about 4.5 points. With 22 Septembers the standard
error of the September mean is ~1.0 point, so a gap of the S&P's size (−1.9) gives t ≈ −1.9,
which is at the edge of the gate; with 54 it is ~0.6 and the same gap gives t ≈ −3. **P3-7 is
under-powered for an effect of the size found, and a fail there is weak evidence either way.**

## 5. Expected outcomes, stated before running

- **P3-7 STOXX 600: fail.** Sign negative, one-sided p between 0.03 and 0.2. The sample is too
  short to clear 0.025 unless the European September is larger than the American one.
- **P3-8 MSCI World: pass, narrowly.** Mostly because it contains the S&P 500 over the half of
  the century where the S&P gap was −1.75. A pass here says little that P3-5 did not already
  say; a fail here would be informative, because it would mean the non-US part of the index
  offsets the US September.

## 6. What follows

Pass or fail, the next honest step for September is a long non-US series (FTSE 100 from 1984,
Nikkei 225 from 1965, DAX from 1959 as a total-return index — each a separate pre-registration),
not more windows on these two. No trade follows from any of this.
