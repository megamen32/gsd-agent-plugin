import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_build_module():
    sys.path.insert(0, str(ROOT / "scripts"))
    path = ROOT / "scripts" / "build_from_upstream.py"
    spec = importlib.util.spec_from_file_location("build_from_upstream", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_overlay_is_present_on_completion_skills_only() -> None:
    build = load_build_module()
    for name in build.COMPLETION_SKILLS:
        text = (ROOT / "skills" / name / "SKILL.md").read_text()
        assert build.OVERLAY_MARKER in text
    assert build.OVERLAY_MARKER not in (ROOT / "skills/gsd-help/SKILL.md").read_text()
    assert (ROOT / "skills/gsd-acceptance-gate/SKILL.md").is_file()
    assert (ROOT / "get-shit-done/workflows/acceptance-gate.md").is_file()


def test_security_authorization_policy_is_present_in_every_skill_and_agent() -> None:
    build = load_build_module()
    for skill in (ROOT / "skills").glob("*/SKILL.md"):
        assert skill.read_text().count(build.SECURITY_AUTHORIZATION_MARKER) == 1, skill
    for pattern in ("*.md", "*.toml"):
        for agent in (ROOT / "agents").glob(pattern):
            assert agent.read_text().count(build.SECURITY_AUTHORIZATION_MARKER) == 1, agent


def test_overlay_reapplies_after_clean_upstream_refresh(tmp_path: Path) -> None:
    build = load_build_module()
    output = tmp_path / "output"
    for name in ("gsd-fast", "gsd-help"):
        skill = output / "skills" / name / "SKILL.md"
        skill.parent.mkdir(parents=True, exist_ok=True)
        skill.write_text(
            f'---\nname: "{name}"\ndescription: "test"\n---\n\n'
            "<execution_context>\n@/fake/.codex/get-shit-done/workflows/test.md\n"
            "</execution_context>\n"
        )
    agent_md = output / "agents/gsd-demo.md"
    agent_md.parent.mkdir(parents=True, exist_ok=True)
    agent_md.write_text("---\nname: gsd-demo\n---\n\n<role>Demo</role>\n")
    agent_toml = output / "agents/gsd-demo.toml"
    agent_toml.write_text("name = \"gsd-demo\"\ndeveloper_instructions = '''\n<role>Demo</role>\n'''\n")

    build.apply_personal_overlay(output, ROOT / "overlay")
    build.inject_runtime_adapters(output, "/fake/.codex")
    build.inject_runtime_adapters(output, "/fake/.codex")

    fast = (output / "skills/gsd-fast/SKILL.md").read_text()
    help_text = (output / "skills/gsd-help/SKILL.md").read_text()
    assert fast.count("<gsd_agent_plugin_adapter>") == 1
    assert fast.count(build.SECURITY_AUTHORIZATION_MARKER) == 1
    assert fast.count(build.OVERLAY_MARKER) == 1
    assert fast.count(build.BUSINESS_MARKER) == 1
    assert fast.index(build.BUSINESS_MARKER) < fast.index(build.OVERLAY_MARKER)
    assert build.BUSINESS_MARKER not in help_text
    supervisor_skill = output / "skills/gsd-business-supervisor/SKILL.md"
    assert supervisor_skill.is_file()
    assert build.BUSINESS_MARKER not in supervisor_skill.read_text()
    assert (output / "agents/gsd-business-supervisor.md").is_file()
    assert (output / "get-shit-done/workflows/business-supervisor.md").is_file()
    assert "@../../get-shit-done/workflows/test.md" in fast
    assert build.OVERLAY_MARKER not in help_text
    assert help_text.count(build.SECURITY_AUTHORIZATION_MARKER) == 1
    assert agent_md.read_text().count(build.SECURITY_AUTHORIZATION_MARKER) == 1
    assert agent_toml.read_text().count(build.SECURITY_AUTHORIZATION_MARKER) == 1
    assert (output / "skills/gsd-acceptance-gate/SKILL.md").is_file()


def test_business_wrapper_covers_existing_and_future_workflows(tmp_path: Path) -> None:
    build = load_build_module()
    output = tmp_path / "output"
    for name in ("gsd-execute-phase", "gsd-new-upstream-action", "gsd-help",
                 "gsd-business-supervisor"):
        skill = output / "skills" / name / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text(f'---\nname: "{name}"\n---\n\nOriginal upstream body.\n')
    build.apply_personal_overlay(output, ROOT / "overlay")
    build.inject_runtime_adapters(output, "")
    build.inject_runtime_adapters(output, "")
    for skill in (output / "skills").glob("*/SKILL.md"):
        text = skill.read_text()
        expected = 0 if skill.parent.name in build.BUSINESS_EXCLUDED_SKILLS else 1
        assert text.count(build.BUSINESS_MARKER) == expected
    assert "Original upstream body." in (
        output / "skills/gsd-new-upstream-action/SKILL.md"
    ).read_text()


def test_packaged_supervisor_is_reachable_from_delivery_skills() -> None:
    build = load_build_module()
    for skill in (ROOT / "skills").glob("*/SKILL.md"):
        expected = 0 if skill.parent.name in build.BUSINESS_EXCLUDED_SKILLS else 1
        assert skill.read_text().count(build.BUSINESS_MARKER) == expected, skill
    for relative in ("agents/gsd-business-supervisor.md",
                     "get-shit-done/workflows/business-supervisor.md"):
        assert (ROOT / relative).is_file()


def test_generated_prompt_references_are_plugin_relative(tmp_path: Path) -> None:
    build = load_build_module()
    output = tmp_path / "output"
    prompt = output / "agents/gsd-demo.md"
    prompt.parent.mkdir(parents=True)
    prompt.write_text("@$HOME/.codex/get-shit-done/references/demo.md\n")
    workflow = output / "get-shit-done/workflows/demo.md"
    workflow.parent.mkdir(parents=True)
    workflow.write_text("Read $HOME/.codex/get-shit-done/templates/demo.md\n")

    build.normalize_generated_references(output, "$HOME/.codex")

    assert "@$GSD_PLUGIN_ROOT/get-shit-done/references/demo.md" in prompt.read_text()
    assert "$GSD_PLUGIN_ROOT/get-shit-done/templates/demo.md" in workflow.read_text()


def test_isolated_projection_path_is_removed_from_agent_toml(tmp_path: Path) -> None:
    build = load_build_module()
    output = tmp_path / "output"
    prompt = output / "agents/gsd-demo.toml"
    prompt.parent.mkdir(parents=True)
    projection = tmp_path / "stage/home/.codex"
    prompt.write_text(
        f"developer_instructions = '''@{projection}/get-shit-done/references/demo.md'''\n"
    )

    build.normalize_generated_references(output, str(projection))

    assert str(projection) not in prompt.read_text()
    assert "@$GSD_PLUGIN_ROOT/get-shit-done/references/demo.md" in prompt.read_text()


def test_coordination_policy_survives_refresh_with_resolvable_skill_agent_routes(tmp_path: Path) -> None:
    """fast unit, expected0.2/max5s: omitted policy, wrong agent path or duplicate refresh."""
    build = load_build_module()
    output = tmp_path / "output"
    skill = output / "skills/gsd-future-coordinator/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text('---\nname: gsd-future-coordinator\ndescription: fixture\n---\n\nOwned upstream body.\n')
    agent_md = output / "agents/gsd-coordinator.md"
    agent_md.parent.mkdir(parents=True)
    agent_md.write_text('---\nname: gsd-coordinator\n---\n\nOwned upstream role.\n')
    agent_toml = output / "agents/gsd-coordinator.toml"
    agent_toml.write_text("name = 'gsd-coordinator'\ndeveloper_instructions = '''\nOwned upstream role.\n'''\n")
    for _ in range(2):
        build.apply_personal_overlay(output, ROOT / "overlay")
        build.inject_runtime_adapters(output, "")
    policy = output / "get-shit-done/references/session-coordination.md"
    assert policy.read_bytes() == (ROOT / "overlay/get-shit-done/references/session-coordination.md").read_bytes()
    for path in (skill, agent_md, agent_toml):
        text = path.read_text()
        assert text.count(build.COORDINATION_MARKER) == 1
        reference = next(line[1:] for line in text.splitlines() if line.startswith('@') and line.endswith('/session-coordination.md'))
        resolved = Path(reference.replace('$GSD_PLUGIN_ROOT', str(output))) if '$GSD_PLUGIN_ROOT' in reference else (path.parent / reference).resolve()
        assert resolved == policy.resolve(), path
        assert 'Owned upstream' in text
    assert '$GSD_PLUGIN_ROOT/get-shit-done/references/session-coordination.md' in (output / 'hooks/autoentry.md').read_text()


def test_sdk_query_overlay_is_idempotent(tmp_path: Path) -> None:
    build = load_build_module()
    output = tmp_path / "output"
    cli = output / "sdk/dist/cli.js"
    cli.parent.mkdir(parents=True)
    cli.write_text(
        "import { GSD } from './index.js';\n"
        "import { CLITransport } from './cli-transport.js';\n"
        "import { WSTransport } from './ws-transport.js';\n"
        "import { InitRunner } from './init-runner.js';\n"
        "import { loadConfig } from './config.js';\n"
        "import { assertRuntimeSupportsAutoMode } from './runtime-gate.js';\n"
        "import { runQueryCliCommand } from './query/query-cli-adapter.js';\n"
        "async function main() {\n"
        "    // Fall back to GSD_WORKSTREAM env var when --ws is not supplied (#2791).\n"
        "}\n"
    )

    build.apply_sdk_lazy_query_overlay(output)
    build.apply_sdk_lazy_query_overlay(output)

    text = cli.read_text()
    assert text.count("async function loadExecutionRuntime()") == 1
    assert "import { GSD } from './index.js';" not in text
    assert "await loadExecutionRuntime()" in text


def test_metadata_versions_follow_upstream_without_hardcoded_test_version(tmp_path: Path) -> None:
    from scripts.sync_upstream import update_metadata

    for relative in ("plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"version": "old", "description": "old", "homepage": "old",
                        **({"extensions": {"com.openai": {"interface": {"longDescription": "old"}}}}
                           if relative == "plugin.json" else {"interface": {"longDescription": "old"}})})
        )
    (tmp_path / "package.json").write_text(json.dumps({"version": "old"}))

    update_metadata(
        tmp_path,
        "9.8.7",
        {"gitHead": "abc", "dist.shasum": "def"},
    )

    plugin = json.loads((tmp_path / "plugin.json").read_text())
    assert plugin["extensions"]["com.openai"]["interface"]["longDescription"].startswith(
        "Megamen32's auto-updating Get Shit Done 9.8.7")
    assert "interface" not in plugin
    assert plugin["version"] == "9.8.7"
    assert plugin["description"].startswith("Megamen32's auto-updating Get Shit Done 9.8.7")
    assert plugin["homepage"] == "https://github.com/megamen32/gsd-agent-plugin"
    package = json.loads((tmp_path / "package.json").read_text())
    assert package["homepage"] == "https://github.com/megamen32/gsd-agent-plugin"
    upstream = json.loads((tmp_path / "UPSTREAM.json").read_text())
    assert upstream["version"] == "9.8.7"
    assert upstream["overlay"] == "megamen32-real-acceptance-security-consent-v2"
