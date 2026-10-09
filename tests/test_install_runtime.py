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


def test_opencode_replaces_existing_checkout_projection_and_bootstraps(tmp_path):
    home=tmp_path/'home'
    path=home/'.config/opencode/opencode.json'
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({'plugin':['/old/gsd-agent-plugin/opencode-plugin/index.js','foreign'],
                                'skills':{'paths':['/old/gsd-agent-plugin/skills','/foreign']},
                                'instructions':['/foreign/policy.md']}))
    env={**os.environ,'HOME':str(home)}
    for _ in range(2):
        subprocess.run([sys.executable,str(INSTALLER),'--plugin-root',str(ROOT)],env=env,check=True,capture_output=True)
    cfg=json.loads(path.read_text())
    assert cfg['plugin']==['foreign',str(ROOT/'opencode-plugin/index.js')]
    assert cfg['skills']['paths']==['/foreign',str(ROOT/'skills')]
    assert cfg['instructions']==['/foreign/policy.md',str(home/'.config/opencode/ogsd-bootstrap.md')]
    assert 'gsd-fast' in (home/'.config/opencode/ogsd-bootstrap.md').read_text()


def test_active_jsonc_override_gets_autoentry_and_preserves_strings(tmp_path):
    home=tmp_path/'home'
    path=home/'.config/opencode/opencode.jsonc'
    path.parent.mkdir(parents=True)
    path.write_text('{// active native config\n"model":"keep/model", "plugin":["foreign",], "instructions":["/policy.md"], "example":"https://example/a,}/*text*/",}')
    (path.parent/'opencode.json').write_text('{"model":"shadowed/model"}')
    env={**os.environ,'HOME':str(home)}
    subprocess.run([sys.executable,str(INSTALLER),'--plugin-root',str(ROOT)],env=env,check=True,capture_output=True)
    cfg=json.loads(path.read_text())
    assert cfg['model']=='keep/model' and cfg['example']=='https://example/a,}/*text*/'
    assert cfg['plugin']==['foreign',str(ROOT/'opencode-plugin/index.js')]
    assert cfg['instructions']==['/policy.md',str(home/'.config/opencode/ogsd-bootstrap.md')]
    assert json.loads((path.parent/'opencode.json').read_text())['model']=='shadowed/model'


def test_install_preserves_foreign_workflow_plugins_and_config_mode(tmp_path):
    home=tmp_path/'home'
    path=home/'.config/opencode/opencode.json'
    path.parent.mkdir(parents=True)
    foreign=['file:///foreign/lhc-time-guard.ts','last-human-commit@foreign','other']
    path.write_text(json.dumps({'plugin':foreign,'model':'preserve/model'}))
    path.chmod(0o600)
    env={**os.environ,'HOME':str(home)}
    subprocess.run([sys.executable,str(INSTALLER),'--plugin-root',str(ROOT)],env=env,check=True,capture_output=True)
    cfg=json.loads(path.read_text())
    assert cfg['plugin']==foreign+[str(ROOT/'opencode-plugin/index.js')]
    assert path.stat().st_mode & 0o777 == 0o600
