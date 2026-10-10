---
name: "gsd-cleanup"
description: "Archive accumulated phase directories from completed milestones"
metadata:
  short-description: "Archive accumulated phase directories from completed milestones"
---

<megamen32_gsd_session_coordination>
Accepting a coordinator role means organizing execution and integration, choosing
owned Git worktrees where writers collide, and protecting compatible existing work.
Before coordinating or delegating, read the shared policy:
@../../get-shit-done/references/session-coordination.md
Normal user updates contain outcomes, owners, blockers and remaining time, never
hash/receipt packets unless explicitly requested. No ACK or repeated-permission loops.
</megamen32_gsd_session_coordination>

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

<codex_skill_adapter>
## A. Skill Invocation
- This skill is invoked by mentioning `$gsd-cleanup`.
- Treat all user text after `$gsd-cleanup` as `{{GSD_ARGS}}`.
- If no arguments are present, treat `{{GSD_ARGS}}` as empty.

## B. AskUserQuestion → request_user_input Mapping
GSD workflows use `AskUserQuestion` (Claude Code syntax). Translate to Codex `request_user_input`:

Parameter mapping:
- `header` → `header`
- `question` → `question`
- Options formatted as `"Label" — description` → `{label: "Label", description: "description"}`
- Generate `id` from header: lowercase, replace spaces with underscores

Batched calls:
- `AskUserQuestion([q1, q2])` → single `request_user_input` with multiple entries in `questions[]`

Multi-select workaround:
- Codex has no `multiSelect`. Use sequential single-selects, or present a numbered freeform list asking the user to enter comma-separated numbers.

Execute mode fallback:
- When `request_user_input` is rejected or unavailable, you MUST stop and present the questions as a plain-text numbered list, then wait for the user's reply. Do NOT pick a default and continue (#3018).
- You may only proceed without a user answer when one of these is true:
  (a) the invocation included an explicit non-interactive flag (`--auto` or `--all`),
  (b) the user has explicitly approved a specific default for this question, or
  (c) the workflow's documented contract says defaults are safe (e.g. autonomous lifecycle paths).
- Do NOT write workflow artifacts (CONTEXT.md, DISCUSSION-LOG.md, PLAN.md, checkpoint files) until the user has answered the plain-text questions or one of (a)-(c) above applies. Surfacing the questions and waiting is the correct response — silently defaulting and writing artifacts is the #3018 failure mode.

## C. Task() → spawn_agent Mapping
GSD workflows use `Task(...)` (Claude Code syntax). Translate to Codex collaboration tools:

Direct mapping:
- `Task(subagent_type="X", prompt="Y")` → `spawn_agent(agent_type="X", message="Y")`
- `Task(model="...")` → omit. `spawn_agent` has no inline `model` parameter;
  GSD embeds the resolved per-agent model directly into each agent's `.toml`
  at install time so `model_overrides` from `.planning/config.json` and
  `~/.gsd/defaults.json` are honored automatically by Codex's agent router.
- Resolved `reasoning_effort="low|medium|high|xhigh"` (`xhigh` is a GSD/Codex tier, not a generic runtime enum) → pass `reasoning_effort`
  to `spawn_agent` when the runtime/tool supports it. Omit missing, empty,
  inherited, or unsupported values; do not invent one-off effort literals in
  workflow prose.
- `fork_context: false` by default — GSD agents load their own context via `<files_to_read>` blocks
- `Task(isolation="worktree")` / `Agent(isolation="worktree")` → no direct Codex mapping.
  Codex `spawn_agent` does not create or bind a git worktree automatically.
  Workflows that require this isolation must fail closed or use an explicit
  manual worktree protocol before spawning (#3360).

Spawn restriction:
- Codex restricts `spawn_agent` to cases where the user has explicitly
  requested sub-agents. When automatic spawning is not permitted, do the
  work inline in the current agent rather than attempting to force a spawn.

Parallel fan-out:
- Spawn multiple agents → collect agent IDs → `wait(ids)` for all to complete

Result parsing:
- Look for structured markers in agent output: `CHECKPOINT`, `PLAN COMPLETE`, `SUMMARY`, etc.
- `close_agent(id)` after collecting results from each agent
</codex_skill_adapter>

<objective>
Archive phase directories from completed milestones into `.planning/milestones/v{X.Y}-phases/`.

Use when `.planning/phases/` has accumulated directories from past milestones.
</objective>

<execution_context>
@../../get-shit-done/workflows/cleanup.md
</execution_context>

<process>
Execute end-to-end.
Identify completed milestones, show a dry-run summary, and archive on confirmation.
</process>
