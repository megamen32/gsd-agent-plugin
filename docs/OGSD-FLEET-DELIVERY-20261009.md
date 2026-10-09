# OGSD fleet delivery — 2026-10-09

Runtime adapter revision: **09a1584c45e9947e3ae44b8a865117bf2fd5746b**.
Upstream plugin version remains 1.42.3. Source owner: the existing GSD Codex
session 01a12172-d34e-7702-8f0d-a804ead3c0b9 on server-100.

| Host | Supported route and delivered result | Preservation / entry evidence |
|---|---|---|
| 100 | Native Codex plugin installer; patched GSD runtime installer | Existing successful Codex/OpenCode consumers reused. Earliest installer JSONC backup mode0640 versus current0664 proved the permission defect; restored0640. No foreign plugin record was missing. Both config bodies remain byte-for-byte unchanged after repair and patched installation. |
| 44 | Native gsd@megamen32-public installer, then installed Codex/OpenCode bootstrap installer | Revision09a1584; original SessionStart route returned; one Codex bootstrap; OpenCode plugin/skills/instructions point to installed payload. All foreign config values and original modes preserved. |
| 88 | Same installer; restored only registration of the already cached public Git marketplace | Revision09a1584; JSON and active JSONC foreign values/modes preserved; one Codex bootstrap; both native entry routes present. Other marketplace/plugin entries retained. |
| Mac M1 | Native installer over the documented server-100 reverse SSH route | MacBook-Pro-User / MacBookPro18,2 / arm64 verified. Revision09a1584; Codex0.160.0 and OpenCode1.18.11 installed bootstrap/config/hook checks passed. Foreign values/modes preserved. |

The old installer could delete unrelated workflow plugins and change config
permissions during atomic replacement. A failing regression test reproduced
both risks. The corrected installer changes only its own GSD routes, preserves
foreign plugins, and retains the existing file mode. On100, comparison with the
saved backups established that only the JSONC mode required restoration:
the unrelated autoloaded workflow file and all foreign plugin records existed.
No whole-config restore was performed.

No active harness session, service, or model turn was restarted for installation.
Autoentry is prepared for the next engineering session. New model sessions and
the already successful native consumers100 were not replayed during this delivery.

## Verification contract

| Check | Purpose / defect caught | Category | Expected / max seconds |
|---|---|---|---|
| Exact SSH identity and current payload | Prevent wrong-host install and stale-plugin claims | focused integration | 2 / 10 per host |
| Supported plugin installation and bootstrap configuration | Deliver original GSD autoentry without manual skill copying | focused integration | 20 / 180 per host; setup failures are failures |
| Hook/config and foreign-setting comparison | Catch absent entry, duplicate bootstrap, lost settings or changed modes | focused integration | 3 / 15 per host |
| Source release aggregate | Complete declared unit/integration coverage; timeout/incomplete cannot GREEN | fast unit + focused integration | 15 / hard180 total |
| One owned native window | Catch process/reservation leak, foreign stop, lost checkpoint or wrong tail ordering | slow nightly | 33 / 60 |

The combined source release passed **41 checks in13.316s**. Remote hook/config
checks passed on all three newly delivered hosts. This is installed
bootstrap/config proof; a new model consumer was deliberately not started.

## Remaining native nightly acceptance

The exact job request and payload were delivered into infraowner2c's verified
active native turn, with an admission receipt. Requested wall30s/window40s,
RAM256/512MiB, CPU1/tasks64/temp16MiB/256files/IO10, host reserve20GiB.
The payload writes only its own TMPDIR checkpoint and intentionally exceeds
the window. Expected result: non-GREEN timeout, stock same-generation owned
cleanup/reservation removal, retained checkpoint, unfinished job at queue tail.

The current GSD engineering owner100 is not an exempt nightly executor.
Do not book active100. Local18787 absence on44/88 proves no free capacity;
central Herder100 without host filtering is not a free-host observation.
Infraowner2c/R38 own the compatible registered runner profile and enduring
authoritative host-specific native route. Their helper/runtime/infra paths
were not changed by GSD. Native cleanup acceptance remains open until one
real cycle runs on a confirmed free host through that route.

Private preserved receipts: .tmp/ogsd/fleet-delivery/receipt.json.
Per-host backup/verification receipts:
~/.local/state/gsd-agent-plugin/fleet-delivery-20261009/.

## Agent Plugin identity and format follow-up

88 and Mac each have exactly one enabled gsd@megamen32-public, one owned
Codex bootstrap and one OpenCode plugin/bootstrap entry. No separate OGSD
package or duplicate active registration was found. Root independently
confirmed the same single identity on100/44.

Full validation against the published Agent Plugins1.0 schema found inherited
top-level skills/interface fields in39f03598 and current manifest. They now
live under extensions.com.openai, retaining gsd,1.42.3, the same source and
Codex compatibility manifest. The standard JSON Schema validator reports zero
errors against the retrieved official schema. New regression coverage keeps
future metadata updates in the valid extension location.
