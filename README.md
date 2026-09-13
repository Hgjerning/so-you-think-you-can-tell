# So You Think You Can Tell

Twelve pre-registered tests of US election, calendar and earnings-surprise effects on stock
indices and stocks, 1927–2026, each judged against a stated gate written down before the
numbers were computed. The article, with interactive charts:
**https://hgjerning.github.io/so-you-think-you-can-tell/**

Henrik Gjerning, September 2026. Title after a song by Pink Floyd; the question it asks is the same one.

## The verdicts

| # | hypothesis | verdict |
|---|---|---|
| P3-1 | S&P 500 unusual in the 60 days after a presidential election (25 elections) | fail — it is the market's drift |
| P3-2 | post-election return differs by winner's party | fail |
| P3-3 | the 60 days into the election are unusual | fail |
| P3-4 | 90 days after a midterm election (24 midterms) | suggestive (p 0.04), fails the gate |
| P3-5 | some calendar month is unusual, Bonferroni 12 + same sign in both halves | **September passes** |
| P3-6 | Sell in May after its 2002 publication | fail |
| P3-7 … P3-10 | September on STOXX 600, MSCI World, FTSE 100, Nikkei 225 | MSCI World passes (it is the S&P again); the three non-US indices have the sign and not the significance |
| P3-11 | post-filing earnings drift, Sharadar point-in-time S&P 500 2013–2026 | fail |
| P3-12 | post-announcement earnings drift, 137k announcements 1997–2012, three regions | fail — the announcement reads (t 29), the drift does not (t 1.4) |

Predictions were written down before each run and scored: ten of twelve right; the two misses
are the two surprises (September, predicted fail; announcement drift, predicted pass).

## What is here

- `index.html` — the article (interactive charts; every number generated from `Data/results/`).
- `PREREGISTRATION_*.md` — the specs: data, windows, statistics, gates and predicted outcomes, committed before running.
- `TRIAL_LEDGER.md` — the count, one row per hypothesis, added before the run.
- `Data/results/` — every CSV the article is built from. `Data/us_presidential_elections.csv` — winners and parties.
- `eventstudies/core.py` — index-level machinery with placebo inference; `eventstudies/firm.py` — firm-level machinery (market-adjusted abnormal returns, calendar-time portfolios); `tests/` — 16 tests, each guard proved by making it fail first.
- `run_*.py` — the trials as run; `build_article.py`, `build_linkedin.py` — the article and its LinkedIn package; `linkedin/` — text and PNG charts.
- `CANDIDATES.md` — the events not (yet) tested and what each would cost.

Not here: the daily index prices (Yahoo, regenerable with the snippet in `build_article.py`'s
sibling README in the private working repo), the Sharadar fundamentals and price caches, and
the ART database pulls, all of which are licensed or private data. Only aggregates derived from
them are published.

## Method in one paragraph

For index-level events the statistic is the mean window return over the N events, and its null
distribution is the same mean over N randomly placed windows of the same length drawn from the
whole history (10,000 draws). That removes the unconditional drift from every "stocks rise
after X" claim: the S&P 500 rose after most things. Party differences use permutations; calendar
months a Welch t with a Bonferroni-12 correction and a same-sign-in-both-halves condition; Sell
in May a paired t on non-overlapping annual differences, gated on the post-publication sample.
For firm-level events: market-adjusted abnormal returns (no fitted intercept — the fitted
intercept manufactures a reversal on earnings-sorted firms), a legibility check that the
announcement itself is visible, and a calendar-time long-short portfolio with Newey–West errors
as the primary statistic.

## Licence

Not yet stated; all rights reserved until the author adds one.
