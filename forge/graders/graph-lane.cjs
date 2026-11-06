// Independent post-patch verification lanes; no agent is running in this workspace.
const {execFileSync}=require('node:child_process');const fs=require('node:fs');const path=require('node:path');const assert=require('node:assert/strict');
const lane=process.argv[2],cwd='/workspace/task',checks=[];
async function check(name,fn){try{await fn();checks.push({name,passed:true});}catch(error){checks.push({name,passed:false,error:String(error),stdout:String(error.stdout??'').slice(-6000),stderr:String(error.stderr??'').slice(-6000)});}}
(async()=>{
 await check('build',()=>{for(const args of [['/opt/app/node_modules/typescript/bin/tsc','-p','tsconfig.node.json'],['/opt/app/node_modules/vite/bin/vite.js','build']])execFileSync('node',args,{cwd,timeout:90000});});
 if(checks[0].passed && lane==='services')await check('patch preserves long-document text and grounded citations',async()=>{
   const load=n=>require(path.join(cwd,'dist/services',n));const p=new (load('persistence-service').PersistenceService)('/tmp/graph-data');
   const d=new (load('document-service').DocumentService)(p),i=new (load('indexing-service').IndexingService)(p),q=new (load('qa-service').QaService)(p,i);
   const text=Array.from({length:8},(_,n)=>`Architecture marker ${n}: indexing preserves source paragraphs and citations. `.repeat(5)).join('\n\n');fs.writeFileSync('/tmp/graph-fixture.txt',text);d.importDocument('/tmp/graph-fixture.txt');await i.startIndexing();
   const chunks=i.getAllChunks();assert.ok(chunks.length>1);assert.ok(chunks.every(c=>c.content.trim()));for(let n=0;n<8;n++)assert.ok(chunks.some(c=>c.content.includes(`marker ${n}`)));
   const a=await q.ask('architecture indexing');assert.ok(a.citations.length);for(const c of a.citations)assert.ok(text.includes(c.excerpt));
   const guard=path.join(cwd,'scripts/check-architecture.sh');assert.ok(fs.existsSync(guard));execFileSync('bash',[guard],{cwd,timeout:10000});
   const probe=path.join(cwd,'src/renderer/graph-boundary-probe.ts');fs.writeFileSync(probe,"import * as fs from 'fs'; export const violation=fs.readFileSync;\n");let rejected=false;try{execFileSync('bash',[guard],{cwd,timeout:10000});}catch{rejected=true;}finally{fs.unlinkSync(probe);}assert.ok(rejected,'architecture guard must detect Node imports');
 });
 if(checks[0].passed && lane==='electron')await check('actual Electron preload and question interaction',async()=>{
   const {_electron}=require('/opt/app/node_modules/playwright');const app=await _electron.launch({executablePath:require('/opt/app/node_modules/electron'),args:['--no-sandbox',path.join(cwd,'dist/main/main.js'),'--user-data-dir=/tmp/graph-ui'],timeout:30000});
   try{const page=await app.firstWindow();await page.getByRole('heading',{name:'Knowledge Base',exact:true}).waitFor();assert.equal(await page.evaluate(()=>typeof window.knowledgeBase.qa.ask),'function');
     await page.locator('input[type=text]').fill('What architecture is used?');await page.getByRole('button',{name:'Ask',exact:true}).click();await page.waitForFunction(async()=>(await window.knowledgeBase.qa.history()).length===1,{},{timeout:10000});await page.screenshot({path:'/tmp/graph-electron.png'});
   }finally{await app.close();}
 });
 if(!['services','electron'].includes(lane))throw new Error('Invalid lane');
 fs.writeFileSync('/tmp/graph-grade.json',JSON.stringify({lane,checks,passed:checks.length===2&&checks.every(c=>c.passed)},null,2));
})().catch(error=>{fs.writeFileSync('/tmp/graph-grade.json',JSON.stringify({lane,passed:false,error:String(error)}));process.exitCode=2;});
