# OGSD delivery, 2026-10-09

Owner: this Codex session, canonical gsd-agent-plugin main on server-100.
Only this repository's source is owned. AutoGram, AutoFind, Exmanager and the
infra owner's helper2c are outside the change boundary.

- Autoentry: original GSD routes supplied by Codex SessionStart and supported
  user AGENTS bootstrap, plus OpenCode's native system transform hook.
  Context only; no session launch, background model or recursive bootstrap.
- Tests: `python3 scripts/test_policy.py` enforces combined release <=180s,
  per-scenario limits, exact classification and complete collected coverage.
  `tests/catalog.json` records purpose, defect and expected/max times.
- Nightly queue: implementation and native lifecycle verification pending.
  Current Herder `/api/sessions` is cache-first and does not expose observation
  timestamp/completeness. Local Herder endpoints on 44/88 refuse connections.
  Neither absence of sessions nor an unreachable API proves a free host.
  Smallest next step: reuse fresh Herder native discovery and the existing
  bounded foreground lifecycle; keep unknown hosts deferred before reservation.

Evidence: `.tmp/ogsd/release2/result.json` retains the first complete fast run.
Installed consumer acceptance remains required before task completion.
