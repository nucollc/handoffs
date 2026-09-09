# Whats Next — data system + Fallbrook seed — handoff for Muiz

> **Status:** Ready for Dev (see queue caveat below) · **Owner:** Dave · **Date:** 2026-09-08
> **Staging is a passthrough.** These files live in `nucollc/handoffs` only until you migrate them into the real product repo. Once you do, that copy is canonical and this folder is stale — don't build long-term against it.
> **Public repo — no secrets.** Nothing here contains keys, `.env`, or client data. Keep it that way: Supabase keys stay in your dev environment / host env vars, never in a commit.

## Where the files are
Repo folder: `https://github.com/nucollc/handoffs/tree/main/whats-next-data-system`

```
whats-next-data-system/
├── whatsnext_schema_v1.sql            run FIRST — DDL: 7 tables + 1 view + 17 seeded categories
├── whatsnext_fallbrook_load.sql       run SECOND — one-time Fallbrook seed (idempotent)
├── whatsnext_fallbrook_load_report.md expected row counts + per-event disposition (acceptance reference)
└── README.md                          this brief
```

## How this handoff works
- **Notion = context, GitHub = build.** The full reasoning, decision log, and acceptance context live in Notion (linked at the bottom). This repo holds the runnable files. Neither is the other's source of truth.
- **Notify-first.** No repo had to exist before this. Create the product repo (or Supabase project) as the first act of the build and migrate these files in.
- **Passthrough, not source of truth.** Once you migrate this folder, the staging copy is stale — later edits go to the product repo or start a fresh handoff.
- **Public repo → no secrets, ever.** Keys live only as host/dev env vars.

## The problem (one line)
Whats Next needs a deduped, occurrence-aware events database — stood up and seeded with the Fallbrook pilot city — that Lovable can read directly.

## The fix
Two runnable SQL files against a **dedicated Whats Next Supabase project**. `whatsnext_schema_v1.sql` creates the events-as-series data model (events = series definition, `event_occurrences` = dated instances) with the hard dedupe backstop at the occurrence level. `whatsnext_fallbrook_load.sql` then seeds the Fallbrook pilot — 106 organizers, 55 series, 50 materialized occurrences, 11 sources, 55 event-source links — with the founder-side data judgment already applied (category normalization, no speculative future dates, vague recurrences flagged as prose rather than guessed). This is the **data layer** — the foundation the collection engine writes into. The collection agent and outreach are separate, later handoffs (see the next section for where this fits).

## What this feeds — the collection (scrape) build model
This database is the contract the **collection engine** (the "data scrape process") writes into. That engine is **designed but not built** — it is a **separate, later handoff, released to you after this seed is loaded**, because it writes into these tables and can't be built against a database that isn't live yet. Its authoritative spec is the **Collection Model** page in Notion — build it from there, not from this README. It's summarized here only so you can see how this schema is its contract and what you're building toward.

**The cycle (per city, repeatable):** Enumerate → Capture → Resolve/dedupe → Measure the gap (us vs. them) → Queue organizers → Report.
- **Enumerate** — wide, shallow census of every org / venue / church / business that *could* host events (the denominator that makes coverage measurable).
- **Capture** — narrow, deep pull of the actual events, source by source (Chamber, aggregators, org sites, library).
- **Resolve/dedupe** — collapse the same event from different sources into one, recording which sources had it.
- **Measure the gap** — the "more than anyone else" metric: what we have that a source lacks, and what they have that we're missing.
- **Queue organizers** — new organizers queued for outreach. The queue is the *output*, not an action; acting on it is a separate outreach process.
- **Report** — a run receipt: events added, net-new organizers, only-we-have events, sources that beat us, conflicts, failures.

**Two outputs:** (1) completed events → the app, published as live city content, source-tagged, no organizer action needed; (2) organizers → GHL as tagged contacts — `sourced organizer` (real channel; fires outreach) or `research contact` (name + ≥1 lead but no channel; fires internal research). Floor to create any GHL contact = name + ≥1 lead; never guess a channel.

**How this schema is the contract for it (build to these seams):**
- Completed events land in the **same `events` / `event_occurrences`** tables an app submission would. The agent materializes occurrences on a rolling ~90-day horizon — the `rrule` + prose rows in this seed that carry **zero** occurrences are exactly what it fills first.
- **`sources` / `event_sources`** is the us-vs-them coverage engine: every captured event records which sources surfaced it.
- **`Specials`** is a real category — a business's standing offer (happy hour, Taco Tuesday) listed as a usually-recurring event.
- Organizer provenance (`added_via` = enumeration vs event_capture) plus the outreach fields on `organizers` are the GHL seam.

**Sequence:** stand up this schema → load this seed → *then* the collection-agent handoff (its own doc) is released to you. **Known ceilings it inherits:** Google Places API upgrades Enumerate from a hand-done undercount to a systematic denominator (not yet wired); Facebook events are login-walled and stay a known-incomplete gap closed by outreach, not scraping.

Collection Model spec: `https://app.notion.com/p/3cf0d046551381f99190efc59185bc99`

## Technical notes & gotchas
- **Run order is strict:** schema first, then load. The load resolves FKs by natural key (`org_code` / `event_code` / category name), so the schema and its 17 seeded categories must exist before the load runs.
- **The load is idempotent** — `ON CONFLICT DO NOTHING` everywhere; safe to re-run without creating duplicates.
- **Dedupe is occurrence-level:** `unique(event_id, occurrence_date)` is the hard key. Venue is deliberately **not** in any hard key (soft score only). Dedupe is on **date, not datetime**. Series matching is the agent's fuzzy job later (normalized name + city + organizer).
- **Recurrence handling (already decided, don't "fix"):** explicit dates are materialized as occurrences; clean recurring rules are stored as `rrule` + prose with **zero** occurrences (the live agent materializes them on first run); 16 vague recurrences are flagged and stored as prose and were **deliberately not guessed**. The per-event disposition is in the report file.
- **Two values are derived, not stored:** organizer event count (the `organizer_event_counts` view) and the organizer-name lookup on events (a join). Don't add columns for these.

## Guardrails (must not miss)
- **Create a new, dedicated Supabase project for Whats Next — do not reuse an existing one.** As of 2026-09-08 the `nucollc's Org` account has exactly two projects, and **neither is Whats Next**: `pulse-prod` (eu-central-1 — this is the PULSE app DB; the guardrail means *this one*, don't touch it) and `CIPHER's Brain` (us-west-2). Stand up a fresh project (a US-West region keeps it close to the California audience and Lovable) and run the schema + seed there.
- **No secrets in the public repo** — these files carry none; keep keys in env vars only.
- **Don't relitigate the locked schema** — occurrence-level dedupe, venue out of the hard key, one canonical category + `tags[]`, fuzzy series matching. Build to it as-is.
- **Preserve the data judgment** — do not materialize the flagged/vague recurrences into invented dates. Flagged-as-prose is the correct final state until the agent or a verification pass resolves them.

## Done when (acceptance checks)
- [ ] Both files run clean, in order, against a dedicated Whats Next Supabase project (not the PULSE app DB).
- [ ] Post-load row counts match the report exactly: **106 organizers · 55 events · 50 occurrences · 11 sources · 55 event_sources**.
- [ ] `select count(*) from events where organizer_id is null` returns **0** (no orphan events).
- [ ] 17 categories present, and the `organizer_event_counts` view returns rows.

## Honest ceiling (state, don't hide)
This is a validated blueprint with a strong Fallbrook reference — **not** a proven cold-start process for an arbitrary city yet. Two standing gaps carried forward on purpose: Google Places API is not yet wired (enumeration undercounts retail / fitness / professional services until it is), and Facebook events are login-walled and unreachable by automation (closed via outreach, not scraping). Neither is a bug to fix in this handoff.

## Full context
Notion handoff page: https://app.notion.com/p/3d60d0465513818aa244dc056677c6b0
