# -*- coding: utf-8 -*-
"""Trial P3-12 / ART #12 of PREREGISTRATION_PEAD_ART_2026-09-13.md.

Written 2026-09-13 while ARTData was RECOVERY_PENDING, so it has NOT been executed against the
live database. It uses the column names of Project1's art_pit.py (verified live 2026-08-31). If
it fails on a schema detail, fixing that is a harness correction (same trial); changing any
window, gate, sample bound or surprise definition is not.

    python run_pead_art.py             -> Data/results/pead_art_*.csv

Requires Project1's venv (pyodbc) and the local SQL Server instance with ARTData online.
"""
import os
import sys
from math import erf, sqrt

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Project1 Investment Strategy"))
from eventstudies import firm  # noqa: E402
from InvestmentLibrary import art_pit  # noqa: E402

OUT = os.path.join(HERE, "Data", "results")
CACHE = os.path.join(HERE, "Data", "art_cache")
EVENT_START, EVENT_END = "1997-01-02", "2012-12-31"
PRICE_START, PRICE_END = "1995-12-01", "2013-04-08"
HALF_SPLIT = "2005-01-01"
HOLD = (2, 60)
REGION = {2: "Asia", 3: "Europe", 4: "America"}


def load_events(conn):
    p = os.path.join(CACHE, "ibes_q_actuals.parquet")
    if os.path.exists(p):
        return pd.read_parquet(p)
    # HARNESS CORRECTION 2026-09-13 (same trial): AllStocks has no RegionId; the region is on
    # UniversesEntry and is attached in gate_membership from the entry that admits the event.
    q = """
        SELECT a.Id AS StockId, a.PerDate, a.RptDate, a.Value AS Actual, a.Currency
        FROM IbesDataActualsPit a
        WHERE a.Measure = 'EPS' AND a.PerType = 'Q' AND a.RptDate >= '1995-01-01'
    """
    df = pd.read_sql(q, conn, parse_dates=["PerDate", "RptDate"])
    df = df.sort_values(["StockId", "PerDate", "RptDate"]).drop_duplicates(["StockId", "PerDate"], keep="first").reset_index(drop=True)
    os.makedirs(CACHE, exist_ok=True); df.to_parquet(p)
    return df


def gate_membership(conn, ev):
    """Global Developed member on RptDate: entry Date_ <= RptDate < ToDate (or ToDate NULL)."""
    p = os.path.join(CACHE, "gd_membership.parquet")
    if os.path.exists(p):
        m = pd.read_parquet(p)
    else:
        m = pd.read_sql("""
            SELECT e.StockId, e.Date_ AS EntryDate, e.ToDate, e.RegionId
            FROM UniversesEntry e JOIN Universes u ON u.UniverseId = e.UniverseId
            WHERE u.Name_ = 'Global Developed'
        """, conn, parse_dates=["EntryDate", "ToDate"])
        os.makedirs(CACHE, exist_ok=True); m.to_parquet(p)
    m["ToDate"] = m["ToDate"].fillna(pd.Timestamp("2099-12-31"))
    j = ev.merge(m, on="StockId", how="inner")
    ok = (j["EntryDate"] <= j["RptDate"]) & (j["RptDate"] < j["ToDate"])
    keep = j.loc[ok, ["StockId", "PerDate", "RegionId"]].drop_duplicates(["StockId", "PerDate"])
    return ev.merge(keep, on=["StockId", "PerDate"], how="inner")


def load_prices(conn, stock_ids):
    p = os.path.join(CACHE, "totret_panel.parquet")
    if os.path.exists(p):
        return pd.read_parquet(p)
    chunks = []
    ids = [int(s) for s in stock_ids]
    for i in range(0, len(ids), 2000):
        batch = ids[i:i + 2000]; ph = ",".join("?" * len(batch))
        q = f"SELECT Id AS StockId, Date_, TotRet FROM PriceData WHERE Id IN ({ph}) AND Date_ BETWEEN ? AND ? AND DeletedAt IS NULL"
        chunks.append(pd.read_sql(q, conn, params=batch + [PRICE_START, PRICE_END], parse_dates=["Date_"]))
        print(f"  prices batch {i // 2000 + 1}/{(len(ids) - 1) // 2000 + 1}", flush=True)
    df = pd.concat(chunks, ignore_index=True)
    panel = df.pivot_table(index="Date_", columns="StockId", values="TotRet", aggfunc="last").sort_index().astype("float32")
    os.makedirs(CACHE, exist_ok=True); panel.to_parquet(p)
    return panel


def main():
    os.makedirs(OUT, exist_ok=True)
    conn = art_pit.get_connection()
    ev = load_events(conn)
    print(f"quarterly EPS actuals, first vintage: {len(ev)} rows, {ev.StockId.nunique()} stocks, RptDate {ev.RptDate.min().date()} -> {ev.RptDate.max().date()}")
    ev = ev.rename(columns={"StockId": "ticker", "PerDate": "reportperiod", "RptDate": "date", "Actual": "epsdil"})
    # same-currency seasonal lag: compute SUE per (ticker, currency) so a currency change breaks the chain
    ev["ticker_ccy"] = ev["ticker"].astype(str) + "|" + ev["Currency"].astype(str)
    s = firm.sue_seasonal_random_walk(ev.rename(columns={"ticker": "stock", "ticker_ccy": "ticker"})).rename(columns={"ticker": "ticker_ccy", "stock": "ticker"})
    s = s[s["sue"].notna() & (s["date"] >= EVENT_START) & (s["date"] <= EVENT_END)].copy()
    s = s.rename(columns={"ticker": "StockId", "reportperiod": "PerDate", "date": "RptDate"})
    s = gate_membership(conn, s)
    print(f"events with SUE, in window, Global Developed members on RptDate: {len(s)}")
    s["region"] = s["RegionId"].map(REGION)
    s["fq"] = s["RptDate"].dt.to_period("Q")
    s["event_id"] = np.arange(len(s))
    s["decile"] = s.groupby("fq")["sue"].transform(lambda x: pd.qcut(x.rank(method="first"), 10, labels=False) + 1)

    panel = load_prices(conn, sorted(s["StockId"].unique()))
    conn.close()
    # HARNESS CORRECTION 2026-09-13 (same trial): the panel spans three regional calendars, so
    # returns are computed on each stock's own trading days (see firm.returns_on_own_calendar);
    # the first execution used panel.pct_change() and lost the day after every foreign-calendar
    # gap, which made 99.9% of American CAR[+2,+60] NaN under the all-days rule.
    returns = firm.returns_on_own_calendar(panel.astype("float64"))
    returns = returns.mask(returns.abs() > 1.0)
    COV = 0.9   # a CAR needs 90% of its window days; a stock's own holidays are NaN by construction
    region_of = s.drop_duplicates("StockId").set_index("StockId")["region"]
    mkt = {}
    for reg in REGION.values():
        cols = [c for c in returns.columns if region_of.get(c) == reg]
        mkt[reg] = returns[cols].mean(axis=1)
    mkt_all = returns.mean(axis=1)

    events = s[["event_id", "StockId", "RptDate", "region"]].rename(columns={"StockId": "ticker", "RptDate": "date"})
    parts = []
    for reg in REGION.values():
        e = events[events["region"] == reg]
        if len(e) == 0:
            continue
        parts.append(firm.abnormal_returns(returns, mkt[reg], e[["event_id", "ticker", "date"]], (-250, -31), 120, (-30, 60), model="market_adjusted"))
    ar = pd.concat([p.ar for p in parts]); sigma = pd.concat([p.sigma for p in parts]); used = pd.concat([p.events for p in parts])
    dropped = pd.concat([p.dropped for p in parts])
    pan = firm.EventPanel(ar=ar, sigma=sigma, n_est=pd.concat([p.n_est for p in parts]), alpha=pd.concat([p.alpha for p in parts]),
                          beta=pd.concat([p.beta for p in parts]), events=used, dropped=dropped)
    dec = s.set_index("event_id")["decile"].reindex(pan.ar.index)
    reg = s.set_index("event_id")["region"].reindex(pan.ar.index)

    def d10_d1(mask, window):
        c = firm.car(pan, window, COV)[mask]; x, y = c[dec[mask] == 10].dropna(), c[dec[mask] == 1].dropna()
        if len(x) < 30 or len(y) < 30:
            return {"diff": np.nan, "t": np.nan, "n10": len(x), "n1": len(y)}
        t = (x.mean() - y.mean()) / np.sqrt(x.var(ddof=1) / len(x) + y.var(ddof=1) / len(y))
        return {"diff": float(x.mean() - y.mean()), "t": float(t), "n10": len(x), "n1": len(y)}

    rows = []
    for d in range(1, 11):
        m = dec == d
        rows.append({"decile": d, "n": int(m.sum()), **{f"car{w[0]}_{w[1]}": float(firm.car(pan, w, COV)[m].mean()) for w in [(-30, -1), (0, 1), (2, 60)]},
                     "n_valid_2_60": int(firm.car(pan, (2, 60), COV)[m].notna().sum()),
                     "t_bmp_2_60": firm.bmp_test(pan, (2, 60), m, COV)["t_bmp"]})
    pd.DataFrame(rows).set_index("decile").to_csv(os.path.join(OUT, "pead_art_deciles.csv"))

    all_mask = pd.Series(True, index=pan.ar.index)
    leg = d10_d1(all_mask, (0, 1)); legible = leg["diff"] > 0 and leg["t"] > 3
    ev2 = pan.events.reset_index(drop=True)
    w = pd.Series(0.0, index=ev2.index); dd = dec.reindex(ev2["event_id"]).to_numpy()
    w[dd == 10] = 1.0; w[dd == 1] = -1.0
    ct = firm.calendar_time_portfolio(returns, ev2, HOLD, weights=w)
    x = pd.DataFrame({"mkt": mkt_all})
    full = firm.newey_west_alpha(ct, x); h1 = firm.newey_west_alpha(ct[ct.index < HALF_SPLIT], x); h2 = firm.newey_west_alpha(ct[ct.index >= HALF_SPLIT], x)
    wl = pd.Series(0.0, index=ev2.index); wl[dd == 10] = 1.0
    lo = firm.newey_west_alpha(firm.calendar_time_portfolio(returns, ev2, HOLD, weights=wl), x)
    p_one = 1 - 0.5 * (1 + erf(full["t"] / sqrt(2)))
    passes = legible and p_one < 0.025 and h1["alpha"] > 0 and h2["alpha"] > 0

    summ = [dict(scope="ALL", n_events=len(pan.ar), **{f"d10_d1_{w[0]}_{w[1]}": d10_d1(all_mask, w)["diff"] for w in [(-30, -1), (0, 1), (2, 60)]},
                 **{f"t_{w[0]}_{w[1]}": d10_d1(all_mask, w)["t"] for w in [(-30, -1), (0, 1), (2, 60)]},
                 ct_alpha_annual=full["alpha"] * 252, ct_t_nw=full["t"], ct_p_one_sided=p_one,
                 ct_alpha_h1_annual=h1["alpha"] * 252, ct_t_h1=h1["t"], ct_alpha_h2_annual=h2["alpha"] * 252, ct_t_h2=h2["t"],
                 long_only_d10_alpha_annual=lo["alpha"] * 252, long_only_t=lo["t"],
                 legibility="PASS" if legible else "FAIL", verdict=("PASS" if passes else "fail") if legible else "uninterpretable")]
    for r in REGION.values():
        m = reg == r
        if m.sum() < 200:
            continue
        summ.append(dict(scope=r, n_events=int(m.sum()), **{f"d10_d1_{w[0]}_{w[1]}": d10_d1(m, w)["diff"] for w in [(-30, -1), (0, 1), (2, 60)]},
                         **{f"t_{w[0]}_{w[1]}": d10_d1(m, w)["t"] for w in [(-30, -1), (0, 1), (2, 60)]}))
    for label, m in [("1997-2004", pan.events.set_index("event_id")["date"].reindex(pan.ar.index) < HALF_SPLIT),
                     ("2005-2012", pan.events.set_index("event_id")["date"].reindex(pan.ar.index) >= HALF_SPLIT)]:
        summ.append(dict(scope=label, n_events=int(m.sum()), **{f"d10_d1_{w[0]}_{w[1]}": d10_d1(m, w)["diff"] for w in [(-30, -1), (0, 1), (2, 60)]},
                         **{f"t_{w[0]}_{w[1]}": d10_d1(m, w)["t"] for w in [(-30, -1), (0, 1), (2, 60)]}))
    sdf = pd.DataFrame(summ); sdf.to_csv(os.path.join(OUT, "pead_art_summary.csv"), index=False)
    ct.rename("ls_ret").to_csv(os.path.join(OUT, "pead_art_calendar_time.csv"))
    dropped["reason"].value_counts().to_csv(os.path.join(OUT, "pead_art_dropped.csv"))
    pd.set_option("display.width", 250)
    print(pd.DataFrame(rows).set_index("decile").round(4).to_string()); print(sdf.round(4).T.to_string())


if __name__ == "__main__":
    main()
