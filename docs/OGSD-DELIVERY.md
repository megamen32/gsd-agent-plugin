# OGSD delivery, 2026-10-09

Owner: owning Codex session, canonical gsd-agent-plugin main on server-100.
Only GSD source is owned. AutoGram, AutoFind, Exmanager and infra helper2c
remain outside this change boundary. Their releases do not wait for OGSD.

| Task | Owner | Confirmed result | Next action |
|---|---|---|---|
| Original GSD autoentry | GSD owning session | Codex fresh session selected/read gsd-fast without manual invocation, wrote and byte-verified READY; plugin installed via gsd@megamen32-public at 996d268 | Codex and OpenCode fresh consumer proof complete after native JSONC precedence fix |
| Fast test policy | GSD owning session | First combined release: 30 PASS in 9.366s, hard aggregate cap 180s; expanded catalog includes purpose, defect, category and expected/max duration | Expanded release: 39 PASS in 12.683s |
| Host-local queue | GSD owning session | Active development skips before booking; unknown defers; own executor identity only; finite window cleanup returns unfinished job to tail; unresolved cleanup retains own claim; separate 100/44/88 queues | Native bounded-runner execution when dependencies are repaired |
| Live active skip | GSD owning session | Fresh Herder native getSession on 100 confirmed running; real queue tick returned SKIP_ACTIVE, reservation_created=false | Retain proof; no replay of finished checks |
| 44/88 native visibility | Root coordinates infrastructure owner | Direct LAN identities verified. Herder 18787 connections refused; queue ticks on both returned DEFER_UNKNOWN without reservation | Owner must supply existing authoritative fresh host-local Herder/native route; unavailable is not free |
| Existing runner lifecycle | Root coordinates infra owner2c | Canonical bounded-foreground.py read-only preflight on 100 returned Held: outer/original boundary mismatch. No compatible deployed runner found in known 44/88 runtime roots. No helper was modified | Owner supplies accepted current per-host profile/budget/lifecycle route. Do not weaken guards or reserve active hosts |

OpenCode defect found and repaired within GSD installer: existing
`opencode.jsonc` overrides the plugin/instruction arrays in `opencode.json`.
The installer now writes the active JSONC layer, preserves setting values and
backs up the original file. It replaces only old GSD paths and wires the native plugin plus supported
instruction bootstrap. Foreign workflow plugins are preserved. Existing config
file permissions are retained during atomic replacement.

Queue adapter: `scripts/nightly_queue.py`. It calls the existing runner in the
same native executor session, reuses admission, reservations, same-generation
cleanup and budgets. It observes stock cleanup completion rather than creating
another process killer. It is not a daemon or a fleet-wide slot. Herder's cached
HTTP inventory can only nominate an active candidate; a native getSession
confirms that candidate. FREE requires fresh complete MCP native discovery;
truncated discovery and API failure stay UNKNOWN. Window timeout never GREEN.

Native resource/window cleanup acceptance is **not claimed**: it cannot be
run on active100 or unknown44/88. Source queue fixtures prove only policy and
ordering. Root's named infrastructure owner must close the concrete dependencies;
this task remains open until the real lifecycle path is verified.

Local retained artifacts under `.tmp/ogsd/`: release result JSON, fresh Codex
session events, OpenCode acceptance attempts, native observation and queue tick
results. Installation backups: `~/.local/state/gsd-agent-plugin/`.

Additional environment defect recorded for infrastructure owner: OpenCode's
third fresh consumer run logged `inotify_add_watch` on this repo's `.git`:
`No space left on device`. The task still selected original GSD and verified
its consumer file. No global inotify limit or foreign process was changed.
Smallest next action: infrastructure owner measures UID watch usage and
repairs the owning watch lifecycle/budget, preserving all active sessions.

The fast runner's descendant cleanup was regression-tested red then green:
a child ignoring TERM is collected while an unrelated process stays running.
A deliberately exhausted aggregate deadline returns failure, never GREEN.

Installed-cache release initially exposed absent optional SDK dependencies
(the Codex git plugin route does not run npm install). Installed the existing
declared dependencies with lifecycle scripts disabled; no package metadata was
changed. The affected installed SDK case is checked before resumed acceptance.
Native runtime verification now reads the active JSONC layer too.

Fleet continuation: [installed host evidence and remaining native window](OGSD-FLEET-DELIVERY-20261009.md). The table above records earlier findings; the follow-up contains the current result. All100/44/88/Mac runtime adapters are4f603b4, one original gsd@megamen32-public each. The installed public manifests pass the official Agent Plugins1.0 schema. The installer100 permission repair and preservation checks are complete.

The legacy original-budget mismatch is resolved by the infra-owned100 profile
gsd-nightly-window100 at8064174. The adapter preserves _profile and invokes
the enduring registered stock route. Actual pure validation passed without
booking. One approved real job is pending in100's queue; connected ticks
confirmed100 ACTIVE and44/88 UNKNOWN, all without reservations. The remaining
acceptance is one real timeout, own cleanup/checkpoint and tail requeue after
confirmed FREE, expected33s/max60s. Host release/completeness is the concrete
blocker; no active development may be exempted or stopped. Infrastructure's
capability check confirms that merely waiting for primary idle cannot resolve
44/88's independent stdio coverage. The actual stdio control-client owners
must supply read-only live-status exports through their existing routes;
infraowner2c owns their observation integration. Details and evidence are in
the fleet follow-up. AutoGram deployment
is independent. The infra-owned watch leak was repaired without a global limit
increase; the earlier ENOSPC note is historical.
