# What's Next TV Event Ads — handoff for Muiz

> **Status:** Ready for Dev · **Owner:** Dave · **Date:** 2026-11-14
> **Staging is a passthrough.** These files live in `nucollc/handoffs` only until you migrate them into the real product repo. Once you do, that copy is canonical and this folder is stale — don't build long-term against it.
> **Public repo — no secrets.** Nothing here contains keys, `.env`, or client data. Keep it that way: any keys (hosting, analytics, storage) go in host env vars, never in a commit.

## Where the files are
Repo folder: `https://github.com/nucollc/handoffs/tree/main/whats-next-tv-event-ads`

```
whats-next-tv-event-ads/
├── README.md                                   this brief
├── requirements.txt                            Python dependency (segno, for QR codes)
├── scripts/fetch_events.py                     reads a city's listings + each event's image and start time
├── scripts/build_ads.py                        picks the ads, makes tracked QR codes, writes the page
├── template/index.html                         the ad page: 3 layouts chosen by URL parameter
├── sample/fallbrook_events_2026-11-14.json     Fallbrook listings snapshot (offline testing)
├── sample/fallbrook_details_2026-11-14.json    image + start time for the 12 selected events
├── preview/WNTV_EventAds_Fallbrook_Preview.html  the approved full-card preview (open in Chrome)
├── preview/*.png                               screenshots of each layout
└── preview/harness.py                          renders those screenshots (Playwright)
```

## How this handoff works
- **Notion = context, GitHub = build.** The full reasoning, decision log, and acceptance context live in Notion (linked at the bottom). This repo holds the runnable files. Neither is the other's source of truth.
- **Notify-first.** No repo had to exist before this. Create the product repo as the first act of the build and migrate these files in.

## The problem (one line)
Every What's Next city needs its upcoming events promoted on What's Next TV — on the 24/7 YouTube stream and on in-store screens at local businesses — with a QR code back to each listing, and nobody should have to update that by hand.

## The fix
One "event ad" web page per city, rebuilt automatically every morning from that city's whatsnext.buzz listings. It shows events from today through the next 5 days (spread across the days, up to 12, featured/paid events first), each with date, start time, venue, the event image and a QR code to the listing. The same page is used three ways via URL parameters: a lower-third banner layered over the 24/7 stream (Upstream Stream Designer "website" layer), a banner strip under the video on in-store screens (Yodeck web-page zone), and a full-screen card with the event image. The prototype runs as a daily Python job producing a static page; build it properly for 400+ cities.

## Technical notes & gotchas
- **Layouts:** `index.html?layout=lowerthird&src=stream` (transparent 1920x1080, for the stream), `?layout=strip&src=store` (1920x270 zone), `?layout=card&src=store` (full screen). Optional `sec=12` per ad. The page re-reads `ads.json` every 10 minutes, so screens and the stream pick up the daily rebuild without a reload.
- **Tracking:** each ad gets one QR code per placement: `utm_source=wntv&utm_medium=stream|store|web&utm_campaign=ads`. Tags are kept short on purpose — longer URLs make denser QR codes that scan worse from across a room. All QR codes in the previews were decoded and checked.
- **Data source is the weak point.** whatsnext.buzz has no RSS, iCal or API. The pilot reads the city page HTML (event links follow `/{city}/events/{event-slug}-{YYYY-MM-DD}`) and then each event page for `og:image` and the first "H:MM AM/PM". A site layout change breaks it. Production: read straight from the site's database — ideally render the page at `whatsnext.buzz/{city}/screen` so no daily job is needed and every city works on day one, or at least add `/api/events?city=&from=&to=` returning title, url, date, end, venue, time, image.
- **Images:** the site's generic `og-image.jpg` means "no event image" (3 of 12 Fallbrook events on Nov 14); those get the text-only card. The card shows the whole image (never cropped) over a blurred fill, so posters and wide banners both work, and falls back to text if the image fails to load. Images currently load from outside hosts (Squarespace, allevents.in at 500x250 AVIF, imgix-rendered PDFs/PNGs): copy them to our own storage at a decent size — the allevents.in ones look soft full-screen and outside hosts can change.
- **Selection rules** (`build_ads.py`): window today + 5 days; one event per day in turn so a busy today doesn't crowd out later days; repeats of the same recurring event dropped by normalized title; sorted by date then start time; `--featured` list always first (future paid boosts).
- **Labels** ("TODAY", "TOMORROW", "MON NOV 16") are baked in at build time, so the rebuild must run every day around 5:00 am Pacific (city-local time once we go beyond California).
- **Not possible:** ads can't go inside the regular videos in the YouTube playlist — only the 24/7 live stream and screens.
- **Prototype rough edges, don't carry over:** HTML parsing of the city page; outside-hosted images; Google Fonts loaded from the web on screens (self-host Poppins).

## Guardrails (must not miss)
- The page must be **public HTTPS** and load fast with no login — Upstream and the signage app load it unattended, 24/7.
- **Never show a past event.** If the daily build fails, the page should keep yesterday's still-upcoming ads or fall back to a "What's happening in {City} · whatsnext.buzz" card — never stale "TODAY" labels.
- **No secrets in this public repo** — any keys (storage, analytics, hosting) live in host env vars only.
- **Be polite to our own site:** if it still reads HTML, cache and rate-limit the event-page fetches (only events in the window, once a day).
- Keep the brand: Next Orange `#FA5723`, Jet Black `#060605`, Poppins.

## Done when (acceptance checks)
- [ ] The Fallbrook page is live at a public HTTPS URL and all three layouts render at 1920x1080 (and the strip at 1920x270) with no broken layout.
- [ ] It shows only events from today through the next 5 days, spread across the days, max 12, featured first — and updates on its own every morning with no manual step.
- [ ] Every QR code scans to the right whatsnext.buzz listing with the right `utm_medium` (stream / store / web).
- [ ] Event images show on the full card; events without their own image, or with a broken image, get the text card.
- [ ] Start times show and match the listings.
- [ ] The page works as a "website" layer over the Upstream 24/7 stream and as a web-page zone in Yodeck.
- [ ] Adding a new city needs only its slug (no code change), and a second city has been tested.
- [ ] No keys, tokens or `.env` anywhere in the repo.

## Full context
Notion handoff page: https://app.notion.com/p/4180d0465513815fa70fc0a96e0612ae
Decision log: Project Registers → "What's Next TV - YouTube city structure" (D3, D17, D18, D19, D20).
