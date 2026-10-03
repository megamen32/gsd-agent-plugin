# Get Shit Done Agent Plugin

This is an auto-updating personal overlay on the upstream
[`get-shit-done-cc`](https://github.com/gsd-build/get-shit-done) release.
It keeps the full upstream skill profile, workflows, agent prompts, and SDK,
then adds one acceptance skill and injects its final gate only into workflows
that can declare delivery complete. Upstream content stays generated; personal
policy lives under `overlay/` and is reapplied after every refresh.

The acceptance overlay adds two outcomes without replacing GSD planning or
UAT: goal-diverse focus groups where they add evidence, and a mandatory final
canary through the real user/consumer surface. For GUI claims that means the
actual browser, desktop application, or device with semantic/computer-use
actions when available—not a health endpoint standing in for the journey.

## Install

Codex, through the public `megamen32-public` marketplace:

```bash
codex plugin marketplace add megamen32/megamen32-public-marketplace --ref main
codex plugin add gsd@megamen32-public
```

Claude Code, through the same marketplace repository:

```bash
claude plugin marketplace add megamen32/megamen32-public-marketplace
claude plugin install gsd@megamen32-public-claude
```

OpenCode and ZCode use the portable package from a stable checkout. The small
runtime adapter only adds this checkout to each runtime's supported plugin and
skill configuration:

```bash
git clone --depth 1 https://github.com/megamen32/gsd-agent-plugin.git \
  ~/.local/share/gsd-agent-plugin
npm install --omit=dev --prefix ~/.local/share/gsd-agent-plugin
python3 ~/.local/share/gsd-agent-plugin/scripts/install_runtime.py --runtime all
```

Use `--runtime opencode` or `--runtime zcode` to configure only one runtime.
Existing JSON configuration is preserved and backed up under
`~/.local/state/gsd-agent-plugin/` before it is changed. Restart the runtime or
start a new session after installation.

Build provenance is recorded in `UPSTREAM.json`. A daily GitHub workflow runs
`scripts/sync_upstream.py`, fetches the latest npm release, builds an isolated
Codex projection, reapplies `overlay/`, validates the full package, and pushes
only a passing generated update. Manual controls:

```bash
python3 scripts/sync_upstream.py --check
python3 scripts/sync_upstream.py --force
```

`scripts/emit_opencode.py` is a generic Agent Plugins 1.0 to OpenCode emitter.
It generates the native `opencode-plugin/index.js` compatibility module, the npm
`package.json`, and a static OpenCode config fragment without changing upstream
GSD or OpenCode. GSD has no MCP servers, so its generated JS module is deliberately
minimal; skills are discovered through the generated `skills.paths` entry.
