# Megamen32 GSD

[Русская версия](docs/README.ru.md) · [Why this version](docs/EVALUATION.md) · [Upstream GSD](https://github.com/gsd-build/get-shit-done)

> My auto-updating version of Get Shit Done: full upstream GSD plus focus-group review and mandatory proof on the real user surface before work is called complete.

GSD was the strongest foundation across every criterion in our internal workflow
evaluations. This repository is the version I ship: it keeps upstream planning,
execution, and UAT, then adds the acceptance discipline that mattered in those
tests.

- Full upstream GSD skills, workflows, prompts, and SDK.
- Focus groups for UX, onboarding, discoverability, and content when varied user goals matter.
- A mandatory final canary through the real browser, desktop app, device, CLI, API, or delivery path.
- An automatic business supervisor that interrupts technical-report drift and sends the executor straight back to the requested outcome and its canary.
- Human-readable notifications and natural Russian TTS by default unless another language was requested.
- Daily tested upstream updates for Codex, Claude Code, OpenCode, and ZCode.

## Install

Codex, through the public `megamen32-public` marketplace:

```bash
codex plugin marketplace add megamen32/megamen32-public-marketplace --ref main
codex plugin add gsd@megamen32-public
```

Start a new Codex session after installation. OGSD automatically selects the
shortest original `gsd:*` route for engineering work, then continues through
consumer acceptance. No manual `gsd-start` is needed. Plugin SessionStart hooks
supply context only and never launch another session. For Codex hosts where
hooks await trust, install the supported user instruction bootstrap once:

```bash
python3 scripts/install_runtime.py --runtime codex --plugin-root /path/to/installed/gsd
```

OpenCode's compatibility installer wires both its native system hook and its
supported instruction bootstrap, preserving unrelated configuration.

 Completion-capable workflows automatically load the personal acceptance
gate; `gsd:gsd-acceptance-gate` is also available directly.

During an active GSD workflow, choosing a technical-report detour or preparing
to end a turn with feasible work remaining triggers one short supervisor subagent. It chooses
one concrete next action and the executor performs it in the same turn, then
continues upstream GSD without waiting for the user to say "continue".
Necessary implementation and real authorization/resource
limits still apply. This is a workflow wrapper, not a background watcher of every
chat. `gsd:gsd-business-supervisor` can also be invoked directly. The wrapper is
reapplied by upstream updates.

## Other harnesses

Claude Code:

```bash
claude plugin marketplace add megamen32/megamen32-public-marketplace
claude plugin install gsd@megamen32-public-claude --scope user
```

ZCode, using its native Agent Plugin support:

```bash
zcode plugins marketplace add megamen32/megamen32-public-marketplace --scope user
zcode plugins install gsd@megamen32-public-claude --scope user
```

Hermes, using its native Agent Plugin support:

```bash
hermes plugins install megamen32/gsd-agent-plugin --ref main --enable --yes-deps
```

OpenCode is the only supported harness here without native Agent Plugin v1
installation, so it uses the bundled compatibility adapter:

```bash
git clone --depth 1 https://github.com/megamen32/gsd-agent-plugin.git \
  ~/.local/share/gsd-agent-plugin
npm install --omit=dev --prefix ~/.local/share/gsd-agent-plugin
python3 ~/.local/share/gsd-agent-plugin/scripts/install_runtime.py --runtime opencode
```

Existing JSON configuration is preserved and backed up under
`~/.local/state/gsd-agent-plugin/`.

## What makes this my version

This is an additive distribution, not a source fork that drifts away from GSD.
Upstream content is regenerated from the published `get-shit-done-cc` package;
personal policy lives under `overlay/` and is reapplied after every refresh.
Only a fully validated generated update is allowed onto `main`.

Security-related changes are globally approval-gated: GSD may report a finding
or propose a fix, but it must not modify code, configuration, infrastructure,
runtime state, or plans for that security change without direct user consent
that clearly covers it. Generic autonomy, review `--fix`, and deviation rules
do not grant that consent.

The claim above is deliberately scoped to our internal evaluations, not a claim
of universal benchmark supremacy. See [the decision and evidence boundary](docs/EVALUATION.md).

## Updating

The scheduled GitHub workflow checks upstream daily, rebuilds the complete
plugin, reapplies the overlay, runs the test suite and CLI canary, and pushes
only a passing change. Manual controls:

```bash
python3 scripts/sync_upstream.py --check
python3 scripts/sync_upstream.py --force
```

Build provenance is recorded in [`UPSTREAM.json`](UPSTREAM.json). The upstream
project remains credited and licensed separately in
[`LICENSE.upstream`](LICENSE.upstream).

## Test modes and nightly

`python3 scripts/test_policy.py` runs fast unit and focused integration checks
with a hard **180-second combined deadline**. `tests/catalog.json` declares every
scenario's purpose, detected defect, category, expected time and maximum time.
Unclassified coverage, timeout and incomplete summaries fail the run.

`python3 scripts/test_policy.py --mode nightly --deadline 120` retains slow
upstream reconstruction separately. Run it through the existing bounded runner
from a clean, pinned input; reconstruction changes generated payload and must
never overwrite unrelated work.

`scripts/nightly_queue.py` is a host-local queue adapter for the existing
`bounded-foreground.py` lifecycle. Each of 100/44/88 owns independent state.
Fresh Herder active development skips before booking; unavailable, stale or
truncated native discovery defers. Only the exact own nightly executor can be
excluded. The runner enforces finite CPU/RAM/tasks/temp/I/O and window budgets,
terminates only its owned generation, and verifies cleanup. An unfinished job
returns to the tail only after cleanup proof; unknown cleanup retains its claim.

No new daemon, MCP or fleet-wide exclusive slot is installed. See
[delivery evidence and remaining dependencies](docs/OGSD-DELIVERY.md).
