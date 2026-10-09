import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('policy', ROOT / 'scripts/test_policy.py')
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)


def test_unclassified_or_missing_coverage_cannot_pass():
    with pytest.raises(ValueError, match='coverage mismatch'):
        policy.validate([], ['tests/example.py::test_unknown'])


def test_timeout_is_failure_and_owned_child_is_collected(tmp_path):
    import sys
    code, timeout = policy.execute([sys.executable, '-c', 'import time; time.sleep(10)'], ROOT, .05, tmp_path/'timeout.log')
    assert code == 124 and timeout


def test_timeout_collects_descendants_without_signalling_foreign_process(tmp_path):
    import subprocess
    import sys
    import time
    foreign=subprocess.Popen([sys.executable,'-c','import time; time.sleep(10)'])
    child_pid=tmp_path/'child.pid'
    script="import subprocess,sys,time; child=subprocess.Popen([sys.executable,'-c','import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(10)']); open(sys.argv[1],'w').write(str(child.pid)); time.sleep(10)"
    try:
        code,timed_out=policy.execute([sys.executable,'-c',script,str(child_pid)],ROOT,.15,tmp_path/'log')
        pid=int(child_pid.read_text())
        deadline=time.monotonic()+.5
        while time.monotonic()<deadline:
            proc=Path(f'/proc/{pid}/stat')
            if not proc.exists() or proc.read_text().split()[2]=='Z':break
            time.sleep(.01)
        else:raise AssertionError('owned descendant survives timeout')
        assert code==124 and timed_out and foreign.poll() is None
    finally:
        foreign.terminate();foreign.wait()
        # Remove only this regression fixture's own leftover if the red proof fails.
        if child_pid.exists():
            try:__import__('os').kill(int(child_pid.read_text()),__import__('signal').SIGKILL)
            except ProcessLookupError:pass
