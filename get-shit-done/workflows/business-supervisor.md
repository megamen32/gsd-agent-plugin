# Business supervisor

The lead runs this before choosing a support-only detour, when the calling
skill's drift trigger fires, and before ending a turn with work still feasible.
Workers pass one short drift signal to their existing lead and keep doing useful
authorized work. They do not start competing supervisors.

1. In memory, retain the user's requested outcome, latest steering, the shortest
   real consumer journey, last two actions, actual result so far, and any concrete
   blocker. Use existing context; do not create packets, hashes, trackers, or a
   new plan to prepare this check. Technical milestones are not the business goal.
2. Read `$GSD_PLUGIN_ROOT/agents/gsd-business-supervisor.md` and launch ONE
   available subagent with that prompt and the concise context above. Give it no
   editing, shell, browser, external messaging, or production access. This is a
   single context-only reply, not a background monitor. Use the existing agent
   allowance; supervision does not justify new infrastructure or a new session.
   If delegation is unavailable or forbidden by higher-priority instructions,
   apply the same prompt inline and continue; say so only if material.
3. Apply its decision immediately in this turn. `DO_NEXT` means perform that
   action now; `CONTINUE` means resume the existing concrete business action;
   `BLOCKED` means state the exact missing authority/capacity in one plain
   sentence and perform its safe independent action if one exists. Do not ask
   for confirmation already granted. Do not call the task complete on a blocker.
   A supervisor reply is not the lead's final answer. Do not hand continuation
   back to the user while the chosen authorized action is feasible.
4. Resume upstream GSD at the affected step. Run the real canary after required
   implementation/review/deployment operations, capture and evaluate its actual
   result, and fix a failed journey. Never invent success or send a business
   message merely to demonstrate activity.

Deduplicate in the lead's existing conversation context: one supervision per
unchanged drift episode. Rearm after a real task action or a newly verified
blocker changes the next step; more hashes or repeated statuses do not rearm it.
Never supervise the supervisor or launch nested reviewers.

User updates explain what now works, what still fails, and what action is
required. Keep provenance available for debugging, outside the main reply unless
requested. A user-requested hash audit, coordination task, or security repair
is itself the requested outcome; do not redirect it to an unrelated canary.
