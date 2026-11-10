// Held-out probe loaded into the real benchmark process and its Node children.
const Module=require('node:module');const fs=require('node:fs');
const original=Module._load;const seen=new WeakSet();
Module._load=function(request,parent,isMain){
  const value=original.apply(this,arguments);
  let resolved='';try{resolved=Module._resolveFilename(request,parent);}catch{}
  if(/\/dist\/services\//.test(resolved))for(const exported of Object.values(value)){
    if(typeof exported!=='function'||!exported.prototype||seen.has(exported))continue;seen.add(exported);
    for(const method of ['importDocument','startIndexing','ask']){
      const fn=exported.prototype[method];if(typeof fn!=='function')continue;
      exported.prototype[method]=function(...args){
        fs.appendFileSync('/tmp/grade/benchmark-calls.jsonl',JSON.stringify({service:exported.name,method,at:Date.now()})+'\n');
        return fn.apply(this,args);
      };
    }
  }
  return value;
};
