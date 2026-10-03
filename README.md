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
- Human-readable notifications and natural Russian TTS by default unless another language was requested.
- Daily tested upstream updates for Codex, Claude Code, OpenCode, and ZCode.

## Install

Codex, through the public `megamen32-public` marketplace:

```bash
codex plugin marketplace add megamen32/megamen32-public-marketplace --ref main
codex plugin add gsd@megamen32-public
```

Start a new Codex session after installation, then use the normal `gsd:*`
skills. Completion-capable workflows automatically load the personal acceptance
gate; `gsd:gsd-acceptance-gate` is also available directly.

## Other harnesses

Claude Code:

```bash
claude plugin marketplace add megamen32/megamen32-public-marketplace
claude plugin install gsd@megamen32-public --scope user
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
