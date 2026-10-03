# Personal GSD acceptance overlay

This overlay is the final gate for completion-capable GSD workflows. It is
additive: upstream GSD continues to own planning, execution, verification, and
UAT. This gate closes the stronger claim that the result actually works for a
user or real consumer.

## 1. Freeze the candidate

Run this only after implementation, review, applicable tests, migrations,
deployment, and every intentional restart are complete. Record the tested
revision and surface. Once the final canary starts, do not change code, config,
or runtime that can affect it until its result is captured. A failed canary
starts a repair cycle followed by a fresh final canary.

## 2. Decide whether a focus group adds evidence

Run a focus-group pass when the result has user-facing UX, onboarding,
discoverability, language/content, multiple plausible goals or conditions, or
when the user requested it. Skip it for purely internal changes where personas
cannot reveal a distinct failure mode.

Prefer an installed focus-group capability. Otherwise use independent fresh
sessions only when the active harness permits them. Give each participant a
distinct realistic goal or constraint, a stable product revision, isolated
state when needed, and no implementation hints. Do not prescribe the click
path in a discoverability test. Synthetic participants are simulated readers,
not human market research.

Collect observed attempts and evidence, consolidate duplicate root obstacles,
separate tool failures from product defects, repair material in-scope failures,
and repeat the affected journey with a fresh attempt. Direct observation
outranks persona opinions or a count of green reports.

## 3. Run the shortest real-surface canary

Choose the actual surface of the accepted claim:

- Web UI: use a visible browser/computer-use session against the real deployed
  URL and intended authenticated state. Prefer accessibility snapshots and
  semantic element targeting; use browser MCP/CDP/Playwright when needed, and
  verified coordinate clicks only as a last resort.
- Desktop application: use the intended operating system and real application
  UI, not an HTTP health endpoint standing in for it.
- Mobile/native: use the real device and its semantic control interface when
  available; inspect, act once, and verify the settled state.
- CLI/API/service: execute the real consumer command or request and verify the
  resulting business state, not only exit code, listener, or HTTP 200.
- External delivery or payment: use the established sandbox/test destination.
  Do not contact unrelated people or spend money without the authority already
  present in the task.

When the journey includes a notification, alarm, incident page, or phone call,
verify that a human can understand it immediately: what happened, why it
matters, the current status, and any required action. Use natural Russian by
default unless the user explicitly requested another language. Do not present
raw event names, thresholds, identifiers, English diagnostics, or machine
payloads as the main user-facing message; TTS must sound like spoken language.

After every navigation or state change, refresh the snapshot before the next
action. Confirm decisive actions from observed state rather than tool success.
On a browser/UI error, timeout, or ambiguity, capture and inspect a secret-safe
screenshot before retrying or cleaning up.

## 4. Evidence and verdict

Before recording evidence, enforce the repository completion invariant for
every Git repository changed by the cycle:

- relevant tests and checks are green, plus the real-surface canary required by
  the accepted claim;
- task-owned work is committed on the default branch (normally `main`) and
  pushed to the authoritative remote;
- after fetching, the authoritative checkout is clean and `HEAD` equals
  `origin/main`, with no ahead/behind/divergence;
- no task work remains in a stash, temporary branch, or secondary worktree;
  task-created branches/worktrees are removed only after proving their commits
  are reachable from remote `main`;
- every other machine or checkout explicitly included in the cycle is clean
  and synchronized to the same remote-main commit.

Never reset, overwrite, silently rebase, stash away, or delete unrelated or
unmerged user work to manufacture a pass. If preserved unrelated work prevents
the invariant, return `BLOCKED_REPOSITORY_STATE` and name the exact boundary.

Record the exact journey, expected and observed result, tested revision, and a
claim-matching artifact: decisive screenshot/reference for UI, or exact command
plus resulting state for nonvisual consumers. Add it to the active GSD UAT or
verification artifact when one exists; otherwise include it in the workflow's
completion evidence.

Return one verdict:

- `PASS`: the accepted journey succeeds on the real surface.
- `CHANGES_REQUIRED`: a reproducible in-scope defect or material usability
  obstacle remains. Repair it and rerun the affected journey.
- `BLOCKED_REAL_SURFACE`: the required account, device, deployment, or control
  surface is genuinely unavailable. State the exact missing boundary; do not
  replace it with simulated success or downgrade the claim silently.
- `BLOCKED_REPOSITORY_STATE`: the repository cannot safely reach clean, green,
  pushed, synchronized remote `main` without user authority or risking
  unrelated/unmerged work. State the exact checkout and obstruction.

Do not broaden the accepted Definition of Done during acceptance testing.
