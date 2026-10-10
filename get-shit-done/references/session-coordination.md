# Coordination is an execution responsibility

Use this policy when accepting a coordinator role, delegating or arranging
parallel sessions. Apply its communication rules to every GSD user update.
Current explicit user instructions and project ownership constraints take precedence.

## One lead, actual executors, one outcome

- Identify the existing lead and join that arrangement; never appoint a competing
  coordinator or supervisor. Accepting the coordinator role means organizing
  execution, removing blockers, integrating results and verifying the outcome.
  Merely forwarding messages is not coordination.
- Reuse one task list: goal, actual executor, owned files, checkout, resource or
  service boundary, verified result and next action. Do not add another planner,
  approval queue or packet registry.
- Assign the goal, ownership, accepted downtime, resources and authority once.
  Executors continue through the authorized result; no expiring micro-permissions
  or repeated ACKs. Product code belongs to its named executor on the actual host.
- The coordinator owns sequencing, real conflicts and integration. Independent
  reviewers inspect evidence; they do not become extra writers or leads.
- Compatible work proceeds in parallel. Resolve a concrete conflict at its owner;
  never interrupt unrelated work merely to make the coordinator's work easier.

## Decide who needs a Git worktree

Before adding a writer, and whenever ownership, dependencies or shared resources
change, reassess the checkout arrangement during normal work, without another
periodic watcher or planning ceremony.

- A worktree is a separate Git working tree of the SAME repository, not another
  chat, independent clone or directory copy. Inspect existing trees first.
- Read-only research, review and consumer inspection normally share accepted
  source. Disjoint small edits may share the canonical checkout when file
  ownership and Git index operations are coordinated.
- Concurrent writers that can collide in files, the index, dependency setup or
  generated output need separate owned worktrees, or explicit serialization of
  the conflicting operation. Neither one shared tree for everybody nor one new
  worktree per session is a default answer.
- When isolation is needed and authorized, the coordinator provisions/reuses the
  worktree and assigns its executor, base, files, integration owner and lifecycle.
  Preserve the primary checkout and foreign WIP. User-granted worktree authority
  lasts throughout its scope; never ask again for the same permission. Respect
  narrower current instructions forbidding new trees or requiring one checkout.
- Worktrees isolate source, not databases, Telegram sessions, browsers, devices,
  builders, deployments or leases. Assign shared resource boundaries separately;
  multiple trees do not authorize concurrent use of one protected resource.
- Integrate only owned reviewed changes into the agreed mainline, run relevant
  checks and actual consumer acceptance, preserve unique history/private work,
  then retire released trees after runtime/process references close normally.
  Never reset, stash, force-delete or kill foreign holders to manufacture clean state.
- If the user's goal is one canonical checkout, consolidation belongs to the
  coordinator. Do not leave completed work scattered across temporary trees or
  create replacement copies to evade a lifecycle defect.

## Decide who is actually interfering

An active or dirty session, another harness or a different approach is not
itself interference. Locate the actual intersection: a shared file/index
operation, planned restart, protected client/device, builder or live reservation.
Use current capacity/pressure evidence, not an old reservation or PSI alone.

Give the owner one concrete resolution: split files, isolate source, serialize
that shared operation or fix its runner/lifecycle seam. Preserve foreign WIP,
data, leases and completed actions. Repeated identical runner refusals are a
repair task for ONE owner, not another committee, global sole slot, fake executor
identity or external-action replay.

## Messages must change the next action

Send only an ownership assignment, needed decision, verified new error,
resource/context handoff or accepted result with an evidence link. No ACKs,
unchanged statuses, duplicate relays or repeated-permission loops. Use a
maintained direct route after checking an active turn; queue only to an actually
inactive session, with stable deduplication. Unknown delivery/outcome never
authorizes external-action replay or automatic resume of stopped/user-paused work.

Proceed without another acknowledgement when authority and inputs suffice.
A handoff gives an owner a usable route and scope; repeated packets do not finish it.

## Human updates explain results and remaining work

Do not include hashes, SHAs, receipt IDs or machine packets in normal user
updates, before OR after successful source delivery. Keep technical provenance
in evidence and provide it only on the user's request or when an exact identifier
is necessary to act on a concrete error.

Explain plainly what works, what still does not, who owns the remaining step,
what actually blocks it, and the measured or honestly estimated time. Tests,
source publication, prepared images, admitted waits and acknowledgements are
not the final business result. A legitimate finite wait with an installed
continuation remains pending; do useful compatible work instead of generating
coordination traffic or waking an executor merely to show activity.
