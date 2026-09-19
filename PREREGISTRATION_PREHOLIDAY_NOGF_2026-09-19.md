# Pre-registration: does the FTSE pre-holiday pass survive without Easter?

**Written 2026-09-19 after P3-14 passed on the FTSE 100 (gap +0.1488 pts, Welch t +3.07,
p 0.0012; placebo p 0.0139; both halves positive). Committed before running. Trial P3-15.**
§7 of `PREREGISTRATION_PREHOLIDAY_FTSE_2026-09-19.md` named this as the next question.

## 0. What this trial is NOT — read before the result

**This is a decomposition of a result I have already seen, not an out-of-sample test.** The
per-holiday table from P3-14 is on the record and I know Good Friday is the strongest component.
Removing the strongest part of a set will weaken it; nothing here is a discovery. Writing a
specification now fixes the procedure but cannot restore ignorance, and pretending otherwise
would be the exact dishonesty this ledger exists to prevent.

Two things follow:

1. **§5 states the answer in advance, to two decimal places.** If the run lands where §5 says, it
   has confirmed arithmetic, not found anything. The trial is worth its slot because it decides
   how P3-14 is *described* in the record — as a general UK pre-holiday effect or as an Easter
   effect with company — and that is a real decision about a claim already made.
2. **The informative outcome is a PASS**, because a pass means the remaining holidays clear the
   bar without the strongest one. A fail was predictable from the table.

## 1. The event set — fixed

The P3-14 event set (252 sessions, FTSE 100, 1984-01-03 → 2026-09-11, UK calendar) **minus every
session whose label names Good Friday.**

**An unavoidable impurity, stated before the numbers.** In the UK those 43 sessions are labelled
*"Easter Monday + Good Friday"*, because the Thursday before Good Friday is also the session
before Easter Monday — the Friday, Saturday and Sunday are all non-trading. **So this test cannot
remove the shared holiday without also removing a UK-only one.** It is not a clean "drop the
American holiday" cut, and no cut on this data can be. What remains is **209 sessions** across
New Year's Day, the Early May, Spring and Summer Bank Holidays, and Christmas/Boxing Day.

## 2. Hypothesis, statistic and gate — fixed and binding

**With the Easter sessions removed, the mean daily FTSE return on the remaining pre-holiday
sessions still exceeds the mean on all other sessions.** "All other sessions" keeps its P3-14
meaning: every session that is not a pre-holiday session at all. The 43 removed Easter days are
dropped from the comparison entirely rather than moved into the control group, so the control
mean is unchanged at +0.0242%.

**The gate is stricter than P3-14's, and the change is made here rather than after the fact.**
P3-14 named Welch primary and the placebo a cross-check, and the two disagreed 11.8× because
pre-holiday sessions are about 30% less volatile (sd 0.7515% against 1.0744%). Both cleared 0.025
there, so nothing turned on it. **Here they will not both clear** — see §5 — so leaving the choice
open would be leaving myself a lever.

**P3-15 passes only if ALL of: Welch one-sided p < 0.025, placebo one-sided p < 0.025, and the gap
positive in both halves (1984–2004 / 2005–2026).** Requiring both statistics is strictly more
conservative than either, and it removes the choice of which to quote.

Reported, not gated: the per-holiday table for the remaining set; both halves; the event count.

## 3. Power

209 events. On the unconditional sd of 1.0744% the standard error is **0.0743 pts**, so the
placebo leg of the gate needs a gap of **+0.146 pts**. On the event-group sd of about 0.75% the
standard error is **0.0519 pts** and the Welch leg needs **+0.102 pts**. The two legs are 43%
apart, which is the whole reason §2 requires both.

## 4. What is NOT tested here

The S&P 500 is not re-cut. P3-13 failed as a whole and decomposing a failed trial to hunt for a
surviving component is precisely the dredging the gates exist to stop. Good Friday's US strength
(+0.375%, n 44) stays a reported diagnostic of P3-13 and nothing more.

## 5. Expected outcome, stated before running — with the arithmetic

From P3-14's published table: 252 events at +0.1730%, of which 43 at +0.3526%. The remaining 209
therefore average **(252 × 0.1730 − 43 × 0.3526) / 209 = +0.1361%**, for a gap of about
**+0.112 pts**.

| leg | needs | expected | verdict |
|---|---|---|---|
| Welch | +0.102 pts | +0.112 pts, t ≈ 2.16, p ≈ 0.016 | **passes, narrowly** |
| placebo | +0.146 pts | +0.112 pts, t ≈ 1.51, p ≈ 0.066 | **fails** |

**So I expect P3-15 to FAIL, on the placebo leg, with the Welch leg passing.** I expect both
halves to stay positive.

If that is what happens, the recorded reading of P3-14 becomes: *the FTSE pre-holiday effect
clears its gate, but not once Easter is taken out — the effect is concentrated in the Easter
session, which is shared with the US.* That is a materially weaker claim than "the pre-holiday
effect is alive in the UK", and it is the claim the record should carry.

If instead both legs clear, the UK effect is general rather than Easter-specific, and **that**
would be worth another market.

## 6. What follows

Nothing trades. On the expected fail, the pre-holiday family closes at: dead in the US, and in the
UK indistinguishable from an Easter effect. On a pass, the Nikkei becomes worth one trial —
Japanese holidays share nothing with either calendar — and that is a new pre-registration.
