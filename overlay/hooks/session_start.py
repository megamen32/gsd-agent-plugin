#!/usr/bin/env python3
"""Existing SessionStart context: restore own assignment; never start work or write state."""
import json
import re
import sys
from pathlib import Path


def context_for(event, root):
    context = 'GSD_PLUGIN_ROOT=' + str(root) + '\n' + (root / 'hooks/autoentry.md').read_text()
    context += '\nRead ' + str(root / 'get-shit-done/references/task-continuity.md') + '\n'
    context += 'Reconcile original assignment with current PROJECT/REQUIREMENTS/ROADMAP/STATE and current SPEC/PLAN before acting.\n'
    session = event.get('session_id')
    cwd = event.get('cwd')
    if isinstance(session, str) and re.fullmatch(r'[A-Za-z0-9_-]{1,128}', session) and isinstance(cwd, str) and Path(cwd).is_absolute():
        task = Path(cwd) / '.agents/tasks' / ('gsd-' + session + '.md')
        context += 'Session task record (use owning project if cwd differs): ' + str(task) + '\n'
        try:
            with task.open(encoding='utf-8') as handle:
                saved = handle.read(8193)
            if len(saved) <= 8192:
                context += '<gsd_saved_assignment>\n' + saved + '\n</gsd_saved_assignment>\n'
            else:
                context += 'Read the complete saved task record at that path; it exceeds the inline context budget.\n'
        except FileNotFoundError:
            context += 'No saved record yet: capture the direct user assignment once before engineering; do not invent one.\n'
        except (OSError, UnicodeError):
            context += 'Saved task could not be read: recover from verified session/task evidence before changing direction.\n'
    else:
        context += 'Native session identity/cwd absent: reuse the known task record from session context; do not read another session.\n'
    return context


def main():
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict):
            event = {}
    except (ValueError, OSError):
        event = {}
    root = Path(__file__).resolve().parents[1]
    print(json.dumps({'hookSpecificOutput': {'hookEventName': 'SessionStart',
                                            'additionalContext': context_for(event, root)}}))


if __name__ == '__main__':
    main()
