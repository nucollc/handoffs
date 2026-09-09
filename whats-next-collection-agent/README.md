# Whats Next — collection (scrape) agent — handoff for Muiz

> **Status:** Ready for Dev · **Owner:** Dave · **Date:** 2026-09-08
> **Staging is a passthrough.** These files live in `nucollc/handoffs` only until you migrate them into the real product repo. Once you do, that copy is canonical and this folder is stale.
> **Public repo — no secrets.** No keys, `.env`, or client data here. GHL and Places keys live only in your dev environment / host env vars, never in a commit.

## Where the files are
Repo folder: `https://github.com/nucollc/handoffs/tree/main/whats-next-collection-agent`

```
whats-next-collection-agent/
├── collection-model-spec.md   the engine you build — six moves, two outputs, GHL seam, ceilings
└── README.md                  this brief
```

## How this handoff works
- **Notion = context, GitHub = build.** The reasoning and the canonical spec live in Notion (linked at the bottom); this repo holds the build spec. Neither is the other's source of truth.
- **Notify-first.** Stand up the real agent (CoWork) in your own account as the first act of the build.
- **Passthrough, not source of truth.** Once you migrate this, the staging copy is stale.
- **Public repo → no secrets, ever.**

## The problem (one line)
Whats Next needs a repeatable, per-city engine that finds who could host events and what events are actually happening, fills the app with live listings, and hands an outreach queue to GHL — measuring how complete we are versus every other source.

## The fix
Build a **CoWork agent** from `collection-model-spec.md`. It runs a six-move cycle per city — **Enumerate → Capture → Resolve/dedupe → Measure the gap → Queue organizers → Report** — and produces two real outputs: completed events written straight into the app's tables as live content, and organizers pushed to GHL as tagged contacts. It's designed but not yet coded; the spec *is* the artifact, and it runs against the schema stood up by the `whats-next-data-system` handoff.

## Technical notes & gotchas
- **This is a spec build, by design.** There is no prototype code — the engine was fully specified but never built. Build the whole thing from the spec; don't wait for a reference implementation that doesn't exist.
- **Build against the finalized schema contract now.** The data model is locked and shipped in the `whats-next-data-system` handoff (`events` / `event_occurrences`, `sources` / `event_sources`, `organizers`, `cities`). You can build the six moves, the matching logic, and the GHL mapping against that contract immediately.
- **The dedupe/matching rules are already locked — build to them** (occurrence-level uniqueness, venue as soft score only, dedupe on date not time, recurring series materialized on a ~90-day rolling horizon). The seed ships `rrule` series with zero occurrences — those are what the agent materializes first.
- **Two decisions are genuinely yours (flagged, not blank):** the GHL delivery method (direct API push vs CSV import — API is cleaner for a recurring agent), and the Google Places API provisioning + wiring.
- **CoWork is the intended runtime.**

## Guardrails (must not miss)
- **Never guess a contact channel** — no pattern-guessed emails. No published channel → `research contact`, not a `sourced organizer` with a made-up email.
- **GHL contact floor = name/company + ≥1 lead.** Bare names stay in the roster for the coverage count but do **not** push to GHL.
- **Places API is paid** — per-lookup cost and a billing decision that's Dave's. Until it's wired, the engine runs but under-counts, and coverage numbers must say so.
- **Facebook is a flagged gap, not a build** — flag it known-incomplete every run; fill it via outreach, not scraping.
- **Don't fold in the separate handoffs** — the outreach process, the `research contact` research action, and GHL pipeline/stage design are named boundaries, not this build.
- **No secrets in the public repo.**

## Done when (acceptance checks)
Run for one city against the live schema, the agent:
- [ ] **Enumerates** the organizer roster (via Places once wired; hand-approx until then, with coverage marked under-counted).
- [ ] **Captures** events source by source and writes completed ones into `events` / `event_occurrences` as live, source-tagged content.
- [ ] **Resolves/dedupes** to the locked rules — no duplicate `(event_id, occurrence_date)`; venue never used as a hard key; date-not-time; recurring series materialized on the rolling horizon.
- [ ] **Measures the gap** — reports what we have that each source lacks, and what they have that we lack.
- [ ] **Queues organizers to GHL** with the correct tag (`sourced organizer` / `research contact`) and the name+≥1-lead floor enforced; no guessed channels.
- [ ] **Emits the run report** (events added, net-new organizers, only-we-have, sources that beat us, conflicts, failures), with **Facebook flagged known-incomplete**.

*Honest sequencing:* the build can start now against the schema contract, but full end-to-end acceptance requires the `whats-next-data-system` schema + seed to be **live**, and complete enumerate requires the **Places API** key. Those are external to the engine, named here so they're not discovered mid-build.

## Full context
- Canonical spec: **Collection Model** page — `https://app.notion.com/p/3cf0d046551381f99190efc59185bc99`
- Notion handoff page: https://app.notion.com/p/3d60d0465513816096f3e7a5d78d754e
- Runs against: **Whats Next — data system + Fallbrook seed** handoff — `https://app.notion.com/p/3d60d0465513818aa244dc056677c6b0`
