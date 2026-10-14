<ogsd_autoentry>
OGSD is a thin adapter of the installed original GSD, not another workflow.
At the first engineering request, automatically select and read the original GSD skill:
- trivial change under two minutes: skills/gsd-fast/SKILL.md;
- bounded change requiring research or verification: skills/gsd-quick/SKILL.md;
- existing .planning project or continuation: skills/gsd-progress/SKILL.md, then its next upstream route;
- substantial new project: skills/gsd-new-project/SKILL.md; bug investigation: skills/gsd-debug/SKILL.md.
Resolve these paths below GSD_PLUGIN_ROOT. Do not ask the user to invoke gsd-start.
Plain questions, translations and status requests need no engineering workflow.
Before entry/reentry, resume/compaction and direction changes, read
$GSD_PLUGIN_ROOT/get-shit-done/references/task-continuity.md and reconcile the
saved original task/mandate/boundaries with current STATE and current SPEC/PLAN.
Ordinary coordination messages do not replace the task; verified human-authorized
coordinator or delegation handoffs within their mandate do, linked to the plan.
Choose the shortest original route; keep the existing task and upstream state across turns.
Continue authorized implementation, relevant checks and delivery to the real consumer result.
A progress report, unit GREEN, or workflow artifact alone does not complete the task.
Stop only for proven consumer acceptance, explicit user pause, or an evidenced blocker with
no useful independent authorized work. Do not create sessions, invoke this bootstrap again,
or supervise the supervisor. This context adds policy; it does not start another agent.
Tests have exactly three categories: fast unit, focused integration, slow nightly.
Before accepting a coordinator role or arranging parallel sessions, read
$GSD_PLUGIN_ROOT/get-shit-done/references/session-coordination.md.
The coordinator owns executor/file assignments, deliberate Git worktree isolation,
conflict resolution and integration while protecting compatible work and foreign WIP.
Normal user updates explain results, owners, blockers and remaining time; do not
emit hashes, receipt packets, ACK traffic or repeated-permission loops.
Each test/scenario records purpose, detected defect, category, expected and maximum seconds.
Expected duration is an observation; the finite emergency wall limit is ten times
the expected duration, including setup. Do not stop a healthy run at 180 seconds.
Timeout, missing summary and incomplete coverage are never GREEN; retain checkpoints.
Nightly uses the existing bounded runner lifecycle and each host's independent finite queue.
Fresh Herder active development means defer before reservation; unknown means defer.
Exclude only the identified own nightly executor, never other development sessions.
At the window deadline, clean up only the owned job/reservation, retain results/checkpoint,
and return the unfinished job to the tail. Never stop foreign work or add a global sole slot.
</ogsd_autoentry>
