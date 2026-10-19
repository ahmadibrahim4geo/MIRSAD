"""Immutable embedded station directory. No parent-repository dependency."""
import hashlib
import json
import sqlite3
import sys
from pathlib import Path


def asset_dir():
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "assets"
    return Path(__file__).resolve().parents[2] / "assets"


class Catalogue:
    def __init__(self, path=None):
        self.path = Path(path) if path else asset_dir() / "stations.sqlite"
        if not self.path.is_file():
            raise RuntimeError("Embedded station catalogue is missing. Prepare the application assets first.")

    def connect(self):
        return sqlite3.connect(self.path.resolve().as_uri() + "?mode=ro", uri=True)

    def metadata(self):
        with self.connect() as db:
            return {key: json.loads(value) for key, value in db.execute("SELECT key,value FROM metadata")}

    def countries(self, region=""):
        query = "SELECT country, country_name, country_ar, COUNT(*) FROM stations"
        args = []
        if region == "Arab":
            query += " WHERE is_arab=1"
        elif region:
            query += " WHERE continent=?"
            args.append(region)
        query += " GROUP BY country ORDER BY country_name"
        with self.connect() as db:
            rows = list(db.execute(query, args))

        total_stations = sum(r[3] for r in rows)
        aggregates = []
        if region == "Arab":
            aggregates.append(("ARAB", "[All Arab League Countries (ARAB)]", "[جميع دول الوطن العربي (ARAB)]", total_stations))
        elif region:
            ar_names = {
                "Africa": "أفريقيا", "Asia": "آسيا", "Europe": "أوروبا",
                "North America": "أمريكا الشمالية", "South America": "أمريكا الجنوبية",
                "Oceania": "أوقيانوسيا", "Antarctica": "القارة القطبية الجنوبية"
            }
            ar_reg = ar_names.get(region, region)
            aggregates.append((region.upper(), f"[All {region} Countries ({region.upper()})]", f"[جميع دول قارة {ar_reg} ({region.upper()})]", total_stations))
        else:
            aggregates.append(("WORLD", "[All Countries Worldwide (WORLD)]", "[جميع دول العالم (WORLD)]", total_stations))

        return aggregates + rows

    def stations(self, country=None, search=""):
        if not country:
            return []
        c_up = str(country).strip().upper()
        if c_up in ("ARAB", "[ALL ARAB LEAGUE COUNTRIES (ARAB)]"):
            query = "SELECT * FROM stations WHERE is_arab=1"
            args = []
        elif c_up in ("AFRICA", "ASIA", "EUROPE", "NORTH AMERICA", "SOUTH AMERICA", "OCEANIA", "ANTARCTICA"):
            query = "SELECT * FROM stations WHERE UPPER(continent)=?"
            args = [c_up]
        elif c_up in ("WORLD", "ALL", "[ALL COUNTRIES WORLDWIDE (WORLD)]"):
            query = "SELECT * FROM stations WHERE 1=1"
            args = []
        else:
            if "(" in country and ")" in country:
                c_code = country.split("(")[1].split(")")[0].strip().upper()
            else:
                c_code = country.strip()
            query = "SELECT * FROM stations WHERE country=?"
            args = [c_code]

        if search:
            query += " AND (name LIKE ? OR usaf LIKE ? OR wban LIKE ?)"
            args += ["%" + search + "%"] * 3
        query += " ORDER BY name, usaf, wban, latitude, longitude"
        with self.connect() as db:
            db.row_factory = sqlite3.Row
            return [dict(row) for row in db.execute(query, args)]

    def digest(self):
        return hashlib.sha256(self.path.read_bytes()).hexdigest()
