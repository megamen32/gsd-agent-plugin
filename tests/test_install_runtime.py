import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install_runtime.py"


def run_installer(tmp_path: Path, runtime: str) -> dict:
    home = tmp_path / "home"
    home.mkdir()
    env = os.environ.copy()
    env["HOME"] = str(home)
    result = subprocess.run(
        [
            sys.executable,
            str(INSTALLER),
            "--plugin-root",
            str(ROOT),
            "--runtime",
            runtime,
        ],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return json.loads(result.stdout)


def run_installer_raw(tmp_path: Path, runtime: str) -> subprocess.CompletedProcess[str]:
    home = tmp_path / "home"
    home.mkdir()
    env = os.environ.copy()
    env["HOME"] = str(home)
    return subprocess.run(
        [
            sys.executable,
            str(INSTALLER),
            "--plugin-root",
            str(ROOT),
            "--runtime",
            runtime,
        ],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )


def test_opencode_install_creates_native_plugin_and_skill_paths(tmp_path: Path) -> None:
    receipt = run_installer(tmp_path, "opencode")
    config_path = tmp_path / "home" / ".config" / "opencode" / "opencode.json"
    config = json.loads(config_path.read_text())

    assert config["plugin"] == [str(ROOT / "opencode-plugin" / "index.js")]
    assert config["skills"]["paths"] == [str(ROOT / "skills")]
    assert receipt["configured"] == ["opencode"]


def test_zcode_is_not_handled_by_the_opencode_compatibility_installer(
    tmp_path: Path,
) -> None:
    result = run_installer_raw(tmp_path, "zcode")

    assert result.returncode != 0
    assert "invalid choice" in result.stderr
    assert not (tmp_path / "home" / ".zcode").exists()


def test_runtime_updates_preserve_unrelated_configuration(tmp_path: Path) -> None:
    home = tmp_path / "home"
    opencode_path = home / ".config" / "opencode" / "opencode.json"
    opencode_path.parent.mkdir(parents=True)
    opencode_path.write_text(json.dumps({"model": "example/model", "plugin": ["other"]}))
    env = os.environ.copy()
    env["HOME"] = str(home)

    subprocess.run(
        [sys.executable, str(INSTALLER), "--plugin-root", str(ROOT), "--runtime", "opencode"],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )

    opencode = json.loads(opencode_path.read_text())
    assert opencode["model"] == "example/model"
    assert opencode["plugin"] == ["other", str(ROOT / "opencode-plugin" / "index.js")]


def test_runtime_updates_replace_legacy_gsd_paths(tmp_path: Path) -> None:
    home = tmp_path / "home"
    old_root = "/home/roomhacker/.codex/plugins/cache/megamen32-plugins/gsd/1.42.3"
    opencode_path = home / ".config" / "opencode" / "opencode.json"
    opencode_path.parent.mkdir(parents=True)
    opencode_path.write_text(
        json.dumps(
            {
                "plugin": ["other", f"{old_root}/opencode-plugin/index.js"],
                "skills": {"paths": ["/other-skills", f"{old_root}/skills"]},
            }
        )
    )
    env = os.environ.copy()
    env["HOME"] = str(home)

    subprocess.run(
        [sys.executable, str(INSTALLER), "--plugin-root", str(ROOT), "--runtime", "opencode"],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )

    opencode = json.loads(opencode_path.read_text())
    assert opencode["plugin"] == ["other", str(ROOT / "opencode-plugin" / "index.js")]
    assert opencode["skills"]["paths"] == ["/other-skills", str(ROOT / "skills")]
