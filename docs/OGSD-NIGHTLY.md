# Existing runner integration

The adapter adds a queue, not another execution lifecycle. Invoke it in the
existing host-local native nightly executor through its installed GSD plugin.
It will not launch or stop a development session. Host identity is exact:
100 = roomhacker-server-100, 44 = server-44, 88 = roomhacker-server-88.

```text
python3 scripts/nightly_queue.py enqueue --host 100 --job /absolute/owned/job.json
python3 scripts/nightly_queue.py tick --host 100
python3 scripts/nightly_queue.py status --host 100
```

Use 44 and 88 on those hosts. Their state defaults independently to
`~/.local/state/gsd-agent-plugin/nightly/{100,44,88}`. No global queue lock.
`--own-executor HARNESS SESSION_ID` is only for the exact session running this
nightly executor; never pass a development session as that exemption.

Job fields: stable safe `id`, exact `command` argv, existing `runner_path`
ending in bounded-foreground.py, explicit registered profile, exact numeric
budget, enduring authorized_case_path, absolute temp_root, finite
`window_seconds` (finite, at most one day; stock runner profile validates the actual wall budget), optional `temp_symlinks` and `admission_receipt`.
The existing helper validates budget and admission and enforces native controls.
Budget wall must fit the window. Numeric job JSON stays identical to the registered budget. At the existing
helper budget boundary, the adapter adds internal _profile from job.profile
and validates the exact enduring case. Execution goes exclusively through
run_authorized_case(case_path,0), which creates fresh admission immediately
before payload. Missing/mismatched profile or case is HELD before reservation;
there is no bare-budget path. Stock own-generation cleanup plus absence of
the own capacity ledger row are required before tail requeue.

Results and checkpoints remain under the host queue's `results/`. A failed,
held or timed-out job returns to the tail only after stock owned-cleanup proof
(or proof that no reservation was started). Unknown cleanup keeps `running`
and refuses replay. Recover through the existing lifecycle owner's receipt
and cleanup route; do not delete another job's reservation or stop foreign work.

Retained slow scenario: upstream reconstruction. Run only from clean pinned
GSD inputs, since it replaces generated payload. Expected90s/max120s; overrun
stays TIMEOUT, is owned repair work, and is retained for the next queue window.
The ordinary release covers fast unit and focused integration in <=180s.

Current native dependencies and evidence: [delivery tracker](OGSD-DELIVERY.md).

## Consumer acceptance scenarios

| Scenario | Purpose | Detected defect | Category | Expected / max seconds |
|---|---|---|---|---|
| Fresh Codex engineering session | Read original GSD automatically and verify owned temporary file | Manual entry required, recursive start, or unverified consumer result | slow nightly | 60 / 180 |
| Fresh OpenCode engineering session | Load original GSD through native config and verify temporary file | JSONC override hides plugin/bootstrap or entry route is ignored | slow nightly | 60 / 180 |
| Live busy-host tick | Native Herder active read then skip before reservation | Nightly books a development host | focused integration | 2 / 12 |
| Unknown44/88 tick | Defer when native activity cannot be observed | Unreachable host is falsely marked free | focused integration | 1 / 12 |
| Native window cleanup | Existing runner terminates owned generation, clears own reserve, retains checkpoint, requeues tail | Foreign stop, leaked reservation, replay or false GREEN | slow nightly | profile-specific / finite reviewed profile wall plus stock cleanup |

A scenario that needs a longer window uses an already accepted registered runner
profile. The adapter never raises that profile's resource or wall limits. Fresh
consumer session checks are excluded from the ordinary small-release run because
model/provider startup timing is variable; their retained proof is required for
changes to entry behavior. Native window proof is currently blocked as tracked.

## Existing host-specific observer connection

When the infra owner provides its authoritative native command, use it directly:

~~~text
python3 scripts/nightly_queue.py tick --host 44 --native-observer /absolute/existing/probe --host 44
~~~

The observer is an existing infra-owned route, not a new GSD daemon or MCP.
Place --native-observer last; its remaining arguments are exact argv.
It has a finite12s observation limit with retained private receipt and uses
the existing finite-command cleanup. Failure, timeout, partial/truncated state
or wrong-host data remains UNKNOWN before any reservation.

Its JSON response must include actual host, observed_unix, source, complete
and sessions with harness/id/status. complete=true means complete fresh native
coverage on that host; host names must match the exact local HOSTS mapping.
Never substitute central Herder100's list for44/88 or exclude a development
session as the own nightly executor.


Published profile: gsd-nightly-window100, registered by infrastructure commit
8064174. This is the100 profile only; no portable44/88 profile is implied.
100/44 active and88 incomplete native coverage defer before reservation.
The GSD engineering session is not an executor exemption. The approved native
case remains pending until actual FREE through the enduring observer/runner.
