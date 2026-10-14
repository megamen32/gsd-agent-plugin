"""Fast unit, expected 2s/emergency 20s: saved task survives native hook reentry.
Detects route-only startup losing task, mandate/boundaries and current plan context.
Actual agent detour/handoff decisions are covered by native Codex consumer separately.
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_resume_and_compaction_restore_saved_task_without_mutating_it(tmp_path):
    task = tmp_path / '.agents/tasks/gsd-own-session.md'
    task.parent.mkdir(parents=True)
    task.write_text('# Original assignment\nFinish adapter A.\n# Authority\nUser assigned own-session; Alice may delegate adapter A.\n# Outcome\nWorking A.\n# Project and boundaries\nOnly adapter A.\n# Acceptance\nNative consumer green.\n# Current plan\n.planning/phases/01-A/01-01-PLAN.md\n')
    before = task.read_bytes()
    for source in ('startup', 'resume', 'compact'):
        event = {'hook_event_name': 'SessionStart', 'session_id': 'own-session',
                 'source': source, 'cwd': str(tmp_path)}
        output = subprocess.run([sys.executable, str(ROOT/'hooks/session_start.py')],
                                input=json.dumps(event), capture_output=True, text=True, check=True)
        context = json.loads(output.stdout)['hookSpecificOutput']['additionalContext']
        assert str(task) in context
        assert 'Finish adapter A.' in context
        assert 'Alice may delegate' in context
        assert 'task-continuity.md' in context
        assert 'STATE' in context and 'SPEC' in context and 'PLAN' in context
        assert task.read_bytes() == before


def test_initial_entry_names_session_record_without_inventing_assignment(tmp_path):
    output = subprocess.run([sys.executable, str(ROOT/'hooks/session_start.py')],
        input=json.dumps({'session_id':'new-session','cwd':str(tmp_path),'source':'startup'}),
        capture_output=True, text=True, check=True)
    context = json.loads(output.stdout)['hookSpecificOutput']['additionalContext']
    assert str(tmp_path/'.agents/tasks/gsd-new-session.md') in context
    assert not (tmp_path/'.agents').exists()


def test_all_original_skills_load_one_shared_task_continuity_reference():
    for skill in (ROOT/'skills').glob('*/SKILL.md'):
        assert '@../../get-shit-done/references/task-continuity.md' in skill.read_text(), skill
    assert (ROOT/'overlay/get-shit-done/references/task-continuity.md').read_bytes() == (ROOT/'get-shit-done/references/task-continuity.md').read_bytes()


def test_hook_with_missing_native_identity_does_not_open_other_sessions(tmp_path):
    task = tmp_path/'.agents/tasks/gsd-other-session.md'
    task.parent.mkdir(parents=True); task.write_text('Foreign task, must not be restored.')
    for event in ({'cwd': str(tmp_path)}, {'cwd': str(tmp_path),'session_id':'../other-session'}):
        result = subprocess.run([sys.executable,str(ROOT/'hooks/session_start.py')],input=json.dumps(event),capture_output=True,text=True,check=True)
        assert 'Foreign task' not in result.stdout
