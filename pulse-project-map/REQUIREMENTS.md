# Pulse project map — Requirements

*Internal Pulse. Design session with Dave, Oct 5, 2026. The visual target is `prototype.html` in this folder. If it isn't written here, it isn't being built. Items marked [ASSUMED] were defaulted, not asked; treat them as permission to proceed.*

## Words used here
- **Action**: a task, placed on the map on its due date.
- **Track**: a lane of work that runs alongside others (e.g. Hosting, Domain).
- **Waits on**: a dependency. Action B can't happen until action A is done.
- **Start**: the project's start date and time. **The result**: the end station, labeled with what the project delivers, sitting on the deadline.
- **Builders**: admins, founders, agents, PMs and developers. Everyone else is a **viewer**.

---

## Part 1 — The map view (tomorrow, Tue Oct 6, if straightforward; Fri Oct 9, 2026 at the latest)

**1. Board / Map toggle.** A toggle in the upper right of the task board on every project page switches between Board and Map. The project page above it is unchanged. The page opens on Board, as today. [ASSUMED]
*Done when:* on any project, clicking Map shows the map and clicking Board returns to today's board.

**2. Dated layout.** The map runs left to right on real dates, from the start to the deadline, or to today if today is later. It shows weekly date marks, a dashed deadline line, and a red dashed "Today" line.
*Done when:* a project starting Sep 4 with a Sep 30 deadline, viewed Oct 5, shows Sep 4 at the left, both lines, and Today to the right of the deadline.

**3. Start and the result.** A start station shows its date and time. An end station labeled "The result" sits on the deadline and shows what the project delivers when clicked.
*Done when:* clicking each station shows those details.

**4. Tracks and actions.** Each track is a labeled lane. Each action sits on its track at its due date. A line runs from the start, through each track's actions in date order, to the result. Segments are solid green up to the last action done in an unbroken run from the start; the rest are dashed grey.
*Done when:* "Ask the Experts" shows four lanes with the line solid through the done actions and dashed after.

**5. Status colors, by plain rule.** Each action is exactly one of these, checked in this order:
- **Done** (green, with a check): the task is complete.
- **Urgent or blocking** (red ring with "!"): the task is marked urgent, or it's blocked or waiting on someone.
- **Behind** (amber): the due date has passed and it's not done. Its label adds "Nd late."
- **Being worked on** (blue with a halo): the task is in progress.
- **Not started** (white with a grey ring): everything else.

Milestones (where tracks join) are drawn larger with a diamond center.
*Done when:* each status above appears correctly on the sample projects, and a legend under the map explains them.

**6. Waits-on lines.** When an action waits on an action in another track, a thin dashed arrow joins them. If an action is due before something it waits on, that arrow turns red, and its panel says so.
*Done when:* moving a dependent action earlier than what it waits on turns its line red.

**7. Behind-plan gap.** "Where the work is" is the earliest due date among unfinished actions. If that date is before today, the map shades the space between it and today and labels it "N days behind plan." A summary line above the map names the blocking action and why, if one is blocked. Otherwise it says "On track."
*Done when:* "Ask the Experts" shows "24 days behind plan," naming the Vercel move waiting on Dave, and a project with nothing overdue shows "On track."

**8. Click a stop.** Clicking an action opens a side panel with its status, due date, days before or after the deadline, owner, track, any blocked reason, its subtasks with check-offs, and what it waits on. Anyone can tick a subtask from here, including viewers. [ASSUMED]
*Done when:* clicking any action shows all of the above, and ticking a subtask updates the count.

**9. On-hold projects.** The on-hold notice stays, and the map still shows where the project stopped.
*Done when:* "Ask the Experts" shows both.

**10. No map yet.** A project with no actions shows an empty state. Builders get a "Draw the map" button; viewers see who owns the project.
*Done when:* Harbor Dental's website build shows this state for both kinds of user.

**11. Signal on the projects list.** Each project in the list shows "N days behind plan," "On track," or "No map yet." [ASSUMED]
*Done when:* the list shows the right signal for each sample project.

**12. Phone viewing.** The map scrolls sideways inside its card on a phone, and the panel drops below it. [ASSUMED]
*Done when:* the map is readable on a phone without the page scrolling sideways.

---

## Part 2 — The map builder (follows Part 1)

**13. Who can build.** Only builders see "Edit map" and "Draw it on the map." Viewers see the map and launch projects only from templates.
*Done when:* signed in as a viewer, neither option appears.

**14. Edit mode.** "Edit map" puts the map in edit mode with a toolbar: Add action, Add track, Draw a line. "Done editing" saves and returns to the view.
*Done when:* changes made in edit mode are still there after Done editing and a page reload.

**15. Start, deadline, delivers.** In edit mode, clicking the start sets its date and time. Clicking the result sets the deadline and the "what this delivers" line. The deadline can't be before the start.
*Done when:* setting a deadline earlier than the start shows an error and doesn't save.

**16. Add and arrange.** Add action places a new action on the selected track (or the first one) at the middle of the timeline and opens it for naming. Add track adds a lane, renamed from the panel. Dragging an action left or right changes its due date to the nearest day. Moving it to another track happens from the panel.
*Done when:* an action dragged a week right shows a due date a week later.

**17. Action details.** In edit mode, an action's panel edits its name, due date, owner, track and priority. It also adds and removes subtasks, removes waits-on links, and deletes the action. Each action shows how many days before the deadline it falls.
*Done when:* every field changes and the map redraws to match.

**18. Draw a line.** With Draw a line on, click the action that comes first, then the one that waits. The link is saved and drawn.
*Done when:* the second action's panel lists the first under "Waits on."

**19. New project.** Builders choose "Draw it on the map" (name, client, what it delivers, start date and time, deadline), which opens the builder. Everyone can choose "Start from a template" (template, client, start date).
*Done when:* both paths create a project and open it on the map.

**20. Templates carry their map.** A template stores its tracks, actions, subtasks and waits-on links, with each action's timing counted from the start. Launching it lays the map out from the chosen start date. Tasks are still born unassigned, as Pulse does today. [ASSUMED]
*Done when:* launching a template on Oct 6 produces a fully drawn map dated from Oct 6.

---

## Explicitly out of scope
- A map across all projects at once.
- Retail Pulse.
- Clients or anyone outside the team seeing maps.
- Moving dependent actions automatically when one moves. The map shows the clash in red; a person fixes it.
- Times of day on actions. Only the start has a time.
- New reminders or notifications driven by the map.
- Dragging actions up or down between tracks. That's done from the panel.
- Building or editing maps on a phone. Phones view only. [ASSUMED]
- Printing or exporting the map.
- Changing the existing "Pulse thinks this can still land" banner or the risk score.

## Open questions for Muiz
1. Actions should be the existing tasks with a track and waits-on links added, not a new kind of thing. Confirm, or say why not.
2. Existing projects have no tracks. Default: their tasks go on one "Main track" until someone edits the map. Could the existing Phase tags seed tracks instead?
3. Waits-on links are item 4 of the Sep 30 template builder upgrades, released for this on Oct 5. Build them once so both use the same links.
4. Which existing Pulse roles count as builders (admin, founder, agent, PM, developer)?
5. Do task checklists (e.g. "0/1" on board cards) become the subtasks here, or are subtasks new?
6. Part 1 is wanted Tue Oct 6 if the build is straightforward, Fri Oct 9 at the latest. Which day will it land? If Friday isn't possible, say what part can, and when.

## Assumptions count
6 items marked [ASSUMED]: items 1, 8, 11, 12 and 20, plus phones being view-only.
