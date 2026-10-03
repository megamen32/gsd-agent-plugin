#!/usr/bin/env python3
"""Build the portable GSD Agent Plugin from an isolated upstream install."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from emit_opencode import emit


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

OVERLAY_MARKER = "<megamen32_gsd_acceptance_overlay>"
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


def inject_runtime_adapters(output: Path, source_prefix: str) -> None:
    """Inject portable path handling and the completion gate idempotently."""
    for skill_file in sorted((output / "skills").glob("*/SKILL.md")):
        text = skill_file.read_text()
        text = text.replace(source_prefix, "../..") if source_prefix else text
        marker = text.find("---", 4)
        if marker < 0:
            raise SystemExit(f"missing frontmatter terminator: {skill_file}")
        insert_at = marker + 3
        additions = ""
        if "<gsd_agent_plugin_adapter>" not in text:
            additions += ADAPTER
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
                additions += COMPLETION_GATE
        if additions:
            text = text[:insert_at] + "\n\n" + additions + text[insert_at:].lstrip("\n")
        skill_file.write_text(text)


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
