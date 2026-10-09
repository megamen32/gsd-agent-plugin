#!/usr/bin/env python3
"""Host-local OGSD queue. Admission and cleanup stay in the existing runner."""
from __future__ import annotations
import argparse
import fcntl
import importlib.util
import json
import os
import re
import socket
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

HOSTS = {'100':'roomhacker-server-100', '44':'server-44', '88':'roomhacker-server-88'}


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, indent=2)+'\n')
    os.chmod(tmp, 0o600)
    tmp.replace(path)


def classify(observation, host, own_executor=None, now=None):
    now = time.time() if now is None else now
    try:
        age = now-observation['observed_unix']
        if observation['host'] != host or not 0 <= age <= 15:
            return 'UNKNOWN'
        sessions = observation['sessions']
        if own_executor:
            sessions = [r for r in sessions if [r['harness'],r['id']] != own_executor]
        for row in sessions:
            # Exclusion is by exact harness+session identity, not title or cwd.
            if own_executor and [row['harness'],row['id']] == own_executor:
                continue
            if row['status'] in ('running','needs_input'):
                return 'ACTIVE'
        if observation.get('complete') is not True or observation.get('warming'):
            return 'UNKNOWN'
        if any(r['status'] not in ('idle','stopped') for r in sessions):
            return 'UNKNOWN'
        return 'FREE'
    except (KeyError,TypeError,ValueError):
        return 'UNKNOWN'


def read_json_url(url, timeout):
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read(4*1024*1024))


def fresh_mcp_sessions(endpoint):
    request=urllib.request.Request(endpoint+'/mcp',method='POST',
        headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream'},
        data=json.dumps({'jsonrpc':'2.0','id':'ogsd-observe','method':'tools/call',
                         'params':{'name':'list_agents','arguments':{'harness':'all','status':'all','limit':100}}}).encode())
    with urllib.request.urlopen(request,timeout=8) as response:
        deadline=time.monotonic()+8
        if 'text/event-stream' in response.headers.get('Content-Type',''):
            while time.monotonic()<deadline:
                line=response.readline(4*1024*1024).decode()
                if line.startswith('data:'):
                    message=json.loads(line[5:].strip())
                    if message.get('id')=='ogsd-observe':break
            else:raise TimeoutError('Herder native discovery deadline')
        else:message=json.loads(response.read(4*1024*1024))
    result=message.get('result',{}).get('structuredContent')
    if not isinstance(result,dict):raise ValueError('Herder structured native result missing')
    return result


def observe(host, endpoint, own_executor=None):
    # HTTP inventory is cache-first. It can nominate a candidate, never prove FREE.
    # Native getSession bypasses that inventory cache and proves ACTIVE safely.
    result = {'host':host,'observed_unix':time.time(),'sessions':[], 'complete':False,
              'source':'Herder native getSession'}
    try:
        candidates = read_json_url(endpoint+'/api/sessions?inventory=1', 3)
        deadline = time.monotonic()+5
        for row in candidates['sessions']:
            if time.monotonic()>deadline:break
            if own_executor and [row['harness'],row['id']] == own_executor:continue
            if row.get('status') not in ('running','needs_input'):continue
            url = endpoint+'/api/sessions/'+urllib.parse.quote(row['harness'],safe='')+'/'+urllib.parse.quote(row['id'],safe='')
            native = read_json_url(url,min(2,max(.1,deadline-time.monotonic())))['session']
            result['sessions'].append({k:native[k] for k in ('harness','id','status')})
            if native['status'] in ('running','needs_input'):break
        result['observed_unix']=time.time()
        if classify(result,host,own_executor)=='UNKNOWN':
            fresh=fresh_mcp_sessions(endpoint)
            result['sessions']=[{k:r[k] for k in ('harness','id','status')} for r in fresh['sessions']]
            result['observed_unix']=time.time()
            result['complete']=(fresh.get('host')==host and fresh.get('limited') is False
                                and fresh.get('total')==len(fresh['sessions']))
            result['source']='Herder MCP list_agents native discovery'
            if not result['complete']:
                result['reason']='Native discovery lacks complete host-bound free-host proof'
    except Exception as error:
        result['reason']='Herder native observation unavailable: '+type(error).__name__
    return result


def observe_native(host, command, state_dir):
    """Call the infra-owned existing native observer, with retained finite evidence."""
    unknown={'host':host,'observed_unix':time.time(),'sessions':[],'complete':False}
    log=state_dir/'observations'/(uuid.uuid4().hex+'.log')
    log.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    log.touch(mode=0o600)
    try:
        if not command or not all(isinstance(x,str) for x in command):
            raise ValueError('exact existing observer argv required')
        path=Path(__file__).with_name('test_policy.py')
        spec=importlib.util.spec_from_file_location('ogsd_existing_finite_command',path)
        policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy)
        code,timed_out=policy.execute(command,state_dir,12,log)
        if code or timed_out or log.stat().st_size>65536:
            raise ValueError('native observer failed, timed out or oversized')
        result=json.loads(log.read_text())
        if not isinstance(result,dict) or not result.get('source'):
            raise ValueError('native observation source required')
        # Preserve returned host/timestamp. Never relabel a central snapshot.
        result['receipt']=str(log)
        return result
    except Exception as error:
        unknown['reason']='Native observer unavailable: '+type(error).__name__
        unknown['receipt']=str(log)
        return unknown


def existing_runner(job, result_path):
    """Delegate the enduring approved case to the stock lifecycle, never bare budget."""
    receipt={'status':'HELD','cleanup_verified':False,'reservation_started':False}
    if not job.get('profile') or not job.get('authorized_case_path'):
        receipt['reason']='Registered profile and enduring authorized case required'
        write(result_path,receipt)
        return receipt
    source=Path(job['runner_path']).resolve()
    if source.name!='bounded-foreground.py':
        raise ValueError('existing bounded foreground runner required')
    spec=importlib.util.spec_from_file_location('ogsd_existing_foreground',source)
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    case_path=Path(job['authorized_case_path'])
    try:
        if '_profile' in job['budget']:
            raise helper.Held('Job budget must remain exact numeric registered budget')
        budget=helper.budget(dict(job['budget'],_profile=job['profile']))
        case,case_budget=helper.authorized_case(case_path)
        if (case['profile']!=job['profile'] or case['budget']!=job['budget']
                or case['command']!=job['command'] or case['temp_root']!=job['temp_root']):
            raise helper.Held('Enduring case does not match exact queued job')
        if budget['wall']>job['window_seconds']:
            raise helper.Held('Runner wall must fit finite nightly window')
    except helper.Held as error:
        receipt['reason']=str(error);write(result_path,receipt)
        return receipt
    receipt.update(status='INCOMPLETE',profile=job['profile'],authorized_case_path=str(case_path))
    reserve,clear=helper.reserve_scope,helper.clear_reservation
    def record_reserve(info):
        receipt['reservation_started']=True
        receipt['generation']={k:info[k] for k in ('unit','cgroup','invocation','inode','pid','start')}
        capacity=getattr(helper,'CAPACITY',None)
        if capacity:receipt['capacity_id']=capacity['id']
        write(result_path,receipt)
        return reserve(info)
    def record_clear(info):
        clear(info)  # Stock same-generation empty/gone proof precedes this call.
        receipt['cleanup_verified']=True
        write(result_path,receipt)
    helper.reserve_scope,helper.clear_reservation=record_reserve,record_clear
    write(result_path,receipt)
    try:
        # Fresh admission is created by the existing route immediately before
        # payload. No stale queued receipt and no extra resource-wait window.
        code=helper.run_authorized_case(case_path,0)
        receipt['status']='PASS' if code==0 else 'FAIL'
        receipt['returncode']=code
        if helper.LAST_RUN:
            receipt['native']=helper.LAST_RUN
        elif code==0:
            # The stock route already validated a completed once-only case.
            completed=case_path.parent/('completed-'+helper.profiles.digest(case_path)+'.json')
            prior=json.loads(completed.read_text())
            receipt.update(native=prior,cleanup_verified=prior['same_generation_cleanup'],reused=True)
    except helper.Held as error:
        reason=str(error)
        receipt['status']='TIMEOUT' if 'wall deadline' in reason else 'FAIL' if receipt['reservation_started'] else 'HELD'
        receipt['reason']=reason
    finally:
        current=getattr(helper,'CAPACITY',None)
        if current and not receipt.get('capacity_id'):
            receipt['capacity_id']=current['id'];receipt['reservation_started']=True
        if receipt.get('capacity_id'):
            try:
                with helper.capacity_transaction() as rows:
                    removed=not any(row['request']['id']==receipt['capacity_id'] for row in rows)
                receipt['reservation_removed']=removed
                receipt['cleanup_verified']=receipt['cleanup_verified'] and removed
            except Exception:
                receipt['cleanup_verified']=False
        write(result_path,receipt)
    return receipt


def tick(state_dir, host, observation, runner=existing_runner, own_executor=None):
    state_dir.mkdir(parents=True,exist_ok=True,mode=0o700)
    lock = (state_dir/'queue.lock').open('a+')
    try:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:return {'status':'EXECUTOR_BUSY'}
        state_path=state_dir/'queue.json'
        state=json.loads(state_path.read_text()) if state_path.exists() else {'pending':[],'running':None,'completed':[]}
        if state['running']:
            return {'status':'CLEANUP_PENDING','job':state['running']['id']}
        decision=classify(observation,host,own_executor)
        if decision!='FREE':
            result={'status':'SKIP_ACTIVE' if decision=='ACTIVE' else 'DEFER_UNKNOWN',
                    'reservation_created':False,'host':host,'reason':observation.get('reason')}
            write(state_dir/'last-tick.json',result)
            return result
        if not state['pending']:return {'status':'EMPTY','host':host}
        job=state['pending'].pop(0)
        state['running']=job
        write(state_path,state)
        result_path=state_dir/'results'/f"{job['id']}-{uuid.uuid4().hex}.json"
        try:result=runner(job,result_path)
        except Exception as error:
            # Unknown cleanup retains the durable running claim. No replay.
            result={'status':'INCOMPLETE','cleanup_verified':False,'reason':type(error).__name__}
        if result.get('cleanup_verified') is not True and result.get('reservation_started') is not False:
            write(result_path,result)
            return {'status':'CLEANUP_PENDING','job':job['id'],'result':str(result_path)}
        state['running']=None
        if result['status']=='PASS':state['completed'].append({'id':job['id'],'result':str(result_path)})
        else:state['pending'].append(job)
        write(state_path,state)
        summary={'status':result['status'],'job':job['id'],'result':str(result_path),
                 'requeued':result['status']!='PASS','cleanup_verified':result.get('cleanup_verified',False)}
        write(state_dir/'last-tick.json',summary)
        return summary
    finally:
        lock.close()


def enqueue(state_dir, job):
    if not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}',job.get('id','')):raise ValueError('safe stable job id required')
    if type(job.get('window_seconds')) is not int or not 1<=job['window_seconds']<=86400:raise ValueError('finite nightly window of at most one day required')
    if not job.get('command') or not all(isinstance(x,str) for x in job['command']):raise ValueError('exact command required')
    if not job.get('budget') or not job.get('runner_path') or not job.get('temp_root'):raise ValueError('existing runner, budget and temporary lease root required')
    if not Path(job['runner_path']).is_absolute() or not Path(job['temp_root']).is_absolute():raise ValueError('absolute existing runner and temporary lease root required')
    wall=job['budget'].get('wall')
    if type(wall) is not int or not 1<=wall<=job['window_seconds']:raise ValueError('budget wall must fit finite nightly window')
    state_dir.mkdir(parents=True,exist_ok=True,mode=0o700)
    with (state_dir/'queue.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        path=state_dir/'queue.json'
        state=json.loads(path.read_text()) if path.exists() else {'pending':[],'running':None,'completed':[]}
        ids=[r['id'] for r in state['pending']+state['completed']+([state['running']] if state['running'] else [])]
        if job['id'] in ids:return {'status':'EXISTING','job':job['id']}
        state['pending'].append(job);write(path,state)
        return {'status':'QUEUED','job':job['id']}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['enqueue','tick','status'])
    parser.add_argument('--host',required=True,choices=HOSTS)
    parser.add_argument('--state-dir',type=Path)
    parser.add_argument('--job',type=Path)
    parser.add_argument('--herder',default='http://127.0.0.1:18787')
    parser.add_argument('--own-executor',nargs=2,metavar=('HARNESS','SESSION_ID'))
    parser.add_argument('--native-observer',nargs=argparse.REMAINDER,
                        help='Existing infra-owned observer argv; must be the last option')
    args=parser.parse_args()
    host=HOSTS[args.host]
    if socket.gethostname()!=host:raise SystemExit('exact local host identity required')
    state_dir=args.state_dir or Path.home()/'.local/state/gsd-agent-plugin/nightly'/args.host
    if args.action=='enqueue':result=enqueue(state_dir,json.loads(args.job.read_text()))
    elif args.action=='status':
        path=state_dir/'queue.json';result=json.loads(path.read_text()) if path.exists() else {'pending':[],'running':None,'completed':[]}
    else:
        observation=(observe_native(host,args.native_observer,state_dir) if args.native_observer
                     else observe(host,args.herder,args.own_executor))
        result=tick(state_dir,host,observation,own_executor=args.own_executor)
    print(json.dumps(result))
    return 0

if __name__=='__main__':raise SystemExit(main())
