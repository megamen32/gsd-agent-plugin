import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_codex_session_start_supplies_original_gsd_route():
    result = subprocess.run([sys.executable, str(ROOT / 'hooks/session_start.py')],
                            input=json.dumps({'hook_event_name': 'SessionStart', 'session_id': 'fresh', 'source': 'startup'}),
                            capture_output=True, text=True, check=True)
    context = json.loads(result.stdout)['hookSpecificOutput']['additionalContext']
    assert 'gsd-fast' in context and 'gsd-progress' in context
    assert '180' in context and 'consumer' in context
    assert 'spawn' not in context.lower()


def test_opencode_system_hook_is_idempotent_and_never_launches_session():
    probe = '''
    const {default: adapter} = await import(process.argv[1]);
    const hooks = await adapter({client: new Proxy({}, {get() {throw Error('recursive client call')}})});
    const output = {system: []};
    await hooks['experimental.chat.system.transform']({sessionID:'fresh'}, output);
    await hooks['experimental.chat.system.transform']({sessionID:'fresh'}, output);
    if(output.system.length !== 1 || !output.system[0].includes('gsd-fast')) throw Error('missing/duplicate autoentry');
    console.log('autoentry: one original GSD route, no client calls');
    '''
    subprocess.run(['node', '--input-type=module', '-e', probe,
                    (ROOT / 'opencode-plugin/index.js').as_uri()], check=True)


def test_codex_bootstrap_preserves_foreign_instructions_and_reinstall(tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location('install', ROOT/'scripts/install_runtime.py')
    install = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(install)
    path = tmp_path/'.codex/AGENTS.md'
    path.parent.mkdir()
    path.write_text('Existing owner instructions.\n')
    install.configure_codex_bootstrap(ROOT, tmp_path)
    install.configure_codex_bootstrap(ROOT, tmp_path)
    assert path.read_text().startswith('Existing owner instructions.')
    assert path.read_text().count('<ogsd_autoentry>') == 1
