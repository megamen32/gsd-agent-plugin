---
name: "gsd-acceptance-gate"
description: "Close GSD delivery with evidence from the real user surface and, when varied user goals matter, an independent focus-group pass. Use immediately before a completion-capable GSD workflow reports success."
metadata:
  short-description: "Final real-surface and focus-group gate"
---

<objective>
Prove the accepted claim through the shortest real user or consumer journey
after the final implementation, deployment, migration, and intentional restart.
Tests and logs are supporting evidence, not substitutes for this gate.
</objective>

<execution_context>
@../../get-shit-done/workflows/acceptance-gate.md
</execution_context>

<process>
1. Read the acceptance workflow completely.
2. Identify the exact accepted claim, real surface, test identity/data, allowed
   side effects, and stop condition.
3. Run the workflow after the final state-changing operation.
4. Return only `PASS`, `CHANGES_REQUIRED`, `BLOCKED_REAL_SURFACE`, or
   `BLOCKED_REPOSITORY_STATE`, with the journey and evidence required by the
   workflow. `PASS` is forbidden until every changed repository is clean,
   green, pushed, and synchronized on its remote default branch.
</process>
