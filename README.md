# Pulse project map — handoff for Muiz

> **Status:** Ready for Dev · **Owner:** Dave · **Date:** 2026-10-05
> **Staging is a passthrough.** These files live in `nucollc/handoffs` only until you migrate them into the Pulse repo. Once you do, that copy is canonical and this folder is stale. Don't build long-term against it.
> **Public repo, no secrets.** Nothing here contains keys, `.env`, or client data. Client names in the prototype are made up on purpose. Keep it that way.

## Where the files are
Repo folder: `https://github.com/nucollc/handoffs/tree/main/pulse-project-map`

```
pulse-project-map/
├── prototype.html      clickable concept of the map view and the map builder (open in a browser)
├── REQUIREMENTS.md     what to build: 20 numbered items, each with a "done when"; out of scope; open questions
├── BRIEF.md            why it exists, who it's for, what success looks like
└── README.md           this brief
```

## How this handoff works
- **Notion = context, GitHub = build.** The gate verdict, reasoning and decision context live in Notion (linked at the bottom). This folder holds the prototype and the written definition. Neither is the other's source of truth.
- **Notify-first.** This is an update to internal Pulse, so the home is the existing Pulse repo. Migrate these files there as the first act of the build.

## The problem (one line)
Projects in internal Pulse get lost in the weeds of their own tasks, so the team can't see whether a project is moving, what it's waiting on, or how far behind it is.

## The fix
A map view on every project, toggled from the upper right of the task board. It runs on real dates from the project's start to the result it delivers. Tasks sit on parallel tracks at their due dates, colored by status. Lines show what waits on what, and a shaded gap shows how far the work is behind where the plan says it should be today. Part 2 makes the same map the way builders create projects and templates: drag actions to dates, draw dependency lines, add subtasks. The prototype shows intent only. Build it properly inside Pulse.

## Technical notes & gotchas
- **Build order and timing:** Part 1 (map view, REQUIREMENTS items 1–12) is wanted **tomorrow, Tue Oct 6, 2026, if the build is straightforward, and Fri Oct 9 at the very latest**. The team needs it on current projects right away. Part 2 (builder, items 13–20) follows. Before starting, tell Dave which day Part 1 will land (open question 6).
- **Actions should be the existing tasks**, with a track and waits-on links added, not a parallel data model (open question 1).
- **Waits-on links are the same thing as item 4 of the Sep 30 template builder upgrades,** released for this on Oct 5. Build them once so templates and maps share them.
- **Existing projects have no tracks.** Default: their tasks go on one "Main track" until edited (open question 2).
- **The "behind plan" rule is deliberately simple:** where the work is = the earliest due date among unfinished tasks. If that's before today, shade to today and label "N days behind plan." Don't swap in a model.
- **Prototype rough edges not to carry over:** it keeps everything in memory, uses made-up dates and subtasks, and lays out label text naively (labels can overlap on busy days). Rebuild the visuals in Pulse's own components and styles; don't paste the prototype's code in.

## Guardrails (must not miss)
- Viewers (anyone who isn't an admin, founder, agent, PM or developer) must not be able to change a map. Enforce it in Pulse itself, not just by hiding the Edit map button.
- Launching from a template keeps tasks born unassigned, as Pulse does today.
- Moving one action never silently moves others. Clashes show in red for a person to fix.
- No client data or keys in this public repo.

## Done when (acceptance checks)
- [ ] Every project page in internal Pulse has the Board / Map toggle in the upper right of the task board, and the map renders on desktop and on a phone (sideways scroll inside its card, no page-wide sideways scroll).
- [ ] The map is drawn from live Pulse data: real tasks, owners, due dates, subtasks and statuses, with no sample data.
- [ ] On "Build 'Ask the Experts' Tool for NLA," the map shows how many days behind plan it is and names the blocked task and why.
- [ ] Status colors follow the five rules in REQUIREMENTS item 5, and a project with nothing overdue shows "On track."
- [ ] Signed in as a viewer, there is no way to edit a map or draw a new one; launching from a template still works.
- [ ] Builder changes (dates, tracks, waits-on lines, subtasks) survive Done editing and a page reload, and a template launched on a chosen date produces a fully drawn map dated from it.
- [ ] Every numbered item in REQUIREMENTS.md passes its own "done when."

## Full context
Notion handoff page: https://app.notion.com/p/3f10d0465513811a80a2cf3ca9e64efe
Gate verdict: https://app.notion.com/p/3f10d046551381daa916cb80a6e1c3d3
