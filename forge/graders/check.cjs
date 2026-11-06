// Delivered only after the actor exits, in a fresh grading workspace.
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const assert = require('node:assert/strict');
const {execFileSync} = require('node:child_process');
const task = process.argv[2];
const cwd = '/workspace/task';
const output = '/tmp/grade';
fs.mkdirSync(output,{recursive:true});
const checks=[];
async function check(name, fn) {
  try {await fn();checks.push({name,passed:true});}
  catch(error){checks.push({name,passed:false,error:String(error)});}
}
const command = (args) => execFileSync(args[0],args.slice(1),{cwd,timeout:90000,encoding:'utf8',stdio:'pipe'});
const save = () => fs.writeFileSync(path.join(output,'result.json'),JSON.stringify({schemaVersion:1,task,checks,passed:checks.every(c=>c.passed)},null,2));

(async()=>{
  await check('strict compile and renderer build',()=>{
    for(const args of [
      ['node','/opt/app/node_modules/typescript/bin/tsc','--noEmit','-p','tsconfig.node.json'],
      ['node','/opt/app/node_modules/typescript/bin/tsc','--noEmit','-p','tsconfig.json'],
      ['node','/opt/app/node_modules/typescript/bin/tsc','-p','tsconfig.node.json'],
      ['node','/opt/app/node_modules/vite/bin/vite.js','build'],
    ]) fs.appendFileSync(path.join(output,'build.log'),command(args));
  });
  if(!checks[0].passed){save();return;}
  const load=name=>require(path.join(cwd,'dist/services',name));
  const {PersistenceService}=load('persistence-service');
  const {DocumentService}=load('document-service');
  const {IndexingService}=load('indexing-service');
  const {QaService}=load('qa-service');
  const data=fs.mkdtempSync(path.join(os.tmpdir(),'heldout-data-'));
  const fixture=path.join(data,'heldout.txt');
  const content=Array.from({length:7},(_,i)=>`Paragraph ${i}: Durable indexing preserves paragraph text and source citations. A layered architecture isolates renderer code from filesystem access. This paragraph contains the unique measurement token evidence-${i}. `.repeat(2)).join('\n\n');
  fs.writeFileSync(fixture,content);
  const persistence=new PersistenceService(path.join(data,'store'));
  const documents=new DocumentService(persistence);
  const index=new IndexingService(persistence);
  const qa=new QaService(persistence,index);
  let imported;
  await check('real import and persistence after reconstruction',()=>{
    imported=documents.importDocument(fixture);
    assert.equal(new DocumentService(new PersistenceService(path.join(data,'store'))).listDocuments()[0].id,imported.id);
    assert.equal(documents.getDocumentContent(imported.id),content);
  });
  await check('actual indexing keeps every nonempty paragraph',async()=>{
    await index.startIndexing(); const chunks=index.getAllChunks();
    fs.writeFileSync(path.join(output,'chunks.json'),JSON.stringify(chunks,null,2));
    assert.ok(chunks.length>1); assert.ok(chunks.every(c=>c.content.trim().length));
    for(let i=0;i<7;i++)assert.ok(chunks.some(c=>c.content.includes(`evidence-${i}`)));
  });
  await check('actual retrieval and Q&A persist two turns',async()=>{
    const responses=[];
    for(const question of ['How does indexing work?','What architecture is used?'])responses.push(await qa.ask(question));
    assert.equal(qa.getHistory().length,2);
    assert.ok(responses.every(r=>r.answer.length>0 && r.citations.length>0));
    for(const r of responses)for(const c of r.citations)assert.ok(content.includes(c.excerpt));
    fs.writeFileSync(path.join(output,'qa.json'),JSON.stringify(responses,null,2));
  });
  if(task==='project-03') {
    await check('extracted metadata',()=>{
      const meta=documents.getDocument(imported.id).metadata;
      for(const field of ['wordCount','lineCount','paragraphCount'])assert.ok(Number(meta?.[field])>0,field);
    });
    await check('single-document indexing is reflected in status',async()=>{
      const p=new PersistenceService(path.join(data,'single'));const d=new DocumentService(p);const i=new IndexingService(p);
      const doc=d.importDocument(fixture);await i.startIndexing(doc.id);assert.equal(i.getStatus().currentIndexed,1);
    });
  }
  if(task==='project-04') await check('architecture checker rejects a seeded boundary violation',()=>{
    const guard=path.join(cwd,'scripts/check-architecture.sh');assert.ok(fs.existsSync(guard));
    command(['bash',guard]);
    const violation=path.join(cwd,'src/renderer/forge-boundary-probe.ts');fs.writeFileSync(violation,"import * as fs from 'fs'; export const broken = fs.readFileSync;\n");
    let rejected=false;try{command(['bash',guard]);}catch{rejected=true;}finally{fs.unlinkSync(violation);}
    assert.ok(rejected,'architecture checker accepted a Node import in the renderer');
  });
  await check('Electron window, preload, import, indexing and question UI under Xvfb',async()=>{
    const {_electron}=require('/opt/app/node_modules/playwright');
    const app=await _electron.launch({executablePath:require('/opt/app/node_modules/electron'),args:['--no-sandbox',path.join(cwd,'dist/main/main.js'),`--user-data-dir=${path.join(data,'electron')}`],timeout:30000});
    try {
      const page=await app.firstWindow();await page.waitForLoadState('domcontentloaded');
      await page.getByRole('heading',{name:'Knowledge Base',exact:true}).waitFor({timeout:15000});
      assert.equal(await page.evaluate(()=>typeof window.knowledgeBase.documents.import),'function');
      assert.equal(await page.evaluate(()=>typeof window.require),'undefined');
      if(task==='project-02') {
        await app.evaluate(({dialog},file)=>{dialog.showOpenDialog=async()=>({canceled:false,filePaths:[file]});},fixture);
        const input=page.locator('input[type=file]');
        if(await input.count())await input.setInputFiles(fixture);
        else await page.getByRole('button',{name:/import/i}).first().click();
        await page.waitForFunction(async()=> (await window.knowledgeBase.documents.list()).length>0,{},{timeout:10000});
        const result=await page.evaluate(async()=>{const d=(await window.knowledgeBase.documents.list())[0];return window.knowledgeBase.documents.getContent(d.id);});
        assert.equal(result,content);
      } else await page.evaluate(file=>window.knowledgeBase.documents.import(file),fixture);
      await page.evaluate(()=>window.knowledgeBase.indexing.start());
      await page.getByRole('button',{name:'Refresh',exact:true}).click();
      await page.getByText('heldout',{exact:true}).first().waitFor({timeout:10000});
      const questions=['How does indexing preserve paragraphs?','What architecture is used?'];
      for(const q of questions){
        await page.locator('input[type=text]').first().fill(q);
        await page.getByRole('button',{name:'Ask',exact:true}).click();
        await page.waitForFunction(async question=>(await window.knowledgeBase.qa.history()).some(h=>h.question===question),q,{timeout:10000});
      }
      if(task==='project-05') {
        await page.getByRole('button',{name:/conversation|history/i}).first().click();
        const history=await page.evaluate(()=>window.knowledgeBase.qa.history());
        const body=await page.locator('body').innerText();
        for(const h of history){assert.ok(body.includes(h.question),'missing question');assert.ok(body.includes(h.response.answer),'truncated answer');}
        assert.ok(body.indexOf(questions[0])<body.indexOf(questions[1]),'history ordering');
        assert.match(body,/confidence|85%|0\.85/i);
        const citationControl=page.getByText(/citations?/i).first();await citationControl.click();
        assert.ok((await page.locator('body').innerText()).includes(history[0].response.citations[0].excerpt));
        page.on('dialog',d=>d.accept());await page.getByRole('button',{name:/clear.*history/i}).click();
        await page.waitForFunction(async()=>(await window.knowledgeBase.qa.history()).length===0,{},{timeout:5000});
      }
      if(task==='project-06') {
        await page.evaluate(async()=>{const h=(await window.knowledgeBase.qa.history())[0];await window.knowledgeBase.feedback.submit(h.response.timestamp,h.question,'positive','sample course feedback');});
        assert.equal((await page.evaluate(()=>window.knowledgeBase.feedback.list())).length,1);
        await page.evaluate(()=>window.knowledgeBase.app.resetData());
        assert.equal((await page.evaluate(()=>window.knowledgeBase.documents.list())).length,0);
        assert.equal((await page.evaluate(()=>window.knowledgeBase.qa.history())).length,0);
        assert.equal((await page.evaluate(()=>window.knowledgeBase.feedback.list())).length,0);
      }
      await page.screenshot({path:path.join(output,'electron.png')});
    } finally {await app.close();}
  });
  save();
})().catch(error=>{checks.push({name:'grader infrastructure',passed:false,error:String(error)});save();process.exitCode=2;});
