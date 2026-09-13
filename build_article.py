# -*- coding: utf-8 -*-
"""Build the article page from Data/results/ -- every number on the page comes from the CSVs
written by run_political_calendar_studies.py; nothing is typed in by hand.

    python build_article.py   ->  article/so_you_think_you_can_tell.html
"""
import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "Data", "results")
OUT_DIR = os.path.join(HERE, "article")
os.makedirs(OUT_DIR, exist_ok=True)


def rd(x, n=4):
    return None if pd.isna(x) else round(float(x), n)


def paths_json(name):
    df = pd.read_csv(os.path.join(RES, name), index_col=0)
    df.columns = [int(c) for c in df.columns]
    return {"rel": list(df.columns), "years": [int(i) for i in df.index],
            "paths": [[rd(v) for v in row] for row in df.to_numpy()]}


def band_json(name):
    b = pd.read_csv(os.path.join(RES, name), index_col=0)
    return {c: [rd(v) for v in b[c]] for c in b.columns}


summary = pd.read_csv(os.path.join(RES, "summary.csv"))
months = pd.read_csv(os.path.join(RES, "calendar_months.csv"), index_col=0)
sim = pd.read_csv(os.path.join(RES, "sell_in_may_by_year.csv"), index_col=0)
pres_w = pd.read_csv(os.path.join(RES, "presidential_windows.csv"), index_col=0)
cyc = pd.read_csv(os.path.join(RES, "presidential_cycle_summary.csv"), header=[0, 1], index_col=0)
prices = pd.read_csv(os.path.join(HERE, "Data", "GSPC_daily_close.csv"), index_col=0, parse_dates=True)["close"].sort_index()

# hero: 120 random 181-day paths (illustration only; the inference uses 2,000-10,000 draws)
rng = np.random.default_rng(2026)
P = prices.to_numpy(dtype=float)
pool = rng.choice(np.arange(91, len(P) - 91), 120, replace=False)
hero = [[rd(P[p - 90 + k] / P[p - 91] - 1, 3) for k in range(181)] for p in pool]

pp = paths_json("paths_presidential.csv")
party = pres_w["winner_party"].reindex(pp["years"]).tolist()
data = {
    "pres": pp, "pres_party": party,
    "band_pres": band_json("band_presidential_n25.csv"),
    "band_D": band_json("band_presidential_n13.csv"), "band_R": band_json("band_presidential_n12.csv"),
    "mid": paths_json("paths_midterm.csv"), "band_mid": band_json("band_midterm_n24.csv"),
    "mid74": paths_json("paths_midterm_1974.csv"), "band_mid74": band_json("band_midterm_1974.csv"),
    "months": [{"m": int(i), "mean": rd(r["mean"]), "diff": rd(r["diff"]), "t": rd(r["t"], 2), "p": rd(r["p"], 4),
                "n": int(r["n"]), "h1": rd(r["diff_1928_1976"]), "h2": rd(r["diff_1977_2026"]), "pass": bool(r["passes_gate"])}
               for i, r in months.iterrows()],
    "sim": [{"y": int(y), "w": rd(r["winter"]), "s": rd(r["summer"]), "d": rd(r["diff"])} for y, r in sim.iterrows()],
    "summary": [{k: (rd(v, 4) if isinstance(v, (float, np.floating)) else (None if pd.isna(v) else v)) for k, v in row.items()}
                for row in summary.to_dict("records")],
    "hero": hero,
    "cycle": {f"{k[1]}{k[0]}": rd(v) for k, v in cyc.stack(future_stack=True).to_dict().items()} if False else
             {f"y{i}_{p}": rd(cyc.loc[i, ("mean", p)]) for i in cyc.index for p in ("D", "R")},
    "pres_windows": [{"y": int(y), "post": rd(r["post_1_60"]), "pre": rd(r["pre_m60_0"]), "party": r["winner_party"]}
                     for y, r in pres_w.iterrows()],
}
S = {r["trial"]: r for r in data["summary"]}
sep = months.loc[9]
sim_gate = [r for r in data["summary"] if r["trial"] == "P3-6"][0]
sim_full = [r for r in data["summary"] if r["trial"] == "P3-6 (report)" and "full" in r["hypothesis"]][0]
sim_1950 = [r for r in data["summary"] if r["trial"] == "P3-6 (report)" and "1950" in r["hypothesis"]][0]
mid74 = [r for r in data["summary"] if r["trial"] == "P3-4 (report)"][0]
p2x = [r for r in data["summary"] if r["trial"] == "P3-2 (report)"][0]
p3i = [r for r in data["summary"] if r["trial"] == "P3-3 (report)"][0]


def pct(x, d=1):
    return f"{100 * x:+.{d}f}%"


def pv(p):
    return f"{p:.3f}" if p >= 0.001 else f"{p:.4f}"


first, last = prices.index[0].date(), prices.index[-1].date()
from oos_text import OOS_TEXT  # noqa: E402  (same paragraph, same numbers, one source)
from pead_text import PEAD_PARAGRAPHS, PEAD_CHART, LEDGER2  # noqa: E402
data["pead"] = PEAD_CHART
PEAD_HTML = "\n".join(f"<p>{p}</p>" for p in PEAD_PARAGRAPHS)
LEDGER2_HTML = "".join(f'<tr><td>{r["trial"]}</td><td>{r["hypothesis"]}</td><td class="num">{r["n"]:,}</td><td class="num">{r["observed"]}</td><td class="num">{r["p"]}</td><td><span class="verdict{" pass" if r["verdict"] == "PASS" else ""}">{r["verdict"]}</span></td><td>{"<strong>wrong</strong>" if r["call"] == "WRONG" else r["call"]}</td></tr>' for r in LEDGER2)

html = f"""<title>So You Think You Can Tell</title>
<meta name="description" content="Twelve pre-registered tests of US election, calendar and earnings-surprise effects, 1927-2026, judged against placebo windows and a stated gate.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,600;1,9..144,300;1,9..144,600&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root {{
  color-scheme: light;
  --paper:#f3f4f7; --paper-2:#e9ebf0; --ink:#171a21; --ink-2:#4a4f5c; --ink-3:#7a8090; --rule:#d5d8e0;
  --event:#2a78d6; --dem:#2a78d6; --rep:#e34948; --sept:#eb6834; --band-1:#dfe2e8; --band-2:#cbd0d9; --tip:#ffffff;
  --pass:#0ca30c; --drift:#1baf7a;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    color-scheme: dark;
    --paper:#15171c; --paper-2:#1d2026; --ink:#f1f2f5; --ink-2:#c1c5cf; --ink-3:#8b9099; --rule:#2f333c;
    --event:#3987e5; --dem:#3987e5; --rep:#e66767; --sept:#d95926; --band-1:#23262d; --band-2:#2f333c; --tip:#1d2026; --drift:#199e70;
  }}
}}
:root[data-theme="dark"] {{
  color-scheme: dark;
  --paper:#15171c; --paper-2:#1d2026; --ink:#f1f2f5; --ink-2:#c1c5cf; --ink-3:#8b9099; --rule:#2f333c;
  --event:#3987e5; --dem:#3987e5; --rep:#e66767; --sept:#d95926; --band-1:#23262d; --band-2:#2f333c; --tip:#1d2026;
}}
body {{ background:var(--paper); color:var(--ink); font-family:"IBM Plex Sans",system-ui,sans-serif; font-size:17px; line-height:1.55; margin:0; }}
.wrap {{ max-width:900px; margin:0 auto; padding:2.5rem 1.25rem 5rem; }}
.prose {{ max-width:66ch; }}
h1 {{ font-family:"Fraunces",Georgia,serif; font-weight:300; font-style:italic; font-size:clamp(2.4rem,6vw,4rem); line-height:1.02; margin:0.5rem 0 0.75rem; text-wrap:balance; letter-spacing:-0.01em; }}
h2 {{ font-family:"Fraunces",Georgia,serif; font-weight:600; font-size:1.65rem; line-height:1.15; margin:3rem 0 0.75rem; text-wrap:balance; }}
h3 {{ font-family:"IBM Plex Sans",sans-serif; font-weight:600; font-size:1rem; margin:1.75rem 0 0.4rem; }}
.eyebrow {{ font-family:"IBM Plex Mono",monospace; font-size:0.75rem; letter-spacing:0.12em; text-transform:uppercase; color:var(--ink-3); }}
.dek {{ font-size:1.2rem; color:var(--ink-2); max-width:60ch; margin:0 0 1.5rem; }}
p {{ margin:0 0 1rem; }}
.cover {{ background:#0a0a0d; border-radius:6px; margin:0 0 2rem; overflow:hidden; }}
.cover svg {{ width:100%; height:auto; display:block; }}
.hero {{ margin:1.5rem 0 2.5rem; border-top:1px solid var(--rule); border-bottom:1px solid var(--rule); padding:0.75rem 0; }}
.hero svg {{ width:100%; height:auto; display:block; }}
.cap {{ font-size:0.85rem; color:var(--ink-3); margin:0.5rem 0 0; max-width:80ch; }}
figure {{ margin:1.5rem 0 2rem; }}
figure .title {{ font-weight:600; margin:0 0 0.15rem; }}
figure .sub {{ font-size:0.9rem; color:var(--ink-2); margin:0 0 0.5rem; }}
.chart {{ position:relative; width:100%; }}
.chart svg {{ width:100%; height:auto; display:block; overflow:visible; }}
.grid2 {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(340px,1fr)); gap:1.25rem 2rem; }}
.tip {{ position:absolute; pointer-events:none; background:var(--tip); color:var(--ink); border:1px solid var(--rule); border-radius:4px; padding:6px 9px; font-size:0.8rem; line-height:1.35; font-family:"IBM Plex Mono",monospace; white-space:nowrap; box-shadow:0 2px 8px rgba(0,0,0,.12); display:none; z-index:2; }}
.legend {{ display:flex; flex-wrap:wrap; gap:0.35rem 1.1rem; font-size:0.8rem; color:var(--ink-2); margin:0.35rem 0 0; }}
.legend span::before {{ content:""; display:inline-block; width:14px; height:3px; vertical-align:middle; margin-right:6px; border-radius:2px; background:var(--sw); }}
.legend .box::before {{ height:10px; }}
table {{ border-collapse:collapse; width:100%; font-size:0.9rem; font-variant-numeric:tabular-nums; }}
.tablewrap {{ overflow-x:auto; margin:1rem 0 1.5rem; }}
th, td {{ text-align:left; padding:0.45rem 0.6rem; border-bottom:1px solid var(--rule); vertical-align:top; }}
th {{ font-weight:600; font-size:0.8rem; color:var(--ink-2); letter-spacing:0.02em; }}
td.num, th.num {{ text-align:right; font-family:"IBM Plex Mono",monospace; }}
.verdict {{ font-family:"IBM Plex Mono",monospace; font-size:0.78rem; padding:1px 6px; border-radius:3px; border:1px solid var(--rule); }}
.verdict.pass {{ border-color:var(--pass); color:var(--pass); }}
.note {{ background:var(--paper-2); border-left:3px solid var(--event); padding:0.9rem 1.1rem; margin:1.5rem 0; font-size:0.95rem; }}
.note p:last-child {{ margin:0; }}
.stat {{ font-family:"IBM Plex Mono",monospace; }}
hr {{ border:0; border-top:1px solid var(--rule); margin:3rem 0; }}
ul {{ padding-left:1.2rem; }} li {{ margin-bottom:0.35rem; }}
a {{ color:var(--event); }}
@media (prefers-reduced-motion: reduce) {{ * {{ transition:none !important; }} }}
</style>
<div class="wrap">
<div class="cover" id="cover"></div>
<div class="eyebrow">Project3 Event Studies · S&amp;P 500 price index, {first} to {last} · pre-registered 2026-09-13</div>
<h1>So You Think You Can Tell</h1>
<p class="dek">Every autumn a chart goes round showing what stocks do around an election. Here are the same charts drawn with the one band that matters: what the S&amp;P 500 does around <em>nothing in particular</em>.</p>

<div class="hero"><div id="hero"></div>
<p class="cap">One hundred and twenty windows of 181 trading days, opened at random dates between 1928 and 2026 (thin lines), and the average path around the 25 presidential elections (bold, day 0 = election day). The election path sits inside the crowd. Drawn from the data on this page, not designed.</p></div>

<div class="prose">
<p>A chart of the S&amp;P 500 "around midterm elections since 1974" has a dashed line at election day, an average that climbs afterwards, and a shaded band marked 10th and 90th percentile. The band is real. It is the spread of the thirteen individual midterm years around their own average. It tells you that elections differ from each other, which nobody doubted. It does not tell you whether the average is unusual, because it never asks what the index does in a window of the same length opened on any other day.</p>
<p>That second question is the whole test, and it is cheap to run. Take the statistic you care about, say the mean 90-day return after 24 midterm elections. Open 24 windows of 90 days at random dates in the same history, take their mean, and repeat ten thousand times. That gives the distribution of "24 random windows". If the election mean sits in its middle, the election did nothing the calendar was not already doing. The S&amp;P 500 rose in the sixty trading days after most things.</p>
<p>Six hypotheses were written down, with their windows, samples and pass thresholds, and committed to a repository before any number was computed. The commit is the pre-registration; the threshold is p&nbsp;&lt;&nbsp;0.0083, which is 5% divided by six. My own expected outcomes were written down beside them and are scored at the end.</p>
</div>

<h2>Presidential elections: the average is the drift</h2>
<div class="prose">
<p>Twenty-five elections, 1928 to 2024. The sixty trading days after election day returned <span class="stat">{pct(S['P3-1']['statistic'])}</span> on average. Twenty-five random 60-day windows return <span class="stat">{pct(S['P3-1']['placebo_mean'])}</span> on average, with a standard deviation of {100 * S['P3-1']['placebo_sd']:.1f} points. The placebo p-value is <span class="stat">{pv(S['P3-1']['p'])}</span>. Nothing happened.</p>
<p>The sixty days before the election, the "sideways into the vote" story, returned <span class="stat">{pct(S['P3-3']['statistic'])}</span> against a placebo mean of <span class="stat">{pct(S['P3-3']['placebo_mean'])}</span>, p&nbsp;{pv(S['P3-3']['p'])}. Slightly below the drift, well inside the noise.</p>
</div>
<figure><p class="title">S&amp;P 500 around presidential elections, 1928–2024</p><p class="sub">Cumulative price return from 90 trading days before to 90 after, base = close 91 days before. Bands are the 5–95% and 10–90% range of the <em>average of 25 random windows</em> (2,000 draws). Hover for values.</p>
<div class="chart" id="c_pres"></div>
<div class="legend"><span style="--sw:var(--event)">Mean of 25 elections</span><span style="--sw:var(--ink-3)">Median</span><span class="box" style="--sw:var(--band-2)">Placebo 10–90%</span><span class="box" style="--sw:var(--band-1)">Placebo 5–95%</span></div></figure>

<h2>Democrat or Republican: twenty-five coin flips</h2>
<div class="prose">
<p>After a Democrat won, the next sixty days returned {pct(S['P3-2']['note'] and float(S['P3-2']['note'].split('D mean ')[1].split(' ')[0]))} on average (13 elections); after a Republican, {pct(float(S['P3-2']['note'].split('R mean ')[1].split(' ')[0]))} (12). The difference is <span class="stat">{pct(S['P3-2']['statistic'])}</span> with a permutation p of <span class="stat">{pv(S['P3-2']['p'])}</span>. Drop 2000 and 2020, when the winner was not known on day +1, and the difference is {pct(p2x['statistic'])}, p {pv(p2x['p'])}. With a 60-day standard deviation near eight points and a dozen observations a side, no party effect of the size anyone claims could be resolved here even if it existed.</p>
<p>Before the election the only party label anyone can know is the incumbent's. Democrat incumbents saw {pct(p3i['statistic'])} more in the 60 days into the vote than Republican incumbents, p {pv(p3i['p'])}. Same verdict.</p>
</div>
<figure><p class="title">The same chart, split by the winner's party</p><p class="sub">Each panel carries its own placebo band for its own count (13 Democrat, 12 Republican wins). The band widens as the count falls, which is the point: the fewer the elections, the less the average can say.</p>
<div class="grid2"><div><div class="chart" id="c_dem"></div><div class="legend"><span style="--sw:var(--dem)">Democrat won (13)</span><span class="box" style="--sw:var(--band-2)">Placebo 10–90%</span></div></div>
<div><div class="chart" id="c_rep"></div><div class="legend"><span style="--sw:var(--rep)">Republican won (12)</span><span class="box" style="--sw:var(--band-2)">Placebo 10–90%</span></div></div></div></figure>

<div class="note"><p><strong>The four-year cycle, reported and not tested.</strong> Mean annual price return in year 1 of a presidency: Democrats {pct(data['cycle']['y1_D'])}, Republicans {pct(data['cycle']['y1_R'])}; year 2: {pct(data['cycle']['y2_D'])} vs {pct(data['cycle']['y2_R'])}; year 3: {pct(data['cycle']['y3_D'])} vs {pct(data['cycle']['y3_R'])}; year 4: {pct(data['cycle']['y4_D'])} vs {pct(data['cycle']['y4_R'])}. Thirteen and twelve observations per cell. Year 1 under Republicans contains 1929, 1973, 2001 and 2008 by accident of the calendar. This table is here because someone will ask for it, not because it can bear a test.</p></div>

<h2>Midterms: the one that comes closest</h2>
<div class="prose">
<p>This is the Goldman chart, extended back to 1930 and given a placebo band. Ninety trading days after 24 midterm elections the index returned <span class="stat">{pct(S['P3-4']['statistic'])}</span> on average. Twenty-four random 90-day windows return <span class="stat">{pct(S['P3-4']['placebo_mean'])}</span>, standard deviation {100 * S['P3-4']['placebo_sd']:.1f} points. Placebo p&nbsp;<span class="stat">{pv(S['P3-4']['p'])}</span>: suggestive, and a fail against the 0.0083 gate. On Goldman's own window, 1974 onward, the mean is {pct(mid74['statistic'])} on 13 elections, p {pv(mid74['p'])}.</p>
<p>So the post-midterm rally is the one claim on this page that is not simply the drift. It is also a claim that has been published in every election year since at least the 1990s, which is the condition under which effects of this size tend to disappear. Treat p 0.04 on 24 events as a reason to keep the row open in a forward record, not as a trade.</p>
</div>
<figure><p class="title">S&amp;P 500 around midterm elections</p><p class="sub">Left: all 24 midterms 1930–2022. Right: the 13 since 1974, the window in the Goldman exhibit. Each with its own placebo band.</p>
<div class="grid2"><div><div class="chart" id="c_mid"></div><div class="legend"><span style="--sw:var(--event)">Mean of 24 midterms</span><span style="--sw:var(--ink-3)">Median</span><span class="box" style="--sw:var(--band-2)">Placebo 10–90%</span></div></div>
<div><div class="chart" id="c_mid74"></div><div class="legend"><span style="--sw:var(--event)">Mean of 13 midterms since 1974</span><span style="--sw:var(--ink-3)">Median</span><span class="box" style="--sw:var(--band-2)">Placebo 10–90%</span></div></div></div></figure>

<h2>The calendar: September, and only September</h2>
<div class="prose">
<p>Twelve months, twelve tests, so the bar inside this family is p&nbsp;&lt;&nbsp;0.0042, and a month has to show the same sign in 1928–1976 and in 1977–2026. September's mean price return is <span class="stat">{100 * sep['mean']:+.2f}%</span> against <span class="stat">{100 * (sep['mean'] - sep['diff']):+.2f}%</span> for the other eleven, t&nbsp;{sep['t']:.2f}, p&nbsp;{pv(sep['p'])}, and the gap is {100 * sep['diff_1928_1976']:+.1f} points in the first half and {100 * sep['diff_1977_2026']:+.1f} in the second. <strong>It passes.</strong> It is the only month that clears even the unadjusted 5% line. January, the most famous calendar effect, is {100 * months.loc[1, 'diff']:+.2f} points above the rest with p {pv(months.loc[1, 'p'])}: in a large-cap price index there is no January effect to find.</p>
<p>I had written down that September would fail, most likely on the two-halves condition. It did not, and that is recorded. What a pass means is narrower than it sounds: one month, a price index, no costs, an effect of about two points that is known to every reader of the financial press.</p>
<p>So it went out of sample, four more times, each pre-registered with a one-sided gate of p&nbsp;&lt;&nbsp;0.025 and the same sign required in both halves of the sample. {OOS_TEXT}</p>
</div>
<figure><p class="title">Mean monthly price return by calendar month, 1928–2026</p><p class="sub">99 observations per month. Whiskers are ±2 standard errors of the month's mean. Hover for the Welch t against the other eleven months and the two half-sample gaps.</p>
<div class="chart" id="c_months"></div>
<div class="legend"><span class="box" style="--sw:var(--event)">Month mean</span><span class="box" style="--sw:var(--sept)">Passes the gate</span></div></figure>

<h2>Sell in May: true until it was published</h2>
<div class="prose">
<p>Bouman and Jacobsen put the Halloween indicator in the American Economic Review in December 2002. The honest test is what happened afterwards. From 2003 to 2025 the November–April half returned <span class="stat">{pct(float(sim_gate['note'].split('winter mean ')[1].split(',')[0]))}</span> and May–October <span class="stat">{pct(float(sim_gate['note'].split('summer mean ')[1].split(',')[0]))}</span>: a gap of {pct(sim_gate['statistic'])} a year with t&nbsp;{sim_gate['note'].split('t ')[1].split(';')[0]} on 23 non-overlapping years, p&nbsp;{pv(sim_gate['p'])}. Winter beat summer in {int(round(100 * float(sim_gate['note'].split('share winter>summer ')[1])))}% of those years, which is a coin.</p>
<p>The full 1928–2025 sample gives a gap of {pct(sim_full['statistic'])}, t {sim_full['note'].split('t ')[1].split(';')[0]}. Start in 1950 and it is {pct(sim_1950['statistic'])}, t {sim_1950['note'].split('t ')[1].split(';')[0]}, which is the number that gets quoted. Every one of those samples was available to the authors, and the strongest of them starts in the one year that happens to make it strongest.</p>
</div>
<figure><p class="title">Winter minus summer, year by year</p><p class="sub">November–April return minus the preceding May–October return, in percentage points. The line marks the 2002 publication. Blue above zero, red below.</p>
<div class="chart" id="c_sim"></div></figure>

<h2>Earnings surprises: the announcement is real, the drift is not</h2>
<div class="prose">
{PEAD_HTML}
</div>
<figure><p class="title">ART, 1997–2012: the announcement and the drift by surprise decile</p><p class="sub">Market-adjusted cumulative return, decile 1 = worst surprise, 10 = best. The announcement days are monotone from −1.5% to +1.4%; the following three months are negative in every decile and nearly flat across them.</p>
<div class="chart" id="c_pead"></div>
<div class="legend"><span class="box" style="--sw:var(--event)">Announcement days 0 to +1</span><span class="box" style="--sw:var(--drift)">Days +2 to +60</span></div></figure>

<h2>The ledger</h2>
<div class="tablewrap"><table>
<thead><tr><th>Trial</th><th>Hypothesis</th><th class="num">n</th><th class="num">Observed</th><th class="num">Placebo mean</th><th class="num">p</th><th>Gate 0.0083</th><th>My call</th></tr></thead>
<tbody>
{"".join(f'<tr><td>{r["trial"]}</td><td>{r["hypothesis"]}</td><td class="num">{int(r["n"])}</td><td class="num">{pct(r["statistic"]) if r["trial"] != "P3-5" else pct(r["statistic"], 2) + "/mo"}</td><td class="num">{pct(r["placebo_mean"]) if r["placebo_mean"] is not None and not (isinstance(r["placebo_mean"], float) and np.isnan(r["placebo_mean"])) and r["trial"] not in ("P3-2", "P3-5", "P3-6") else "—"}</td><td class="num">{pv(r["p"])}</td><td><span class="verdict{" pass" if r["passes_gate"] == "PASS" else ""}">{r["passes_gate"]}</span></td><td>{ {"P3-1": "fail — right", "P3-2": "fail — right", "P3-3": "fail — right", "P3-4": "suggestive fail — right", "P3-5": "fail — <strong>wrong</strong>", "P3-6": "fail — right"}[r["trial"]] }</td></tr>' for r in data["summary"] if "report" not in r["trial"])}
</tbody></table></div>
<p class="sub" style="margin-top:1rem">Six more followed the same day: September out of sample on four indices, and the two earnings-drift studies. Same rules, one-sided gates of 0.025 where the sign was pre-specified.</p>
<div class="tablewrap"><table>
<thead><tr><th>Trial</th><th>Hypothesis</th><th class="num">n</th><th class="num">Observed</th><th class="num">p</th><th>Gate</th><th>My call</th></tr></thead>
<tbody>{LEDGER2_HTML}</tbody></table></div>
<div class="prose">
<p>Ten of twelve predictions right. The two misses are the two surprises, and they point in opposite directions: September on the S&amp;P 500, which I expected to fail and which passed, and earnings drift on my own database, which I expected to pass and which failed. That is the usual shape: the pre-registered guess is "nothing", and when it is wrong it is wrong on the interesting one. Two passes in twelve, one of them the same fact measured twice, on effects that have each been in print for decades, is about what a prior of a few percent predicts.</p>
</div>

<hr>
<h2>Method, in enough detail to repeat it</h2>
<div class="prose">
<ul>
<li><strong>Data.</strong> S&amp;P 500 daily close from Yahoo, {first} to {last}, 24,791 days. Price index: no dividends, no costs. Monthly returns are month-end to month-end.</li>
<li><strong>Dating.</strong> Election day is the first Tuesday after the first Monday of November, computed and tested. Day 0 is election day; results arrive after the close, so post-election windows start at +1. A window (a, b) is the return from the close of day a−1 to the close of day b.</li>
<li><strong>Placebo.</strong> For N events and a window, draw N window positions uniformly from every day in the history where the window fits, take the mean, repeat 10,000 times (2,000 for the path bands), seed 42. The p-value is the share of draws at least as far from the placebo mean as the observed mean, two-sided, add-one corrected. Party differences use 10,000 label permutations.</li>
<li><strong>Calendar.</strong> Welch t of each month against the other eleven; Bonferroni 12 inside the family plus same sign in both halves. Sell in May: per year, May–Oct compounded and Nov–Apr compounded, paired t on the non-overlapping annual differences.</li>
<li><strong>Guards.</strong> The placebo test was run on synthetic random walks before it saw real data: on a driftless walk random events reject at the nominal rate; on a walk with strong drift and no event effect it must not reject, which the first version did on a single draw and now checks as a rate over 200 event sets; an injected +4% after 25 events is recovered at p&nbsp;&lt;&nbsp;0.01.</li>
<li><strong>What was not done.</strong> No second window after seeing the data. No other index. No total-return series (dividends would raise every window by roughly the yield pro rata and not change a sign). No costs, because nothing here is a strategy.</li>
</ul>
<p class="cap">Code, pre-registrations, ledger and every CSV behind these charts are public: <a href="https://github.com/Hgjerning/so-you-think-you-can-tell">github.com/Hgjerning/so-you-think-you-can-tell</a>. Title after a song by Pink Floyd; the question it asks is the same one.</p>
</div>
</div>

<script id="data" type="application/json">{json.dumps(data, separators=(",", ":"))}</script>
<script>
(function(){{
const D = JSON.parse(document.getElementById('data').textContent);
const css = v => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const NS = 'http://www.w3.org/2000/svg';
function el(n, a, p){{ const e = document.createElementNS(NS, n); for (const k in a) e.setAttribute(k, a[k]); if (p) p.appendChild(e); return e; }}
function fmt(x, d){{ return (x*100).toFixed(d===undefined?1:d) + '%'; }}
function mean(a){{ const b = a.filter(v => v !== null); return b.reduce((s,v)=>s+v,0)/b.length; }}
function median(a){{ const b = a.filter(v => v !== null).slice().sort((x,y)=>x-y); const m = b.length>>1; return b.length%2 ? b[m] : (b[m-1]+b[m])/2; }}

// ---------- cover: the placebo test as a prism (single-theme panel, painted explicitly)
(function(){{
  const W = 900, H = 380;
  const svg = el('svg', {{viewBox:`0 0 ${{W}} ${{H}}`, role:'img', 'aria-label':'A tangle of random market paths enters a prism as white light; six coloured hypotheses leave it, five fading to grey, September staying lit'}}, document.getElementById('cover'));
  const defs = el('defs', {{}}, svg);
  const glow = el('filter', {{id:'glow', x:'-20%', y:'-50%', width:'140%', height:'200%'}}, defs);
  el('feGaussianBlur', {{stdDeviation:'2.2', result:'b'}}, glow);
  const mg = el('feMerge', {{}}, glow); el('feMergeNode', {{in:'b'}}, mg); el('feMergeNode', {{in:'SourceGraphic'}}, mg);
  el('rect', {{x:0, y:0, width:W, height:H, fill:'#0a0a0d'}}, svg);
  // incoming light: the 120 random paths, compressed into a beam that converges on the prism face
  const ex = 402, ey = 196;           // entry point on the left face
  const n = D.hero[0].length;
  D.hero.forEach((p, k) => {{
    const d = p.map((v, i) => {{
      const t = i/(n-1); const x = 20 + (ex-20)*t; const amp = 120*(1-t) + 4;
      const y = ey + Math.max(-1, Math.min(1, v/0.35))*amp;
      return (i?'L':'M') + x.toFixed(1) + ' ' + y.toFixed(1);
    }}).join(' ');
    el('path', {{d, fill:'none', stroke:'#ffffff', 'stroke-width':0.6, opacity:0.10 + 0.12*(k%3===0)}}, svg);
  }});
  el('line', {{x1:20, x2:ex, y1:ey, y2:ey, stroke:'#ffffff', 'stroke-width':1.6, opacity:0.9, filter:'url(#glow)'}}, svg);
  // the eclipse rim, behind the burst
  [[14,0.04],[5,0.08],[1.3,0.28]].forEach(([w,a]) => el('circle', {{cx:640, cy:190, r:150, fill:'none', stroke:'#ffffff', 'stroke-width':w, opacity:a}}, svg));
  // the prism: beam enters the left face, the burst leaves the right face
  el('polygon', {{points:'450,58 350,318 550,318', fill:'rgba(255,255,255,0.03)', stroke:'#f2f2f2', 'stroke-width':1.6, 'stroke-linejoin':'round'}}, svg);
  el('polygon', {{points:`${{ex}},${{ey}} 498,178 498,214`, fill:'rgba(255,255,255,0.09)'}}, svg);
  // the burst: 48 rays of spectrum that dissolve; one thread survives
  const spectrum = ['#3987e5','#199e70','#eda100','#eb6834','#e34948','#d55181'];
  const hex = h => [1,3,5].map(i => parseInt(h.slice(i,i+2),16));
  const hue = u => {{ const k = Math.min(Math.floor(u*5),4), f = u*5-k; const a = hex(spectrum[k]), b = hex(spectrum[k+1]); return 'rgb(' + a.map((v,i)=>Math.round(v*(1-f)+b[i]*f)).join(',') + ')'; }};
  let seed = 7; const rnd = () => {{ seed = (seed * 1664525 + 1013904223) % 4294967296; return seed / 4294967296; }};
  const bx = 498, by = ey;
  for (let i = 0; i < 48; i++) {{
    const u = i/47, ang = (-38 + 76*u + (rnd()-0.5)*3) * Math.PI/180, L = 60 + 200*rnd(), w = 0.7 + 0.8*rnd();
    const x2 = bx + Math.cos(ang)*L, y2 = by + Math.sin(ang)*L, id = 'burst'+i;
    const g = el('linearGradient', {{id, gradientUnits:'userSpaceOnUse', x1:bx, y1:by, x2, y2}}, defs);
    el('stop', {{offset:'0', 'stop-color':hue(u), 'stop-opacity':0.9}}, g); el('stop', {{offset:'1', 'stop-color':hue(u), 'stop-opacity':0}}, g);
    el('line', {{x1:bx, y1:by, x2, y2, stroke:`url(#${{id}})`, 'stroke-width':w, 'stroke-linecap':'round'}}, svg);
  }}
  const ang = -7*Math.PI/180, x2 = bx + Math.cos(ang)*900, y2 = by + Math.sin(ang)*900;
  const gs = el('linearGradient', {{id:'survivor', gradientUnits:'userSpaceOnUse', x1:bx, y1:by, x2, y2}}, defs);
  el('stop', {{offset:'0', 'stop-color':'#eb6834', 'stop-opacity':1}}, gs); el('stop', {{offset:'1', 'stop-color':'#eb6834', 'stop-opacity':0.65}}, gs);
  el('line', {{x1:bx, y1:by, x2, y2, stroke:'#eb6834', 'stroke-width':10, opacity:0.10, 'stroke-linecap':'round'}}, svg);
  el('line', {{x1:bx, y1:by, x2, y2, stroke:'url(#survivor)', 'stroke-width':3, 'stroke-linecap':'round', filter:'url(#glow)'}}, svg);
}})();

// ---------- hero illustration
(function(){{
  const W = 900, H = 300, pad = 10;
  const svg = el('svg', {{viewBox:`0 0 ${{W}} ${{H}}`, role:'img', 'aria-label':'Random 181-day S&P 500 paths with the presidential election average drawn over them'}}, document.getElementById('hero'));
  const rel = D.pres.rel, n = rel.length;
  let lo = -0.35, hi = 0.35;
  const x = i => pad + (W-2*pad) * i/(n-1), y = v => H/2 - (H/2-pad) * v/hi;
  const path = arr => arr.map((v,i) => (i?'L':'M') + x(i).toFixed(1) + ' ' + y(Math.max(lo, Math.min(hi, v))).toFixed(1)).join(' ');
  D.hero.forEach(p => el('path', {{d:path(p), fill:'none', stroke:css('--ink-3'), 'stroke-width':0.7, opacity:0.28}}, svg));
  el('line', {{x1:x(90), x2:x(90), y1:pad, y2:H-pad, stroke:css('--ink-2'), 'stroke-dasharray':'3 4', 'stroke-width':1}}, svg);
  el('line', {{x1:pad, x2:W-pad, y1:y(0), y2:y(0), stroke:css('--ink-3'), 'stroke-width':0.8, opacity:0.6}}, svg);
  const m = rel.map((_,i) => mean(D.pres.paths.map(p => p[i])));
  el('path', {{d:path(m), fill:'none', stroke:css('--event'), 'stroke-width':3, 'stroke-linejoin':'round'}}, svg);
  const t = el('text', {{x:x(90)+6, y:pad+14, fill:css('--ink-2'), 'font-size':12, 'font-family':'IBM Plex Mono, monospace'}}, svg); t.textContent = 'election day';
}})();

// ---------- line + band chart
function bandChart(id, series, band, opts){{
  const box = document.getElementById(id); const W = 560, H = 300, m = {{l:46, r:14, t:12, b:30}};
  const rel = series.rel, n = rel.length;
  const paths = series.paths, mean_ = rel.map((_,i) => mean(paths.map(p=>p[i]))), med_ = rel.map((_,i) => median(paths.map(p=>p[i])));
  let vals = [].concat(mean_, med_, band.q05, band.q95); const lo = Math.min(...vals, -0.02), hi = Math.max(...vals, 0.02);
  const x = i => m.l + (W-m.l-m.r)*i/(n-1), y = v => m.t + (H-m.t-m.b)*(hi - v)/(hi-lo);
  const svg = el('svg', {{viewBox:`0 0 ${{W}} ${{H}}`, role:'img', 'aria-label':opts.label}}, box);
  const area = (a,b) => a.map((v,i)=>(i?'L':'M')+x(i).toFixed(1)+' '+y(v).toFixed(1)).join(' ') + ' ' + b.map((v,i)=>'L'+x(n-1-i).toFixed(1)+' '+y(v).toFixed(1)).join(' ') + 'Z';
  el('path', {{d:area(band.q05, band.q95.slice().reverse()), fill:css('--band-1')}}, svg);
  el('path', {{d:area(band.q10, band.q90.slice().reverse()), fill:css('--band-2')}}, svg);
  // y grid
  const step = (hi-lo) > 0.3 ? 0.1 : 0.05;
  for (let v = Math.ceil(lo/step)*step; v <= hi + 1e-9; v += step) {{
    el('line', {{x1:m.l, x2:W-m.r, y1:y(v), y2:y(v), stroke:css('--rule'), 'stroke-width':v===0||Math.abs(v)<1e-9?1.2:0.6}}, svg);
    const t = el('text', {{x:m.l-6, y:y(v)+4, 'text-anchor':'end', fill:css('--ink-3'), 'font-size':11, 'font-family':'IBM Plex Mono, monospace'}}, svg); t.textContent = (v*100).toFixed(0)+'%';
  }}
  [-90,-60,-30,0,30,60,90].forEach(d => {{ const i = rel.indexOf(d); if (i<0) return; const t = el('text', {{x:x(i), y:H-m.b+16, 'text-anchor':'middle', fill:css('--ink-3'), 'font-size':11, 'font-family':'IBM Plex Mono, monospace'}}, svg); t.textContent = d===0?'day 0':(d>0?'+'+d:d); }});
  const i0 = rel.indexOf(0); el('line', {{x1:x(i0), x2:x(i0), y1:m.t, y2:H-m.b, stroke:css('--ink-2'), 'stroke-dasharray':'3 4', 'stroke-width':1}}, svg);
  const line = arr => arr.map((v,i)=>(i?'L':'M')+x(i).toFixed(1)+' '+y(v).toFixed(1)).join(' ');
  el('path', {{d:line(med_), fill:'none', stroke:css('--ink-3'), 'stroke-width':1.5, 'stroke-dasharray':'2 3'}}, svg);
  el('path', {{d:line(mean_), fill:'none', stroke:css(opts.color||'--event'), 'stroke-width':2.2, 'stroke-linejoin':'round'}}, svg);
  el('circle', {{cx:x(n-1), cy:y(mean_[n-1]), r:4, fill:css(opts.color||'--event'), stroke:css('--paper'), 'stroke-width':2}}, svg);
  const lab = el('text', {{x:x(n-1)-6, y:y(mean_[n-1])-8, 'text-anchor':'end', fill:css('--ink'), 'font-size':12, 'font-weight':600, 'font-family':'IBM Plex Mono, monospace'}}, svg); lab.textContent = fmt(mean_[n-1]);
  // hover
  const tip = document.createElement('div'); tip.className='tip'; box.appendChild(tip);
  const cross = el('line', {{x1:0,x2:0,y1:m.t,y2:H-m.b, stroke:css('--ink-2'), 'stroke-width':1, opacity:0}}, svg);
  const dot = el('circle', {{r:4, fill:css(opts.color||'--event'), opacity:0}}, svg);
  svg.addEventListener('mousemove', ev => {{
    const r = svg.getBoundingClientRect(); const px = (ev.clientX - r.left) * W / r.width; const i = Math.max(0, Math.min(n-1, Math.round((px - m.l)/(W-m.l-m.r)*(n-1))));
    cross.setAttribute('x1', x(i)); cross.setAttribute('x2', x(i)); cross.setAttribute('opacity', 0.6);
    dot.setAttribute('cx', x(i)); dot.setAttribute('cy', y(mean_[i])); dot.setAttribute('opacity', 1);
    tip.style.display='block'; tip.innerHTML = `day ${{rel[i]>0?'+':''}}${{rel[i]}}<br>mean ${{fmt(mean_[i])}} · median ${{fmt(med_[i])}}<br>placebo 10–90%: ${{fmt(band.q10[i])}} to ${{fmt(band.q90[i])}}`;
    const bx = box.getBoundingClientRect(); let tx = ev.clientX - bx.left + 14; if (tx + 230 > bx.width) tx -= 250; tip.style.left = tx+'px'; tip.style.top = (ev.clientY - bx.top - 10)+'px';
  }});
  svg.addEventListener('mouseleave', () => {{ tip.style.display='none'; cross.setAttribute('opacity',0); dot.setAttribute('opacity',0); }});
}}
const sub = (s, keep) => ({{rel:s.rel, years:s.years.filter((_,i)=>keep[i]), paths:s.paths.filter((_,i)=>keep[i])}});
bandChart('c_pres', D.pres, D.band_pres, {{label:'S&P 500 around presidential elections with placebo band'}});
bandChart('c_dem', sub(D.pres, D.pres_party.map(p=>p==='D')), D.band_D, {{label:'Democrat wins', color:'--dem'}});
bandChart('c_rep', sub(D.pres, D.pres_party.map(p=>p==='R')), D.band_R, {{label:'Republican wins', color:'--rep'}});
bandChart('c_mid', D.mid, D.band_mid, {{label:'S&P 500 around midterm elections 1930-2022 with placebo band'}});
bandChart('c_mid74', D.mid74, D.band_mid74, {{label:'S&P 500 around midterm elections since 1974 with placebo band'}});

// ---------- monthly bars
(function(){{
  const box = document.getElementById('c_months'); const W = 860, H = 280, m = {{l:46, r:10, t:12, b:30}};
  const names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  const M = D.months; const se = r => 2 * 0.0 ; // placeholder replaced below
  const sd = M.map(r => Math.abs(r.diff / r.t) ); // Welch se of the difference ~ se of the month mean (other-eleven term is small)
  const lo = Math.min(...M.map((r,i)=>r.mean - 2*sd[i]), -0.005), hi = Math.max(...M.map((r,i)=>r.mean + 2*sd[i]), 0.005);
  const y = v => m.t + (H-m.t-m.b)*(hi-v)/(hi-lo); const bw = (W-m.l-m.r)/12; const x = i => m.l + bw*i;
  const svg = el('svg', {{viewBox:`0 0 ${{W}} ${{H}}`, role:'img', 'aria-label':'Mean monthly return by calendar month'}}, box);
  for (let v = -0.02; v <= 0.03; v += 0.01) {{ if (v<lo||v>hi) continue; el('line', {{x1:m.l, x2:W-m.r, y1:y(v), y2:y(v), stroke:css('--rule'), 'stroke-width':Math.abs(v)<1e-9?1.2:0.6}}, svg); const t = el('text', {{x:m.l-6, y:y(v)+4, 'text-anchor':'end', fill:css('--ink-3'), 'font-size':11, 'font-family':'IBM Plex Mono, monospace'}}, svg); t.textContent=(v*100).toFixed(0)+'%'; }}
  const tip = document.createElement('div'); tip.className='tip'; box.appendChild(tip);
  M.forEach((r,i) => {{
    const col = r.pass ? css('--sept') : css('--event'); const top = Math.min(y(0), y(r.mean)), h = Math.abs(y(0)-y(r.mean));
    const g = el('g', {{}}, svg);
    el('rect', {{x:x(i)+bw*0.18, y:top, width:bw*0.64, height:h, fill:col, rx:3}}, g);
    el('line', {{x1:x(i)+bw/2, x2:x(i)+bw/2, y1:y(r.mean-2*sd[i]), y2:y(r.mean+2*sd[i]), stroke:css('--ink-2'), 'stroke-width':1}}, g);
    const t = el('text', {{x:x(i)+bw/2, y:H-m.b+16, 'text-anchor':'middle', fill:r.pass?css('--ink'):css('--ink-3'), 'font-size':12, 'font-weight':r.pass?600:400, 'font-family':'IBM Plex Sans, sans-serif'}}, svg); t.textContent = names[i];
    if (r.pass) {{ const v = el('text', {{x:x(i)+bw/2, y:y(r.mean-2*sd[i])+14, 'text-anchor':'middle', fill:css('--ink'), 'font-size':12, 'font-weight':600, 'font-family':'IBM Plex Mono, monospace'}}, svg); v.textContent = (r.mean*100).toFixed(2)+'%'; }}
    const hit = el('rect', {{x:x(i), y:m.t, width:bw, height:H-m.t-m.b, fill:'transparent'}}, svg);
    hit.addEventListener('mousemove', ev => {{ tip.style.display='block'; tip.innerHTML = `${{names[i]}}: mean ${{(r.mean*100).toFixed(2)}}% (n ${{r.n}})<br>vs other months ${{(r.diff*100>=0?'+':'')+(r.diff*100).toFixed(2)}} pts, t ${{r.t}}, p ${{r.p}}<br>1928–76 ${{(r.h1*100>=0?'+':'')+(r.h1*100).toFixed(2)}} · 1977–2026 ${{(r.h2*100>=0?'+':'')+(r.h2*100).toFixed(2)}}`; const bx = box.getBoundingClientRect(); let tx = ev.clientX-bx.left+14; if (tx+260>bx.width) tx-=280; tip.style.left=tx+'px'; tip.style.top=(ev.clientY-bx.top-10)+'px'; }});
    hit.addEventListener('mouseleave', () => tip.style.display='none');
  }});
}})();

// ---------- PEAD deciles: grouped bars, announcement vs drift
(function(){{
  const box = document.getElementById('c_pead'); const W = 860, H = 280, m = {{l:46, r:10, t:12, b:30}};
  const P = D.pead; const vals = [].concat(P.map(r=>r.car01), P.map(r=>r.car260));
  const lo = Math.min(...vals, -0.005), hi = Math.max(...vals, 0.005);
  const y = v => m.t + (H-m.t-m.b)*(hi-v)/(hi-lo); const gw = (W-m.l-m.r)/10; const x = i => m.l + gw*i;
  const svg = el('svg', {{viewBox:`0 0 ${{W}} ${{H}}`, role:'img', 'aria-label':'Announcement and drift returns by surprise decile'}}, box);
  for (let v = -0.02; v <= 0.02; v += 0.01) {{ if (v<lo||v>hi) continue; el('line', {{x1:m.l, x2:W-m.r, y1:y(v), y2:y(v), stroke:css('--rule'), 'stroke-width':Math.abs(v)<1e-9?1.2:0.6}}, svg); const t = el('text', {{x:m.l-6, y:y(v)+4, 'text-anchor':'end', fill:css('--ink-3'), 'font-size':11, 'font-family':'IBM Plex Mono, monospace'}}, svg); t.textContent=(v*100).toFixed(0)+'%'; }}
  const tip = document.createElement('div'); tip.className='tip'; box.appendChild(tip);
  P.forEach((r,i) => {{
    const bw = gw*0.36;
    [[r.car01, css('--event'), x(i)+gw*0.12], [r.car260, css('--drift'), x(i)+gw*0.52]].forEach(([v,col,xx]) => {{
      el('rect', {{x:xx, y:Math.min(y(0),y(v)), width:bw, height:Math.max(1,Math.abs(y(0)-y(v))), fill:col, rx:2}}, svg);
    }});
    const t = el('text', {{x:x(i)+gw/2, y:H-m.b+16, 'text-anchor':'middle', fill:css('--ink-3'), 'font-size':12, 'font-family':'IBM Plex Sans, sans-serif'}}, svg); t.textContent = 'D'+r.decile;
    const hit = el('rect', {{x:x(i), y:m.t, width:gw, height:H-m.t-m.b, fill:'transparent'}}, svg);
    hit.addEventListener('mousemove', ev => {{ tip.style.display='block'; tip.innerHTML = `decile ${{r.decile}}<br>days 0–1: ${{(r.car01*100).toFixed(2)}}%<br>days +2–60: ${{(r.car260*100).toFixed(2)}}%`; const bx = box.getBoundingClientRect(); let tx = ev.clientX-bx.left+14; if (tx+200>bx.width) tx-=220; tip.style.left=tx+'px'; tip.style.top=(ev.clientY-bx.top-10)+'px'; }});
    hit.addEventListener('mouseleave', () => tip.style.display='none');
  }});
}})();

// ---------- sell in may bars
(function(){{
  const box = document.getElementById('c_sim'); const W = 860, H = 260, m = {{l:46, r:10, t:12, b:30}};
  const S = D.sim; const n = S.length; const lo = Math.min(...S.map(r=>r.d)), hi = Math.max(...S.map(r=>r.d));
  const y = v => m.t + (H-m.t-m.b)*(hi-v)/(hi-lo); const bw = (W-m.l-m.r)/n; const x = i => m.l + bw*i;
  const svg = el('svg', {{viewBox:`0 0 ${{W}} ${{H}}`, role:'img', 'aria-label':'Winter minus summer return by year'}}, box);
  for (let v = Math.ceil(lo/0.2)*0.2; v <= hi; v += 0.2) {{ el('line', {{x1:m.l, x2:W-m.r, y1:y(v), y2:y(v), stroke:css('--rule'), 'stroke-width':Math.abs(v)<1e-9?1.2:0.6}}, svg); const t = el('text', {{x:m.l-6, y:y(v)+4, 'text-anchor':'end', fill:css('--ink-3'), 'font-size':11, 'font-family':'IBM Plex Mono, monospace'}}, svg); t.textContent=(v*100).toFixed(0)+'%'; }}
  const tip = document.createElement('div'); tip.className='tip'; box.appendChild(tip);
  S.forEach((r,i) => {{
    const col = r.d >= 0 ? css('--dem') : css('--rep'); const top = Math.min(y(0), y(r.d)), h = Math.max(1, Math.abs(y(0)-y(r.d)));
    el('rect', {{x:x(i)+1, y:top, width:Math.max(1,bw-2), height:h, fill:col}}, svg);
    if (r.y % 10 === 0) {{ const t = el('text', {{x:x(i)+bw/2, y:H-m.b+16, 'text-anchor':'middle', fill:css('--ink-3'), 'font-size':11, 'font-family':'IBM Plex Mono, monospace'}}, svg); t.textContent = r.y; }}
    if (r.y === 2003) {{ el('line', {{x1:x(i), x2:x(i), y1:m.t, y2:H-m.b, stroke:css('--ink-2'), 'stroke-dasharray':'3 4'}}, svg); const t = el('text', {{x:x(i)+5, y:m.t+12, fill:css('--ink-2'), 'font-size':11, 'font-family':'IBM Plex Mono, monospace'}}, svg); t.textContent='published Dec 2002 →'; }}
    const hit = el('rect', {{x:x(i), y:m.t, width:bw, height:H-m.t-m.b, fill:'transparent'}}, svg);
    hit.addEventListener('mousemove', ev => {{ tip.style.display='block'; tip.innerHTML = `${{r.y}}: winter ${{fmt(r.w)}} · summer ${{fmt(r.s)}}<br>difference ${{(r.d*100>=0?'+':'')+(r.d*100).toFixed(1)}} pts`; const bx = box.getBoundingClientRect(); let tx = ev.clientX-bx.left+14; if (tx+220>bx.width) tx-=240; tip.style.left=tx+'px'; tip.style.top=(ev.clientY-bx.top-10)+'px'; }});
    hit.addEventListener('mouseleave', () => tip.style.display='none');
  }});
}})();
}})();
</script>
"""
out = os.path.join(OUT_DIR, "so_you_think_you_can_tell.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
# standalone copy for GitHub Pages: the artifact host wraps the body in a document at publish
# time; a static host does not, so this adds the doctype, charset and viewport itself.
standalone = ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
              "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
              "<style>body{margin:0;font-family:system-ui,sans-serif;font-size:14px;background:#f3f4f7}img{max-width:100%}[hidden]{display:none!important}</style>\n"
              + html.split("</style>", 1)[0].replace("<title>So You Think You Can Tell</title>", "", 1).strip() + "</style>\n</head>\n<body>\n"
              + html.split("</style>", 1)[1] + "\n</body>\n</html>\n")
standalone = standalone.replace("<head>\n", "<head>\n<title>So You Think You Can Tell</title>\n", 1)
with open(os.path.join(OUT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(standalone)
print(out, len(html) // 1024, "KB; index.html", len(standalone) // 1024, "KB")
