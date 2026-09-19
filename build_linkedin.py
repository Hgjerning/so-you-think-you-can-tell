# -*- coding: utf-8 -*-
"""LinkedIn package: article text (paste-ready), PNG charts and cover, and a feed post.
Everything numeric is read from Data/results/; nothing is typed in.

    python build_linkedin.py   ->  linkedin/
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "Data", "results")
OUT = os.path.join(HERE, "linkedin")
os.makedirs(OUT, exist_ok=True)

INK, INK2, INK3, RULE, PAPER = "#171a21", "#4a4f5c", "#7a8090", "#d5d8e0", "#ffffff"
EVENT, DEM, REP, SEPT, BAND1, BAND2 = "#2a78d6", "#2a78d6", "#e34948", "#eb6834", "#e6e8ee", "#d0d4dd"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12, "axes.edgecolor": RULE, "axes.labelcolor": INK2,
                     "xtick.color": INK3, "ytick.color": INK3, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": PAPER, "axes.facecolor": PAPER, "savefig.dpi": 160})

summary = pd.read_csv(os.path.join(RES, "summary.csv"))
S = {r["trial"]: r for r in summary.to_dict("records")}
months = pd.read_csv(os.path.join(RES, "calendar_months.csv"), index_col=0)
sim = pd.read_csv(os.path.join(RES, "sell_in_may_by_year.csv"), index_col=0)
pres_w = pd.read_csv(os.path.join(RES, "presidential_windows.csv"), index_col=0)
cyc = pd.read_csv(os.path.join(RES, "presidential_cycle_summary.csv"), header=[0, 1], index_col=0)
prices = pd.read_csv(os.path.join(HERE, "Data", "GSPC_daily_close.csv"), index_col=0, parse_dates=True)["close"].sort_index()


def load_paths(name):
    df = pd.read_csv(os.path.join(RES, name), index_col=0); df.columns = [int(c) for c in df.columns]; return df


def load_band(name):
    return pd.read_csv(os.path.join(RES, name), index_col=0)


def pct(x, d=1):
    return f"{100 * x:+.{d}f}%"


def pv(p):
    return f"{p:.3f}" if p >= 0.001 else f"{p:.4f}"


_WORDS = ("zero one two three four five six seven eight nine ten eleven twelve thirteen "
          "fourteen fifteen sixteen seventeen eighteen nineteen twenty").split()


def num_word(n):
    """Small counts as words, to match the prose around them."""
    return _WORDS[n] if 0 <= n < len(_WORDS) else str(n)


def foot(fig, text, color=INK3, fontsize=9):
    """Footer caption wrapped to the figure width (about 150 characters at 9pt on a 10-12in figure)."""
    import textwrap
    width = int(fig.get_figwidth() * 14.5)
    fig.text(0.01, 0.012, "\n".join(textwrap.wrap(text, width)), color=color, fontsize=fontsize, va="bottom")


def band_chart(ax, paths, band, color, title, label):
    rel = np.array(paths.columns); mean = paths.mean(axis=0).to_numpy(); med = paths.median(axis=0).to_numpy()
    ax.fill_between(rel, band["q05"], band["q95"], color=BAND1, lw=0, label="placebo 5–95%")
    ax.fill_between(rel, band["q10"], band["q90"], color=BAND2, lw=0, label="placebo 10–90%")
    ax.axhline(0, color=RULE, lw=1); ax.axvline(0, color=INK2, lw=1, ls=(0, (3, 4)))
    ax.plot(rel, med, color=INK3, lw=1.4, ls=(0, (2, 3)), label="median")
    ax.plot(rel, mean, color=color, lw=2.4, label=label)
    ax.plot(rel[-1], mean[-1], "o", color=color, ms=7, mec=PAPER, mew=1.5)
    ax.annotate(pct(mean[-1]), (rel[-1], mean[-1]), xytext=(-8, 8), textcoords="offset points", ha="right", color=INK, fontsize=11, fontweight="bold")
    ax.set_xticks([-90, -60, -30, 0, 30, 60, 90]); ax.set_xticklabels(["−90", "−60", "−30", "day 0", "+30", "+60", "+90"])
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v * 100:.0f}%"))
    ax.set_title(title, loc="left", color=INK, fontsize=13, fontweight="bold", pad=10)
    ax.grid(axis="y", color=RULE, lw=0.6); ax.set_axisbelow(True)


# ---------------------------------------------------------------- 01 presidential
pp = load_paths("paths_presidential.csv")
fig, ax = plt.subplots(figsize=(10, 5.6))
band_chart(ax, pp, load_band("band_presidential_n25.csv"), EVENT, "S&P 500 around 25 presidential elections, 1928–2024", "mean of 25 elections")
ax.legend(loc="upper left", frameon=False, fontsize=10)
foot(fig,"Cumulative price return, base = close 91 trading days before election day. Band: the range of the AVERAGE of 25 random 181-day windows, 1928–2026, 2,000 draws.", color=INK3, fontsize=9)
fig.tight_layout(rect=(0, 0.07, 1, 1)); fig.savefig(os.path.join(OUT, "01_presidential.png")); plt.close(fig)

# ---------------------------------------------------------------- 02 by party
party = pres_w["winner_party"].reindex(pp.index)
fig, axes = plt.subplots(1, 2, figsize=(12, 5.2), sharey=True)
band_chart(axes[0], pp[party == "D"], load_band("band_presidential_n13.csv"), DEM, "Democrat won (13)", "mean")
band_chart(axes[1], pp[party == "R"], load_band("band_presidential_n12.csv"), REP, "Republican won (12)", "mean")
foot(fig,"Each panel has its own placebo band for its own count. Post-election 60-day difference D − R: " + pct(S["P3-2"]["statistic"]) + f", permutation p {pv(S['P3-2']['p'])}.", color=INK3, fontsize=9)
fig.tight_layout(rect=(0, 0.07, 1, 1)); fig.savefig(os.path.join(OUT, "02_by_party.png")); plt.close(fig)

# ---------------------------------------------------------------- 03 midterm
pm = load_paths("paths_midterm.csv"); pm74 = load_paths("paths_midterm_1974.csv")
fig, axes = plt.subplots(1, 2, figsize=(12, 5.2), sharey=True)
band_chart(axes[0], pm, load_band("band_midterm_n24.csv"), EVENT, "All 24 midterms, 1930–2022", "mean")
band_chart(axes[1], pm74, load_band("band_midterm_1974.csv"), EVENT, "The 13 since 1974 (the Goldman window)", "mean")
foot(fig,f"90 days after: {pct(S['P3-4']['statistic'])} vs placebo {pct(S['P3-4']['placebo_mean'])}, p {pv(S['P3-4']['p'])} (all 24); {pct(S['P3-4 (report)']['statistic'])} vs {pct(S['P3-4 (report)']['placebo_mean'])}, p {pv(S['P3-4 (report)']['p'])} (since 1974).", color=INK3, fontsize=9)
fig.tight_layout(rect=(0, 0.07, 1, 1)); fig.savefig(os.path.join(OUT, "03_midterm.png")); plt.close(fig)

# ---------------------------------------------------------------- 04 months
names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
fig, ax = plt.subplots(figsize=(10, 5.2))
se = (months["diff"] / months["t"]).abs()
cols = [SEPT if p else EVENT for p in months["passes_gate"]]
ax.bar(range(12), months["mean"], color=cols, width=0.64)
ax.errorbar(range(12), months["mean"], yerr=2 * se, fmt="none", ecolor=INK2, elinewidth=1, capsize=0)
ax.axhline(0, color=INK2, lw=1)
ax.set_xticks(range(12)); ax.set_xticklabels(names)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v * 100:.1f}%"))
ax.set_title("Mean monthly price return by calendar month, S&P 500 1928–2026", loc="left", color=INK, fontsize=13, fontweight="bold", pad=10)
ax.grid(axis="y", color=RULE, lw=0.6); ax.set_axisbelow(True)
sep = months.loc[9]
ax.set_ylim(-0.034, ax.get_ylim()[1])
ax.annotate(f"September {100 * sep['mean']:+.2f}%\nt {sep['t']:.2f}, p {pv(sep['p'])}\nsame sign in both halves", (8, sep["mean"] - 2 * se[9]), xytext=(0, -6), textcoords="offset points", ha="center", va="top", color=INK, fontsize=10, fontweight="bold")
foot(fig,"99 observations per month; whiskers ±2 standard errors. Orange = clears Bonferroni-12 and keeps its sign in 1928–1976 and 1977–2026. No other month clears even the plain 5% line.", color=INK3, fontsize=9)
fig.tight_layout(rect=(0, 0.07, 1, 1)); fig.savefig(os.path.join(OUT, "04_months.png")); plt.close(fig)

# ---------------------------------------------------------------- 05 sell in may
fig, ax = plt.subplots(figsize=(11, 4.8))
ax.bar(sim.index, sim["diff"], color=[DEM if d >= 0 else REP for d in sim["diff"]], width=0.8)
ax.axhline(0, color=INK2, lw=1); ax.axvline(2002.5, color=INK2, lw=1, ls=(0, (3, 4)))
ax.text(2003.2, ax.get_ylim()[1] * 0.92, "published Dec 2002 →", color=INK2, fontsize=10)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v * 100:.0f}%"))
ax.set_title("Sell in May: November–April return minus the preceding May–October, by year", loc="left", color=INK, fontsize=13, fontweight="bold", pad=10)
ax.grid(axis="y", color=RULE, lw=0.6); ax.set_axisbelow(True)
ALL = summary.to_dict("records")   # S keeps one row per trial label; the three "P3-6 (report)" rows need the list
g = S["P3-6"]; f = [r for r in ALL if "full" in str(r["hypothesis"])][0]; y50 = [r for r in ALL if "1950" in str(r["hypothesis"])][0]
foot(fig,f"Post-publication 2003–2025: {pct(g['statistic'])}/yr, t {g['note'].split('t ')[1].split(';')[0]}, p {pv(g['p'])}. Full sample: {pct(f['statistic'])}, t {f['note'].split('t ')[1].split(';')[0]}. From 1950: {pct(y50['statistic'])}, t {y50['note'].split('t ')[1].split(';')[0]}.", color=INK3, fontsize=9)
fig.tight_layout(rect=(0, 0.07, 1, 1)); fig.savefig(os.path.join(OUT, "05_sell_in_may.png")); plt.close(fig)

# ---------------------------------------------------------------- 06 ledger as an image (LinkedIn articles have no tables)
rows = [r for r in summary.to_dict("records") if "report" not in r["trial"]]
calls = {"P3-1": "right", "P3-2": "right", "P3-3": "right", "P3-4": "right", "P3-5": "WRONG", "P3-6": "right"}
fig, ax = plt.subplots(figsize=(14, 3.6)); ax.axis("off")
cells = [[r["trial"], r["hypothesis"].replace(" vs placebo", "").replace(", 1930-2022", ""), str(int(r["n"])),
          (pct(r["statistic"]) if r["trial"] != "P3-5" else pct(r["statistic"], 2) + "/mo"),
          (pct(r["placebo_mean"]) if r["trial"] in ("P3-1", "P3-3", "P3-4") else "—"), pv(r["p"]), r["passes_gate"], calls[r["trial"]]] for r in rows]
tbl = ax.table(cellText=cells, colLabels=["trial", "hypothesis", "n", "observed", "placebo mean", "p", "gate 0.0083", "my call"], loc="center", cellLoc="left", colLoc="left",
               colWidths=[0.06, 0.46, 0.05, 0.09, 0.10, 0.06, 0.09, 0.08])
tbl.auto_set_font_size(False); tbl.set_fontsize(10); tbl.scale(1, 1.6)
for (i, j), c in tbl.get_celld().items():
    c.set_edgecolor(RULE); c.set_linewidth(0.6)
    if i == 0: c.set_text_props(color=INK2, fontweight="bold"); c.set_facecolor("#f3f4f7")
    if i > 0 and j == 6 and cells[i - 1][6] == "PASS": c.set_text_props(color="#0ca30c", fontweight="bold")
ax.set_title("Six pre-registered trials, run once. Gate: two-sided p < 0.0083 (0.05 / 6).", loc="left", color=INK, fontsize=12, fontweight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "06_ledger.png")); plt.close(fig)

# ---------------------------------------------------------------- 00 cover (1920x1080): the prism
rng = np.random.default_rng(2026); P = prices.to_numpy(dtype=float)
pool = rng.choice(np.arange(91, len(P) - 91), 120, replace=False)
hero = np.array([[P[p - 90 + k] / P[p - 91] - 1 for k in range(181)] for p in pool])
fig = plt.figure(figsize=(19.2, 10.8), facecolor="#0a0a0d"); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 900); ax.set_ylim(380, 0); ax.axis("off"); ax.set_facecolor("#0a0a0d")
ex, ey, n = 402, 196, 181
t = np.arange(n) / (n - 1); xs = 20 + (ex - 20) * t; amp = 120 * (1 - t) + 4
for k, p in enumerate(hero):
    ax.plot(xs, ey + np.clip(p / 0.35, -1, 1) * amp, color="white", lw=0.6, alpha=0.10 + 0.12 * (k % 3 == 0))
for w, a in [(9, 0.06), (5, 0.15), (1.8, 0.95)]:
    ax.plot([20, ex], [ey, ey], color="white", lw=w, alpha=a, solid_capstyle="round")
# the eclipse rim, behind the burst
from matplotlib.colors import to_rgb
from matplotlib.patches import Circle
for w, a in [(14, 0.04), (5, 0.08), (1.3, 0.28)]:
    ax.add_patch(Circle((640, 190), 150, facecolor="none", edgecolor="white", lw=w, alpha=a))
# the prism: beam enters the left face, the burst leaves the right face
ax.add_patch(Polygon([(450, 58), (350, 318), (550, 318)], closed=True, facecolor=(1, 1, 1, 0.03), edgecolor="#f2f2f2", lw=1.8))
ax.add_patch(Polygon([(ex, ey), (498, 178), (498, 214)], closed=True, facecolor=(1, 1, 1, 0.09), edgecolor="none"))
# the burst: 48 rays of spectrum, dissolving; one thread survives
spectrum = [np.array(to_rgb(c)) for c in ["#3987e5", "#199e70", "#eda100", "#eb6834", "#e34948", "#d55181"]]
def hue(u):
    k = min(int(u * 5), 4); f_ = u * 5 - k
    return spectrum[k] * (1 - f_) + spectrum[k + 1] * f_
rr = np.random.default_rng(7)
bx, by = 498, ey
for i in range(48):
    u = i / 47; ang = np.deg2rad(-38 + 76 * u + rr.normal(0, 1.2)); L = rr.uniform(60, 260); w = rr.uniform(0.7, 1.5)
    xs_r = bx + np.cos(ang) * np.linspace(0, L, 30); ys_r = by + np.sin(ang) * np.linspace(0, L, 30); c = hue(u)
    for j in range(29):
        ax.plot(xs_r[j:j + 2], ys_r[j:j + 2], color=c, lw=w, alpha=0.9 * (1 - j / 29) ** 1.3, solid_capstyle="round")
ang = np.deg2rad(-7); L = 900; c = np.array(to_rgb("#eb6834"))
xs_r = bx + np.cos(ang) * np.linspace(0, L, 80); ys_r = by + np.sin(ang) * np.linspace(0, L, 80)
for j in range(79):
    a = 1 - 0.35 * j / 79
    ax.plot(xs_r[j:j + 2], ys_r[j:j + 2], color=c, lw=10, alpha=0.10 * a, solid_capstyle="round")
    ax.plot(xs_r[j:j + 2], ys_r[j:j + 2], color=c, lw=3.0, alpha=a, solid_capstyle="round")
ax.text(20, 40, "So You Think You Can Tell", color="white", fontsize=34, style="italic", family="DejaVu Serif")
fig.savefig(os.path.join(OUT, "00_cover.png"), dpi=100, facecolor="#0a0a0d"); plt.close(fig)

# ---------------------------------------------------------------- article text
first, last = prices.index[0].date(), prices.index[-1].date()


from oos_text import OOS_TEXT  # noqa: E402  (shared with build_article.py)
from pead_text import PEAD_PARAGRAPHS, PEAD_CHART, LEDGER2  # noqa: E402

# ---------------------------------------------------------------- 07 PEAD deciles (ART)
fig, ax = plt.subplots(figsize=(10, 5))
xs = np.arange(10); bw = 0.38
ax.bar(xs - bw / 2, [r["car01"] for r in PEAD_CHART], width=bw, color=EVENT, label="announcement days 0 to +1")
ax.bar(xs + bw / 2, [r["car260"] for r in PEAD_CHART], width=bw, color="#1baf7a", label="days +2 to +60")
ax.axhline(0, color=INK2, lw=1); ax.set_xticks(xs); ax.set_xticklabels([f"D{r['decile']}" for r in PEAD_CHART])
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v * 100:.1f}%"))
ax.set_title("ART 1997–2012: announcement and drift by earnings-surprise decile", loc="left", color=INK, fontsize=13, fontweight="bold", pad=10)
ax.grid(axis="y", color=RULE, lw=0.6); ax.set_axisbelow(True); ax.legend(frameon=False, fontsize=10, loc="upper left")
foot(fig, "Market-adjusted cumulative return by decile of the seasonal-random-walk surprise (1 = worst, 10 = best), 136,822 announcements, Global Developed members on the day. The announcement is monotone; the three months after are negative everywhere and nearly flat across deciles.")
fig.tight_layout(rect=(0, 0.07, 1, 1)); fig.savefig(os.path.join(OUT, "07_pead_art.png")); plt.close(fig)

# ---------------------------------------------------------------- 08 ledger, trials 7-12
fig, ax = plt.subplots(figsize=(14, 3.6)); ax.axis("off")
cells2 = [[r["trial"], r["hypothesis"], f"{r['n']:,}", r["observed"], r["p"], r["verdict"], r["call"]] for r in LEDGER2]
tbl = ax.table(cellText=cells2, colLabels=["trial", "hypothesis", "n", "observed", "p", "gate", "my call"], loc="center", cellLoc="left", colLoc="left",
               colWidths=[0.06, 0.50, 0.08, 0.14, 0.06, 0.08, 0.08])
tbl.auto_set_font_size(False); tbl.set_fontsize(10); tbl.scale(1, 1.6)
for (i, j), c in tbl.get_celld().items():
    c.set_edgecolor(RULE); c.set_linewidth(0.6)
    if i == 0: c.set_text_props(color=INK2, fontweight="bold"); c.set_facecolor("#f3f4f7")
    if i > 0 and j == 5 and cells2[i - 1][5] == "PASS": c.set_text_props(color="#0ca30c", fontweight="bold")
ax.set_title("Trials 7–12: September out of sample, and the two earnings-drift studies. One-sided gate 0.025.", loc="left", color=INK, fontsize=12, fontweight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "08_ledger_2.png")); plt.close(fig)

# ---------------------------------------------------------------- 09 pre-holiday, mean by holiday
from preholiday_text import PREHOLIDAY_PARAGRAPHS, PREHOLIDAY_CHART, LEDGER3  # noqa: E402

# Paragraph 7 (index 6) -- the missing Juneteenths and the legibility criterion that counted the
# wrong quantity -- is cut from the LINKEDIN version only. Both are lessons about my own
# specification rather than about the market, and the result reads whole without them. The web
# article keeps it: there the length costs nothing and the record should carry the faults.
LINKEDIN_CUT = {6}
PH = [p for i, p in enumerate(PREHOLIDAY_PARAGRAPHS) if i not in LINKEDIN_CUT]

ph = PREHOLIDAY_CHART
fig, ax = plt.subplots(figsize=(13, 6.4))
ypos, labels, colors, prev = [], [], [], None
y = 0.0
for r in ph:
    if prev is not None and r["market"] != prev:
        y += 0.8                      # a gap between the two markets
    prev = r["market"]
    ypos.append(y); labels.append(r["holiday"])
    colors.append(SEPT if r["market"] == "FTSE 100" else EVENT)
    y += 1.0
vals = [r["mean"] for r in ph]
ax.barh(ypos, vals, color=colors, height=0.72)
for yy, r in zip(ypos, ph):
    # the count next to every bar: an n of 5 must not read like an n of 44
    ax.text(r["mean"] + (0.006 if r["mean"] >= 0 else -0.006), yy, f"n {r['n']}",
            va="center", ha="left" if r["mean"] >= 0 else "right", color=INK3, fontsize=8.5)
ax.set_yticks(ypos); ax.set_yticklabels(labels, fontsize=9)
ax.invert_yaxis(); ax.axvline(0, color=RULE, lw=1.0)
ax.set_xlabel("mean simple return on the session before the holiday, %", color=INK2, fontsize=9)
ax.set_title("The day before a holiday: S&P 500 1983–2026 (blue) and FTSE 100 1984–2026 (orange)",
             loc="left", color=INK, fontsize=12, fontweight="bold")
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.tick_params(colors=INK3, length=0)
foot(fig, "One session can precede two holidays: the Thursday before Good Friday is also the session before "
          "Easter Monday, and Christmas Eve precedes Boxing Day, so those carry both names. The British Christmas "
          "Day row is the handful of years the substitution rules separate it from Boxing Day and is too small to "
          "read anything into.")
fig.tight_layout(rect=(0, 0.07, 1, 1)); fig.savefig(os.path.join(OUT, "09_preholiday.png")); plt.close(fig)

# ---------------------------------------------------------------- 10 ledger, trials 13-15
# All three rows in ONE image on purpose. P3-14 is the project's only pass and P3-15 takes it
# apart; a screenshot of the pass on its own would travel without its own refutation.
fig, ax = plt.subplots(figsize=(14, 2.4)); ax.axis("off")
cells3 = [[r["trial"], r["hypothesis"], f"{r['n']:,}", r["observed"], r["p"], r["verdict"], r["call"]] for r in LEDGER3]
tbl = ax.table(cellText=cells3, colLabels=["trial", "hypothesis", "n", "observed", "p", "gate", "my call"], loc="center", cellLoc="left", colLoc="left",
               colWidths=[0.06, 0.44, 0.06, 0.24, 0.06, 0.07, 0.07])
tbl.auto_set_font_size(False); tbl.set_fontsize(10); tbl.scale(1, 1.6)
for (i, j), c in tbl.get_celld().items():
    c.set_edgecolor(RULE); c.set_linewidth(0.6)
    if i == 0: c.set_text_props(color=INK2, fontweight="bold"); c.set_facecolor("#f3f4f7")
    if i > 0 and j == 5 and cells3[i - 1][5] == "PASS": c.set_text_props(color="#0ca30c", fontweight="bold")
ax.set_title("Trials 13–15: the pre-holiday effect. P3-14 is the one pass in this family — and P3-15 removes "
             "Easter from it, where it does not survive.", loc="left", color=INK, fontsize=12, fontweight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "10_ledger_3.png")); plt.close(fig)
d_mean = float(S["P3-2"]["note"].split("D mean ")[1].split(" ")[0]); r_mean = float(S["P3-2"]["note"].split("R mean ")[1].split(" ")[0])
p2x = S["P3-2 (report)"]; p3i = S["P3-3 (report)"]; mid74 = S["P3-4 (report)"]
gw = float(g["note"].split("winter mean ")[1].split(",")[0]); gs = float(g["note"].split("summer mean ")[1].split(",")[0])
share = int(round(100 * float(g["note"].split("share winter>summer ")[1])))
text = f"""So You Think You Can Tell

[Cover image: 00_cover.png]

Every autumn a chart goes round showing what the stock market does around an election. Here are the same charts drawn with the one band that matters: what the S&P 500 does around nothing in particular.

The chart that started this shows the S&P 500 "around midterm elections since 1974". A dashed line at election day, an average that climbs afterwards, and a shaded band marked 10th and 90th percentile. The band is real. It is the spread of the thirteen individual midterm years around their own average. It tells you that elections differ from each other, which nobody doubted. It does not tell you whether the average is unusual, because it never asks what the index does in a window of the same length opened on any other day.

That second question is the whole test, and it is cheap to run. Take the statistic you care about, say the mean 90-day return after 24 midterm elections. Open 24 windows of 90 days at random dates in the same history, take their mean, and repeat ten thousand times. That is the distribution of "24 random windows". If the election mean sits in its middle, the election did nothing the calendar was not already doing. The S&P 500 rose in the sixty trading days after most things.

I wrote down six hypotheses with their windows, samples and pass thresholds, and committed them to a repository before computing any number. The commit is the pre-registration. The threshold is p < 0.0083, which is 5% divided by six. I also wrote down what I expected each one to do, and I score myself at the end.

**Presidential elections: the average is the drift**

Twenty-five elections, 1928 to 2024. The sixty trading days after election day returned {pct(S['P3-1']['statistic'])} on average. Twenty-five random 60-day windows return {pct(S['P3-1']['placebo_mean'])} on average. Placebo p-value {pv(S['P3-1']['p'])}. Nothing happened.

The sixty days before the election, the "sideways into the vote" story, returned {pct(S['P3-3']['statistic'])} against a placebo mean of {pct(S['P3-3']['placebo_mean'])}, p {pv(S['P3-3']['p'])}. Slightly below the drift, well inside the noise.

[Image: 01_presidential.png]

**Democrat or Republican: twenty-five coin flips**

After a Democrat won, the next sixty days returned {pct(d_mean)} on average (13 elections). After a Republican, {pct(r_mean)} (12). The difference is {pct(S['P3-2']['statistic'])} with a permutation p of {pv(S['P3-2']['p'])}. Drop 2000 and 2020, when the winner was not known the next day, and the difference is {pct(p2x['statistic'])}, p {pv(p2x['p'])}. With a 60-day standard deviation near eight points and a dozen observations a side, no party effect of the size anyone claims could be resolved here even if it existed.

Before the election the only party label anyone can know is the incumbent's. Democrat incumbents saw {pct(p3i['statistic'])} more in the 60 days into the vote than Republican incumbents, p {pv(p3i['p'])}. Same verdict.

[Image: 02_by_party.png]

For completeness, the four-year cycle, mean annual price return by year of the term, Democrats then Republicans: year 1 {pct(cyc.loc[1, ('mean', 'D')])} vs {pct(cyc.loc[1, ('mean', 'R')])}; year 2 {pct(cyc.loc[2, ('mean', 'D')])} vs {pct(cyc.loc[2, ('mean', 'R')])}; year 3 {pct(cyc.loc[3, ('mean', 'D')])} vs {pct(cyc.loc[3, ('mean', 'R')])}; year 4 {pct(cyc.loc[4, ('mean', 'D')])} vs {pct(cyc.loc[4, ('mean', 'R')])}. Thirteen and twelve observations per cell. Year 1 under Republicans contains 1929, 1973, 2001 and 2008 by accident of the calendar. This is here because someone will ask, not because it can bear a test.

**Midterms: the one that comes closest**

This is the Goldman chart, extended back to 1930 and given a placebo band. Ninety trading days after 24 midterm elections the index returned {pct(S['P3-4']['statistic'])} on average. Twenty-four random 90-day windows return {pct(S['P3-4']['placebo_mean'])}. Placebo p {pv(S['P3-4']['p'])}: suggestive, and a fail against the 0.0083 gate. On Goldman's own window, 1974 onward, the mean is {pct(mid74['statistic'])} on 13 elections, p {pv(mid74['p'])}.

So the post-midterm rally is the one claim on this page that is not simply the drift. It is also a claim that has been published in every election year since at least the 1990s, which is the condition under which effects of this size tend to disappear. I treat p 0.04 on 24 events as a reason to keep the row open in a forward record. The next observation is 3 November 2026.

[Image: 03_midterm.png]

**The calendar: September, and only September**

Twelve months, twelve tests, so the bar inside this family is p < 0.0042, and a month also has to show the same sign in 1928–1976 and in 1977–2026. September's mean price return is {100 * sep['mean']:+.2f}% against {100 * (sep['mean'] - sep['diff']):+.2f}% for the other eleven, t {sep['t']:.2f}, p {pv(sep['p'])}, and the gap is {100 * sep['diff_1928_1976']:+.1f} points in the first half and {100 * sep['diff_1977_2026']:+.1f} in the second. It passes. It is the only month that clears even the unadjusted 5% line. January, the most famous calendar effect, is {100 * months.loc[1, 'diff']:+.2f} points above the rest with p {pv(months.loc[1, 'p'])}. In a large-cap price index there is no January effect to find.

I had written down that September would fail. It did not, and that is recorded. What a pass means is narrower than it sounds: one month, a price index, no costs, an effect of about two points that is known to every reader of the financial press.

So I took it out of sample, four more times, each pre-registered with a one-sided gate of p < 0.025 and the same sign required in both halves of the sample. {OOS_TEXT}

[Image: 04_months.png]

**Sell in May: true until it was published**

Bouman and Jacobsen put the Halloween indicator in the American Economic Review in December 2002. The honest test is what happened afterwards. From 2003 to 2025 the November–April half returned {pct(gw)} and May–October {pct(gs)}: a gap of {pct(g['statistic'])} a year with t {g['note'].split('t ')[1].split(';')[0]} on 23 non-overlapping years, p {pv(g['p'])}. Winter beat summer in {share}% of those years, which is a coin.

The full 1928–2025 sample gives a gap of {pct(f['statistic'])}, t {f['note'].split('t ')[1].split(';')[0]}. Start in 1950 and it is {pct(y50['statistic'])}, t {y50['note'].split('t ')[1].split(';')[0]}, which is the number that gets quoted. Every one of those samples was available to the authors, and the strongest of them starts in the one year that happens to make it strongest.

[Image: 05_sell_in_may.png]

**Earnings surprises: the announcement is real, the drift is not**

{(chr(10) * 2).join(PEAD_PARAGRAPHS[:4])}

[Image: 07_pead_art.png]

{PEAD_PARAGRAPHS[4]}

**The day before a holiday: dead in America, Easter in Britain**

{(chr(10) * 2).join(PH[:5])}

[Image: 09_preholiday.png]

{(chr(10) * 2).join(PH[5:])}

**The ledger**

[Image: 06_ledger.png]

Six more followed the same day: September out of sample on four indices, and the two earnings-drift studies.

[Image: 08_ledger_2.png]

And three on the pre-holiday effect, six days later.

[Image: 10_ledger_3.png]

Twelve of fifteen predictions right. The three misses are the three surprises, and they do not point the same way: September on the S&P 500, which I expected to fail and which passed; earnings drift on my own database, which I expected to pass and which failed; and the pre-holiday effect on the FTSE, which I argued was not even worth a trial and which is the only thing here that passed and then partly survived. That is the usual shape: the pre-registered guess is "nothing", and when it is wrong it is wrong on the one worth knowing about. Three passes in fifteen — one of them the same fact measured twice, one of them an Easter effect once you take it apart — on claims that have each been in print for decades, is about what a prior of a few percent predicts.

**Method, in enough detail to repeat it**

Data: S&P 500 daily close, {first} to {last}, 24,791 days. Price index, no dividends, no costs. Monthly returns are month-end to month-end.

Dating: election day is the first Tuesday after the first Monday of November, computed and tested. Results arrive after the close, so post-election windows start the next day.

Placebo: for N events and a window, draw N window positions at random from the whole history, take the mean, repeat 10,000 times. The p-value is the share of draws at least as far from the placebo mean as the observed mean, two-sided. Party differences use 10,000 label permutations.

Calendar: Welch t of each month against the other eleven, Bonferroni 12 inside the family plus the same sign in both halves. Sell in May: per year, May–October compounded and November–April compounded, paired t on the non-overlapping annual differences.

Guards: the placebo test was run on synthetic random walks before it saw real data. On a driftless walk, random events reject at the nominal rate. On a walk with strong drift and no event effect it must not reject. An injected +4% after 25 events is recovered at p < 0.01.

What was not done: no second window after seeing the data, no other index, no total-return series, no costs, because nothing here is a strategy.

Code, pre-registrations, ledger and the numbers behind every chart are public at github.com/Hgjerning/so-you-think-you-can-tell, and the article with its interactive charts is at hgjerning.github.io/so-you-think-you-can-tell. The title is after a song by Pink Floyd; the question it asks is the same one.
"""
with open(os.path.join(OUT, "article_linkedin.txt"), "w", encoding="utf-8") as fh:
    fh.write(text)

# ---------------------------------------------------------------- paste-ready article (txt + html)
# These two were hand-made on 2026-09-13 and were still the twelve-trial version six days later,
# because nothing regenerated them. Derived from `text` from now on, so the package cannot drift.
PAGES = "https://hgjerning.github.io/so-you-think-you-can-tell"


def _blocks(t):
    return [b.strip() for b in t.strip().split("\n\n") if b.strip()]


def paste_txt(t):
    out = []
    for b in _blocks(t):
        if b.startswith("[Cover image:") or b.startswith("So You Think You Can Tell"):
            continue                                   # LinkedIn takes the title and cover separately
        if b.startswith("[Image:"):
            # keep the position, as the hand-made 2026-09-13 file did: LinkedIn's editor takes
            # images one at a time and without these markers nobody knows where they go
            f = b.split(":", 1)[1].strip().rstrip("]").strip()
            out.append(f">>> INSERT IMAGE HERE: {f} <<<")
            continue
        out.append(b[2:-2] if b.startswith("**") and b.endswith("**") else b)
    return "\n\n".join(out) + "\n"


def paste_html(t):
    from html import escape
    out = ['<!doctype html><html><head><meta charset="utf-8"><title>So You Think You Can Tell '
           '(paste version)</title><style>body{font-family:Georgia,serif;max-width:720px;'
           'margin:2rem auto;line-height:1.5}h2{font-family:sans-serif;margin-top:2rem}'
           'img{max-width:100%}</style></head><body>']
    for b in _blocks(t):
        if b.startswith("[Cover image:") or b.startswith("So You Think You Can Tell"):
            continue
        if b.startswith("[Image:"):
            f = b.split(":", 1)[1].strip().rstrip("]").strip()
            alt = f.split("_", 1)[-1].rsplit(".", 1)[0].replace("_", " ")
            out.append(f'<p><img src="{PAGES}/linkedin/{f}" alt="{alt}" style="max-width:100%"></p>')
        elif b.startswith("**") and b.endswith("**"):
            out.append(f"<h2>{escape(b[2:-2])}</h2>")
        else:
            out.append(f"<p>{escape(b)}</p>")
    out.append("</body></html>")
    return "\n".join(out) + "\n"


with open(os.path.join(OUT, "article_linkedin_paste.txt"), "w", encoding="utf-8") as fh:
    fh.write(paste_txt(text))
with open(os.path.join(OUT, "paste.html"), "w", encoding="utf-8") as fh:
    fh.write(paste_html(text))

# counts derived from the ledgers, same as build_article.py, so the post cannot contradict
# the tables it links to (P3-5 is the first ledger's one pass)
N_TRIALS = len([r for r in summary.to_dict('records') if 'report' not in r['trial']]) + len(LEDGER2) + len(LEDGER3)
N_PASS = 1 + sum(r['verdict'] == 'PASS' for r in LEDGER2 + LEDGER3)

post = f"""Every autumn a chart goes round showing what stocks do around a US election. I redrew it with the one band that matters: what the S&P 500 does around nothing in particular.

Fifteen hypotheses now, each pre-registered and committed before a single number was computed. Presidential elections, Democrat vs Republican, the run-up, midterms, every calendar month, Sell in May after it was published, earnings drift on two databases, and the day before a public holiday.

{num_word(N_TRIALS - N_PASS).capitalize()} fail and {num_word(N_PASS)} pass. Post-midterm comes closest of the failures ({pct(S['P3-4']['statistic'])} in 90 days, p {pv(S['P3-4']['p'])}, not enough). Sell in May has returned t {g['note'].split('t ')[1].split(';')[0]} since the paper came out. September passes, and it was one I had predicted would fail.

The newest one is the one I got most wrong. I said a second index was not worth a trial; the pre-holiday effect then passed on the FTSE, the only pass in its family. Taking Easter out of it — a holiday Britain shares with America — it fails again. So the honest version of a result that passed its gate is "an Easter effect with company", and that sentence only exists because the test that could kill it was written down first.

The method is cheap: compare the event window with ten thousand random windows of the same length. The market rose after most things.

Full article with the charts below. Code, pre-registrations and every number: github.com/Hgjerning/so-you-think-you-can-tell
"""
with open(os.path.join(OUT, "post.txt"), "w", encoding="utf-8") as fh:
    fh.write(post)
print(sorted(os.listdir(OUT)), "words:", len(text.split()))
