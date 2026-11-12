import {readFile,mkdir,rm,lstat,open} from 'node:fs/promises';
import {resolve,relative,join,isAbsolute} from 'node:path';
import {createHash} from 'node:crypto';
import {writeJson} from './records.js';
import {setTimeout as delay} from 'node:timers/promises';

export type OperationPhase='prepared'|'running'|'grading'|'finalizing'|'completed'|'recoverable'|'blocked_unknown';
export interface Operation {
  schemaVersion:2;id:string;kind:'qualification'|'trial'|'loop'|'graph';sourceCommit:string;protocolSha256:string;
  identity:{entity:string;project:string;owner?:string;notebook?:string};phase:OperationPhase;
  createdAt:string;updatedAt:string;executionOutcome?:string;
  cleanup:'pending'|'verified'|'unknown';telemetry:'pending'|'complete'|'missing';publication:'pending'|'verified'|'failed'|'not_required';
  childPid?:number;sandboxIds:string[];reservationIds:string[];evidence:Record<string,{path:string;sha256:string}>;
  requests:Record<string,{status:'reserved'|'reported'|'unknown';inputTokens?:number;outputTokens?:number;payloadBytes:number}>;
  events:Array<{at:string;event:string;detail?:string}>;
}
/** The Python coordinator reads this same schema from the pinned checkout. */
let schemaPromise:Promise<any>|undefined;
export async function validateOperation(value:unknown){
  schemaPromise??=readFile(new URL('../operation.schema.json',import.meta.url),'utf8').catch(error=>{if(error.code!=='ENOENT')throw error;return readFile(new URL('../../operation.schema.json',import.meta.url),'utf8');}).then(JSON.parse);
  const schema=await schemaPromise;
  function validate(rule:any,item:any,path:string){
    if('const'in rule&&item!==rule.const||rule.enum&&!rule.enum.includes(item))throw new Error(`Invalid operation value at ${path}`);
    if(rule.type){const valid=rule.type==='object'?item!==null&&typeof item==='object'&&!Array.isArray(item):rule.type==='array'?Array.isArray(item):rule.type==='integer'?Number.isInteger(item):typeof item===rule.type;if(!valid)throw new Error(`Invalid operation type at ${path}`);}
    if(rule.minimum!=null&&item<rule.minimum||rule.pattern&&!new RegExp(rule.pattern).test(item))throw new Error(`Invalid operation constraint at ${path}`);
    if(rule.type==='object'){
      for(const key of rule.required??[])if(!(key in item))throw new Error(`Missing operation field ${path}.${key}`);
      for(const [key,child]of Object.entries(item)){if(child===undefined&&!rule.required?.includes(key))continue;const definition=rule.properties?.[key]??(typeof rule.additionalProperties==='object'?rule.additionalProperties:undefined);if(definition)validate(definition,child,`${path}.${key}`);}
    }
    if(rule.items)item.forEach((child:any,index:number)=>validate(rule.items,child,`${path}[${index}]`));
  }
  validate(schema,value,'operation');
  const op=value as Operation;
  for(const request of Object.values(op.requests))if(request.status==='reported'&&(request.inputTokens===undefined||request.outputTokens===undefined))throw new Error('Reported usage requires both token counts');
}

export function operationFile(root:string,id:string) {
  if(!/^[a-zA-Z0-9][a-zA-Z0-9_-]{0,100}$/.test(id))throw new Error('Invalid operation ID');
  return join(root,'operations',`${id}.json`);
}
export async function updateOperation(root:string,id:string,change:(op:Operation)=>void) {
  const file=operationFile(root,id),lock=file+'.lock';await mkdir(join(root,'operations'),{recursive:true});
  for(let i=0;;i++){try{await mkdir(lock);break;}catch(e){if((e as NodeJS.ErrnoException).code!=='EEXIST'||i===100)throw e;await delay(20);}}
  try {const op:Operation=JSON.parse(await readFile(file,'utf8'));await validateOperation(op);change(op);op.updatedAt=new Date().toISOString();await validateOperation(op);await writeJson(file,op);return op;}
  finally {await rm(lock,{recursive:true});}
}
export async function createOperation(root:string,seed:Pick<Operation,'id'|'kind'|'sourceCommit'|'protocolSha256'|'identity'>) {
  const file=operationFile(root,seed.id);await mkdir(join(root,'operations'),{recursive:true});
  // An existing operation is never interpreted as permission to launch again.
  const now=new Date().toISOString();
  const op:Operation={schemaVersion:2,...seed,phase:'prepared',createdAt:now,updatedAt:now,cleanup:'pending',telemetry:'pending',publication:seed.kind==='qualification'?'not_required':'pending',sandboxIds:[],reservationIds:[],requests:{},evidence:{},events:[]};
  // Exclusive creation survives checkpoint archives, which need not retain empty
  // lock directories. An interrupted creation blocks recovery rather than replay.
  await validateOperation(op);const handle=await open(file,'wx',0o600);
  try {await handle.writeFile(JSON.stringify(op,null,2)+'\n');await handle.sync();}finally{await handle.close();}
  return op;
}
export async function evidencePath(root:string,ref:string) {
  if(isAbsolute(ref)||ref.includes('\\')||ref.includes(':')||ref.split('/').some(p=>p==='..'||p==='.'||p===''))throw new Error('Unsafe evidence reference');
  const target=resolve(root,ref);if(relative(resolve(root),target).startsWith('..'))throw new Error('Evidence escapes root');
  let here=resolve(root);for(const part of ref.split('/')){here=join(here,part);if((await lstat(here)).isSymbolicLink())throw new Error('Evidence symlink rejected');}
  return target;
}
export async function evidenceReference(root:string,file:string) {
  const path=relative(resolve(root),resolve(file)).split('\\').join('/');
  const verified=await evidencePath(root,path);return {path,sha256:createHash('sha256').update(await readFile(verified)).digest('hex')};
}
export async function verifyEvidence(root:string,ref:{path:string;sha256:string}) {
  const file=await evidencePath(root,ref.path);
  if(createHash('sha256').update(await readFile(file)).digest('hex')!==ref.sha256)throw new Error('Evidence checksum mismatch');return file;
}
