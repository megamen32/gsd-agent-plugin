---
name: "gsd-business-supervisor"
description: "Automatically interrupt GSD drift into hashes, coordination, safety bureaucracy, or technical completion reports while the user's outcome is unproven. Launch one outcome-focused supervisor and immediately execute its next business action. Also use when the user says stop reporting and finish the business task or canary."
---

<megamen32_gsd_security_authorization>
Security-related changes require direct, current user consent. Do not create,
apply, auto-fix, deploy, or expand security controls merely because execution,
review, audit, planning, or verification discovers a security concern.

Without that consent:
- report the finding and the proposed change, but do not modify code, config,
  infrastructure, runtime state, or planning artifacts as if the change were approved;
- do not treat security work as a Rule 1-3 deviation or other automatic fix;
- mark security work blocked pending user approval and continue only independent,
  non-security work that remains in scope.

General permission to fix, finish, run autonomously, or fix what you find is not
security consent. Consent must identify or clearly encompass the security change,
including approval of a plan that names it. An explicit security request such as
fixing a named vulnerability, adding auth, hardening a named surface, or invoking a
security-specific workflow counts only for that stated scope. Generic review `--fix`
or autonomous flags do not. Propagate this rule to spawned agents and downstream plans.
</megamen32_gsd_security_authorization>

<megamen32_gsd_session_coordination>
Accepting a coordinator role means organizing execution and integration, choosing
owned Git worktrees where writers collide, and protecting compatible existing work.
Before coordinating or delegating, read the shared policy:
@../../get-shit-done/references/session-coordination.md
Normal user updates contain outcomes, owners, blockers and remaining time, never
hash/receipt packets unless explicitly requested. No ACK or repeated-permission loops.
</megamen32_gsd_session_coordination>

<gsd_agent_plugin_adapter>
This GSD distribution is loaded from an Agent Plugin rather than a fixed runtime home.

- Resolve `GSD_PLUGIN_ROOT` as the absolute directory two levels above this `SKILL.md`.
- Resolve every `@../../...` execution-context reference relative to this skill directory.
- Before running a workflow shell command, replace `gsd-sdk` with
  `node "$GSD_PLUGIN_ROOT/bin/gsd-sdk.js"` and turn any `../../get-shit-done/...`
  command path into an absolute path below `$GSD_PLUGIN_ROOT`.
- Named GSD agent prompts live in `$GSD_PLUGIN_ROOT/agents/`. If the runtime has no
  matching registered agent type, spawn an available generic worker/default agent and
  include the corresponding `agents/<name>.md` prompt in its task message.
</gsd_agent_plugin_adapter>

Read and execute the workflow below. This is a thin interruption of the current
real GSD workflow, not a replacement planner or another acceptance committee.

<execution_context>
@../../get-shit-done/workflows/business-supervisor.md
</execution_context>
