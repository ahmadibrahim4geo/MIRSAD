# -*- coding: utf-8 -*-
"""Generate interactive HTML map for Egypt weather stations from NOAA ISD / WMO."""
import urllib.request
import json
import os

url = "https://www.ncei.noaa.gov/pub/data/noaa/isd-history.txt"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

stations = []
with urllib.request.urlopen(req, timeout=20) as resp:
    for line in resp:
        l = line.decode("utf-8", errors="ignore")
        if len(l) > 47 and l[43:45] == "EG":
            usaf = l[0:6].strip()
            name = l[13:42].strip()
            lat_str = l[57:64].strip()
            lon_str = l[65:73].strip()
            elev_str = l[74:81].strip()
            beg = l[82:90].strip()
            end = l[91:99].strip()
            try:
                lat = float(lat_str)
                lon = float(lon_str)
                elev = float(elev_str)
                if 21.0 <= lat <= 32.5 and 24.0 <= lon <= 37.0:
                    stations.append({
                        "id": usaf,
                        "name": name,
                        "lat": lat,
                        "lon": lon,
                        "elev": elev,
                        "start": beg[:4],
                        "end": end[:4]
                    })
            except Exception:
                pass

# Sort by name
stations.sort(key=lambda x: x["name"])

html_content = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>خريطة محطات الرصد الجوي الرسمية في مصر (NOAA / WMO)</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  * { box-sizing: border-box; }
  body { margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; height: 100vh; overflow: hidden; }
  #sidebar { width: 380px; height: 100%; overflow-y: auto; background: #0f172a; color: #fff; padding: 18px; box-sizing: border-box; display: flex; flex-direction: column; }
  #map { flex: 1; height: 100%; }
  h2 { margin-top: 0; color: #38bdf8; font-size: 1.25rem; border-bottom: 2px solid #1e293b; padding-bottom: 10px; }
  .stat-card { background: #1e293b; border-radius: 8px; padding: 12px; margin-bottom: 10px; cursor: pointer; transition: all 0.2s; border-right: 4px solid #38bdf8; }
  .stat-card:hover { background: #334155; transform: translateX(-4px); }
  .stat-name { font-weight: bold; color: #f8fafc; font-size: 0.95rem; }
  .stat-meta { font-size: 0.82rem; color: #94a3b8; margin-top: 4px; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; background: #0284c7; color: #fff; margin-top: 6px; }
  .search-box { width: 100%; padding: 10px 14px; border-radius: 8px; border: 1px solid #334155; background: #1e293b; color: #fff; margin-bottom: 14px; font-size: 0.9rem; }
  .search-box:focus { outline: none; border-color: #38bdf8; }
  #stationList { flex: 1; overflow-y: auto; padding-left: 4px; }
  .leaflet-popup-content-wrapper { direction: ltr; text-align: left; border-radius: 8px; }
</style>
</head>
<body>
<div id="sidebar">
  <h2>محطات رصد جمهورية مصر العربية</h2>
  <p style="font-size:0.85rem; color:#94a3b8; line-height:1.5;">
    قاعدة بيانات الأرصاد الدولية (NOAA ISD / WMO): 
    <br><strong style="color:#38bdf8; font-size:1.05rem;">""" + str(len(stations)) + """ محطة رسمية</strong> تغطي كافة محافظات الجمهورية من الإسكندرية ومطروح وحتى أسوان وشلاتين وسيناء والواحات.
  </p>
  <input type="text" id="search" class="search-box" placeholder="ابحث باسم المحطة أو الكود..." oninput="filterStations()">
  <div id="stationList"></div>
</div>
<div id="map"></div>
<script>
const stations = """ + json.dumps(stations, ensure_ascii=False) + """;

const map = L.map('map').setView([27.0, 30.5], 6);

const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; OpenStreetMap contributors'
});

const satellite = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
  maxZoom: 19,
  attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
});

satellite.addTo(map);

L.control.layers({ 'الأقمار الصناعية (Satellite)': satellite, 'خريطة الشوارع (OpenStreetMap)': osm }, null, { position: 'topleft' }).addTo(map);

const markers = {};

function renderList(items) {
  const listEl = document.getElementById('stationList');
  listEl.innerHTML = '';
  items.forEach(s => {
    const card = document.createElement('div');
    card.className = 'stat-card';
    card.onclick = () => {
      map.flyTo([s.lat, s.lon], 11, { duration: 1.2 });
      markers[s.id].openPopup();
    };
    card.innerHTML = `
      <div class="stat-name">${s.name}</div>
      <div class="stat-meta">الكود الدولي: <code>${s.id}</code> | المنسوب: ${s.elev} م</div>
      <div class="stat-meta">الإحداثيات: ${s.lat.toFixed(3)}° N, ${s.lon.toFixed(3)}° E</div>
      <span class="badge">سنوات الرصد: ${s.start} - ${s.end}</span>
    `;
    listEl.appendChild(card);
  });
}

stations.forEach(s => {
  const marker = L.circleMarker([s.lat, s.lon], {
    radius: 7,
    fillColor: '#38bdf8',
    color: '#0369a1',
    weight: 2,
    opacity: 1,
    fillOpacity: 0.9
  }).addTo(map);

  marker.bindPopup(`
    <div style="font-family:'Segoe UI',sans-serif; min-width:180px;">
      <h3 style="margin:0 0 6px; color:#0369a1; font-size:1.05rem;">${s.name}</h3>
      <p style="margin:4px 0; font-size:12px; color:#475569;"><b>USAF / WMO ID:</b> <code>${s.id}</code></p>
      <p style="margin:4px 0; font-size:12px; color:#475569;"><b>Latitude:</b> ${s.lat}° N</p>
      <p style="margin:4px 0; font-size:12px; color:#475569;"><b>Longitude:</b> ${s.lon}° E</p>
      <p style="margin:4px 0; font-size:12px; color:#475569;"><b>Elevation:</b> ${s.elev} meters</p>
      <p style="margin:4px 0; font-size:12px; color:#0284c7;"><b>Data Record:</b> ${s.start} &ndash; ${s.end}</p>
    </div>
  `);

  markers[s.id] = marker;
});

renderList(stations);

function filterStations() {
  const q = document.getElementById('search').value.toLowerCase();
  const filtered = stations.filter(s => s.name.toLowerCase().includes(q) || s.id.toLowerCase().includes(q));
  renderList(filtered);
}
</script>
</body>
</html>
"""

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out_path = os.path.join(base_dir, "Documents", "Egypt_Weather_Stations_Map.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated {out_path} with {len(stations)} stations.")
