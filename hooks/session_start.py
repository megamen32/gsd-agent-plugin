#!/usr/bin/env python3
"""Provide context only: no model, child session, daemon or workflow recursion."""
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
context = (root / 'hooks/autoentry.md').read_text()
context = 'GSD_PLUGIN_ROOT=' + str(root) + '\n' + context
print(json.dumps({'hookSpecificOutput': {'hookEventName': 'SessionStart',
                                        'additionalContext': context}}))
