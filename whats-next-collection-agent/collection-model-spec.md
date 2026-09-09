# The Whats Next Data Collection Model — build spec (for Muiz)

**From:** Dave (Founder account) · **To:** Muiz (Dev account)
**Companion to:** the `whats-next-data-system` handoff (stand up the database + load Fallbrook first; this engine runs against it).
**What this is:** the design for the recurring engine that finds organizers and events in a city, fills the Whats Next app with ready-to-show events, and hands our outreach queue to GoHighLevel. This document describes *what the engine does and why*; **you decide *how* to build it** in the Dev account as a **CoWork agent**.

> **Status:** designed, fully specified — **not yet built**. There is no prototype code; this spec *is* the artifact. Build the whole engine from it.

---

## How to use this document
Paste this into Claude in the **Dev account** as the spec for the collection agent. It defines the steps, the inputs, and the two outputs precisely. Where it says a choice is yours (the Dev side's), that's flagged. Where it names something *out of scope*, don't build it here — it's a separate, deliberate handoff.

**Two things that are true about this engine:**
1. **Fully specified, but runs at partial coverage until one thing is provisioned.** The organizer-finding step ("enumerate") is only as complete as the **Google Places API** being wired in. Until then it runs on a hand-approximated organizer list that undercounts. Build the whole engine; treat Places as the enumeration source to connect (see *Known ceilings*).
2. **Facebook is a permanent, flagged gap, not a bug to fix.** Public FB events sit behind a login with no reliable programmatic access. The engine works around it by leaning on outreach and by *labelling* Facebook coverage as incomplete every run — never by pretending coverage we don't have.

---

## The one-line purpose
For any one city, find **who could host events** and **what events are actually happening**, turn that into live app content, and turn the organizers into an outreach queue in our CRM — on a repeatable schedule, measuring how complete we are versus every other source.

---

## The two jobs, kept separate on purpose
They must stay separate steps or the whole thing stops scaling around the sixth city:
- **Enumerate = the census.** Wide, shallow, cheap. Find *every* organization / venue / church / business that could host public events. Record that they exist, rough contact info, and a guess at whether they host events (confirmed / likely / unknown / no). Don't dig. This makes coverage *measurable* — it's the denominator ("we have X of a possible Y") — and it catches organizers pure event-scraping never sees.
- **Capture = the interviews.** Narrow, deep, real effort per event. Go source by source and pull the actual events with dates, times, details.

Both write to the **same organizer roster** in the database. Enumerate marks its finds as census-added (`organizers.added_via = enumeration`); capture-found organizers are `event_capture`.

---

## The cycle (per city, repeatable)
**Input:** one city's config row (from the `cities` table) — its ZIP(s), boundary rule, source list, chamber URL, etc. This is the only per-city input; the engine is city-agnostic otherwise.

1. **Enumerate** — sweep the city, refresh the organizer roster. (Source: Google Places API once wired; hand-approximation until then.)
2. **Capture** — go source by source (Chamber, aggregators, org sites, library, etc.) and pull candidate events.
3. **Resolve / dedupe** — collapse the same event reported by multiple sources into one record, and record *which* sources had it. (Matching rules below.)
4. **Measure the gap** — the core "more than anyone else" metric: what we have that a given source doesn't, and what they have that we don't.
5. **Queue organizers for outreach** — push each organizer to the CRM as a tagged contact (below). The engine *produces the queue*; it does not do the outreach.
6. **Report** — emit a plain run receipt: events added, net-new organizers, events only-we-have, sources that beat us, data conflicts, anything that failed.

---

## Matching / dedupe rules (already locked in the schema — build to these, don't re-derive)
- **Hard uniqueness lives at the occurrence level:** a series cannot have two rows for the same date (`unique(event_id, occurrence_date)`). This is the backstop that stops duplicates on every re-run.
- **Series matching is the agent's fuzzy job:** deciding "is this scraped event the same series we already have?" compares normalized event name + city + organizer, with **venue as a soft score only — never part of a hard key.** (Venue data across sources is too inconsistent to key on; keying on it causes false splits.)
- **Dedupe on date, not time.** Sources routinely disagree on start times; keying on the date avoids splitting one real event into two.
- **Recurring events** are stored once as a series with a recurrence rule (`rrule` + prose), and their dated instances are generated out to a near-term horizon (a **90-day rolling window** is the default; the engine extends it each run). The seed already contains series with `rrule` and **zero** occurrences — those are exactly what the engine materializes first.

---

## OUTPUT 1 — Completed events → the app
Any event the engine finds **and can fill out enough to stand as a real listing** flows straight into the Whats Next event tables and becomes live content for that city — so the app shows a populated calendar with no organizer action required.
- These land in the **same tables** an organizer's own submission would (`events` / `event_occurrences`).
- Because every event records its **source** (`sources` / `event_sources`), agent-found and organizer-submitted events coexist cleanly and we can always tell which is which.
- Events that can't be completed enough to publish stay in the database but out of the live view (they still count for the coverage math and may still produce an organizer to queue).

---

## OUTPUT 2 — Organizers → GoHighLevel (our CRM)
Every organizer the engine surfaces becomes a **GHL contact carrying one tag**. The tag fires an automation inside GHL. **The engine's job ends at delivering the correctly-tagged contact** — what the automation then does is the outreach process, *out of scope for this doc* (separate model).

**Two tags, decided by contactability:**

| Situation | Tag | What it triggers (in GHL, not here) |
|---|---|---|
| We have a real channel — email, contact form, or phone | `sourced organizer` | the outreach automation |
| Name/company **plus at least one lead** (website, social handle, or physical address) but **no channel yet** | `research contact` | an internal automation for the team to find the missing contact info |

**Floor to create a contact at all:** name/company **plus at least one lead**. A bare name with nothing to chase does **not** create a GHL contact — that keeps the research queue full of *findable* organizers, not dead ends. (Bare entries still live in the organizer roster for the coverage count; they just don't push to GHL.)

**Never guess a contact channel.** No pattern-guessed emails. If no channel is published, it's a `research contact`, not a `sourced organizer` with a made-up email.

**Contact payload → GHL field mapping.** Map our organizer roster to a GHL contact; fields GHL has no native home for become **custom fields** on the GHL side — at minimum:
- organizer name / company → contact name + company
- email / phone → native contact channels
- **hosts-events heat** (confirmed / likely / unknown) → custom field
- **the proof event** (a specific event of theirs we already found & listed) → custom field, so outreach can open with "we already have your event on [date] listed"
- **our organizer ID** (`org_code`) → custom field (stable link back to our database)
- **source** (where we found them) → custom field
- the tag (`sourced organizer` / `research contact`)

**Delivery method is your call.** CSV import works, but a direct **API push** likely skips the manual upload and is cleaner for a recurring agent. Pick what fits the CoWork build. (You already have GHL Agency access.)

---

## Report (the receipt)
Each run emits a short, plain summary — not the point of the engine, just the record that a pass happened: events added/updated · net-new organizers · events only *we* have (vs. each source) · sources that had events we lacked · unresolved data conflicts · anything that failed (a source down, Facebook unreachable, etc.).

---

## Known ceilings (build with these visible, don't design around them dishonestly)
1. **Google Places API — the fix for enumerate.** A provisioning + wiring job on your side: obtain a Places API key (a **paid** Google service — per-lookup cost and a billing decision for Dave, who is provisioning it), then point the enumerate step at it, querying by the city's ZIP(s) and place categories. Upgrades enumerate from today's hand-done, undercounting sweep to a systematic denominator. **Until it's wired, the engine runs — it just under-counts organizers, and coverage numbers must say so.**
2. **Facebook — a standing gap, not a build.** No reliable programmatic access to public FB events. Stock everything reachable elsewhere, **flag Facebook as known-incomplete every run**, and rely on **outreach** (organizers self-reporting their FB events) to fill it. Scope whether any access path currently exists, but plan as if it doesn't.

---

## Explicitly out of scope for this doc (clean handoffs, not omissions)
- **The outreach process** — what the `sourced organizer` automation actually does (messaging, cadence, listing-claim flow). Its own model, in the separate *Whats Next marketing* project.
- **The research action** — what the `research contact` automation triggers for the team. Defined with outreach.
- **Designing the GHL pipeline/stages themselves** — named here only as the destination; built on the GHL side.

---

## Current-state notes (updated 2026-09-08)
- **"Specials" is now defined** (it was the one open category when this spec was first drafted): a business's standing promotional offer — happy hour, Taco Tuesday, locals' night — treated as a listable, usually-recurring event. It's category #15 in the seeded canonical list.
- **The Fallbrook seed now exists and is being handed off** (the `whats-next-data-system` package). So the database this engine runs against is defined; standing it up is the companion handoff.
- **Still not proven cold.** Fallbrook worked partly because the terrain was already known. The "duplicatable process" claim is only earned when the engine actually runs somewhere new — a document can't close that.
