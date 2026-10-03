---
name: "gsd-acceptance-gate"
description: "Close GSD delivery with evidence from the real user surface and, when varied user goals matter, an independent focus-group pass. Use immediately before a completion-capable GSD workflow reports success."
metadata:
  short-description: "Final real-surface and focus-group gate"
---

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
4. Return only `PASS`, `CHANGES_REQUIRED`, or `BLOCKED_REAL_SURFACE`, with the
   journey and evidence required by the workflow.
</process>
