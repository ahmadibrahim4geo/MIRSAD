# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import math
import csv
import concurrent.futures
import requests
import xlwt

BASE_DIR = r"C:\Users\ahmad\Desktop\Egypt Climate Data 1996-2025"
PTS_JSON = os.path.join(BASE_DIR, "00_Tables_And_Reports", "egypt_points_646.json")
RAW_TS_JSON = os.path.join(BASE_DIR, "00_Tables_And_Reports", "Egypt_TS_Raw_Monthly_1996_2025.json")
STAGING_DIR = os.path.join(BASE_DIR, "19_Land_Surface_Temperature_STAGING")
TABLES_DIR = os.path.join(BASE_DIR, "00_Tables_And_Reports")
MONTHLY_CLIM_DIR = os.path.join(TABLES_DIR, "Monthly_Climatology")

SEASONS = {
    "Winter": (1, 2, 12),
    "Spring": (3, 4, 5),
    "Summer": (6, 7, 8),
    "Autumn": (9, 10, 11),
}

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]


def fetch_point_ts(pt, retries=5):
    pid = str(pt["OBJECTID"])
    lat = float(pt["Point_Lat"])
    lon = float(pt["Point_Lon"])
    url = (
        "https://power.larc.nasa.gov/api/temporal/monthly/point?"
        "parameters=TS&community=AG&longitude={:.4f}&latitude={:.4f}&start=1996&end=2025&format=JSON"
    ).format(lon, lat)

    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=35)
            if resp.status_code == 200:
                data = resp.json()
                ts_dict = data.get("properties", {}).get("parameter", {}).get("TS", {})
                if ts_dict and len(ts_dict) >= 360:
                    return pid, ts_dict
            elif resp.status_code == 429:
                time.sleep(2 ** (attempt + 1))
            else:
                time.sleep(1 + attempt)
        except Exception as e:
            time.sleep(1 + attempt)
    raise RuntimeError("Failed to fetch TS for point %s (lat=%s, lon=%s) after %d retries" % (pid, lat, lon, retries))


def main():
    if not os.path.exists(STAGING_DIR):
        os.makedirs(STAGING_DIR)
    if not os.path.exists(MONTHLY_CLIM_DIR):
        os.makedirs(MONTHLY_CLIM_DIR)

    with open(PTS_JSON, "r") as f:
        points = json.load(f)

    temp_json_path = os.path.join(TABLES_DIR, "egypt_temp_seasons_646.json")
    with open(temp_json_path, "r") as f:
        temp_dict = {int(k): v for k, v in json.load(f).items()}

    temp_months_json_path = os.path.join(TABLES_DIR, "egypt_temp_months_646.json")
    temp_months_dict = {}
    if os.path.exists(temp_months_json_path):
        with open(temp_months_json_path, "r") as f:
            temp_months_dict = {int(k): v for k, v in json.load(f).items()}

    print("Loaded %d points from %s, seasonal temps from %s, and monthly temps from %s" % (
        len(points), PTS_JSON, temp_json_path, temp_months_json_path))

    # Check cache
    raw_cache = {}
    if os.path.exists(RAW_TS_JSON):
        try:
            with open(RAW_TS_JSON, "r") as f:
                raw_cache = json.load(f)
            print("Loaded %d cached points from %s" % (len(raw_cache), RAW_TS_JSON))
        except Exception:
            raw_cache = {}

    missing_pts = [p for p in points if str(p["OBJECTID"]) not in raw_cache or len(raw_cache[str(p["OBJECTID"])]) < 360]
    print("Points needing download: %d" % len(missing_pts))

    if missing_pts:
        completed = 0
        total = len(missing_pts)
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_pt = {executor.submit(fetch_point_ts, pt): pt for pt in missing_pts}
            for future in concurrent.futures.as_completed(future_to_pt):
                pt = future_to_pt[future]
                try:
                    pid, ts_dict = future.result()
                    raw_cache[pid] = ts_dict
                    completed += 1
                    if completed % 25 == 0 or completed == total:
                        print("Downloaded %d / %d points..." % (completed, total))
                        with open(RAW_TS_JSON, "w") as f:
                            json.dump(raw_cache, f)
                except Exception as exc:
                    print("Error on point %s: %s" % (pt["OBJECTID"], exc))
                    raise exc

        with open(RAW_TS_JSON, "w") as f:
            json.dump(raw_cache, f)
        print("All %d points cached in %s" % (len(raw_cache), RAW_TS_JSON))

    # Now calculate all 25 indicators for each point
    calculated_data = []

    for pt in points:
        pid = str(pt["OBJECTID"])
        ts_raw = raw_cache[pid]
        # ts_raw keys: "YYYYMM", e.g. "199601" .. "202512" (and index 13 e.g. "199613" annual)
        # Parse into month buckets: month 1..12
        month_vals = {m: [] for m in range(1, 13)}
        for k, v in ts_raw.items():
            if v is not None and abs(float(v) + 999.0) > 1e-5:
                ym = str(k).strip()
                if len(ym) == 6:
                    m_str = ym[4:6]
                    if m_str.isdigit():
                        m_int = int(m_str)
                        if 1 <= m_int <= 12:
                            month_vals[m_int].append(float(v))

        # 12 monthly climatological means
        clim_monthly = {}
        for m in range(1, 13):
            vlist = month_vals[m]
            if not vlist:
                raise ValueError("Missing month %d for point %s" % (m, pid))
            clim_monthly[m] = sum(vlist) / float(len(vlist))

        # 4 seasonal means
        seasonal_means = {}
        for sname, smonths in SEASONS.items():
            svals = [clim_monthly[m] for m in smonths]
            seasonal_means[sname] = sum(svals) / float(len(svals))

        # Annual mean
        ann_vals = [clim_monthly[m] for m in range(1, 13)]
        ann_mean = sum(ann_vals) / 12.0
        month_mean = ann_mean

        # Ranges
        ann_range = max(ann_vals) - min(ann_vals)
        s_vals = [seasonal_means[s] for s in ["Winter", "Spring", "Summer", "Autumn"]]
        sea_range = max(s_vals) - min(s_vals)

        # Differences with air temperature
        t_data = temp_dict[int(pt["OBJECTID"])]
        t_ann = float(t_data["T_Annual_Mean"])
        t_win = float(t_data["T_Winter_Mean"])
        t_spr = float(t_data["T_Spring_Mean"])
        t_sum = float(t_data["T_Summer_Mean"])
        t_aut = float(t_data["T_Autumn_Mean"])
        diff_ann = ann_mean - t_ann
        diff_win = seasonal_means["Winter"] - t_win
        diff_spr = seasonal_means["Spring"] - t_spr
        diff_sum = seasonal_means["Summer"] - t_sum
        diff_aut = seasonal_means["Autumn"] - t_aut

        record = {
            "OBJECTID": pt["OBJECTID"],
            "Source_ID": pt["Source_ID"],
            "Point_Lat": round(pt["Point_Lat"], 4),
            "Point_Lon": round(pt["Point_Lon"], 4),
            "X_3857": pt["X_3857"],
            "Y_3857": pt["Y_3857"],
            "Data_Start": "1996",
            "Data_End": "2025",
            "Temporal": "Monthly",
            "Interp_Meth": "Spline(Tension,w=30.00,n=12)",
            "Cell_Size": 250.0,
            "Wind_Cell": 50000.0,
            "Measurement_Unit": u"°C",
            "Status": "OK",
            "Error_Msg": "None",
            "LST_Annual_Mean": round(ann_mean, 2),
            "LST_Month_Mean": round(month_mean, 2),
            "LST_Winter_Mean": round(seasonal_means["Winter"], 2),
            "LST_Spring_Mean": round(seasonal_means["Spring"], 2),
            "LST_Summer_Mean": round(seasonal_means["Summer"], 2),
            "LST_Autumn_Mean": round(seasonal_means["Autumn"], 2),
            "LST_Annual_Range": round(ann_range, 2),
            "LST_Seasonal_Range": round(sea_range, 2),
            "LST_minus_T_Annual": round(diff_ann, 2),
            "LST_minus_T_Winter": round(diff_win, 2),
            "LST_minus_T_Spring": round(diff_spr, 2),
            "LST_minus_T_Summer": round(diff_sum, 2),
            "LST_minus_T_Autumn": round(diff_aut, 2),
        }
        for m_idx, m_name in enumerate(MONTH_NAMES, 1):
            record["LST_%s_Mean" % m_name] = round(clim_monthly[m_idx], 2)
            if temp_months_dict and int(pt["OBJECTID"]) in temp_months_dict:
                t_m = float(temp_months_dict[int(pt["OBJECTID"])][m_name])
                record["LST_minus_T_%s" % m_name] = round(clim_monthly[m_idx] - t_m, 2)

        calculated_data.append(record)

    print("Calculated all 37 indicators for all %d points." % len(calculated_data))

    # Save calculated JSON for ArcPy
    calc_json_path = os.path.join(TABLES_DIR, "egypt_lst_calculated_646.json")
    with open(calc_json_path, "w") as f:
        json.dump(calculated_data, f, indent=2)
    print("Saved calculated JSON to %s" % calc_json_path)

    # 1. Export CSV without BOM: 19_Land_Surface_Temperature.csv
    csv_fields = [
        "OBJECTID", "Source_ID", "Point_Lat", "Point_Lon", "Data_Start", "Data_End",
        "Temporal", "Interp_Meth", "Cell_Size", "Wind_Cell", "Measurement_Unit", "Status", "Error_Msg",
        "LST_Annual_Mean", "LST_Month_Mean", "LST_Winter_Mean", "LST_Spring_Mean",
        "LST_Summer_Mean", "LST_Autumn_Mean", "LST_Annual_Range", "LST_Seasonal_Range",
        "LST_minus_T_Annual", "LST_minus_T_Winter", "LST_minus_T_Spring",
        "LST_minus_T_Summer", "LST_minus_T_Autumn"
    ]
    csv_path = os.path.join(STAGING_DIR, "19_Land_Surface_Temperature.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields, extrasaction="ignore")
        writer.writeheader()
        for r in calculated_data:
            writer.writerow(r)
    print("Exported staging CSV without BOM: %s" % csv_path)

    # 2. Export Monthly_Climatology CSV
    clim_csv_fields = ["OBJECTID", "Source_ID"] + ["LST_%s_Mean" % m for m in MONTH_NAMES]
    clim_csv_path = os.path.join(MONTHLY_CLIM_DIR, "Land_Surface_Temperature.csv")
    with open(clim_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=clim_csv_fields, extrasaction="ignore")
        writer.writeheader()
        for r in calculated_data:
            writer.writerow(r)
    print("Exported Monthly_Climatology CSV: %s" % clim_csv_path)

    # 3. Export .xls Workbook (Data and Month sheets) using xlwt
    wb = xlwt.Workbook(encoding="utf-8")
    ws_data = wb.add_sheet("Data")
    ws_month = wb.add_sheet("Month")

    header_font = xlwt.Font()
    header_font.name = "Arial"
    header_font.bold = True
    header_style = xlwt.XFStyle()
    header_style.font = header_font

    data_style = xlwt.XFStyle()
    data_style.font = xlwt.Font()
    data_style.font.name = "Arial"

    # Write Data sheet
    for col_idx, fld in enumerate(csv_fields):
        ws_data.write(0, col_idx, fld, header_style)

    for row_idx, r in enumerate(calculated_data, 1):
        for col_idx, fld in enumerate(csv_fields):
            val = r.get(fld)
            ws_data.write(row_idx, col_idx, val, data_style)

    # Write Month sheet
    month_sheet_cols = (
        ["OBJECTID", "Source_ID", "Point_Lat", "Point_Lon"]
        + ["LST_%s_Mean" % m for m in MONTH_NAMES]
        + ["LST_minus_T_%s" % m for m in MONTH_NAMES]
    )
    for col_idx, fld in enumerate(month_sheet_cols):
        ws_month.write(0, col_idx, fld, header_style)

    for row_idx, r in enumerate(calculated_data, 1):
        for col_idx, fld in enumerate(month_sheet_cols):
            val = r.get(fld)
            ws_month.write(row_idx, col_idx, val, data_style)

    staging_xls_path = os.path.join(STAGING_DIR, "19_Land_Surface_Temperature.xls")
    wb.save(staging_xls_path)
    print("Saved staging XLS: %s" % staging_xls_path)

    reports_xls_path = os.path.join(TABLES_DIR, "Land_Surface_Temperature.xls")
    wb.save(reports_xls_path)
    print("Copied XLS to 00_Tables_And_Reports: %s" % reports_xls_path)

    # 4. Export GeoJSON
    geojson_features = []
    for r in calculated_data:
        feat = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [r["Point_Lon"], r["Point_Lat"]]
            },
            "properties": {k: v for k, v in r.items() if k not in ("X_3857", "Y_3857")}
        }
        geojson_features.append(feat)

    geojson_obj = {
        "type": "FeatureCollection",
        "features": geojson_features
    }
    geojson_path = os.path.join(STAGING_DIR, "19_Land_Surface_Temperature_Grid_Points.geojson")
    with open(geojson_path, "w", encoding="utf-8") as f:
        json.dump(geojson_obj, f, indent=2)
    print("Exported staging GeoJSON: %s" % geojson_path)

    print("\nPhase 2 Download and Table Generation complete!")


if __name__ == "__main__":
    main()
