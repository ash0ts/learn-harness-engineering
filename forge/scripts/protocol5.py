"""Freeze and run the separate revision-five cohort; no paid work by default.

The durable schedule preserves IDs and stops on unknown accounting. An interrupted
step must be reconciled before an explicit resume. Human decisions stay in the graph
CLI; this coordinator never approves a candidate. Run from the frozen checkout.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import signal
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]

def read(path):
    return json.loads(path.read_text())

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    temporary.replace(path)

def freeze(destination):
    if destination.exists():
        raise RuntimeError('A frozen schedule already exists; use its IDs and source')
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if subprocess.check_output(['git', 'diff', '--name-only', 'HEAD', '--', 'forge/src', 'forge/tasks', 'forge/graders', 'forge/protocol.json', 'forge/package-lock.json'], cwd=ROOT):
        raise RuntimeError('Commit runtime and measurement changes before freezing')
    paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', source, '--', 'forge/src', 'forge/tasks', 'forge/graders', 'forge/fixtures', 'forge/protocol.json', 'forge/package-lock.json', 'forge/sandbox/package-lock.json', 'forge/scripts/protocol5.py'], cwd=ROOT, text=True).splitlines()
    hashes = {path:hashlib.sha256(subprocess.check_output(['git','show',source+':'+path],cwd=ROOT)).hexdigest() for path in paths}
    def step(kind, **values):
        return {'id':str(uuid.uuid4()), 'kind':kind, 'status':'prepared', **values}
    steps = [step('qualification')]
    steps += [step('control', project=f'project-{i:02}', control=kind) for i in range(1,9) for kind in ('baseline','reference','regression')]
    steps += [step('comparisons')]
    # Rotate controller order per repeat; the timer's persisted deadline is 7200s.
    modes = ['goal','timer','maker-checker']
    for repeat in range(3):
        steps += [step('loop', mode=mode, repeat=repeat+1) for mode in modes[repeat:] + modes[:repeat]]
    steps += [step('graph', repeat=i) for i in range(1,4)]
    steps += [step('verification-pairs', trial='REQUIRES_QUALIFIED_PROJECT_08_TRIAL')]
    result = {'schemaVersion':1,'protocolRevision':5,'sourceCommit':source,'inputsSha256':hashes,'protocol':read(ROOT/'forge/protocol.json'),
        'targets':{'comparisons':39,'loopControllers':9,'realTwoHourTimers':3,'graphs':3,'verificationPairs':3,'newHumanDecisions':2},
        'steps':steps,'humanDecisions':'Use graph --decision with a newly reviewed checksum; never inherited from older cohorts'}
    write(destination,result)
    return result

def command(step, output, source):
    prefix = ['node','--import',str(ROOT/'forge/node_modules/tsx/dist/loader.mjs'),str(ROOT/'forge/src/cli.ts')]
    identifier = step['id']
    if step['kind']=='qualification':
        args=['doctor','--qualify','--operation-id','qualification-'+identifier]
    elif step['kind']=='control':
        args=['controls','--project',step['project'],'--kind',step['control'],'--source',source,'--operation-id',f"control-{step['project']}-{step['control']}-{identifier}"]
    elif step['kind']=='comparisons':
        args=['compare','--source',source,'--repeats','3']
    elif step['kind']=='loop':
        args=['loop','--mode',step['mode'],'--operation-id',identifier,'--checkpoint',str(output/f"cohort-loop-{identifier}-checkpoint.json"),
              '--duration-seconds','7200' if step['mode']=='timer' else '1800','--max-rounds','8' if step['mode']=='timer' else '3']
    elif step['kind']=='verification-pairs':
        args=['graph-pairs','--trial',step['trial']]
    else:
        args=['graph','--operation-id',identifier,'--checkpoint',str(output/f"cohort-graph-{identifier}-checkpoint.json")]
    return prefix+args+['--output',str(output),'--execute']

def run(schedule_file, output):
    schedule=read(schedule_file)
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if source != schedule['sourceCommit']:
        raise RuntimeError('Use the exact frozen checkout; evidence lives separately in --output')
    for path,digest in schedule['inputsSha256'].items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=digest:
            raise RuntimeError('Frozen input changed: '+path)
    ledger=output/'budget.json'
    def gate():
        if ledger.exists():
            state=read(ledger)
            if state.get('halted') or state.get('reservations'):
                raise RuntimeError('Unresolved accounting: recover/reconcile before any paid launch')
    gate()
    if any(s['status'] in ('running','interrupted') for s in schedule['steps']):
        raise RuntimeError('A scheduled step is interrupted. Recover its existing operations; do not replay it')
    for step in schedule['steps']:
        if step['status']=='completed':
            continue
        if step['status']!='prepared':
            raise RuntimeError('Stopped step requires evidence review; a new qualification is a new explicit operation')
        gate()
        if step['kind']=='verification-pairs':
            candidates=[read(path) for path in output.glob('*/trial.json')]
            candidates=[r for r in candidates if r.get('project')=='project-08' and r.get('sourceCommit')==source and r.get('outcome')=='passed' and r.get('protocol',{}).get('protocolRevision')==5]
            if not candidates:
                step.update(status='blocked',error='No qualified Project 08 patch; no pairs launched');write(schedule_file,schedule);break
            step['trial']=sorted(candidates,key=lambda r:r['id'])[0]['id']
        step.update(status='running',startedAt=time.time());write(schedule_file,schedule)
        log=output/f"cohort-{step['id']}.log";log.parent.mkdir(parents=True,exist_ok=True)
        env={**os.environ,'FORGE_RESULTS_DIR':str(output)}
        step['reportsBefore']=[p.name for p in output.glob('report-*.json')];write(schedule_file,schedule)
        child=None
        try:
            with log.open('w') as stream:
                child=subprocess.Popen(command(step,output,source),cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
                step['pid']=child.pid;write(schedule_file,schedule)
                code=child.wait(timeout=7800 if step['kind']=='loop' else 60300 if step['kind']=='comparisons' else 3600)
            gate()
            if code==0 and step['kind']=='comparisons':
                reports=[p for p in output.glob('report-*.json') if p.name not in step['reportsBefore']]
                if len(reports)!=1 or read(reports[0]).get('completedTrials')!=39 or read(reports[0]).get('stopReason'):
                    raise RuntimeError('Comparison block schedule did not finish; retain actual counts and recover evidence')
            if code==0 and step['kind'] in ('loop','graph'):
                checkpoint=read(output/f"cohort-{step['kind']}-{step['id']}-checkpoint.json")
                if checkpoint.get('node',checkpoint.get('status')) in ('blocked','infrastructure_recovery'):
                    raise RuntimeError('Controller needs recovery; subsequent launches stopped')
            step.update(status='completed' if code==0 else 'failed',exitCode=code,finishedAt=time.time())
            write(schedule_file,schedule)
            if code:break
        except BaseException as error:
            if child and child.poll() is None:
                os.killpg(child.pid,signal.SIGTERM)
                try:child.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid,signal.SIGKILL)
                    child.wait(timeout=10)
                step['forcedShutdown']=True
            step.update(status='interrupted',error=str(error));write(schedule_file,schedule)
            raise
    return schedule

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['freeze','run','commands'])
    parser.add_argument('--schedule',type=Path,required=True)
    parser.add_argument('--output',type=Path,default=ROOT/'forge/local-results/protocol-v5')
    parser.add_argument('--execute',action='store_true')
    args=parser.parse_args();output=args.output.resolve()
    if args.action=='freeze':
        result=freeze(args.schedule)
        print(json.dumps({'sourceCommit':result['sourceCommit'],'targets':result['targets']}))
    elif args.action=='commands':
        schedule=read(args.schedule)
        print(json.dumps([{'id':step['id'],'argv':command(step,output,schedule['sourceCommit'])} for step in schedule['steps']],indent=2))
    else:
        if not args.execute:raise RuntimeError('Paid campaign requires --execute')
        result=run(args.schedule,output);print(json.dumps({'steps':[(s['kind'],s['status']) for s in result['steps']]}))

if __name__=='__main__':main()
