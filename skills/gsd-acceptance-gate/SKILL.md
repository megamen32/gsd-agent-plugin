---
name: "gsd-acceptance-gate"
description: "Close GSD delivery with evidence from the real user surface and, when varied user goals matter, an independent focus-group pass. Use immediately before a completion-capable GSD workflow reports success."
metadata:
  short-description: "Final real-surface and focus-group gate"
---

<megamen32_gsd_business_supervisor>
At workflow entry, anchor the user's requested outcome and its shortest real
consumer canary in existing context. Before CHOOSING a support-only detour
(hash packets, coordination, admission, unsolicited security expansion), run the
business supervisor, before spending another action on that detour.
Before reporting hashes/SHA, packets, receipts,
coordination, admission, or security work while that outcome remains unproven,
automatically run the business supervisor. Also run it after two consecutive
support-only steps without progress toward the outcome, or before ending with
any turn-ending response while authorized task work remains. Do not wait for
user invocation or a "continue" message.

@../../get-shit-done/workflows/business-supervisor.md

The supervisor selects ONE next action; execute it in this same turn, then resume
the real GSD workflow. Do not turn supervision into another report/review loop.
Do not end the turn with a checkpoint, partial result, or offer to continue when
the next authorized action is feasible. End only on the proven requested outcome,
an explicit user stop/pause, or a concrete blocker with no useful authorized work.
Keep technical provenance internal unless the user requested it. A genuine
authorization/resource blocker stays binding; invented gates and unsolicited
security expansion do not become the task. Propagate these triggers to delegated
GSD workers; only the lead launches the supervisor, never recursively.
</megamen32_gsd_business_supervisor>

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

<objective>
Prove the accepted claim through the shortest real user or consumer journey
after the final implementation, deployment, migration, and intentional restart.
Tests and logs are supporting evidence, not substitutes for this gate.
</objective>

<execution_context>
@../../get-shit-done/workflows/acceptance-gate.md
</execution_context>

<process>
1. Read the acceptance workflow completely.
2. Identify the exact accepted claim, real surface, test identity/data, allowed
   side effects, and stop condition.
3. Run the workflow after the final state-changing operation.
4. Return only `PASS`, `CHANGES_REQUIRED`, `BLOCKED_REAL_SURFACE`, or
   `BLOCKED_REPOSITORY_STATE`, with the journey and evidence required by the
   workflow. `PASS` is forbidden until every changed repository is clean,
   green, pushed, and synchronized on its remote default branch.
</process>
