import {join} from 'node:path';
import {readFile,mkdir} from 'node:fs/promises';
import {randomUUID} from 'node:crypto';
import {createAppHooks as hooks} from '../runtime/app.js';
import {Budget,estimate} from '../runtime/budget.js';
import {requirePrivateProject,config} from '../runtime/config.js';
import {writeJson} from '../runtime/records.js';
import {makeRequest} from '../workshop/inference.js';
import {observe} from '../workshop/instrumentation.js';

export async function createAppHooks(variant:string) {
  const c=config();await requirePrivateProject(c);
  const prices=JSON.parse(await readFile(join(process.cwd(),'workshop/pricing.json'),'utf8'));
  const folder=process.env.FORGE_APP_EVIDENCE_DIR||join(process.cwd(),'.workshop-evidence');await mkdir(folder,{recursive:true});
  const id=process.env.FORGE_CONVERSATION_ID||`workshop-app-${randomUUID()}`;
  const remote=process.env.WORKSHOP_PRE_RESERVED==='true';
  const maxRequests=Number(process.env.WORKSHOP_MAX_REQUESTS||'24');
  if(!Number.isInteger(maxRequests)||maxRequests<1||maxRequests>24)throw new Error('Invalid request allowance');
  const ledger=new Budget(join(folder,'budget.json'),c.budgetUsd);
  const requests:Record<string,unknown>={};
  const save=()=>writeJson(join(folder,'request-receipts.json'),{id,requests});
  return hooks(variant,{conversationId:id,evidencePath:join(folder,'app.json'),maxRequests,
    attributes:{'course.protocol':'workshop-v1','course.snapshot':process.env.WORKSHOP_SNAPSHOT||'local-unpublished'},
    requestFactory:makeRequest,instrumentTool:observe,
    async beforeRequest(number,bytes){
      if(!remote)await ledger.reserve({[`${id}-${number}`]:estimate(c.maxInputBytes,1024,0,prices)});
      requests[number]={status:'dispatched',payloadBytes:bytes};await save();
    },
    async afterRequest(number,inputTokens,outputTokens){
      const complete=inputTokens!==undefined&&outputTokens!==undefined;
      requests[number]={status:complete?'reported':'unknown',inputTokens,outputTokens};await save();
      if(!remote)await ledger.settle(`${id}-${number}`,complete?estimate(inputTokens!,outputTokens!,0,prices):null);
    },
  });
}
