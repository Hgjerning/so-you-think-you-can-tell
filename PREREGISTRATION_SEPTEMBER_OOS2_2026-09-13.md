# Pre-registration: September out of sample, second round — FTSE 100 and Nikkei 225

**Written 2026-09-13 after P3-7 (STOXX 600, fail on 22 observations) and P3-8 (MSCI World,
pass, but the S&P 500 again). Committed before running. Trials P3-9 and P3-10.**
Henrik: "run september on ftse 100 and nikkei 225".

## 1. Data — fixed (inventory 2026-09-13, Yahoo, price indices, no dividends)

| trial | index | symbol | daily history | Septembers | independence from the US result |
|---|---|---|---|---|---|
| P3-9 | FTSE 100 | `^FTSE` | 1984-01-03 → 2026-09-11 | **43** (1984–2025 complete; 1984 included) | no US stocks; monthly correlation with the S&P 500 roughly 0.7 since 1984, so shared shocks (1987, 1998, 2001, 2008, 2022) are in both |
| P3-10 | Nikkei 225 | `^N225` | 1965-01-05 → 2026-09-11 | **62** (1965–2025; 1965 included) | no US stocks; the lowest US correlation of any index used here, especially before 1990; Japanese fiscal half-year ends in September, a mechanism of its own |

Monthly returns month-end to month-end; the last month used is 2026-08. Files
`Data/FTSE_daily_close.csv`, `Data/N225_daily_close.csv`. The first September in each series is
kept (1984 for FTSE, 1965 for Nikkei); nothing is trimmed.

## 2. Hypothesis, statistic, halves, gate — identical to P3-7/P3-8

September's mean monthly return is below the mean of the other eleven months. Welch t,
**one-sided** p from the t-distribution with Welch degrees of freedom. Halves split at the
median year (FTSE 1984–2004 / 2005–2026; Nikkei 1965–1995 / 1996–2026). **Gate: one-sided
p < 0.025 AND the gap negative in both halves.** No other month is tested; the twelve-month
table is reported for the record.

Reported, not gated: the S&P 500 on the same window as each index; the twelve-month tables.

## 3. Power

43 and 62 Septembers against a monthly standard deviation of about 5 points (FTSE) and 5.5
(Nikkei): standard errors of the September mean about 0.8 and 0.7 points. A gap of the US size
(−1.8) would give t ≈ −2.3 and −2.6; a gap of half that size would not clear the gate. These
two are adequately powered for the US-sized effect and not for a smaller one.

## 4. Expected outcomes, stated before running

- **P3-9 FTSE 100: fail, narrowly.** Sign negative, gap −1 to −2 points, one-sided p between
  0.025 and 0.08. The UK shares the US September shocks and a September effect is part of UK
  market folklore, which is why I expect the sign; 43 observations is why I expect it to miss
  the gate. I put the chance of a pass near 40%.
- **P3-10 Nikkei 225: fail.** Sign negative but smaller, gap −0.5 to −1 point, p 0.05 to 0.3.
  Japan's calendar is different (fiscal year from April, half-year end in September), and the
  1965–1990 bull market drowns month effects. A Nikkei pass would be the first evidence that
  September is not a US-and-satellites phenomenon.

## 5. What follows

Two passes → September is a global feature of price indices and the next question is
mechanism, not more indices. Two fails → September stands as a US (and US-dominated) feature
only. Split → the record says so and no tie-break is run. No trade follows in any case; a
calendar month with a two-point gap and a 5-point standard deviation is a fact, not a position.
