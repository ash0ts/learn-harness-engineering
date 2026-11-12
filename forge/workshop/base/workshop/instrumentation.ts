import type {tracing} from '@coreweave/forge-sdk/agentlens';
/** Called inside the supplied conversation/turn and runIsolated lifecycle. */
export function observe<T>(sdk:typeof tracing,name:string,input:unknown,work:()=>T):T {
  const span=sdk.startTool({name:'student.'+name,args:JSON.stringify(input)});
  const done=(result:unknown)=>{
    const chunks=Array.isArray(result)?result:undefined;
    span.end({result:JSON.stringify({value:result,chunkCount:chunks?.length,
      nonemptyCount:chunks?.filter(c=>typeof c?.content==='string'&&c.content.trim()).length})});
  };
  try {
    const value=work();
    if(value instanceof Promise)return value.then(result=>{done(result);return result;},error=>{
      span.end({error,errorType:'service_error'});throw error;
    }) as T;
    done(value);return value;
  }catch(error){span.end({error:error as Error,errorType:'service_error'});throw error;}
}
