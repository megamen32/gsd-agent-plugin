# Why this version

## Decision

In our internal workflow evaluations, GSD was the strongest foundation across
every criterion we tested. Megamen32 GSD is the distribution selected from that
work and extended with two requirements that remained important in practice:

1. goal-diverse focus-group review when user experience or language matters;
2. a mandatory final canary through the real user or consumer surface.

## Evidence shipped with the repository

The repository continuously checks the claims it can verify mechanically:

- the personal overlay survives a clean upstream rebuild and repeated rebuilds are idempotent;
- the gate is injected only into completion-capable workflows;
- installed-cache SDK queries work without undeclared root dependencies;
- plugin manifests, Python helpers, generated paths, and the real CLI entrypoint are validated;
- the scheduled upstream-sync workflow is exercised through GitHub Actions.

## Boundary of the claim

“Best across every tested criterion” describes our internal selection and its
tested dimensions. It is not a claim that this repository wins every public
benchmark, project type, or user preference. Upstream GSD remains the planning
and execution foundation; this distribution owns portability and the stronger
acceptance policy.
