# Pre-registration: the pre-holiday effect, out of sample

**Written 2026-09-19. Committed before running. Trial P3-13 — the warning line of the Project3
ledger.** From the `CANDIDATES.md` queue, section A: "the trading day before a market holiday
returns ~10× a normal day (Ariel 1990, 1963–1982)", with the note that "Marquering et al. report
a 77% post-publication decay in the holiday effect".

This is chosen over the other queue items because it is the one calendar claim that arrives with
**a published estimation sample and a published decay estimate**, so the gate can be set against a
real prior instead of against zero. It needs no new data and costs nothing from the ART budget.

## 1. Data — fixed (inventory 2026-09-19)

`Data/GSPC_daily_close.csv`, Yahoo `^GSPC` daily closes, **1927-12-30 → 2026-09-11, 24,791
sessions.** Price index, no dividends — the same series P3-1 … P3-6 used. Returns are simple
close-to-close. The missing dividend depresses every daily mean by the same ~0.01 pts, so a
*difference between day types*, which is all that is tested here, is very nearly unaffected.

| period | sessions | use |
|---|---|---|
| 1928-01-03 → 1962-12-31 | — | **reserved. Not looked at.** Pre-publication but independent of Ariel's sample; testing it is a separate pre-registration, not a fallback if 1983+ fails |
| 1963-01-01 → 1982-12-31 | 5,020 | **legibility check only**, not a trial — Ariel's own sample |
| 1983-01-01 → 2026-09-11 | 11,010 | **the trial.** Post-publication out of sample |

Daily mean and standard deviation, measured 2026-09-19 before any event was identified:
1963–1982 mean +0.0193%, sd 0.7964%; 1983–2026 mean +0.0429%, sd 1.1277%.

## 2. Identifying the event — fixed, and the part most likely to go wrong

The event day is **the last trading session strictly before a scheduled NYSE closure.** The
closure is not in the price series, so it must be recovered from the series' own gap structure,
and the recovery has a trap: between 1983 and 2026 there are **390 weekdays absent from the
index, 8.9 per year**, but only about eight per year are scheduled holidays. The remainder are
unscheduled closures — 2001-09-11 and the four sessions after it, Hurricane Sandy in 2012,
presidential funerals, weather. **The day before an unscheduled closure is exactly the day the
market fell or panicked**, so leaving them in would bias the event set in a direction nobody
intends.

Therefore, mechanically and in this order:

1. Take every weekday in the sample absent from the trading index — the candidate closures.
2. Classify each against the nine scheduled US market holidays by calendar rule: New Year's Day,
   Martin Luther King Jr. Day (third Monday of January, NYSE from 1998), Washington's Birthday /
   Presidents' Day, Good Friday, Memorial Day, Independence Day, Labor Day, Thanksgiving,
   Christmas Day — each with the NYSE's weekend-observance rule (a Saturday holiday observed the
   Friday before, a Sunday holiday the Monday after).
3. **Anything unclassified is an unscheduled closure. It is excluded, and the run prints the
   complete list of exclusions with dates.** If that list is not in the output, the run is not
   reportable. If it contains more than ~25 dates over 1983–2026, the classifier is wrong rather
   than the market unusually disaster-prone, and that is a harness bug to fix before reading any
   result — the same trial, re-run, as the ledger's rules require.
4. Consecutive scheduled closures (Christmas and New Year in the same week in some years) yield
   **one** event day each — the last session before each closure — and a session that precedes
   two closures is counted once.

Expected event count: approximately **350** pre-holiday days over 1983–2026. The run reports the
exact count and the count per holiday.

## 3. Hypothesis and statistic — fixed

**The mean simple daily return on pre-holiday sessions exceeds the mean on all other sessions,
1983-01-01 → 2026-09-11.** Welch t of the pre-holiday days against every other session in the
sample, **one-sided** p from the t-distribution with Welch degrees of freedom. This is the same
statistic P3-5 used for September against the other eleven months.

Cross-check, reported alongside and not a separate gate: the placebo p from
`placebo_window_means` drawing the same number of one-day windows at random from the same
sample, via `placebo_pvalue`. If the Welch p and the placebo p disagree by more than a factor of
two, neither is reported as the result and the disagreement is investigated first.

## 4. Gate — fixed and binding

One trial. **P3-13 passes if one-sided p < 0.025 and the pre-holiday mean is above the ordinary
mean in both halves** (1983–2004 / 2005–2026). Nothing else is tested. If some other calendar day
type looks more extreme in the diagnostics below, that is reported and is not a result.

**Pre-committed interpretation rule — the overlap.** Two of the nine pre-holiday days sit inside
other claimed anomalies: the session before New Year's Day *is* the last trading day of December,
which is simultaneously the turn-of-month window and the Santa Claus window, both separately
listed in `CANDIDATES.md`. So: the run also reports the same statistic with the **Christmas and
New Year's Day events removed**. This is not a second gate and not a second trial. But if P3-13
passes overall while the seven-holiday subset has one-sided p > 0.10 or a sign flip, **the pass is
recorded as attributable to the turn-of-year window and no general pre-holiday claim is made.**
Deciding that afterwards would be the double-counting `CANDIDATES.md` warns about; deciding it
here costs nothing.

Reported, not gated: the mean return and count for each of the nine holidays separately; the
day-of-week distribution of pre-holiday days against the day-of-week means over the same sample
(Thanksgiving's event day is always a Wednesday, Good Friday's always a Thursday, so the event set
is not a random draw from the week); the same statistic on each half; and the full exclusion list
from §2.

## 5. Power, stated before running — and this is the finding before the finding

With sd 1.1277% and ~350 events, the standard error of the pre-holiday mean is about **0.060
pts**. The ordinary-day mean is +0.043%.

- Ariel's effect, taken at the `CANDIDATES.md` characterisation of ~10× an ordinary day, is a gap
  of roughly **+0.39 pts**. On this sample that would give **t ≈ 6.4** — detected easily.
- To clear the one-sided 0.025 gate needs t ≥ 1.96, i.e. a gap of **+0.118 pts**, which is
  Ariel's effect **decayed by 70%**.
- The decay figure already recorded in `CANDIDATES.md` is **77%**. That implies a gap of ~+0.09
  pts and **t ≈ 1.5, one-sided p ≈ 0.07 — a fail.**

**So this design cannot distinguish "the effect decayed as published" from "the effect is gone".**
Both land in the same failing range. That is stated here, before the run, so that a fail is not
later read as evidence of absence, and so that a pass — which would require the effect to have
decayed *less* than the literature says — is the informative outcome. A single US index cannot be
made more powerful; only more exchanges can, and that is §7.

## 6. Expected outcome, stated before running

**Fail.** Sign positive, one-sided p between 0.03 and 0.25, point estimate somewhere around +0.05
to +0.15 pts. My reasoning is entirely the arithmetic in §5: the published decay estimate puts the
surviving effect just under this sample's resolution. I expect the 1963–1982 legibility check to
read clearly positive with t above 3 — if it does not, the event identification in §2 is wrong and
nothing else in the run means anything.

I also expect the seven-holiday subset to be weaker than the nine-holiday set, because I think a
material part of whatever survives is the turn-of-year window rather than holidays as such.

## 7. What follows

Nothing trades, at any outcome. A pass would not be a strategy: ~350 days at ~0.1 pts gross, on a
position entered and exited around a holiday, is inside the cost model Project1 measured.

If it passes, the next honest step is the **same test on an exchange with a different holiday
calendar** — the FTSE 100 series from 1984 and the Nikkei 225 from 1965 are already in `Data/`,
each a separate pre-registration — not more windows on the S&P 500. If it fails, the queue item is
closed at "consistent with the published decay, and under-powered to say more", the reserved
1928–1962 window stays reserved, and the next candidate from `CANDIDATES.md` section A is chosen
on its own merits.

## 8. Not counted as trials

- The 1963–1982 legibility check (§1, §6): it decides whether the event identification works, not
  whether anything is true. Same footing as the PEAD legibility check under P3-11.
- The per-holiday table, the day-of-week diagnostic, the half-sample split and the exclusion list:
  attached to P3-13, reported, not gated.
