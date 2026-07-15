#!/usr/bin/env python3
"""Geocode addresses to lat/lon for Paris-guide map pins, via OpenStreetMap Nominatim.

Usage:
  python3 tools/geocode.py "Label|Address, City, Country" "Label2|Address2 …"
  # or pipe lines on stdin (one "Label|Address" per line):
  printf '%s\n' "Grand Palais|Grand Palais, Paris, France" | python3 tools/geocode.py

If a line has no "|", the whole line is treated as both label and address.
Prints:  Label: <lat>, <lon>  | <matched display name>
Respects Nominatim's usage policy: sets a User-Agent and throttles ~1.2s/request.
"""
import sys, time, json, urllib.request, urllib.parse

UA = "paris-trip-planner/1.0 (crumley@gmail.com)"

def items():
    if len(sys.argv) > 1:
        yield from sys.argv[1:]
    else:
        for line in sys.stdin:
            line = line.strip()
            if line:
                yield line

def geocode(q):
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": q, "format": "json", "limit": 1})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

def main():
    rows = list(items())
    if not rows:
        print(__doc__); return
    for i, raw in enumerate(rows):
        label, _, addr = raw.partition("|")
        addr = (addr or label).strip()
        label = label.strip()
        try:
            d = geocode(addr)
            if d:
                print(f"{label}: {d[0]['lat']}, {d[0]['lon']}  | {d[0]['display_name'][:70]}")
            else:
                print(f"{label}: NO RESULT for {addr!r} — simplify (drop street number / use landmark)")
        except Exception as e:
            print(f"{label}: ERROR {e}")
        if i < len(rows) - 1:
            time.sleep(1.2)

if __name__ == "__main__":
    main()
