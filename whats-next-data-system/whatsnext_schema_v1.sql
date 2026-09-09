-- ============================================================================
-- WHATS NEXT — San Diego County event platform
-- Supabase / Postgres schema  v1  (2026-08-31)
--
-- Reflects three locked decisions:
--   1. Dedupe: venue EXCLUDED from any hard key. Hard uniqueness lives at the
--      occurrence level (event_id + occurrence_date). Series matching is the
--      agent's fuzzy job (normalized name + city + organizer; venue = soft score).
--   2. Occurrences adopted now: events = the SERIES definition; event_occurrences
--      = materialized dated instances. One-time event = series with one occurrence.
--   3. Categories: one canonical main category (categories lookup, editable as
--      data) + tags[] feeding a keyword search_vector.
--
-- Two workbook "columns" are DERIVED, not stored:
--   - Organizers."Event Count"        -> a query/view (count of events per org)
--   - Events."Organizer Name (lookup)"-> a join to organizers.org_name
-- ============================================================================

create extension if not exists pg_trgm;   -- trigram similarity for series matching

-- ---------------------------------------------------------------------------
-- ENUMS
-- ---------------------------------------------------------------------------
create type org_type        as enum ('nonprofit','business','civic','institution','venue','church','school');
create type hosts_events     as enum ('Confirmed','Likely','Unknown','No');
create type outreach_status  as enum ('Not Contacted','Invited','Responded','Claimed','Declined','Bounced'); -- PROPOSED; extend as lifecycle grows
create type added_via        as enum ('enumeration','event_capture');  -- "two jobs, one roster" provenance
create type event_status     as enum ('Confirmed','Tentative','Cancelled');       -- series-level
create type occurrence_status as enum ('Scheduled','Cancelled','Postponed','Completed'); -- lets you cancel ONE date of a series

-- ---------------------------------------------------------------------------
-- CITIES  (was the "City Config" tab; the agent's per-run coverage config)
-- NOTE: this is the COVERAGE AREA, not the literal community. The Fallbrook
-- config covers events whose city = 'Rainbow' or 'Bonsall'. So rows keep their
-- literal community in .city/.county AND point at a coverage config below.
-- ---------------------------------------------------------------------------
create table cities (
  id               bigint generated always as identity primary key,
  city_name        text not null,          -- coverage config name, e.g. 'Fallbrook'
  county           text not null,
  primary_zips     text[],                 -- enumeration filter for Places API
  boundary_rule    text,
  event_definition text,
  incorporated     boolean,
  chamber_url      text,
  local_paper      text,
  library_system   text,
  facebook_note    text,
  last_event_sweep date,
  config_owner     text,
  unique (city_name, county)
);

-- ---------------------------------------------------------------------------
-- CATEGORIES  (canonical main list — editable as data, seeded at bottom)
-- ---------------------------------------------------------------------------
create table categories (
  id         bigint generated always as identity primary key,
  name       text unique not null,
  sort_order int default 0,
  active     boolean default true
);

-- ---------------------------------------------------------------------------
-- ORGANIZERS  (ORG-xxx)  — the asset roster
-- ---------------------------------------------------------------------------
create table organizers (
  id                bigint generated always as identity primary key,
  org_code          text unique not null,            -- 'ORG-001' — legacy/human key, stable across 18-city namespacing
  org_name          text not null,
  type              org_type,
  city              text not null,                   -- literal community (Fallbrook / Rainbow / Bonsall)
  county            text not null,
  coverage_config_id bigint references cities(id),   -- which coverage area this org rolls up to
  website           text,
  primary_email     text,
  phone             text,
  contact_name      text,
  contact_title     text,
  physical_address  text,
  facebook          text,
  instagram         text,
  hosts_events      hosts_events default 'Unknown',  -- outreach heat map
  source_of_contact text,
  date_collected    date,
  verified          boolean,                          -- sparse: only contact-verified orgs
  priority_tier     smallint check (priority_tier in (1,2,3)),
  outreach_status   outreach_status default 'Not Contacted',
  date_contacted    date,
  follow_up_date    date,
  claim_link        text,
  added_via         added_via,                        -- enumeration vs event_capture
  notes             text
);
create index on organizers (city);
create index on organizers (hosts_events);
create index on organizers (priority_tier);

-- ---------------------------------------------------------------------------
-- EVENTS  (EVT-xxx)  — the SERIES DEFINITION (one row per event/series)
-- ---------------------------------------------------------------------------
create table events (
  id                bigint generated always as identity primary key,
  event_code        text unique,                      -- 'EVT-001'
  organizer_id      bigint references organizers(id),
  event_name        text not null,
  city              text not null,                    -- literal community
  county            text not null,
  coverage_config_id bigint references cities(id),
  category_id       bigint references categories(id),
  tags              text[] default '{}',              -- keyword surface (winery, live, teen, ...)
  description       text,
  venue_name        text,                             -- default venue for the series (NOT in any key)
  address           text,
  event_url         text,
  image_url         text,
  image_prompt      text,
  cost              text,

  -- recurrence: prose (migrated) + structured (for materializing occurrences)
  recurrence_text   text,                             -- original human description
  rrule             text,                             -- RFC-5545, e.g. 'FREQ=WEEKLY;BYDAY=SA'; NULL = one-time
  series_start_date date,
  series_end_date   date,
  default_start_time text,                            -- text: sources disagree / ranges / TBD
  default_end_time  text,

  status            event_status default 'Confirmed', -- series-level
  last_verified     date,
  notes             text,

  -- SERIES MATCH KEY: normalized name + city. NOT UNIQUE (by design — two distinct
  -- one-time events may share a name). Indexed to power the agent's fuzzy lookup.
  match_key text generated always as (
    lower(regexp_replace(coalesce(event_name,''), '[^a-zA-Z0-9]', '', 'g'))
    || '|' || lower(regexp_replace(coalesce(city,''), '[^a-zA-Z0-9]', '', 'g'))
  ) stored,

  -- keyword search over name + description + tags
  search_vector tsvector generated always as (
    to_tsvector('english',
      coalesce(event_name,'') || ' ' ||
      coalesce(description,'') || ' ' ||
      array_to_string(tags, ' '))
  ) stored
);
create index on events (match_key);
create index on events using gin (tags);
create index on events using gin (search_vector);
create index on events using gin (event_name gin_trgm_ops);  -- fuzzy series matching
create index on events (city);
create index on events (organizer_id);
create index on events (category_id);

-- ---------------------------------------------------------------------------
-- EVENT_OCCURRENCES  — dated instances. THE HARD DEDUPE BACKSTOP.
-- No denormalized city: filter by joining events (cheap at this scale, no drift).
-- "What's on <date> in <city>":
--   select ... from event_occurrences o
--   join events e on e.id = o.event_id
--   where o.occurrence_date = $1 and e.city = $2;  -- uses occurrences(occurrence_date) + events(city)
-- (A venues table later makes city derive from venue — the permanent single source of truth.)
-- ---------------------------------------------------------------------------
create table event_occurrences (
  id              bigint generated always as identity primary key,
  event_id        bigint not null references events(id) on delete cascade,
  occurrence_date date not null,
  start_time      text,                               -- override; falls back to events.default_start_time
  end_time        text,
  venue_name      text,                               -- override for a one-off relocation
  status          occurrence_status default 'Scheduled',
  last_verified   date,
  notes           text,
  unique (event_id, occurrence_date)                  -- <-- deterministic idempotency guard, ON CONFLICT target
);
create index on event_occurrences (occurrence_date);

-- ---------------------------------------------------------------------------
-- SOURCES + EVENT_SOURCES  — the "us vs. them" coverage engine
-- ---------------------------------------------------------------------------
create table sources (
  id          bigint generated always as identity primary key,
  name        text unique not null,                   -- 'Chamber calendar', 'AllEvents.in', 'Our scrape'
  kind        text,                                   -- aggregator | org_site | paper | places_api | manual
  city_scoped boolean default true
);

create table event_sources (                          -- many-to-many: which sources surfaced each event
  event_id    bigint references events(id) on delete cascade,
  source_id   bigint references sources(id),
  external_id text,                                    -- the event's id at that source
  external_url text,
  first_seen  timestamptz default now(),
  last_seen   timestamptz default now(),
  primary key (event_id, source_id)
);
-- Coverage queries:
--   Events WE have that source X lacks  -> events with no event_sources row for X.
--   Events source X has that we lack    -> logged at ingest: X candidates that matched no event.

-- ---------------------------------------------------------------------------
-- DERIVED VIEW  (replaces the workbook's COUNTIF "Event Count")
-- ---------------------------------------------------------------------------
create view organizer_event_counts as
  select o.id as organizer_id, o.org_code, o.org_name,
         count(e.id) as event_count
  from organizers o
  left join events e on e.organizer_id = o.id
  group by o.id, o.org_code, o.org_name;

-- ---------------------------------------------------------------------------
-- SEED: canonical main categories  (CONFIRMED 2026-08-31 — still editable as data)
-- ---------------------------------------------------------------------------
insert into categories (name, sort_order) values
  ('Arts',1),('Auto',2),('Business',3),('Civic',4),('Community',5),('Cultural',6),
  ('Education',7),('Family',8),('Food & Drink',9),('Fundraiser',10),('Health & Wellness',11),
  ('Music',12),('Outdoors',13),('Religious',14),('Specials',15),('Sports',16),('Volunteer',17);
