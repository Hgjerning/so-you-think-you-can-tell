# Pre-registration: the pre-holiday effect on the FTSE 100

**Written 2026-09-19, after P3-13 failed on the S&P 500 (gap +0.0745 pts, t +1.61, one-sided
p 0.0538 against a 0.025 gate; legibility on 1963–1982 +0.2930, t +5.79; decay 75%). Committed
before running. Trial P3-14.** Henrik: "run the FTSE version next".

**I advised against this trial and was overruled, which is recorded here because it is part of
the trial's history.** My argument was that a second index would reproduce the same
under-powered fail. My argument was *partly wrong* and §3 says why: the UK calendar is mostly
disjoint from the US one, so this is a different event set rather than a re-run. It remains
right about power, and §5 shows the design is again pre-committed to failing at the effect size
P3-13 actually measured.

## 1. Data — fixed (inventory 2026-09-19)

`Data/FTSE_daily_close.csv`, Yahoo `^FTSE` daily closes, **1984-01-03 → 2026-09-11, 10,785
sessions.** Price index, no dividends, same convention as P3-13. Measured before any event was
identified: daily mean **+0.0277%**, sd **1.0682%**. Weekdays absent from the index: **354, or
8.3 per year**, against eight scheduled bank holidays — so, as in the US, a handful of
unscheduled closures are mixed in and must come out.

There is no reserved window: the series begins in 1984 and nothing earlier exists to hold back.

## 2. Identifying the event — fixed

Identical machinery to P3-13 (`eventstudies.core.scheduled_closures`, `preceding_sessions`) with
the **UK** calendar. The event day is the last trading session strictly before a scheduled LSE
closure. The eight scheduled holidays are New Year's Day, Good Friday, **Easter Monday**, the
Early May Bank Holiday, the Spring Bank Holiday, the Summer Bank Holiday, Christmas Day and
**Boxing Day**. Weekend holidays substitute **forward** in the UK, the opposite of the NYSE rule,
and Christmas and Boxing Day cascade into each other; both are handled by offering candidates and
letting the price series decide which was actually a closure.

Ad-hoc royal closures — jubilees, the 2011 wedding, the 2022 state funeral, the 2023 coronation —
are **deliberately not in the list**. They are not scheduled, they will land in the unscheduled
bucket, and **the full exclusion list must be printed or the run is not reportable**, exactly as
in P3-13. The same tripwire applies: more than 25 exclusions means the classifier is wrong rather
than the market unusually eventful.

Expected event count: approximately **340**.

## 3. Independence from P3-13 — stated honestly, because it is the reason for running

| | |
|---|---|
| UK holidays with **no** US counterpart | Easter Monday, Early May, Spring Bank Holiday, Summer Bank Holiday, Boxing Day — **five of eight** |
| shared with the NYSE | New Year's Day, Good Friday, Christmas Day — three of eight |

So roughly five eighths of the event set is new. **That is the case for the trial and it is
stronger than I first allowed.** But two qualifications are fixed here, before the numbers:

1. **The markets are not independent even on UK-only holidays.** FTSE and S&P daily returns are
   substantially correlated, and the session before a UK-only bank holiday is an ordinary US
   trading day. A UK pass would therefore not be a clean second observation.
2. **Good Friday is shared, and it was the strongest US holiday** (+0.375%, n 44). If the UK
   result is carried by Good Friday, it is plausibly the same phenomenon in a second venue rather
   than independent confirmation. The per-holiday table is reported for exactly this reason.

## 4. Hypothesis, statistic and gate — fixed and binding

**The mean simple daily return on pre-holiday sessions exceeds the mean on all other sessions,
1984-01-03 → 2026-09-11.** Welch t, **one-sided** p on Welch degrees of freedom. Placebo
cross-check by `placebo_window_means` / `placebo_pvalue` as in P3-13, with the same rule: a
disagreement worse than a factor of two means neither is reported until it is understood.

One trial. **P3-14 passes if one-sided p < 0.025 and the gap is positive in both halves**
(1984–2004 / 2005–2026).

**Pre-committed interpretation rule — and the UK overlap is worse than the US one.** Three of the
eight UK holidays sit at the turn of the year: Christmas Day, Boxing Day and New Year's Day. The
session before Boxing Day is Christmas Eve, and the session before New Year's Day is the last
trading day of December — the turn-of-month and Santa Claus windows both. So the run also reports
the statistic with **all three year-end holidays removed**. This is not a second gate and not a
second trial. **If P3-14 passes overall while the five-holiday subset has one-sided p > 0.10 or a
sign flip, the pass is recorded as the turn-of-year window and no general pre-holiday claim is
made.**

Reported, not gated: mean and count per holiday; the day-of-week distribution against
day-of-week means; each half; the full exclusion list.

**Structural legibility check** (P3-13 used Ariel's own sample; no such window exists here, and a
trial with no legibility check is unreadable). The run must show **all eight** holidays matched,
at **7.5–8.5 events per year**, with the known ad-hoc royal closures appearing in the exclusion
list and not in the event set. If the classifier instead swallows a coronation or misses a bank
holiday, the structure will show it before any statistic is read.

## 5. Power, stated before running

sd 1.0682% over ~340 events gives a standard error of about **0.058 pts**, against an ordinary-day
mean of +0.0277%. Clearing the gate needs t ≥ 1.96, i.e. a gap of **+0.114 pts**.

**The surviving US effect measured in P3-13 was +0.0745 pts.** If the UK effect is the same size,
this design returns **t ≈ 1.29, one-sided p ≈ 0.10 — a fail.** The UK gap would have to be about
**1.5× the surviving US gap** to pass.

So, as in P3-13 and for the same reason, *this trial cannot distinguish a real decayed effect from
no effect.* It is pre-committed to failing at the effect size we have actually measured. A pass
would mean the UK pre-holiday effect is materially larger than the American one.

## 6. Expected outcome, stated before running

**Fail.** Sign positive, one-sided p between 0.03 and 0.25, gap between +0.05 and +0.15 pts — the
same band as P3-13, because I have no UK-specific prior to narrow it with.

I expect the five-holiday subset to be **weaker** than the eight, since the UK packs three
holidays into the turn of the year. I made the same prediction for the US and it was wrong there,
which is a reason to state it again rather than quietly drop it.

## 7. What follows

Nothing trades, at any outcome. If it fails, **the pre-holiday family is closed** — two markets,
both under-powered, decay consistent with the literature — and the Nikkei is *not* run, because a
third under-powered fail adds nothing but a trial. If it passes, the interesting question is
whether the pass survives removing Good Friday, and that is a new pre-registration.
