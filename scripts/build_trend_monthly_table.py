# -*- coding: utf-8 -*-
"""Phase A (pure Python): recompute Trends & Anomalies from the raw JSON archive.

1. Parity check: recompute the 9 core fields for all points and compare with
   the GDB Trends_And_Anomalies values (must match exactly after rounding).
2. Compute the 60 monthly fields (T/R anomaly + pct + trend) per point and
   save Monthly_Climatology/Trends_Monthly.csv (OBJECTID, Source_ID, ...).
"""
import csv
import json
import os
import sys
from importlib.machinery import SourceFileLoader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = r"C:\Users\ahmad\Desktop\Egypt Climate Data 1996-2025"
TABLES = os.path.join(BASE, "00_Tables_And_Reports")
RAW_JSON = os.path.join(TABLES, "Egypt_Monthly_Raw_1996_2025.json")
GDB = os.path.join(BASE, "Climate_Database_From_1996_To_2025.gdb")
OUT_CSV = os.path.join(TABLES, "Monthly_Climatology", "Trends_Monthly.csv")

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
CORE = ["T_Annual_Trend_Decade", "R_Annual_Trend_Decade", "T_Annual_Anom", "T_Anom_Winter",
        "T_Anom_Summer", "R_Annual_Anom", "R_Annual_Anom_Pct",
        "R_Anom_Winter", "R_Anom_Winter_Pct"]
MONTHLY = []
for _mn in MONTHS:
    MONTHLY += ["T_Anom_%s" % _mn, "R_Anom_%s" % _mn,
                "R_Anom_%s_Pct" % _mn, "T_Trend_%s" % _mn,
                "R_Trend_%s" % _mn]
YEARS = list(range(1996, 2026))


def load_tool():
    return SourceFileLoader(
        "pytmod", os.path.join(ROOT, "Toolboxes/POWER_Climate_Atlas_Generator_10_8.pyt")).load_module()


def build_monthly(pyt, series):
    monthly = {}
    for param, s in series.items():
        monthly[param] = {}
        for k, v in s.items():
            try:
                m = int(k[4:])
            except Exception:
                continue
            if 1 <= m <= 12:
                monthly[param][(int(k[:4]), m)] = v
    m_tmean = monthly.get("T2M", {})
    totals_p = {}
    for ym, v in monthly.get("PRECTOTCORR", {}).items():
        totals_p[ym] = pyt.monthly_precip_total_from_rate(v, ym[0], ym[1])
    return m_tmean, totals_p


def oid_to_sid_map():
    """OBJECTID (JSON keys) -> Source_ID (GDB), via Temperature.xls Data sheet."""
    import shutil
    import tempfile
    import openpyxl
    tmp = os.path.join(tempfile.gettempdir(), "opencode_oidmap.xlsx")
    shutil.copy(os.path.join(TABLES, "Temperature.xls"), tmp)
    wb = openpyxl.load_workbook(tmp, read_only=True, data_only=True)
    sh = wb["Data"]
    rows = list(sh.iter_rows(values_only=True))
    hdr = rows[0]
    i_oid = hdr.index("OBJECTID")
    i_sid = hdr.index("Source_ID")
    m = {}
    for r in rows[1:]:
        if r[i_oid] is None:
            continue
        m[int(r[i_oid])] = int(r[i_sid])
    return m


def main():
    pyt = load_tool()
    raw = json.load(open(RAW_JSON, "r", encoding="utf-8-sig"))
    oid2sid = oid_to_sid_map()
    import geopandas as gpd
    lyr = gpd.read_file(GDB, layer="Trends_And_Anomalies")
    gdb_by_sid = {}
    for _, r in lyr.iterrows():
        try:
            gdb_by_sid[int(r["Source_ID"])] = r
        except Exception:
            pass
    print("gdb rows: %d | json points: %d" % (len(lyr), len(raw)))
    computed = {}
    worst = {}
    n_match = 0
    for pid, series in raw.items():
        try:
            oid = int(float(pid))
        except Exception:
            continue
        sid = oid2sid.get(oid)
        if sid is None:
            continue
        m_tmean, totals_p = build_monthly(pyt, series)
        out = pyt.compute_trend_anomaly_fields(m_tmean, totals_p)
        computed[sid] = out
        grow = gdb_by_sid.get(sid)
        if grow is None:
            continue
        for f in CORE:
            gv = grow[f]
            gv = None if gv is None or (gv != gv) else float(gv)
            cv = out.get(f)
            if gv is None and cv is None:
                continue
            if gv is None or cv is None:
                worst[f] = max(worst.get(f, 0.0), 999.0)
                continue
            d = abs(gv - cv)
            if d > worst.get(f, 0.0):
                worst[f] = d
        n_match += 1
    print("matched points: %d" % n_match)
    print("max |recomputed - gdb| per core field (expect 0.0):")
    for f in CORE:
        print("  %-18s %s" % (f, worst.get(f, 0.0)))
    # --- write CSV ---
    sid2oid = {s: o for o, s in oid2sid.items()}
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["OBJECTID", "Source_ID"] + MONTHLY)
        for sid in sorted(computed):
            out = computed[sid]
            w.writerow([sid2oid.get(sid), sid] +
                       [("" if out.get(f) is None else out.get(f)) for f in MONTHLY])
    print("wrote %s (%d rows)" % (OUT_CSV, len(computed)))


if __name__ == "__main__":
    main()
