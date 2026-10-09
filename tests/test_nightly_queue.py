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


def test_registered_slow_window_is_not_capped_by_generic_runner_envelope(tmp_path):
    job=dict(id='registered-slow',window_seconds=600,budget={'wall':600},
             runner_path='/existing/bounded-foreground.py',temp_root='/owned/tmp',command=['true'])
    assert queue.enqueue(tmp_path,job)['status']=='QUEUED'


def test_native_observer_preserves_host_binding_and_retains_receipt(tmp_path):
    import sys
    script="import json,time; print(json.dumps({'host':'foreign','observed_unix':time.time(),'sessions':[],'complete':True,'source':'existing native probe'}))"
    observation=queue.observe_native('host',[sys.executable,'-c',script],tmp_path)
    assert queue.classify(observation,'host')=='UNKNOWN'
    assert any((tmp_path/'observations').glob('*.log'))


def test_native_observer_active_result_skips_without_reservation(tmp_path):
    import sys
    script="import json,time; print(json.dumps({'host':'host','observed_unix':time.time(),'sessions':[{'harness':'codex','id':'developer','status':'running'}],'complete':True,'source':'existing native probe'}))"
    observation=queue.observe_native('host',[sys.executable,'-c',script],tmp_path)
    result=queue.tick(tmp_path,'host',observation,runner=lambda *args: (_ for _ in ()).throw(AssertionError('reserved development host')))
    assert result['status']=='SKIP_ACTIVE' and result['reservation_created'] is False


def test_native_observer_failure_stays_unknown(tmp_path):
    import sys
    observation=queue.observe_native('host',[sys.executable,'-c','raise SystemExit(75)'],tmp_path)
    assert queue.classify(observation,'host')=='UNKNOWN'


def test_central_herder_without_host_binding_cannot_prove_remote_free():
    original_read,original_mcp=queue.read_json_url,queue.fresh_mcp_sessions
    try:
        queue.read_json_url=lambda *args:{'sessions':[]}
        queue.fresh_mcp_sessions=lambda *args:{'sessions':[],'total':0,'limited':False}
        assert queue.classify(queue.observe('remote44','http://central100'),'remote44')=='UNKNOWN'
    finally:
        queue.read_json_url,queue.fresh_mcp_sessions=original_read,original_mcp


def test_existing_runner_keeps_profile_and_uses_enduring_authorized_route(tmp_path):
    helper=tmp_path/'bounded-foreground.py'
    helper.write_text("""
import json
from pathlib import Path
LAST_RUN=None
class Held(Exception):pass
def budget(value):
    assert value.get('_profile')=='accepted-profile', 'profile lost at budget boundary'
    assert {k:v for k,v in value.items() if k!='_profile'}=={'wall':1}, 'budget changed'
    return value
def authorized_case(path):
    case=json.loads(Path(path).read_text())
    return case,budget(dict(case['budget'],_profile=case['profile']))
def reserve_scope(info):pass
def clear_reservation(info):pass
def run(*args):raise AssertionError('bare budget route used')
def run_authorized_case(path,wait):
    global LAST_RUN
    case=json.loads(Path(path).read_text())
    info=dict(unit='own',cgroup='own',invocation='one',inode=1,pid=123,start='1')
    reserve_scope(info)
    clear_reservation(info)
    LAST_RUN={'same_generation_cleanup':True}
    return 0
""")
    case=tmp_path/'case.json'
    job=dict(profile='accepted-profile',budget={'wall':1},window_seconds=2,
             command=['true'],temp_root=str(tmp_path),runner_path=str(helper),authorized_case_path=str(case))
    case.write_text(json.dumps(dict(profile=job['profile'],budget=job['budget'],command=job['command'],temp_root=job['temp_root'])))
    result=queue.existing_runner(job,tmp_path/'result.json')
    assert result['status']=='PASS' and result['cleanup_verified'] is True
    assert result['profile']=='accepted-profile'


def test_bare_budget_cannot_reserve_without_enduring_authorized_case(tmp_path):
    helper=tmp_path/'bounded-foreground.py'
    helper.write_text("raise AssertionError('unapproved helper entered')")
    result=queue.existing_runner(dict(runner_path=str(helper),budget={'wall':1},window_seconds=1),tmp_path/'result.json')
    assert result['status']=='HELD' and result['reservation_started'] is False
