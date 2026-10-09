import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('queue',ROOT/'scripts/nightly_queue.py')
queue=importlib.util.module_from_spec(spec);spec.loader.exec_module(queue)


def observed(sessions=(),complete=True,host='host'):
    return dict(host=host,observed_unix=100,sessions=list(sessions),complete=complete)


def test_active_development_skips_before_runner_or_reservation(tmp_path):
    obs=observed([dict(harness='codex',id='developer',status='running')]);obs['observed_unix']=queue.time.time()
    result=queue.tick(tmp_path,'host',obs,runner=lambda *a: (_ for _ in ()).throw(AssertionError('booked busy host')))
    assert result['status']=='SKIP_ACTIVE' and not result['reservation_created']
    assert not (tmp_path/'queue.json').exists()


def test_unknown_stale_and_partial_are_never_free():
    assert queue.classify(observed(complete=False),'host',now=100)=='UNKNOWN'
    assert queue.classify(observed(),'host',now=116)=='UNKNOWN'
    assert queue.classify(observed(),'other',now=100)=='UNKNOWN'
    assert queue.classify(observed([dict(harness='codex',id='x',status='error')]),'host',now=100)=='UNKNOWN'


def test_only_exact_own_nightly_executor_is_excluded():
    rows=[dict(harness='codex',id='own',status='running')]
    assert queue.classify(observed(rows),'host',['codex','own'],now=100)=='FREE'
    rows.append(dict(harness='codex',id='foreign',status='running'))
    assert queue.classify(observed(rows),'host',['codex','own'],now=100)=='ACTIVE'


def test_window_cleanup_requeues_tail_and_retains_result(tmp_path):
    state={'pending':[{'id':'slow'},{'id':'next'}],'running':None,'completed':[]}
    queue.write(tmp_path/'queue.json',state)
    obs=observed();obs['observed_unix']=queue.time.time()
    def stock_fixture(job,path):
        result=dict(status='TIMEOUT',cleanup_verified=True,reservation_started=True)
        queue.write(path,result);return result
    result=queue.tick(tmp_path,'host',obs,stock_fixture)
    state=json.loads((tmp_path/'queue.json').read_text())
    assert result['status']=='TIMEOUT' and result['requeued']
    assert [r['id'] for r in state['pending']]==['next','slow']
    assert state['running'] is None and Path(result['result']).exists()


def test_unverified_cleanup_keeps_own_claim_without_replay(tmp_path):
    queue.write(tmp_path/'queue.json',dict(pending=[dict(id='slow')],running=None,completed=[]))
    obs=observed();obs['observed_unix']=queue.time.time()
    result=queue.tick(tmp_path,'host',obs,lambda *a:dict(status='INCOMPLETE',cleanup_verified=False,reservation_started=True))
    assert result['status']=='CLEANUP_PENDING'
    assert queue.tick(tmp_path,'host',obs,lambda *a: (_ for _ in ()).throw(AssertionError('replayed')))['status']=='CLEANUP_PENDING'


def test_host_queues_are_independent(tmp_path):
    obs=observed();obs['observed_unix']=queue.time.time()
    queue.write(tmp_path/'100/queue.json',dict(pending=[],running={'id':'owned100'},completed=[]))
    assert queue.tick(tmp_path/'100','host',obs)['status']=='CLEANUP_PENDING'
    assert queue.tick(tmp_path/'44','host',obs)['status']=='EMPTY'
    assert queue.tick(tmp_path/'88','host',obs)['status']=='EMPTY'
