"""Download Natural Earth country boundaries (public domain) and cut small GeoJSON files for the site's maps.

- site/data/geo_sea.json: Southeast Asia and neighbours, 1:50m, simplified (landing map)
- site/data/geo_sgp.json: Singapore from geoBoundaries (CC BY 4.0), with offshore islands (country profile map)
Raw files go to data/raw/geo/ (git-ignored). Run: python scripts/fetch_geo.py
"""
import json
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "geo"
OUT = ROOT / "site" / "data"
RAW.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
BASE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/"
HEADERS = {"User-Agent": "ec391-singapore/1.0 (university course project)"}
BBOX = (88, -12, 135, 30)  # lon_min, lat_min, lon_max, lat_max


def get(name):
    path = RAW / name
    if not path.exists():
        r = requests.get(BASE + name, headers=HEADERS, timeout=600)
        r.raise_for_status()
        path.write_bytes(r.content)
    return json.loads(path.read_text(encoding="utf-8"))


def rings(geom):
    if geom["type"] == "Polygon":
        return [geom["coordinates"]]
    return geom["coordinates"]


def simplify(poly, step):
    """Round coordinates and drop consecutive duplicates (enough for a small overview map)."""
    out = []
    for ring in poly:
        pts, last = [], None
        for x, y in ring:
            p = (round(x / step) * step, round(y / step) * step)
            if p != last:
                pts.append([round(p[0], 3), round(p[1], 3)])
                last = p
        if len(pts) >= 4:
            out.append(pts)
    return out


def touches(geom):
    for poly in rings(geom):
        for x, y in poly[0]:
            if BBOX[0] <= x <= BBOX[2] and BBOX[1] <= y <= BBOX[3]:
                return True
    return False


def main():
    world = get("ne_50m_admin_0_countries.geojson")
    feats = []
    for f in world["features"]:
        if not touches(f["geometry"]):
            continue
        polys = [p for p in (simplify(poly, 0.05) for poly in rings(f["geometry"])) if p]
        feats.append({"type": "Feature", "properties": {"name": f["properties"]["NAME"],
                                                        "iso3": f["properties"]["ADM0_A3"]},
                      "geometry": {"type": "MultiPolygon", "coordinates": polys}})
    (OUT / "geo_sea.json").write_text(json.dumps({"type": "FeatureCollection", "features": feats},
                                                 separators=(",", ":")))
    # Singapore detail: geoBoundaries gbOpen ADM0 (CC BY 4.0, Runfola et al. 2020), includes offshore islands
    gb = RAW / "geoBoundaries-SGP-ADM0_simplified.geojson"
    if not gb.exists():
        r = requests.get("https://github.com/wmgeolab/geoBoundaries/raw/main/releaseData/gbOpen/SGP/ADM0/"
                         "geoBoundaries-SGP-ADM0_simplified.geojson", headers=HEADERS, timeout=300)
        r.raise_for_status()
        gb.write_bytes(r.content)
    sgp = json.loads(gb.read_text(encoding="utf-8"))["features"]
    for f in sgp:
        f["properties"] = {"name": "Singapore", "iso3": "SGP"}
        f["geometry"] = {"type": "MultiPolygon",
                         "coordinates": [p for p in (simplify(p, 0.0003) for p in rings(f["geometry"])) if p]}
    (OUT / "geo_sgp.json").write_text(json.dumps({"type": "FeatureCollection", "features": sgp},
                                                 separators=(",", ":")))
    print(f"geo_sea.json: {len(feats)} countries; geo_sgp.json: {len(sgp)} feature(s)")


if __name__ == "__main__":
    main()
