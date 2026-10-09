#!/usr/bin/env python3
"""Wire this portable Agent Plugin into OpenCode's compatibility layer."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    text = path.read_text()
    if path.suffix == ".jsonc":
        # Preserve quoted comment-like strings while accepting native JSONC.
        token = r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*[\s\S]*?\*/'
        text = re.sub(token, lambda m: m.group() if m.group().startswith('"') else ' ', text)
        text = re.sub(r'"(?:\\.|[^"\\])*"|,\s*(?=[}\]])',
                      lambda m: m.group() if m.group().startswith('"') else '', text)
    data = json.loads(text)
    if not isinstance(data, dict):
        raise SystemExit(f"expected a JSON object: {path}")
    return data


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(path)


def backup(path: Path, backup_root: Path, home: Path) -> str | None:
    if not path.exists():
        return None
    try:
        relative = path.relative_to(home)
    except ValueError:
        relative = Path(path.name)
    target = backup_root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)
    return str(target)


def opencode_path(home: Path) -> Path:
    directory = home / ".config/opencode"
    # OpenCode loads JSONC after JSON; its arrays override the JSON layer.
    return directory / ("opencode.jsonc" if (directory / "opencode.jsonc").exists() else "opencode.json")


def configure_opencode(plugin_root: Path, home: Path) -> Path:
    path = opencode_path(home)
    data = load_json(path)
    shim = str(plugin_root / "opencode-plugin" / "index.js")
    plugins = [
        value
        for value in data.get("plugin", [])
        if value == shim
        or not (
            "last-human-commit" in str(value)
            or "/lhc-" in str(value)
            or "/gsd/" in str(value)
            or "/gsd-agent-plugin/" in str(value)
            or "@megamen32/gsd-opencode-plugin" in str(value)
        )
    ]
    if shim not in plugins:
        plugins.append(shim)
    data["plugin"] = plugins

    skills = data.get("skills", {})
    if not isinstance(skills, dict):
        raise SystemExit(f"expected skills to be a JSON object: {path}")
    skill_path = str(plugin_root / "skills")
    paths = [value for value in skills.get("paths", [])
             if "/gsd/" not in str(value) and "/gsd-agent-plugin/" not in str(value)]
    if skill_path not in paths:
        paths.append(skill_path)
    skills["paths"] = paths
    data["skills"] = skills
    # Supported instruction bootstrap also covers hosts whose experimental
    # system transform hook is unavailable. One marked policy, same upstream route.
    bootstrap = home / ".config/opencode/ogsd-bootstrap.md"
    if (plugin_root / "hooks/autoentry.md").exists():
        bootstrap.parent.mkdir(parents=True, exist_ok=True)
        bootstrap.write_text("GSD_PLUGIN_ROOT=" + str(plugin_root) + "\n" +
                             (plugin_root / "hooks/autoentry.md").read_text())
        instructions = data.setdefault("instructions", [])
        if str(bootstrap) not in instructions:
            instructions.append(str(bootstrap))
    write_json(path, data)
    return path


def configure_codex_bootstrap(plugin_root: Path, home: Path) -> Path:
    # Supported user AGENTS bootstrap works even when plugin hooks await trust.
    # Only this marked block is owned; all existing instructions are preserved.
    path = home / ".codex/AGENTS.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    text = path.read_text() if path.exists() else ""
    block = ("<!-- ogsd-autoentry:begin -->\n" + "GSD_PLUGIN_ROOT=" + str(plugin_root)
             + "\n" + (plugin_root / "hooks/autoentry.md").read_text()
             + "<!-- ogsd-autoentry:end -->\n")
    pattern = r"<!-- ogsd-autoentry:begin -->.*?<!-- ogsd-autoentry:end -->\n?"
    text = re.sub(pattern, lambda _: block, text, flags=re.DOTALL) if "<!-- ogsd-autoentry:begin -->" in text else text.rstrip() + "\n\n" + block
    path.write_text(text)
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--plugin-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Stable checkout path (defaults to this repository).",
    )
    parser.add_argument("--runtime", choices=("opencode", "codex"), default="opencode")
    parser.add_argument("--backup-root", type=Path)
    args = parser.parse_args()

    plugin_root = args.plugin_root.expanduser().resolve()
    if not (plugin_root / "plugin.json").is_file():
        raise SystemExit(f"invalid plugin root: {plugin_root}")
    if not (plugin_root / "skills").is_dir():
        raise SystemExit(f"missing skills directory: {plugin_root / 'skills'}")

    home = Path.home()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_root = (
        args.backup_root or home / ".local" / "state" / "gsd-agent-plugin" / stamp
    ).expanduser()
    selected = [args.runtime]
    paths = {"opencode": opencode_path(home),
             "codex": home / ".codex/AGENTS.md"}
    backup(home / ".config/opencode/ogsd-bootstrap.md", backup_root, home)
    backups = {
        runtime: saved
        for runtime in selected
        if (saved := backup(paths[runtime], backup_root, home)) is not None
    }

    if args.runtime == "opencode":
        configure_opencode(plugin_root, home)
    else:
        configure_codex_bootstrap(plugin_root, home)
    configured = [args.runtime]

    print(
        json.dumps(
            {
                "pluginRoot": str(plugin_root),
                "configured": configured,
                "backups": backups,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
