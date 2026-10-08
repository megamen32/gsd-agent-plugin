#!/usr/bin/env python3
"""Build the portable GSD Agent Plugin from an isolated upstream install."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from emit_opencode import emit


ADAPTER_MARKER = "<gsd_agent_plugin_adapter>"
ADAPTER = """<gsd_agent_plugin_adapter>
This GSD distribution is loaded from an Agent Plugin rather than a fixed runtime home.

- Resolve `GSD_PLUGIN_ROOT` as the absolute directory two levels above this `SKILL.md`.
- Resolve every `@../../...` execution-context reference relative to this skill directory.
- Before running a workflow shell command, replace `gsd-sdk` with
  `node \"$GSD_PLUGIN_ROOT/bin/gsd-sdk.js\"` and turn any `../../get-shit-done/...`
  command path into an absolute path below `$GSD_PLUGIN_ROOT`.
- Named GSD agent prompts live in `$GSD_PLUGIN_ROOT/agents/`. If the runtime has no
  matching registered agent type, spawn an available generic worker/default agent and
  include the corresponding `agents/<name>.md` prompt in its task message.
</gsd_agent_plugin_adapter>

"""

SECURITY_AUTHORIZATION_MARKER = "<megamen32_gsd_security_authorization>"
SECURITY_AUTHORIZATION = """<megamen32_gsd_security_authorization>
Security-related changes require direct, current user consent. Do not create,
apply, auto-fix, deploy, or expand security controls merely because execution,
review, audit, planning, or verification discovers a security concern.

Without that consent:
- report the finding and the proposed change, but do not modify code, config,
  infrastructure, runtime state, or planning artifacts as if the change were approved;
- do not treat security work as a Rule 1-3 deviation or other automatic fix;
- mark security work blocked pending user approval and continue only independent,
  non-security work that remains in scope.

General permission to fix, finish, run autonomously, or fix what you find is not
security consent. Consent must identify or clearly encompass the security change,
including approval of a plan that names it. An explicit security request such as
fixing a named vulnerability, adding auth, hardening a named surface, or invoking a
security-specific workflow counts only for that stated scope. Generic review `--fix`
or autonomous flags do not. Propagate this rule to spawned agents and downstream plans.
</megamen32_gsd_security_authorization>

"""

OVERLAY_MARKER = "<megamen32_gsd_acceptance_overlay>"
BUSINESS_MARKER = "<megamen32_gsd_business_supervisor>"
BUSINESS_WRAPPER = """<megamen32_gsd_business_supervisor>
At workflow entry, anchor the user's requested outcome and its shortest real
consumer canary in existing context. Before CHOOSING a support-only detour
(hash packets, coordination, admission, unsolicited security expansion), run the
business supervisor, before spending another action on that detour.
Before reporting hashes/SHA, packets, receipts,
coordination, admission, or security work while that outcome remains unproven,
automatically run the business supervisor. Also run it after two consecutive
support-only steps without progress toward the outcome, or before ending with
any turn-ending response while authorized task work remains. Do not wait for
user invocation or a "continue" message.

@../../get-shit-done/workflows/business-supervisor.md

The supervisor selects ONE next action; execute it in this same turn, then resume
the real GSD workflow. Do not turn supervision into another report/review loop.
Do not end the turn with a checkpoint, partial result, or offer to continue when
the next authorized action is feasible. End only on the proven requested outcome,
an explicit user stop/pause, or a concrete blocker with no useful authorized work.
Keep technical provenance internal unless the user requested it. A genuine
authorization/resource blocker stays binding; invented gates and unsolicited
security expansion do not become the task. Propagate these triggers to delegated
GSD workers; only the lead launches the supervisor, never recursively.
</megamen32_gsd_business_supervisor>

"""
# Informational commands do not execute a delivery task. The supervisor must
# never supervise itself; every other upstream/new workflow gets the wrapper.
BUSINESS_EXCLUDED_SKILLS = {
    "gsd-business-supervisor", "gsd-help", "gsd-settings", "gsd-set-profile",
    "gsd-stats", "gsd-whats-new",
}
COMPLETION_SKILLS = {
    "gsd-audit-fix",
    "gsd-autonomous",
    "gsd-complete-milestone",
    "gsd-execute-phase",
    "gsd-fast",
    "gsd-quick",
    "gsd-ship",
    "gsd-verify-work",
}
COMPLETION_GATE = """<megamen32_gsd_acceptance_overlay>
Before this completion-capable workflow reports success, execute the personal
acceptance overlay:

@../../get-shit-done/workflows/acceptance-gate.md

Unit tests, build output, logs, and GSD verification artifacts support this gate
but do not replace its final real-surface canary. If the gate returns
`CHANGES_REQUIRED`, repair the defect and repeat the affected real journey. If
it returns `BLOCKED_REAL_SURFACE`, report that boundary instead of claiming the
user-facing result complete.
</megamen32_gsd_acceptance_overlay>

"""


def replace_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def apply_personal_overlay(output: Path, overlay_root: Path) -> None:
    """Copy additive files that must survive every upstream refresh."""
    for relative in (
        Path("skills/gsd-acceptance-gate"),
        Path("get-shit-done/workflows/acceptance-gate.md"),
        Path("skills/gsd-business-supervisor"),
        Path("get-shit-done/workflows/business-supervisor.md"),
        Path("agents/gsd-business-supervisor.md"),
    ):
        src = overlay_root / relative
        dst = output / relative
        if src.is_dir():
            replace_tree(src, dst)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def normalize_generated_references(output: Path, source_prefix: str) -> None:
    """Remove the isolated install root from bundled prompts and workflows."""
    for directory in (output / "agents", output / "get-shit-done"):
        for path in directory.rglob("*"):
            if not path.is_file():
                continue
            try:
                text = path.read_text()
            except UnicodeDecodeError:
                continue
            if source_prefix in text:
                path.write_text(text.replace(source_prefix, "$GSD_PLUGIN_ROOT"))


def apply_sdk_lazy_query_overlay(output: Path) -> None:
    """Keep read-only SDK queries usable in git marketplace caches.

    Upstream CLI imports the optional Claude execution runtime eagerly. Codex
    git marketplace checkouts do not run npm install, so even a read-only query
    fails before dispatch. The personal distribution loads that runtime only
    after the query fast path has returned.
    """
    path = output / "sdk/dist/cli.js"
    text = path.read_text()
    if "async function loadExecutionRuntime()" in text:
        return
    static_imports = (
        "import { GSD } from './index.js';\n",
        "import { CLITransport } from './cli-transport.js';\n",
        "import { WSTransport } from './ws-transport.js';\n",
        "import { InitRunner } from './init-runner.js';\n",
        "import { loadConfig } from './config.js';\n",
        "import { assertRuntimeSupportsAutoMode } from './runtime-gate.js';\n",
    )
    missing_imports = [line.strip() for line in static_imports if line not in text]
    if missing_imports:
        raise RuntimeError(
            "upstream SDK import shape changed; lazy-query overlay needs review: "
            + ", ".join(missing_imports)
        )
    for static_import in static_imports:
        text = text.replace(static_import, "", 1)
    query_import = "import { runQueryCliCommand } from './query/query-cli-adapter.js';\n"
    lazy_runtime = """// Query commands are the workflow-facing API used by Codex skills. Keep their
// dependency graph independent of the optional Claude execution SDK so a git
// marketplace cache can answer project-state queries without an npm install.
let executionRuntime;
async function loadExecutionRuntime() {
    executionRuntime ??= Promise.all([
        import('./index.js'),
        import('./cli-transport.js'),
        import('./ws-transport.js'),
        import('./init-runner.js'),
        import('./config.js'),
        import('./runtime-gate.js'),
    ]).then(([sdk, cliTransport, wsTransport, initRunner, config, runtimeGate]) => ({
        GSD: sdk.GSD,
        CLITransport: cliTransport.CLITransport,
        WSTransport: wsTransport.WSTransport,
        InitRunner: initRunner.InitRunner,
        loadConfig: config.loadConfig,
        assertRuntimeSupportsAutoMode: runtimeGate.assertRuntimeSupportsAutoMode,
    }));
    return executionRuntime;
}
"""
    if query_import not in text:
        raise RuntimeError("upstream SDK query import changed; lazy-query overlay needs review")
    text = text.replace(query_import, query_import + lazy_runtime, 1)
    fallback = "    // Fall back to GSD_WORKSTREAM env var when --ws is not supplied (#2791)."
    if fallback not in text:
        raise RuntimeError("upstream SDK query boundary changed; lazy-query overlay needs review")
    text = text.replace(
        fallback,
        "    const { GSD, CLITransport, WSTransport, InitRunner, loadConfig, "
        "assertRuntimeSupportsAutoMode } = await loadExecutionRuntime();\n" + fallback,
        1,
    )
    path.write_text(text)


def inject_after_frontmatter(text: str, block: str, marker: str, path: Path) -> str:
    """Replace or insert one generated policy block after YAML frontmatter."""
    if marker in text:
        return re.sub(
            rf"{re.escape(marker)}.*?</{re.escape(marker[1:])}\n*",
            block,
            text,
            count=1,
            flags=re.DOTALL,
        )
    terminator = text.find("---", 4)
    if terminator < 0:
        raise SystemExit(f"missing frontmatter terminator: {path}")
    insert_at = terminator + 3
    return text[:insert_at] + "\n\n" + block + text[insert_at:].lstrip("\n")


def inject_runtime_adapters(output: Path, source_prefix: str) -> None:
    """Inject portable runtime and authorization policies idempotently."""
    for skill_file in sorted((output / "skills").glob("*/SKILL.md")):
        text = skill_file.read_text()
        text = text.replace(source_prefix, "../..") if source_prefix else text
        text = inject_after_frontmatter(text, ADAPTER, ADAPTER_MARKER, skill_file)
        text = inject_after_frontmatter(
            text, SECURITY_AUTHORIZATION, SECURITY_AUTHORIZATION_MARKER, skill_file
        )
        if skill_file.parent.name in COMPLETION_SKILLS:
            if OVERLAY_MARKER in text:
                text = re.sub(
                    r"<megamen32_gsd_acceptance_overlay>.*?</megamen32_gsd_acceptance_overlay>\n*",
                    COMPLETION_GATE,
                    text,
                    count=1,
                    flags=re.DOTALL,
                )
            else:
                text = inject_after_frontmatter(text, COMPLETION_GATE, OVERLAY_MARKER, skill_file)
        if skill_file.parent.name not in BUSINESS_EXCLUDED_SKILLS:
            text = inject_after_frontmatter(
                text, BUSINESS_WRAPPER, BUSINESS_MARKER, skill_file
            )
        skill_file.write_text(text)

    for agent_file in sorted((output / "agents").glob("*.md")):
        text = inject_after_frontmatter(
            agent_file.read_text(),
            SECURITY_AUTHORIZATION,
            SECURITY_AUTHORIZATION_MARKER,
            agent_file,
        )
        agent_file.write_text(text)

    for agent_file in sorted((output / "agents").glob("*.toml")):
        text = agent_file.read_text()
        if SECURITY_AUTHORIZATION_MARKER in text:
            text = re.sub(
                rf"{re.escape(SECURITY_AUTHORIZATION_MARKER)}.*?</{re.escape(SECURITY_AUTHORIZATION_MARKER[1:])}\n*",
                SECURITY_AUTHORIZATION,
                text,
                count=1,
                flags=re.DOTALL,
            )
        else:
            boundary = "developer_instructions = '''\n"
            if boundary not in text:
                raise SystemExit(f"missing developer_instructions boundary: {agent_file}")
            text = text.replace(boundary, boundary + SECURITY_AUTHORIZATION, 1)
        agent_file.write_text(text)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--projection", type=Path, required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--source-prefix", required=True)
    args = parser.parse_args()

    version_file = args.projection / "VERSION"
    if not version_file.exists():
        version_file = args.projection / "get-shit-done" / "VERSION"
    version = version_file.read_text().strip()
    package_meta = json.loads((args.package / "package.json").read_text())
    if package_meta.get("version") != version:
        raise SystemExit(f"version mismatch: projection={version} package={package_meta.get('version')}")

    for name in ("skills", "get-shit-done", "agents"):
        replace_tree(args.projection / name, args.output / name)
    replace_tree(args.package / "sdk" / "dist", args.output / "sdk" / "dist")
    replace_tree(args.package / "sdk" / "shared", args.output / "sdk" / "shared")
    replace_tree(args.package / "sdk" / "prompts", args.output / "sdk" / "prompts")
    replace_tree(args.package / "node_modules", args.output / "node_modules")
    shutil.copy2(args.package / "sdk" / "package.json", args.output / "sdk" / "package.json")
    shutil.copy2(args.package / "package-lock.json", args.output / "package-lock.upstream.json")
    (args.output / "bin").mkdir(parents=True, exist_ok=True)
    shutil.copy2(args.package / "bin" / "gsd-sdk.js", args.output / "bin" / "gsd-sdk.js")
    shutil.copy2(args.package / "LICENSE", args.output / "LICENSE.upstream")

    normalize_generated_references(args.output, args.source_prefix)
    # Upstream's Codex installer writes its resolved --config-dir into TOML
    # agent prompts. The isolated projection lives under a random .tmp path,
    # so normalize that concrete path as well as the portable source prefix.
    normalize_generated_references(args.output, str(args.projection))
    apply_sdk_lazy_query_overlay(args.output)
    overlay_root = Path(__file__).resolve().parents[1] / "overlay"
    apply_personal_overlay(args.output, overlay_root)
    inject_runtime_adapters(args.output, args.source_prefix)

    (args.output / "VERSION").write_text(version + "\n")
    emit(
        args.output,
        package_name="@megamen32/gsd-opencode-plugin",
        includes=[
            "agents",
            "bin",
            "get-shit-done",
            "sdk",
            "README.md",
            "UPSTREAM.json",
            "VERSION",
            "LICENSE.upstream",
            "overlay",
        ],
        dependencies_from=args.package / "sdk/package.json",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
