#!/usr/bin/env python3
"""Verify GSD across native Agent Plugin hosts and OpenCode's adapter."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


def run(*argv: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, capture_output=True, text=True, timeout=45)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plugin-root", type=Path, required=True)
    args = parser.parse_args()
    root = args.plugin_root.expanduser().resolve()
    home = Path.home()
    report: dict[str, object] = {"pluginRoot": str(root)}
    failures: list[str] = []

    expected_skills = len(list((root / "skills").glob("*/SKILL.md")))
    codex = run("codex", "plugin", "list")
    gsd_line = next(
        (x for x in codex.stdout.splitlines() if x.startswith("gsd@megamen32-public")),
        "",
    )
    report["codex"] = {"gsd": gsd_line}
    if "installed, enabled" not in gsd_line:
        failures.append("codex registration")
    if expected_skills < 1:
        failures.append("plugin skill count")
    if run("node", str(root / "bin/gsd-sdk.js"), "--help").returncode:
        failures.append("bundled SDK")

    opencode_cfg = home / ".config/opencode/opencode.json"
    if opencode_cfg.exists():
        cfg = json.loads(opencode_cfg.read_text())
        paths = cfg.get("skills", {}).get("paths", [])
        plugins = cfg.get("plugin", [])
        config_ok = (
            str(root / "skills") in paths
            and str(root / "opencode-plugin/index.js") in plugins
        )
        try:
            with tempfile.TemporaryFile(mode="w+") as output:
                skill_result = subprocess.run(
                    ["opencode", "debug", "skill"],
                    stdout=output,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=45,
                )
                output.seek(0)
                skill_data = json.load(output)
            if skill_result.returncode:
                raise RuntimeError(skill_result.stderr)
            gsd_count = sum(str(item.get("name", "")).startswith("gsd-") for item in skill_data)
        except Exception:
            gsd_count = -1
        report["opencode"] = {"configured": config_ok, "gsdSkills": gsd_count}
        if not config_ok or gsd_count != expected_skills:
            failures.append("opencode loader")
    else:
        report["opencode"] = {"configured": False}
        failures.append("opencode config missing")

    zcode_cli = shutil.which("zcode")
    zcode_report: dict[str, object] = {"cli": zcode_cli or "absent"}
    if zcode_cli:
        try:
            plugin_data = json.loads(run(zcode_cli, "plugins", "list", "--json").stdout)
            native = next(
                item
                for item in plugin_data
                if item.get("id") == "gsd@megamen32-public-claude"
            )
            skill_data = json.loads(run(zcode_cli, "skills", "list", "--json").stdout)
            skill_names = {
                item.get("name") for item in skill_data.get("skills", [])
            }
            loader_ok = (
                native.get("enabled") is True
                and native.get("source") == "cache"
                and native.get("skillCount") == expected_skills
                and "gsd-acceptance-gate" in skill_names
            )
        except (json.JSONDecodeError, StopIteration, TypeError):
            loader_ok = False
        zcode_report["nativePlugin"] = loader_ok
        if not loader_ok:
            failures.append("zcode loader")
    report["zcode"] = zcode_report
    report["expectedSkills"] = expected_skills
    report["failures"] = failures
    print(json.dumps(report, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
