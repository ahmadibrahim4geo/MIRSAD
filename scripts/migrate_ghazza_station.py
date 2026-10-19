"""Reproducible migration: Correct station 623380 (GHAZZA) from EG to Palestine (PS).

MIRSAD development guidelines require explicit, reproducible migrations with
before/after evidence, retaining identifiers, coordinates, and deterministic hash.
"""
import datetime as dt
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data/stations.sqlite"


def migrate():
    print("=== MIRSAD Station Catalogue Migration ===")
    print(f"Target Database: {DB_PATH}")

    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        cur = db.cursor()

        # 1. Before state
        before = cur.execute(
            "SELECT station_key, usaf, wban, name, country, country_name, country_ar, continent, is_arab, latitude, longitude FROM stations WHERE usaf = '623380'"
        ).fetchone()
        if not before:
            raise RuntimeError("Station 623380 not found in database!")

        print("\n[BEFORE MIGRATION]")
        print(dict(before))

        # 2. Execute update
        cur.execute(
            """
            UPDATE stations
            SET country = 'PS',
                country_name = 'Palestine',
                country_ar = 'دولة فلسطين',
                continent = 'Asia',
                is_arab = 1
            WHERE usaf = '623380'
            """
        )

        # 3. After state
        after = cur.execute(
            "SELECT station_key, usaf, wban, name, country, country_name, country_ar, continent, is_arab, latitude, longitude FROM stations WHERE usaf = '623380'"
        ).fetchone()
        print("\n[AFTER MIGRATION]")
        print(dict(after))

        assert after["country"] == "PS"
        assert after["country_name"] == "Palestine"
        assert after["continent"] == "Asia"
        assert after["is_arab"] == 1

        # 4. Check total count
        count = cur.execute("SELECT COUNT(*) FROM stations").fetchone()[0]
        meta = {k: json.loads(v) for k, v in cur.execute("SELECT key, value FROM metadata")}
        assert count == meta["count"], f"Station count changed: {count} vs {meta['count']}"

        # 5. Compute new semantic hash
        rows = [dict(r) for r in cur.execute("SELECT * FROM stations ORDER BY rowid")]
        new_hash = hashlib.sha256(json.dumps(rows, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        new_version = "2026.10.17.3"

        print(f"\nPrevious Catalogue Version: {meta['catalogue_version']} ({meta['catalogue_hash']})")
        print(f"New Catalogue Version:      {new_version} ({new_hash})")

        cur.execute("UPDATE metadata SET value = ? WHERE key = 'catalogue_version'", (json.dumps(new_version),))
        cur.execute("UPDATE metadata SET value = ? WHERE key = 'catalogue_hash'", (json.dumps(new_hash),))
        cur.execute(
            "UPDATE metadata SET value = ? WHERE key = 'audited_utc'",
            (json.dumps(dt.datetime.now(dt.timezone.utc).isoformat()),)
        )

        db.commit()
        print("\nMigration completed and committed successfully.")


if __name__ == "__main__":
    migrate()
