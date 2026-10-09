# OGSD fleet delivery — 2026-10-09

Installed runtime adapter revision on all four hosts:
**4f603b40b93da5025b42336db40cf88725d27cc3**.
Upstream plugin version remains 1.42.3. Source owner: the existing GSD Codex
session 01a12172-d34e-7702-8f0d-a804ead3c0b9 on server-100.

| Host | Supported route and delivered result | Preservation / entry evidence |
|---|---|---|
| 100 | Native Codex plugin installer; patched GSD runtime installer | Existing successful Codex/OpenCode consumers reused. Earliest installer JSONC backup mode0640 versus current0664 proved the permission defect; restored0640. No foreign plugin record was missing. Both config bodies remain byte-for-byte unchanged after repair and patched installation. |
| 44 | Native gsd@megamen32-public installer, then installed Codex/OpenCode bootstrap installer | Revision4f603b4; original SessionStart route returned; one Codex bootstrap; OpenCode plugin/skills/instructions point to installed payload. All foreign config values and original modes preserved. |
| 88 | Same installer; restored only registration of the already cached public Git marketplace | Revision4f603b4; JSON and active JSONC foreign values/modes preserved; one Codex bootstrap; both native entry routes present. Other marketplace/plugin entries retained. |
| Mac M1 | Native installer over the documented server-100 reverse SSH route | MacBook-Pro-User / MacBookPro18,2 / arm64 verified. Revision4f603b4; Codex0.160.0 and OpenCode1.18.11 installed bootstrap/config/hook checks passed. Foreign values/modes preserved. |

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
| Actual installed standard manifest | Validate each host's public manifest against official Agent Plugins1.0 schema | focused integration | 2 / 30 total |
| Pure registered enduring case | Detect dropped profile, numeric-budget drift or stale job pin without booking | focused integration | 1 / 5 |
| Connected queued active/unknown tick | Keep pending work unreserved when native activity is active or incompletely observed | focused integration | 2 / 12 per host |
| One owned native window | Catch process/reservation leak, foreign stop, lost checkpoint or wrong tail ordering | slow nightly | 33 / 60 |

The latest combined source release passed **48 checks in16.418s**. Remote hook/config
checks passed on all three newly delivered hosts. This is installed
bootstrap/config proof; a new model consumer was deliberately not started.

## Remaining native nightly acceptance

The exact job request and payload were delivered into infraowner2c's verified
active native turn, with an admission receipt. Requested wall30s/window40s,
RAM256/512MiB, CPU1/tasks64/temp16MiB/256files/IO10, host reserve20GiB.
The payload writes only its own TMPDIR checkpoint and intentionally exceeds
the window. Expected result: non-GREEN timeout, stock same-generation owned
cleanup/reservation removal, retained checkpoint, unfinished job at queue tail.

Infrastructure published the100-only registered profile gsd-nightly-window100
at8064174 and the enduring authorized case. The adapter now retains _profile
at helper.budget and uses only stock run_authorized_case(case_path,0), keeping
the numeric job budget unchanged. Actual pure stock validation accepted this
case; it created no scope, reservation or payload. The approved job
ogsd-native-window-20261009 is pending in100's existing host-local queue.

The installed adapter was connected to the existing infra-owned per-host
native observer. Actual connected ticks returned100 SKIP_ACTIVE,44
DEFER_UNKNOWN and88 DEFER_UNKNOWN, all reservation_created=false. The queued
100 job stayed pending with running=null. In this fresh44 observation the
primary session was idle, but OpenCode/independent native coverage was incomplete;
the earlier ACTIVE observation does not imply FREE now.88 coverage was also
incomplete. No development session was excluded as an executor.

Native cleanup acceptance remains open until one real cycle runs on confirmed
FREE through that existing route. The remaining run is expected33s/max60s
after FREE becomes available; no honest wall-clock ETA exists for host release.
Infraowner2c/R38 own observation completeness and the infrastructure profile;
their helper/runtime/infra paths were not changed by GSD. No portable44/88
runner profile, new scheduler, service or daemon was introduced. Nightly does
not block AutoGram deployment.

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
errors against the retrieved official schema, including the actual installed
public manifest on each of100/44/88/Mac. New regression coverage keeps
future metadata updates in the valid extension location.

Final private evidence under .tmp/ogsd/fleet-delivery/ includes per-host
final-verified.json and final-public-manifest.json, final-fleet-schema-validation.json,
actual-pure-registered-receipt.json and queued-native-active-deferral.json.
These are installed/configuration and admission-policy results, not a claim
that the deferred native timeout/cleanup cycle has executed.
