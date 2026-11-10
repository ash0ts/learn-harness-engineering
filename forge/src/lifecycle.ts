import {spawn} from 'node:child_process';
import {open} from 'node:fs/promises';
import {setTimeout as delay} from 'node:timers/promises';
import {writeJson} from './records.js';

export async function deadline<T>(work:Promise<T>,ms:number,label:string):Promise<T> {
  let timer:NodeJS.Timeout|undefined;
  try {return await Promise.race([work,new Promise<never>((_,reject)=>{timer=setTimeout(()=>reject(new Error(`${label} timed out after ${ms}ms`)),ms);})]);}
  finally {clearTimeout(timer);}
}

export interface ChildResult {exitCode:number;signal:string|null;forced:boolean;startedAt:string;finishedAt:string;cleanupVerified?:boolean;error?:string}
/** Bound both the work and its shutdown; a forced exit is always evidence. */
export async function boundedChild(executable:string,args:string[],options:{cwd:string;log?:string;receipt?:string;timeoutMs:number;graceMs?:number;env?:NodeJS.ProcessEnv;signal?:AbortSignal}):Promise<ChildResult> {
  const file=options.log?await open(options.log,'a',0o600):undefined;
  const startedAt=new Date().toISOString();let timer:NodeJS.Timeout|undefined,killTimer:NodeJS.Timeout|undefined;
  let forced=false;
  const child=spawn(executable,args,{cwd:options.cwd,env:options.env??process.env,detached:true,stdio:['ignore',file?.fd??'inherit',file?.fd??'inherit']});
  const kill=(signal:NodeJS.Signals)=>{if(child.pid)try{process.kill(-child.pid,signal);}catch(error){if((error as NodeJS.ErrnoException).code!=='ESRCH')throw error;}};
  const stop=()=>{if(forced)return;forced=true;kill('SIGTERM');killTimer=setTimeout(()=>kill('SIGKILL'),options.graceMs??15000);};
  options.signal?.addEventListener('abort',stop,{once:true});
  try {
    const result=await new Promise<ChildResult>((resolve,reject)=>{
      child.once('error',error=>resolve({exitCode:1,signal:null,forced:false,startedAt,finishedAt:new Date().toISOString(),cleanupVerified:!child.pid,error:String(error)}));
      child.once('close',(code,signal)=>resolve({exitCode:code??1,signal,forced,startedAt,finishedAt:new Date().toISOString()}));
      timer=setTimeout(stop,options.timeoutMs);
      if(options.signal?.aborted)stop();
    });
    clearTimeout(timer);clearTimeout(killTimer);
    const alive=()=>{if(!child.pid)return false;try{process.kill(-child.pid,0);return true;}catch(error){if((error as NodeJS.ErrnoException).code==='ESRCH')return false;throw error;}};
    if(alive()){
      result.forced=true;kill('SIGTERM');const until=Date.now()+(options.graceMs??15000);
      while(alive()&&Date.now()<until)await delay(25);
      if(alive()){kill('SIGKILL');const end=Date.now()+2000;while(alive()&&Date.now()<end)await delay(25);}
    }
    result.cleanupVerified=!alive();result.finishedAt=new Date().toISOString();
    if(!result.cleanupVerified){result.forced=true;result.error='Child process group termination is unverified';}
    if(options.receipt)await writeJson(options.receipt,result);
    return result;
  } finally {clearTimeout(timer);clearTimeout(killTimer);options.signal?.removeEventListener('abort',stop);await file?.close();}
}
