# -*- coding: utf-8 -*-
"""Comprehensive Coordinate Reference System (CRS) registry and ArcMap-style hierarchical taxonomy."""

import re

# Comprehensive list of standard and regional GIS Coordinate Reference Systems (flat list for quick access)
COMMON_CRS_LIST = [
    # Global Geographic & Projected
    ("EPSG:4326", "WGS 84 — World Geodetic System 1984 (Geographic Lat/Lon)"),
    ("EPSG:3857", "WGS 84 / Pseudo-Mercator — Spherical Web Mercator"),
    ("EPSG:6933", "WGS 84 / World Cylindrical Equal Area"),
    ("EPSG:4087", "WGS 84 / World Equidistant Cylindrical"),
    ("EPSG:4258", "ETRS89 — European Terrestrial Reference System 1989"),
    ("EPSG:4269", "NAD83 — North American Datum 1983"),

    # Middle East & Arab Region UTM & National Grids
    ("EPSG:32635", "WGS 84 / UTM zone 35N (Western Egypt, Libya, Greece)"),
    ("EPSG:32636", "WGS 84 / UTM zone 36N (Egypt Nile & Delta, Levant, Western Saudi)"),
    ("EPSG:32637", "WGS 84 / UTM zone 37N (Sinai, Red Sea, Central Saudi Arabia)"),
    ("EPSG:32638", "WGS 84 / UTM zone 38N (Eastern Saudi Arabia, Iraq, Gulf)"),
    ("EPSG:32639", "WGS 84 / UTM zone 39N (UAE, Oman, Eastern Gulf)"),
    ("EPSG:32640", "WGS 84 / UTM zone 40N (Oman, Arabian Sea)"),
    ("EPSG:32629", "WGS 84 / UTM zone 29N (Morocco West, Mauritania)"),
    ("EPSG:32630", "WGS 84 / UTM zone 30N (Morocco East, Algeria West, Spain)"),
    ("EPSG:32631", "WGS 84 / UTM zone 31N (Algeria Central, France)"),
    ("EPSG:32632", "WGS 84 / UTM zone 32N (Algeria East, Tunisia, Italy)"),
    ("EPSG:32633", "WGS 84 / UTM zone 33N (Libya, Central Europe)"),
    ("EPSG:32634", "WGS 84 / UTM zone 34N (Libya East, Eastern Europe)"),
    ("EPSG:22992", "Egypt 1907 / Red Belt (Nile Valley & Delta)"),
    ("EPSG:22993", "Egypt 1907 / Purple Belt (Sinai Peninsula)"),
    ("EPSG:22991", "Egypt 1907 / Blue Belt (Western Desert)"),
    ("EPSG:22994", "Egypt 1907 / Extended Purple Belt"),
    ("EPSG:28191", "Palestine 1923 / Palestine Grid (Levant / Palestine)"),
    ("EPSG:28192", "Palestine 1923 / Israeli CS Grid"),
    ("EPSG:20436", "Ain el Abd 1970 / Aramco Lambert (Saudi Arabia)"),
    ("EPSG:20437", "Ain el Abd 1970 / UTM zone 37N (Saudi Arabia)"),
    ("EPSG:20438", "Ain el Abd 1970 / UTM zone 38N (Saudi Arabia)"),
    ("EPSG:20439", "Ain el Abd 1970 / UTM zone 39N (Saudi Arabia)"),
    ("EPSG:3889", "Nahrwan 1967 / UTM zone 37N (Iraq)"),
    ("EPSG:3890", "Nahrwan 1967 / UTM zone 38N (Iraq)"),
    ("EPSG:3891", "Nahrwan 1967 / UTM zone 39N (Iraq)"),
    ("EPSG:3994", "Trucial Coast 1948 / UTM zone 39N (UAE)"),
    ("EPSG:3995", "Trucial Coast 1948 / UTM zone 40N (UAE)"),

    # Europe & International Projected Grids
    ("EPSG:3035", "ETRS89-extended / LAEA Europe (Equal Area)"),
    ("EPSG:2154", "RGF93 v1 / Lambert-93 (France)"),
    ("EPSG:27700", "OSGB36 / British National Grid (UK)"),
    ("EPSG:25832", "ETRS89 / UTM zone 32N (Germany, Europe)"),
    ("EPSG:25833", "ETRS89 / UTM zone 33N (Central Europe)"),

    # Americas & Global UTM Zones
    ("EPSG:32610", "WGS 84 / UTM zone 10N (US Pacific Northwest)"),
    ("EPSG:32611", "WGS 84 / UTM zone 11N (US West, California)"),
    ("EPSG:32612", "WGS 84 / UTM zone 12N (US Mountain West)"),
    ("EPSG:32613", "WGS 84 / UTM zone 13N (US Great Plains West)"),
    ("EPSG:32614", "WGS 84 / UTM zone 14N (US Great Plains Central, Texas)"),
    ("EPSG:32615", "WGS 84 / UTM zone 15N (US Midwest)"),
    ("EPSG:32616", "WGS 84 / UTM zone 16N (US Great Lakes)"),
    ("EPSG:32617", "WGS 84 / UTM zone 17N (US East Coast)"),
    ("EPSG:32618", "WGS 84 / UTM zone 18N (US Northeast / New York)"),
    ("EPSG:32619", "WGS 84 / UTM zone 19N (US New England)"),
    ("EPSG:31983", "SIRGAS 2000 / UTM zone 23S (Brazil / Rio / Sao Paulo)"),
    ("EPSG:28355", "GDA94 / MGA zone 55 (Australia East Coast / Sydney)"),
    ("EPSG:28356", "GDA94 / MGA zone 56 (Australia Brisbane)")
]


from functools import lru_cache
import gzip
import json
from .catalogue import asset_dir


@lru_cache(maxsize=1)
def crs_catalogue():
    path=asset_dir()/"crs_catalogue.json.gz"
    return json.loads(gzip.decompress(path.read_bytes()))


@lru_cache(maxsize=1)
def catalogue_by_code():
    return {entry["code"].upper():entry for entry in crs_catalogue()}


def resolve_crs(value):
    """Resolve official definitions even when the local PROJ database is older."""
    from pyproj import CRS
    text=str(value).strip()
    if text.isdigit():text="EPSG:"+text
    # Prefer PROJ's canonical EPSG/ESRI definition (including current datum
    # ensembles); use the official WKT only for codes absent from this runtime.
    try:return CRS.from_user_input(text)
    except Exception:
        entry=catalogue_by_code().get(text.upper())
        if not entry:raise
        return CRS.from_wkt(entry["wkt"])


@lru_cache(maxsize=1)
def native_crs_catalogue():
    """Versioned Pro folder paths, including native aliases in multiple folders."""
    return json.loads(gzip.decompress((asset_dir()/"crs_pro_tree.json.gz").read_bytes()))


@lru_cache(maxsize=1)
def additional_crs_catalogue():
    native_codes={row["code"].upper() for row in native_crs_catalogue()}
    return [row for row in crs_catalogue() if row["code"].upper() not in native_codes]


@lru_cache(maxsize=1)
def native_by_code():
    return {row["code"].upper():row for row in native_crs_catalogue()}


def crs_display_name(value):
    row=native_by_code().get(str(value).upper()) or catalogue_by_code().get(str(value).upper())
    if row:return row["name"]
    info=validate_and_describe_crs(value)
    return info.get("name") or str(value)


def build_crs_hierarchy(arabic=False,latest=False):
    """Always retain native paths; optional additions have an explicit provenance.

    Public PE definitions declare areas of use, not Pro UI folder paths. They
    must never replace the native taxonomy or masquerade as native folders.
    """
    root={"folders":[]};folders={}
    entries=list(native_crs_catalogue())
    if latest:
        extra_title="Additional Esri definitions (outside Pro 3.6 tree)"
        entries.extend(dict(row,folder=[row["folder"][0],extra_title,*row["folder"][1:]])
                       for row in additional_crs_catalogue())
    for entry in entries:
        current=root
        for depth,title in enumerate(entry["folder"]):
            key=tuple(entry["folder"][:depth+1])
            if key not in folders:
                node={"title":title,"subfolders":[],"items":[]}
                current.setdefault("folders" if depth==0 else "subfolders",[]).append(node)
                folders[key]=node
            current=folders[key]
        current.setdefault("items",[]).append((entry["code"],entry["name"],
            entry["esri_name"]+(" [deprecated]" if entry["deprecated"] else "")))
    # Keep the scientific/navigation folder names identical in both languages.
    return root


# Quick choices use the same official definitions and labels as the complete tree.
COMMON_CRS_LIST=[(code,catalogue_by_code().get(code,{}).get("name",name)) for code,name in COMMON_CRS_LIST]


def validate_and_describe_crs(crs_input):
    """
    Validates any user CRS input (EPSG code, string, or WKT) via pyproj.
    Extracts complete ArcMap-style Spatial Reference properties.
    Returns: dict with validation status and structured parameters.
    """
    if not crs_input or not str(crs_input).strip():
        return dict(valid=False, code=None, name=None, is_projected=False, error="CRS input is empty")

    crs_str = str(crs_input).strip()
    if crs_str.isdigit():
        crs_str = f"EPSG:{crs_str}"

    try:
        from pyproj import CRS
        proj = resolve_crs(crs_str)
        auth = f"{proj.to_authority()[0]}:{proj.to_authority()[1]}" if proj.to_authority() else crs_str

        # Extract projection method and parameters if projected
        proj_method = None
        params = []
        if proj.is_projected and proj.coordinate_operation:
            proj_method = proj.coordinate_operation.method_name
            if hasattr(proj.coordinate_operation, "params"):
                for p in proj.coordinate_operation.params:
                    params.append({"name": p.name, "value": p.value})

        datum_name = proj.datum.name if proj.datum else "N/A"
        ellipsoid_name = proj.ellipsoid.name if proj.ellipsoid else "N/A"
        semi_major = proj.ellipsoid.semi_major_metre if proj.ellipsoid else None
        inv_flattening = proj.ellipsoid.inverse_flattening if proj.ellipsoid else None
        prime_meridian = proj.prime_meridian.name if proj.prime_meridian else "Greenwich"
        unit_name = proj.axis_info[0].unit_name if hasattr(proj, "axis_info") and proj.axis_info else "degree"
        area_of_use = proj.area_of_use.name if proj.area_of_use else "World"

        return dict(
            valid=True,
            code=auth,
            name=proj.name,
            is_projected=bool(proj.is_projected),
            is_geographic=bool(proj.is_geographic),
            projection_method=proj_method,
            parameters=params,
            datum=datum_name,
            ellipsoid=ellipsoid_name,
            semi_major=semi_major,
            inverse_flattening=inv_flattening,
            prime_meridian=prime_meridian,
            unit=unit_name,
            area_of_use=area_of_use,
            axis_info=[str(axis) for axis in proj.axis_info] if hasattr(proj, 'axis_info') else [],
            error=None
        )
    except Exception as exc:
        return dict(valid=False, code=crs_str, name=None, is_projected=False, error=str(exc))
