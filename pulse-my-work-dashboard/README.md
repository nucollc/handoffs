# Pulse · My Work team-member dashboard — handoff for Muiz

> **Status:** Ready for Dev · **Owner:** Dave · **Date:** 2026-11-18
> **Staging is a passthrough.** These files sit in `nucollc/handoffs` only until you move them into the Pulse repo. Once you do, that copy is the real one and this folder is stale. Don't build long-term against it.
> **Public repo, no secrets.** Nothing here contains keys, `.env` or client data. Keep it that way.

## Where the files are

Repo folder: https://github.com/nucollc/handoffs/tree/main/pulse-my-work-dashboard

```
pulse-my-work-dashboard/
├── README.md               this brief, plus the Claude Code prompt
├── REQUIREMENTS.md         numbered build list, each item with a "done when"
└── prototype/index.html    clickable prototype: the visual target (open in a browser)
```

## How this handoff works

- **Notion = context, GitHub = build.** The reasoning, the gate verdict and the decision history live in Notion (linked at the bottom). This folder holds the files.
- **Notify-first.** This is an update to the existing Pulse app, so move these files into the Pulse repo as the first step, then build there.

## The problem (one line)

When a team member opens Pulse, their work arrives mixed together, and nothing tells them what matters most today or how their day is going.

## The fix

My Work becomes each team member's dashboard, in two columns.

- **Left column:** a row of **filter cards** (Blocked, Late, Others waiting on you, Due today, Needs a word, For your review, Due in 7 days, Is it done?, Sitting still). A card only appears when it has open items, and clicking one filters the task list below. Under the cards, work is sorted into three sections by **who it's for**: Client work (grouped by client), Others are waiting on you, and Your tasks.
- **Right column:** a **temp gauge** reads the day as Cool / Warm / Hot using a plain rule, alongside the status donut. Below it sits the "Your role" link.
- **Availability:** the toggle moves to the top right, and its panel opens attached to the toggle instead of centred on the screen.

Most of the data already exists on My Work today: attention counts, subtasks others are waiting on, statuses, availability. This is mainly a re-layout plus the filter behaviour and the gauge rule. Build it properly; the prototype only shows what "it" is.

## Technical notes & gotchas

- **Reuse what My Work already computes.** "Others are waiting on you", "For your review", "Is it done?" and "Tasks sitting still" all exist today. Keep their definitions so the numbers don't change meaning.
- **Every count must equal the items it filters to.** Build the cards from the same list the sections render, so they can't drift apart.
- **The temp gauge is a rule, not AI** (see REQUIREMENTS #9). It's cheap, instant and explainable.
- **The availability panel:** reuse the existing component and only change where it opens: anchored under the pill, with a pointer, and kept on screen at phone width.
- **In the prototype:** the dark top bar (View as / Desktop / Phone) is a prototype control, and the people and numbers are sample data. Client names in this copy are invented because this repo is public; the hosted prototype linked below uses real client names and is otherwise identical. Paisha's view is set on a sample day in Jan 2027 and shows the two future cards filled with samples, so you can see the intent. **Don't build those two cards yet.**
- The "Your role" link is already your task ("My Work: add a 'Your role' block"). This layout just gives it a home at the bottom of the right column.

## Guardrails (must not miss)

- **Own work only.** My Work shows only items assigned to the signed-in person. Staff only; clients never see My Work.
- **No made-up numbers.** Every number comes from live Pulse data. No placeholder boxes for the AI focus card or the role indicators.
- **Each item shows once** (REQUIREMENTS #6). A subtask on a teammate's task always goes under "Others are waiting on you".
- **Nothing else changes:** the task view, Projects, Heartbeat, Vitals and the availability panel's contents stay as they are.
- **Ask before building** if anything in REQUIREMENTS is unbuildable as written, or if you disagree with an [ASSUMED] item.

## Done when (acceptance checks)

- [ ] A staff member sees the new two-column My Work, matching the prototype, on desktop and at 375px wide.
- [ ] Filter cards appear only when they have items. Every count matches the items shown when that card is clicked. Clicking filters the sections, hides empty ones and shows the "Showing … / Show everything" bar. A second click or "Show everything" clears it.
- [ ] Someone with nothing open sees the "All clear" line instead of cards.
- [ ] Every item sits in exactly one of Client work (grouped by client), Others are waiting on you, or Your tasks.
- [ ] The temp gauge shows Cool, Warm and Hot correctly for test users built to each case, and its numbers match the sections.
- [ ] The availability pill sits at the top right. Its panel opens attached to it, updates the pill when the status changes, and closes on ✕, Esc and a click outside.
- [ ] The Scoreboard block, the due-date strip and the separate attention cards are gone. Paused work is one expandable line.
- [ ] A client account still can't see My Work, and nothing outside My Work has changed.

## Prompt for Claude Code

Paste this into Claude Code from the Pulse repo, after copying this folder into it (for example as `handoffs/pulse-my-work-dashboard/`).

```text
Redesign the Pulse My Work page as each team member's dashboard.

Read first, in this order:
1. handoffs/pulse-my-work-dashboard/README.md (this brief)
2. handoffs/pulse-my-work-dashboard/REQUIREMENTS.md (numbered build list with "done when" checks; this is the contract)
3. handoffs/pulse-my-work-dashboard/prototype/index.html (the visual target; open it in a browser and use "View as" to compare Paisha, Laura and Dave)
Then read the current My Work page code and whatever computes its counts (attention cards, subtasks for you, scoreboard, availability).

STEP 1: REPORT BEFORE BUILDING. Change nothing yet. Report back:
- How each filter card (REQUIREMENTS #4) maps to data My Work already has, and anything missing.
- How you'll decide "Client work" vs "Your tasks" (REQUIREMENTS #6, open question 1).
- Your view on the four [ASSUMED] items.
- Which parts of the current page you'll remove (Scoreboard block, due-date strip, attention cards) and anything else that uses them.
- Effort and risks, and anything unbuildable as written.
Then stop and wait for approval.

RULES
- Own work only: a person sees only items assigned to them. Staff only; clients never see My Work.
- Integrity: every number comes from live Pulse data, and each card's count equals the items it filters to. No placeholder boxes for the AI focus card or the role indicators: render nothing for them.
- Each item appears in exactly one section.
- The temp gauge is a plain rule (REQUIREMENTS #9), not AI.
- Reuse the existing availability panel; only change where it opens (anchored under the pill).
- Don't change the task view, Projects, Heartbeat, Vitals or Team & roles.
- Work on a branch. Show Dave on test data before it goes live.

DONE WHEN: every "done when" in REQUIREMENTS.md passes on test users built to cover each card, each temp gauge reading, the empty state and phone width.
```

## Full context

- Notion handoff page: https://app.notion.com/p/41f0d046551381069f35e021fe23c661
- Gate verdict: https://app.notion.com/p/41d0d046551381fdad7ec1aff2f9c326
- Clickable prototype (hosted): https://claude.ai/artifact/F22RLgWsijujus7TtNFCRG
