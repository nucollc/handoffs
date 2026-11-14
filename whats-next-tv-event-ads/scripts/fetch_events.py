#!/usr/bin/env python3
"""Fetch a city's event listings from whatsnext.buzz and write events JSON.

Pilot version: reads the public city page (whatsnext.buzz/{city}/events) because
the site has no feed yet. Event links follow
    /{city}/events/{event-slug}-{YYYY-MM-DD}
so the date comes from the URL and the title from the link text.

RECOMMENDED for scale: replace this with a JSON endpoint on whatsnext.buzz
(e.g. /api/events?city=fallbrook&from=...&to=...) read straight from the
site's database. Output format below is what build_ads.py expects.

Usage:
    python3 scripts/fetch_events.py fallbrook --out data/fallbrook_events.json

Output:
    {"city": "fallbrook", "city_name": "Fallbrook", "fetched_at": ISO,
     "events": [{"title", "url", "date", "end", "venue", "time", "image"}]}
    image and time come from each event page (og:image, first "H:MM AM/PM");
    the site's generic og-image.jpg is treated as "no image".
"""
import argparse
import datetime as dt
import json
import re
import sys
import urllib.request
from html.parser import HTMLParser

BASE = "https://whatsnext.buzz"


class LinkCollector(HTMLParser):
    """Collects <a href> links plus the text that follows each one, so the
    venue (shown after the link as "date · venue · city") can be picked up."""

    def __init__(self):
        super().__init__()
        self.links = []          # [href, link_text, trailing_text]
        self._in_a = False
        self._href = None
        self._text = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._in_a = True
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_endtag(self, tag):
        if tag == "a" and self._in_a:
            self.links.append([self._href, " ".join(self._text).strip(), ""])
            self._in_a = False

    def handle_data(self, data):
        if self._in_a:
            self._text.append(data.strip())
        elif self.links:
            # text between this link and the next one
            self.links[-1][2] += " " + data.strip()


def parse(html, city):
    pat = re.compile(rf"^(?:{re.escape(BASE)})?/{re.escape(city)}/events/(.+)-(\d{{4}}-\d{{2}}-\d{{2}})/?$")
    p = LinkCollector()
    p.feed(html)
    seen, events = set(), []
    for href, text, trailing in p.links:
        if not href:
            continue
        m = pat.match(href)
        if not m or not text:
            continue
        url = href if href.startswith("http") else BASE + href
        if url in seen:
            continue
        seen.add(url)
        trailing = re.sub(r"\s+", " ", trailing).strip(" —-·")
        end = None
        m_end = re.search(r"through\s+(\d{4}-\d{2}-\d{2})", trailing)
        if m_end:
            end = m_end.group(1)
        # venue: the part after the first "·" separator, if present
        parts = [x.strip() for x in re.split(r"·|—", trailing) if x.strip()]
        venue = None
        for part in parts:
            if not re.search(r"\d{4}-\d{2}-\d{2}|on now|through", part, re.I):
                venue = part
                break
        events.append({"title": text, "url": url, "date": m.group(2),
                       "end": end, "venue": venue, "time": None})
    return events


DEFAULT_IMAGES = ("/og-image.jpg",)   # the site's generic share image = no event image


class MetaCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.text = []

    def handle_starttag(self, tag, attrs):
        if tag == "meta":
            a = dict(attrs)
            k = a.get("property") or a.get("name")
            if k and "content" in a:
                self.meta.setdefault(k, a["content"])

    def handle_data(self, data):
        self.text.append(data)


def fetch_details(url):
    """Read one event page for its image (og:image) and start time."""
    req = urllib.request.Request(url, headers={"User-Agent": "WhatsNextTV-EventAds/1.0"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    p = MetaCollector()
    p.feed(html)
    img = p.meta.get("og:image") or p.meta.get("twitter:image")
    if img and any(img.endswith(d) for d in DEFAULT_IMAGES):
        img = None
    m = re.search(r"\b(\d{1,2}:\d{2}\s?[AP]M)\b", " ".join(p.text), re.I)
    return {"image": img, "time": re.sub(r"\s*([AP]M)$", r" \1", m.group(1).upper()) if m else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("city", help="city slug, e.g. fallbrook")
    ap.add_argument("--city-name", help="display name, defaults to the slug title-cased")
    ap.add_argument("--out", required=True)
    ap.add_argument("--details-days", type=int, default=6,
                    help="read event pages (image, start time) for events in the next N days; 0 = skip")
    a = ap.parse_args()

    req = urllib.request.Request(f"{BASE}/{a.city}/events",
                                 headers={"User-Agent": "WhatsNextTV-EventAds/1.0"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    events = parse(html, a.city)
    if not events:
        sys.exit("No events parsed: the page layout may have changed. Check parse().")
    if a.details_days:
        today = dt.date.today()
        last = today + dt.timedelta(days=a.details_days)
        for e in events:
            start = dt.date.fromisoformat(e["date"])
            end = dt.date.fromisoformat(e["end"]) if e.get("end") else None
            if today <= start <= last or (end and start <= today <= end):
                try:
                    e.update(fetch_details(e["url"]))
                except Exception as err:          # keep going; the ad falls back to text
                    print(f"  details failed for {e['url']}: {err}", file=sys.stderr)
    out = {"city": a.city,
           "city_name": a.city_name or a.city.replace("-", " ").title(),
           "fetched_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
           "events": events}
    with open(a.out, "w") as f:
        json.dump(out, f, indent=1)
    print(f"{len(events)} events -> {a.out}")


if __name__ == "__main__":
    main()
