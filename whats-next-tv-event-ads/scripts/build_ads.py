#!/usr/bin/env python3
"""Build a city's event ad page from its events JSON.

Picks events from today through the next N days, removes repeats of the same
recurring event, caps the count, makes QR codes (one set per placement so the
scans can be told apart in analytics) and writes a static site folder:

    site/{city}/index.html   the ad page (layouts chosen by URL parameter)
    site/{city}/ads.json     today's ads
    site/{city}/qr/*.svg     QR codes

Usage:
    python3 scripts/build_ads.py data/fallbrook_events.json --out site \
        [--days 5] [--max 12] [--today 2026-11-14] [--featured featured.json]

featured.json (optional): {"urls": ["https://whatsnext.buzz/fallbrook/events/..."]}
Featured events always run first, even outside the date window (paid boosts).

Run once a day (e.g. 5:00 am Pacific). The page re-reads ads.json every
10 minutes, so screens and the stream pick up the new ads without a reload.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
from urllib.parse import urlencode

import segno  # pip install segno

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "template", "index.html")
PLACEMENTS = ("stream", "store", "web")


def norm_title(t):
    t = t.lower()
    t = re.sub(r"\(.*?\)", "", t)
    t = re.sub(r"[-–—:].*every .*$", "", t)
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def date_label(start, end, today):
    if start is None or start < today:
        if end:
            e = dt.date.fromisoformat(end)
            return f"ON NOW\nTHRU {e.strftime('%b').upper()} {e.day}"
        return "ON NOW"
    d = (start - today).days
    if d == 0:
        return "TODAY"
    if d == 1:
        return "TOMORROW"
    return f"{start.strftime('%a').upper()}\n{start.strftime('%b').upper()} {start.day}"


def clean_venue(v):
    """Shorten long addresses: drop country, state and ZIP tails."""
    if not v:
        return ""
    v = re.sub(r",?\s*United States.*$", "", v)
    v = re.sub(r",?\s*(CA|California)\s*\d{5}(-\d{4})?\s*$", "", v)
    v = re.sub(r",?\s*\d{5}\s*$", "", v)
    return v.strip(" ,")


def tracked(url, placement, city):
    sep = "&" if "?" in url else "?"
    return url + sep + urlencode({"utm_source": "wntv",
                                  "utm_medium": placement,
                                  "utm_campaign": "ads"})


def pick(events, today, days, limit, featured):
    last = today + dt.timedelta(days=days)
    chosen, seen = [], set()

    def add(e, start):
        key = norm_title(e["title"])
        if key in seen:
            return
        seen.add(key)
        chosen.append((e, start))

    by_url = {e["url"]: e for e in events}
    for u in featured:
        if u in by_url:
            e = by_url[u]
            add(e, dt.date.fromisoformat(e["date"]) if e.get("date") else None)

    dated = []
    for e in events:
        start = dt.date.fromisoformat(e["date"]) if e.get("date") else None
        end = dt.date.fromisoformat(e["end"]) if e.get("end") else None
        if start and today <= start <= last:
            dated.append((start, 0, e))
        elif end and end >= today and (start is None or start <= today):
            dated.append((today, 1, e))     # running now; after same-day events
    dated.sort(key=lambda x: (x[0], x[1]))

    # Spread the slots across the window: take one event per day in turn
    # (today, tomorrow, ... day N, then round again) so later days are not
    # crowded out by a busy today. Featured events are already in.
    buckets = {}
    for start, _, e in dated:
        buckets.setdefault(start, []).append(e)
    days_in_order = sorted(buckets)
    while len(chosen) < limit and any(buckets.values()):
        for d in days_in_order:
            if len(chosen) >= limit:
                break
            while buckets[d]:
                e = buckets[d].pop(0)
                before = len(chosen)
                add(e, dt.date.fromisoformat(e["date"]) if e.get("date") else None)
                if len(chosen) > before:
                    break

    # featured first, then the rest in date order (running events count as today)
    n_feat = sum(1 for e, _ in chosen if e["url"] in featured)
    def minutes(e):
        m = re.match(r"(\d{1,2}):(\d{2})\s*([AP]M)", e.get("time") or "", re.I)
        if not m:
            return 24 * 60
        h = int(m.group(1)) % 12 + (12 if m.group(3).upper() == "PM" else 0)
        return h * 60 + int(m.group(2))
    rest = sorted(chosen[n_feat:], key=lambda x: (max(x[1] or today, today), minutes(x[0])))
    return chosen[:n_feat] + rest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("events_json")
    ap.add_argument("--out", default="site")
    ap.add_argument("--days", type=int, default=5)
    ap.add_argument("--max", type=int, default=12)
    ap.add_argument("--today", help="YYYY-MM-DD; default is today")
    ap.add_argument("--featured", help="featured.json with a list of event URLs")
    ap.add_argument("--details", help="optional {url: {image, time}} file merged into the events "
                                      "(used for offline tests; fetch_events.py adds these itself)")
    a = ap.parse_args()

    data = json.load(open(a.events_json))
    city, city_name = data["city"], data.get("city_name", data["city"].title())
    today = dt.date.fromisoformat(a.today) if a.today else dt.date.today()
    featured = json.load(open(a.featured))["urls"] if a.featured else []
    if a.details:
        det = json.load(open(a.details))
        for e in data["events"]:
            e.update(det.get(e["url"], {}))

    outdir = os.path.join(a.out, city)
    qrdir = os.path.join(outdir, "qr")
    if os.path.isdir(qrdir):
        shutil.rmtree(qrdir)
    os.makedirs(qrdir, exist_ok=True)

    ads = []
    for e, start in pick(data["events"], today, a.days, a.max, featured):
        aid = hashlib.sha1(e["url"].encode()).hexdigest()[:10]
        qr = {}
        for p in PLACEMENTS:
            name = f"{aid}-{p}.svg"
            segno.make(tracked(e["url"], p, city), error="m").save(
                os.path.join(qrdir, name), scale=10, border=2, dark="#060605", light="#ffffff")
            qr[p] = f"qr/{name}"
        ads.append({"id": aid,
                    "title": e["title"],
                    "venue": clean_venue(e.get("venue")),
                    "when": date_label(start, e.get("end"), today),
                    "time": e.get("time") or "",
                    "image": None if not e.get("image") or e["image"].endswith("/og-image.jpg") else e["image"],
                    "url": e["url"],
                    "qr": qr,
                    "featured": e["url"] in featured})

    out = {"city": city, "city_name": city_name, "built_for": today.isoformat(),
           "window_days": a.days, "generated_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
           "ads": ads}
    with open(os.path.join(outdir, "ads.json"), "w") as f:
        json.dump(out, f, indent=1)
    shutil.copy(TEMPLATE, os.path.join(outdir, "index.html"))
    print(f"{len(ads)} ads for {city_name} ({today} + {a.days} days) -> {outdir}")
    for ad in ads:
        print(f"  {ad['when'].replace(chr(10),' '):<20} {ad['time']:>8}  {'IMG' if ad['image'] else '---'}  {ad['title'][:50]}")


if __name__ == "__main__":
    main()
