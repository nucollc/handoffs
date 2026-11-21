# Pulse · My Work team-member dashboard — Requirements

**If it is not written here, it is not being built.** Visual target: `prototype/index.html` (open it in a browser). Approved by Dave Nov 18, 2026 (D11).

Core insight: **My Work sorts the day by who the work is for, and ranks it by what the role is for.**

Items marked **[ASSUMED]** are Dave's defaults. Confirm or push back on them before building (see Open questions).

---

## Who sees it

- Every **staff** team member sees My Work with **only their own** work. Founders see their own work here too.
- Client accounts never see My Work (unchanged).

## In scope

### A. Page top

**1. Greeting row with availability toggle.** The greeting reads "Good morning/afternoon/evening [Name]. Here's your work today." Below it is the existing summary line (open tasks · subtasks others are waiting on · paused). On the right of the same row sits an availability pill: a coloured dot plus the status (Active / In meetings / Away).
*Done when:* the pill is at the top right, level with the greeting, and shows the person's current status and colour.

**2. Availability panel anchored to the toggle.** Clicking the pill opens the **existing** availability panel (status, "Team sees", Active / In meetings / Away switch, Time off booked, Your day) as a popover **directly under the pill, with a pointer to it**, not centred on the screen. The panel's contents and behaviour don't change.
*Done when:* clicking the pill opens the panel attached to it. Choosing a status updates the pill immediately. ✕, Esc and a click outside all close it. On a phone-width screen the panel stays fully on screen.

**3. Buttons and Plan your week stay.** "+ New task", "+ From template" and the Plan your week strip stay as they are today. "+ New project" shows for founders only. **[ASSUMED]**
*Done when:* staff see New task and From template; founders also see New project; Plan your week works as before.

### B. Filter cards (left column, top)

**4. Filter cards, shown only when they have open items.** In this order:

| Card | Counts items that are… |
|---|---|
| Blocked | status Blocked |
| Late | due before today |
| Others waiting on you | subtasks assigned to you on a teammate's task (today's "Others are waiting on you") |
| Due today | due today |
| Needs a word | status Needs a word |
| For your review | sent to you to check (today's "For your review") |
| Due in 7 days | due today through the next 7 days |
| Is it done? | every subtask ticked, task still open (today's definition) |
| Sitting still | nothing moved in 7+ days (today's definition) |

The counts cover everything shown in the three sections (tasks and subtasks). Paused work is excluded. **A card with zero items isn't rendered at all.** If every card is zero, show one line instead: "All clear: nothing late, blocked or waiting on you."
*Done when:* each card's number matches the items it filters to. A card disappears when its count reaches zero. A person with nothing open sees the All clear line.

**5. Clicking a card filters the sections.** Clicking a card shows only matching items in the three sections. Any section with no matches is hidden while the filter is on. A bar shows "Showing [card] · N items" with a "Show everything" button. Clicking the active card again also clears the filter. Only one filter is on at a time.
*Done when:* clicking *Needs a word* shows only Needs-a-word items, hides empty sections and shows the bar; "Show everything" or a second click restores the full view.

### C. Three task sections (left column)

**6. One home per item.** Each item appears in exactly one section:
1. **Others are waiting on you**: a subtask assigned to you on someone else's task.
2. **Client work**: otherwise, if the task's project belongs to a client (not NUCO's own internal company). **[ASSUMED definition]**
3. **Your tasks**: everything else. Subtasks on your own tasks sit in a "Subtasks on your own tasks" group at the bottom of this section.

*Done when:* no item shows twice, and a subtask on a teammate's task never appears under Client work.

**7. Section order and contents.** The order is Client work, Others are waiting on you, Your tasks.
- **Client work** is grouped under a header per client ("Harbor Lane Bakery · 2").
- Rows show the title, project, status pill, priority and due date (late in red, "Today" in accent).
- Sort order inside groups stays as today: blocked, then priority, then soonest.
- Each section header shows its count and its late count, and collapses and expands.
- Clicking a row opens the task as it does today.

*Done when:* it matches the prototype, and the task view is unchanged.

**8. Paused work on one line.** Paused items (on-hold projects) collapse to a single line under the sections ("⏸ N paused with on-hold projects · not counted above · show"), which expands to today's paused groups.
*Done when:* paused items aren't counted in the cards, sections or gauge, and can still be opened.

### D. Right column

**9. Temp gauge.** This replaces the plain status chart. The card is titled "Your temp gauge" and contains:
- a reading pill and a large reading: "Running cool" / "Running warm" / "Running hot", in green / amber / red, with a matching coloured top border
- one line saying why and what to do (for example "2 late (1 that others are waiting on) · nothing blocked. A few things slipping. Catch them today.")
- the status donut (To do, In progress, Review, Needs a word, Blocked) with the open-task count in the centre and counts beside it
- "N due in the next 7 days"
- a three-line key explaining the rule

**The rule is plain logic, not AI.** "Items" means open tasks plus subtasks others are waiting on; "late" counts both.
- **Hot:** any task is Blocked, **or** 25% or more of items are late.
- **Warm:** otherwise, if anything is late or anything is in Needs a word.
- **Cool:** nothing late and nothing blocked.

*Done when:* the reading matches the rule for test users built to each case, and every number on the card matches the sections.

**10. Your role link.** This is already built under its own task ("My Work: add a 'Your role' block"). It sits at the bottom of the right column.
*Done when:* it renders below the gauge on desktop and last on phone.

### E. Phone layout

**11. Single-column stack.** The order is: greeting and availability, buttons, Plan your week, filter cards (two per row), temp gauge, Client work, Others are waiting on you, Your tasks, paused line, Your role.
*Done when:* at 375px wide nothing overflows, and the order matches.

## Coming off My Work

- The **Scoreboard** block (tasks late, due in 7 days, blocked, subtasks late, your projects). The filter cards replace it.
- The **due-date strip** (Due in 1 day / In 3 days / This week / Overdue / No date). **[ASSUMED]**
- The six **attention cards** as a separate group. For your review, Needs a word, Is it done? and Sitting still come back as filter cards. **Projects needing updates** and **Say how long** leave My Work. **[ASSUMED]**

## Explicitly out of scope

- **Your focus today** (AI daily pick) and **How your role is tracking** (role indicator cards). The prototype shows them as samples in Paisha's view to explain the intent. **Render nothing for them now [ASSUMED]**: no placeholder boxes. The AI focus pick is being tested outside Pulse first. The role indicators need "Role · [Role] · [Person]" projects, which don't exist yet.
- Any change to the task view, Projects, Heartbeat, Vitals, Team & roles, or the contents of the availability panel (only its position changes).
- New task fields or data. Every card and number uses data Pulse already has.
- Slack, notifications and reminders.
- The prototype's dark top bar ("View as", Desktop/Phone) is a prototype control only. Don't build it.

## Rules

- **Integrity:** every number comes from live Pulse data and matches the items it refers to. Pulse never shows a number it hasn't measured.
- **Own work only:** a person's My Work shows only items assigned to them.
- **For later (the focus and tracking cards):** they read tasks and never change them, and they may only quote numbers Pulse measures.

## Open questions for Muiz

1. Can "Client work" be decided from the project's client (anything other than NUCO's own internal company)? If not, what's the cleanest rule?
2. Confirm the four [ASSUMED] items: New project founders-only, nothing rendered for the two later cards, the due-date strip off, Projects needing updates and Say how long off.
3. Is "Sitting still" counted per task today, and does it include subtasks? Use whatever My Work counts now.
4. Anything here that's unbuildable as written. Say so before starting.
