import {execFile} from 'node:child_process';
import {join} from 'node:path';
import {createRequire} from 'node:module';
import {workshopCourseRoot} from './workshop-workspace.js';
/** Pure student policy runs without credentials in a bounded child. Never give
 * its output authority over accounting, cleanup, approval or hard bounds. */
export async function workshopPolicy(source:string,method:string,observation:unknown){
  const require=createRequire(join(workshopCourseRoot,'forge/workshop/base/package.json'));
  const compiled=require('esbuild').transformSync(source,{loader:'ts',format:'cjs'}).code;
  const script=`const vm=require('node:vm');const payload=JSON.parse(require('node:fs').readFileSync(0,'utf8'));
const context=vm.createContext({module:{exports:{}}});
new vm.Script(payload.compiled).runInContext(context,{timeout:500});
context.input=payload.observation;
const result=new vm.Script('module.exports['+JSON.stringify(payload.method)+'](input)').runInContext(context,{timeout:500});
process.stdout.write(JSON.stringify(result));`;
  const stdout=await new Promise<string>((resolve,reject)=>{
    const child=execFile(process.execPath,['--permission','--input-type=commonjs','-e',script],{env:{},timeout:3000,maxBuffer:200000},(error,stdout)=>error?reject(error):resolve(stdout));
    child.stdin!.end(JSON.stringify({compiled,method,observation}));
  });
  return JSON.parse(stdout);
}
