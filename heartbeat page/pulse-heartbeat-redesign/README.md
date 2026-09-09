# Pulse — Heartbeat redesign (connective hub)

**Product:** Pulse (getpulse.build)
**Handoff from:** Dave — strategy/design account
**For:** Muiz — build account
**Date:** 8 Sep 2026
**Prototype:** `heartbeat-mockup.html` — open in a browser. Static, no data wired. Design-system tokens are declared at the top of the file.
**Handoff context (Notion):** https://app.notion.com/p/3d60d046551381b1a118c9c7bc0fb8f9 — this repo folder is the build layer; that page is the context layer and holds the standing process, role/visibility decision, and open questions.

---

## What this is
A redesign of the existing **Heartbeat** page in the Pulse web app. Today Heartbeat renders as an operational-risk surface (flag counts, overdue projects, deadline risk) — which duplicates what **Vitals** already does. This redesign repositions Heartbeat as the company's **connective hub**: the place the team feels the company, not where it gets flagged.

## Core insight
Heartbeat is felt collectively and warmly; Vitals is read clinically. Heartbeat should carry culture, momentum, and belonging — announcements, events, wins, recognition, presence — while Vitals keeps the risk/oversight readout. Two surfaces, opposite emotional charge.

## Nav context (unchanged)
My Work → Heartbeat → Vitals → All Projects → Tasks → Meeting Inbox. People section: Clients, Team & roles. Heartbeat keeps its position in the nav; only its contents change.

## Roles & visibility (first-class decision — see Open Questions)
Heartbeat renders per role: Founder, Admin, Agent, PM, Producer. The prototype shows the **Founder** view. Announcements, kudos, presence, and events are naturally all-company. Financial/scoreboard elements and "What we're building" may need role-gating. The visibility boundary must be explicit before build — which role sees which section, and which financials.

---

## Sections in the prototype (build targets)
1. **Pinned announcement** — one founder-pinned post in the dark feature card: title, body, reactions, reactor avatars, timestamp.
2. **Around this week (presence)** — team list with status: In / Heads-down (with focus) / Out (PTO with dates).
3. **Celebratory stat strip** — company wins, not risk: shipped this month, on-time delivery (with trend), kudos count, new clients. Same visual weight as the old risk cards, opposite charge.
4. **Announcements feed** — recent posts with author, role, tag (Client win / Product / Branding), body, reactions.
5. **Shoutouts & kudos** — peer-to-peer recognition cards (line + giver).
6. **Upcoming** — event schedule with date chips: all-hands, demos, socials, work anniversaries, birthdays.
7. **What we're building** — current product pushes with a stage badge (Design / Building / Live) and a progress bar.

---

## In scope (v1) — one capability per item
1. Heartbeat page shell + section layout matching the prototype's design system (tokens declared at top of the HTML).
2. Pinned announcement: founder can pin one announcement; renders in the feature card with reactions.
3. Announcements feed: create/read posts with author, role, tag, body; emoji reactions.
4. Kudos: post a kudo (recipient + line); renders on the wall; counts into the weekly kudos stat.
5. Presence: per-person status field (In / Heads-down + focus / Out + dates); renders in "Around this week."
6. Upcoming events: event list with date, title, type chip; includes team milestones (anniversaries/birthdays) where a start-date/DOB exists.
7. Celebratory stats: shipped-this-month, on-time %, kudos-this-week, new-clients-this-month — each sourced from real data (see Provenance).
8. "What we're building": list of current builds with stage + progress; source TBD (manual vs project-derived — see Open Questions).
9. Role-based render: Founder view first; scaffold the role switch so other roles can be layered.

## Explicitly out of scope (v1)
- Comment threads on posts (reactions only in v1).
- Rich media / file attachments in announcements.
- Full moderation UI (author + admin edit is fine; a moderation surface is out).
- Notifications / email digests off Heartbeat.
- Assets/perks links section (parked — was in the original Heartbeat concept; hold for v2).
- Any write-back to Vitals or project data.

## Acceptance criteria (checkable by clicking)
- Founder can pin an announcement and it appears in the feature card; unpinning removes it.
- A new announcement posts to the feed with correct author/role/tag and is reactable.
- A kudo posts to the wall and the "kudos this week" number increments.
- Changing a teammate's status updates "Around this week."
- Each celebratory stat shows a real number, or an honest empty state — never a placeholder (see Provenance).
- Switching role changes what renders, with no cross-role leakage of gated sections.

---

## Provenance / integrity (non-negotiable)
Pulse never shows a number it hasn't measured. Every stat must be real-sourced or show an honest empty / "not enough data yet" state. **No invented or placeholder numbers ship in the page.** The prototype's numbers are mock and must not survive into the build — flag any stat that can't yet be sourced rather than faking it.

## Open questions for Muiz
1. Confirm the current Heartbeat build state — build against where Pulse is now, not the prototype's assumptions.
2. Role/visibility matrix: which role sees which section and which financials? (Founder view is drawn; the rest need Dave's boundary.)
3. "What we're building" source: manual founder-curated list, or derived from tagged projects?
4. "On-time delivery %" and "shipped this month" — confirm the definitions/queries so the numbers are defensible.
5. Milestones (anniversaries/birthdays): is start-date/DOB data available, and is showing it acceptable on privacy grounds?

## File manifest
- `README.md` — this brief
- `heartbeat-mockup.html` — clickable static prototype (design-system tokens at top; Founder view)
