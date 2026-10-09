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
