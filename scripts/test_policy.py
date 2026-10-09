#!/usr/bin/env python3
"""Exactly three categories, complete coverage, finite aggregate and per-case time."""
from __future__ import annotations
import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {'fast unit', 'focused integration', 'slow nightly'}


def execute(command, cwd, seconds, log):
    with log.open('w') as output:
        process = subprocess.Popen(command, cwd=cwd, stdout=output, stderr=subprocess.STDOUT,
                                   start_new_session=True, env={**os.environ, 'PYTEST_DISABLE_PLUGIN_AUTOLOAD': '1'})
        try:
            return process.wait(timeout=seconds), False
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
            return 124, True


def validate(catalog, collected):
    ids = [case['id'] for case in catalog]
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate scenario')
    for case in catalog:
        if case['category'] not in CATEGORIES or not case['purpose'] or not case['defect']:
            raise ValueError('missing test classification')
        if not 0 < case['expected_seconds'] <= case['max_seconds']:
            raise ValueError('invalid duration')
        if case['category'] == 'slow nightly' and not case.get('nightly_reason'):
            raise ValueError('nightly requires retained coverage rationale')
    declared = {case['id'] for case in catalog if case.get('pytest')}
    if set(collected) != declared:
        raise ValueError(f'coverage mismatch: unclassified={sorted(set(collected)-declared)}, missing={sorted(declared-set(collected))}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['release', 'nightly'], default='release')
    parser.add_argument('--catalog', type=Path, default=ROOT / 'tests/catalog.json')
    parser.add_argument('--result-dir', type=Path, default=ROOT / '.tmp/test-policy')
    parser.add_argument('--deadline', type=float, default=180)
    args = parser.parse_args()
    started = time.monotonic()
    deadline = min(args.deadline, 180) if args.mode == 'release' else args.deadline
    args.result_dir.mkdir(parents=True, exist_ok=True)
    report = {'mode': args.mode, 'status': 'INCOMPLETE', 'cases': []}
    result_path = args.result_dir / 'result.json'
    def save():
        report['elapsed_seconds'] = round(time.monotonic()-started, 3)
        result_path.write_text(json.dumps(report, indent=2)+'\n')
    save()
    try:
        catalog = json.loads(args.catalog.read_text())
        collection_log = args.result_dir / 'collection.log'
        code, timed_out = execute([sys.executable, '-m', 'pytest', '--collect-only', '-q', 'tests'], ROOT,
                                  max(0.001, min(15, deadline-(time.monotonic()-started))), collection_log)
        if code or timed_out:
            raise ValueError('collection failed or timed out')
        collected = [line for line in collection_log.read_text().splitlines() if line.startswith('tests/') and '::' in line]
        validate(catalog, collected)
        selected = [c for c in catalog if (c['category']=='slow nightly') == (args.mode=='nightly')]
        report['planned'] = len(selected)
        for index, case in enumerate(selected):
            remaining = deadline-(time.monotonic()-started)
            if remaining <= 0:
                report['status'] = 'TIMEOUT'; break
            command = [sys.executable, '-m', 'pytest', '-q', case['id']] if case.get('pytest') else case['command']
            command = [x.replace('{root}',str(ROOT)).replace('{python}',sys.executable) for x in command]
            case_start = time.monotonic()
            code, timed_out = execute(command, ROOT, min(remaining, case['max_seconds']), args.result_dir / f'{index}.log')
            report['cases'].append({'id':case['id'], 'status':'TIMEOUT' if timed_out else 'PASS' if code==0 else 'FAIL',
                                    'elapsed_seconds':round(time.monotonic()-case_start,3),'returncode':code})
            save()
            if code:
                report['status']='TIMEOUT' if timed_out else 'FAIL'; break
        else:
            report['status']='GREEN' if selected and len(report['cases'])==len(selected) else 'INCOMPLETE'
    except Exception as error:
        report['error']=str(error); report['status']='FAIL'
    save()
    print(json.dumps(report))
    return 0 if report['status']=='GREEN' else 1

if __name__ == '__main__':
    raise SystemExit(main())
