import {hostname} from 'node:os';
import {readFile} from 'node:fs/promises';
import {join,relative} from 'node:path';
import {createHash} from 'node:crypto';
import {Budget,estimate} from './budget.js';
import {config} from './config.js';
import {createOperation,updateOperation,operationFile,evidenceReference,evidencePath,type Operation} from './operations.js';
import type {SandboxJournal} from './sandbox.js';
import type {RequestUsage} from './pi.js';
import {writeJson} from './records.js';

/** One operation owns every external request and resource reservation. */
export class Execution {
  readonly c=config();readonly incremental=process.env.FORGE_BUDGET_MODE==='incremental';
  readonly budget:Budget;
  readonly journals=new Map<string,string>();
  constructor(readonly root:string,readonly id:string,readonly p:any){this.budget=new Budget(join(root,'budget.json'),this.c.budgetUsd);}
  async begin(kind:Operation['kind'],sourceCommit:string){
    const seed={id:this.id,kind,sourceCommit,protocolSha256:createHash('sha256').update(JSON.stringify(this.p)).digest('hex'),identity:{entity:this.c.entity,project:this.c.project,owner:process.env.FORGE_NOTEBOOK_OWNER,notebook:process.env.FORGE_NOTEBOOK_ID}};
    try{await createOperation(this.root,seed);}catch(error){if((error as NodeJS.ErrnoException).code!=='EEXIST')throw error;}
    await updateOperation(this.root,this.id,op=>{
      if(op.phase!=='prepared'||op.sourceCommit!==sourceCommit||JSON.stringify(op.identity)!==JSON.stringify(seed.identity))throw new Error('Existing operation requires recovery; refusing duplicate execution');
      op.phase='running';op.childPid=process.pid;
      op.events.push({at:new Date().toISOString(),event:'execution_started',detail:hostname()});
    });
    const file=join(this.root,this.id,'execution-configuration.json');await writeJson(file,{sourceCommit,protocol:this.p,incremental:this.incremental,identity:seed.identity});
    const ref=await evidenceReference(this.root,file);await updateOperation(this.root,this.id,op=>{op.evidence.configuration=ref;});
  }
  async event(event:string,detail?:string){await updateOperation(this.root,this.id,op=>{op.events.push({at:new Date().toISOString(),event,detail});});}
  private async reserve(id:string,cost:number){
    await updateOperation(this.root,this.id,op=>{if(!op.reservationIds.includes(id))op.reservationIds.push(id);});
    if(this.incremental)await this.budget.reserve({[id]:cost});
  }
  requestHooks(phase:string){return {
    beforeRequest:async(number:number,payloadBytes:number)=>{
      const key=`${phase}-${number}`,reservation=`${this.id}-request-${key}`;
      await this.reserve(reservation,estimate(this.p.maxInputBytes,this.p.maxOutputTokens,0,this.p.pricing));
      await updateOperation(this.root,this.id,op=>{if(op.requests[key])throw new Error('Duplicate request dispatch');op.requests[key]={status:'reserved',payloadBytes};});
    },
    afterRequest:async(usage:RequestUsage)=>{
      const key=`${phase}-${usage.request}`,reservation=`${this.id}-request-${key}`;
      await updateOperation(this.root,this.id,op=>{
        const prior=op.requests[key];if(!prior)throw new Error('Usage has no dispatched request');
        if(prior.status==='reported'&&(!usage.complete||prior.inputTokens!==usage.inputTokens||prior.outputTokens!==usage.outputTokens))throw new Error('Conflicting request usage');
        op.requests[key]={status:usage.complete?'reported':'unknown',payloadBytes:usage.payloadBytes,inputTokens:usage.complete?usage.inputTokens:undefined,outputTokens:usage.complete?usage.outputTokens:undefined};
      });
      if(this.incremental)await this.budget.settle(reservation,usage.complete?estimate(usage.inputTokens,usage.outputTokens,0,this.p.pricing):null);
    },
  };}
  workspace(label:string,dir:string){
    const reservation=`${this.id}-sandbox-${label}`,file=join(dir,'sandbox.json');this.journals.set(label,file);
    return {
      beforeLaunch:async()=>{
        await this.reserve(reservation,estimate(0,0,1500,this.p.pricing));
        await this.event('sandbox_launch',relative(this.root,file));
      },
      onJournal:async(j:SandboxJournal)=>{
        await updateOperation(this.root,this.id,op=>{for(const id of [...(j.sandboxId?[j.sandboxId]:[]),...(j.recoveredSandboxIds??[])])if(!op.sandboxIds.includes(id))op.sandboxIds.push(id);});
        if(j.state==='terminated'&&j.requestedAt&&j.terminatedAt){
          const seconds=(Date.parse(j.terminatedAt)-Date.parse(j.requestedAt))/1000;
          if(this.incremental)await this.budget.settle(reservation,estimate(0,0,seconds,this.p.pricing));
          const ref=await evidenceReference(this.root,file);
          await updateOperation(this.root,this.id,op=>{op.evidence[`sandbox-${label}`]=ref;});
        }
      },
    };
  }
  async finish(outcome:string){
    const op:Operation=JSON.parse(await readFile(operationFile(this.root,this.id),'utf8'));
    let seconds=0,cleanup=true;
    for(const event of op.events.filter(e=>e.event==='child_launch')){
      try{
        const file=await evidencePath(this.root,event.detail??''),child=JSON.parse(await readFile(file,'utf8'));
        if(child.cleanupVerified!==true)cleanup=false;
        const ref=await evidenceReference(this.root,file);await updateOperation(this.root,this.id,current=>{current.evidence[`child-${Object.keys(current.evidence).length}`]=ref;});
      }catch(error){if((error as NodeJS.ErrnoException).code!=='ENOENT')throw error;cleanup=false;}
    }
    for(const [label,file]of this.journals){
      const j:SandboxJournal=JSON.parse(await readFile(file,'utf8'));
      if(j.requestedAt){
        if(j.state!=='terminated'||!j.terminatedAt){cleanup=false;if(this.incremental)await this.budget.settle(`${this.id}-sandbox-${label}`,null);}
        else seconds+=(Date.parse(j.terminatedAt)-Date.parse(j.requestedAt))/1000;
      }else if(this.incremental){
        const ledger=JSON.parse(await readFile(this.budget.file,'utf8')),id=`${this.id}-sandbox-${label}`;
        if(id in ledger.reservations)await this.budget.settle(id,0);
      }
    }
    const complete=Object.values(op.requests).every(r=>r.status==='reported');
    if(this.incremental)for(const [key,r]of Object.entries(op.requests))if(r.status!=='reported')await this.budget.settle(`${this.id}-request-${key}`,null);
    const inputTokens=Object.values(op.requests).reduce((s,r)=>s+(r.inputTokens??0),0),outputTokens=Object.values(op.requests).reduce((s,r)=>s+(r.outputTokens??0),0);
    await updateOperation(this.root,this.id,current=>{current.cleanup=cleanup?'verified':'unknown';current.telemetry=complete?'complete':'missing';current.executionOutcome=outcome;current.phase=cleanup&&complete?'finalizing':'blocked_unknown';});
    return {inputTokens,outputTokens,sandboxSeconds:seconds,cleanupVerified:cleanup,usageComplete:complete,estimatedCostUsd:cleanup&&complete?estimate(inputTokens,outputTokens,seconds,this.p.pricing):null};
  }
}
