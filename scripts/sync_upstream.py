#!/usr/bin/env python3
"""Refresh the portable GSD payload while preserving the personal overlay."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "get-shit-done-cc"


def run(*args: str, cwd: Path | None = None, env: dict[str, str] | None = None) -> str:
    try:
        result = subprocess.run(
            list(args),
            cwd=cwd,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or error.stdout or "command failed").strip()
        raise RuntimeError(f"{' '.join(args)}: {detail[-1200:]}") from error
    return result.stdout.strip()


def npm_json(*args: str) -> object:
    return json.loads(run("npm", *args, "--json"))


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def update_metadata(root: Path, version: str, npm_meta: dict[str, object]) -> None:
    description = (
        f"Megamen32's auto-updating Get Shit Done {version} distribution with "
        "focus-group review and mandatory real-surface acceptance."
    )
    for relative in (
        "plugin.json",
        ".codex-plugin/plugin.json",
        ".claude-plugin/plugin.json",
    ):
        path = root / relative
        data = json.loads(path.read_text())
        data["version"] = version
        data["description"] = description
        data["homepage"] = "https://github.com/megamen32/gsd-agent-plugin"
        interface = data.get("extensions", {}).get("com.openai", {}).get("interface", data.get("interface"))
        if isinstance(interface, dict):
            interface["displayName"] = "Megamen32 GSD"
            interface["shortDescription"] = "My GSD with focus groups and real-surface proof"
            interface["longDescription"] = description
            interface["developerName"] = "megamen32"
        write_json(path, data)

    package_path = root / "package.json"
    package = json.loads(package_path.read_text())
    package["version"] = version
    package["description"] = "OpenCode compatibility package for " + description
    package["homepage"] = "https://github.com/megamen32/gsd-agent-plugin"
    write_json(package_path, package)

    upstream = {
        "package": PACKAGE,
        "version": version,
        "repository": "https://github.com/gsd-build/get-shit-done.git",
        "tag": f"v{version}",
        "commit": npm_meta.get("gitHead", ""),
        "npmShasum": npm_meta.get("dist.shasum", ""),
        "profile": "full",
        "overlay": "megamen32-real-acceptance-security-consent-v2",
    }
    write_json(root / "UPSTREAM.json", upstream)


def safe_extract(archive: Path, destination: Path) -> None:
    root = destination.resolve()
    with tarfile.open(archive) as bundle:
        for member in bundle.getmembers():
            target = (destination / member.name).resolve()
            if target != root and root not in target.parents:
                raise RuntimeError(f"unsafe archive member: {member.name}")
        bundle.extractall(destination)


def current_version() -> str:
    return json.loads((ROOT / "UPSTREAM.json").read_text())["version"]


def refresh(version: str, *, preserve_existing_lock: bool = False) -> None:
    tmp_root = ROOT / ".tmp"
    tmp_root.mkdir(exist_ok=True)
    installed_lock_path = ROOT / "package-lock.upstream.json"
    installed_lock = (
        installed_lock_path.read_bytes()
        if preserve_existing_lock and installed_lock_path.exists()
        else None
    )
    meta = npm_json(
        "view",
        f"{PACKAGE}@{version}",
        "gitHead",
        "dist.shasum",
        "dist.tarball",
    )
    if not isinstance(meta, dict):
        raise RuntimeError("npm returned invalid package metadata")

    update_metadata(ROOT, version, meta)
    with tempfile.TemporaryDirectory(prefix="gsd-upstream-", dir=tmp_root) as temp:
        stage = Path(temp)
        packed = npm_json("pack", f"{PACKAGE}@{version}", "--pack-destination", str(stage))
        if not isinstance(packed, list) or not packed:
            raise RuntimeError("npm pack returned no artifact")
        archive = stage / str(packed[0]["filename"])
        safe_extract(archive, stage)
        package_root = stage / "package"
        # The published archive's package-lock can be intentionally older than
        # package.json. npm install is tolerant enough to materialize runtime
        # dependencies, but it rewrites that upstream-owned lockfile. Preserve
        # the exact published bytes so a refresh changes only real upstream
        # payload and our deterministic overlay.
        lock_path = package_root / "package-lock.json"
        original_lock = lock_path.read_bytes() if lock_path.exists() else None
        run("npm", "install", "--omit=dev", cwd=package_root)
        if original_lock is not None:
            lock_path.write_bytes(original_lock)

        home = stage / "home"
        projection = home / ".codex"
        home.mkdir()
        env = os.environ.copy()
        env["HOME"] = str(home)
        run(
            "node",
            str(package_root / "bin/install.js"),
            "--codex",
            "--global",
            "--config-dir",
            str(projection),
            "--profile=full",
            cwd=package_root,
            env=env,
        )
        try:
            run(
                sys.executable,
                str(ROOT / "scripts/build_from_upstream.py"),
                "--projection",
                str(projection),
                "--package",
                str(package_root),
                "--output",
                str(ROOT),
                "--source-prefix",
                "$HOME/.codex",
                cwd=ROOT,
            )
        finally:
            # A fail-closed overlay check may reject a changed upstream shape
            # after generated files have already been copied. Even then, a
            # same-version rebuild must not mutate our recorded dependency lock.
            if installed_lock is not None:
                installed_lock_path.write_bytes(installed_lock)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", help="specific upstream version; default is npm latest")
    parser.add_argument("--check", action="store_true", help="report whether an update exists")
    parser.add_argument("--force", action="store_true", help="rebuild even when versions match")
    args = parser.parse_args()

    latest = args.version or str(npm_json("view", PACKAGE, "version"))
    current = current_version()
    state = {"current": current, "latest": latest, "update_available": current != latest}
    if args.check:
        print(json.dumps(state, sort_keys=True))
        return 3 if state["update_available"] else 0
    if current == latest and not args.force:
        print(json.dumps({**state, "changed": False}, sort_keys=True))
        return 0

    refresh(latest, preserve_existing_lock=current == latest)
    print(json.dumps({**state, "changed": True}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
