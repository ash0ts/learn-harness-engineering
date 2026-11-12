// Delivered only after the actor exits, in a fresh grading workspace.
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const assert = require('node:assert/strict');
const {execFileSync} = require('node:child_process');
const {poll} = require('/tmp/poll.cjs');
const task = process.argv[2];
const cwd = '/workspace/task';
const output = '/tmp/grade';
fs.mkdirSync(output,{recursive:true});
const checks=[];
const serviceLogs=[];const originalLog=console.log;console.log=(...args)=>{serviceLogs.push(args.map(String).join(' '));originalLog(...args);};
async function check(name, fn) {
  try {await fn();checks.push({name,passed:true});}
  catch(error){checks.push({name,passed:false,error:String(error)});}
}
const command = (args) => {
  fs.appendFileSync(path.join(output,'build.log'),`\n$ ${args.join(' ')}\n`);
  try {
    const stdout=execFileSync(args[0],args.slice(1),{cwd,timeout:90000,encoding:'utf8',stdio:'pipe'});
    fs.appendFileSync(path.join(output,'build.log'),stdout);return stdout;
  } catch(error) {
    fs.appendFileSync(path.join(output,'build.log'),String(error.stdout??'')+String(error.stderr??'')+'\n'+String(error));
    throw error;
  }
};
const save = () => fs.writeFileSync(path.join(output,'result.json'),JSON.stringify({schemaVersion:1,task,checks,passed:checks.every(c=>c.passed)},null,2));

(async()=>{
  await check('strict compile and renderer build',()=>{
    for(const args of [
      ['node','/opt/app/node_modules/typescript/bin/tsc','--noEmit','-p','tsconfig.node.json'],
      ['node','/opt/app/node_modules/typescript/bin/tsc','--noEmit','-p','tsconfig.json'],
      ['node','/opt/app/node_modules/typescript/bin/tsc','-p','tsconfig.node.json'],
      ['node','scripts/forge-build-preload.cjs'],
      ['node','/opt/app/node_modules/vite/bin/vite.js','build'],
    ]) command(args);
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
  if(task==='project-06')await check('benchmark invokes actual import, indexing and Q&A services',()=>{
    assert.ok(fs.existsSync(path.join(cwd,'scripts/benchmark.sh')),'missing benchmark');
    command(['env','NODE_OPTIONS=--require=/tmp/benchmark-probe.cjs','bash','scripts/benchmark.sh']);
    const calls=fs.readFileSync(path.join(output,'benchmark-calls.jsonl'),'utf8').trim().split('\n').map(JSON.parse);
    fs.writeFileSync(path.join(output,'benchmark.json'),JSON.stringify({calls},null,2));
    for(const method of ['importDocument','startIndexing','ask'])assert.ok(calls.some(c=>c.method===method),`benchmark did not execute ${method}`);
  });
  await check('Electron window, preload, import, indexing and question UI under Xvfb',async()=>{
    const {_electron}=require('/opt/app/node_modules/playwright');
    let app=await _electron.launch({executablePath:require('/opt/app/node_modules/electron'),args:['--no-sandbox',path.join(cwd,'dist/main/main.js'),`--user-data-dir=${path.join(data,'electron')}`],timeout:30000});
    let page;const uiEvents=[];
    try {
      page=await app.firstWindow();
      page.on('pageerror',e=>uiEvents.push({type:'renderer-error',error:String(e)}));
      page.on('console',m=>uiEvents.push({type:'console',level:m.type(),text:m.text()}));
      await app.evaluate(({ipcMain})=>{globalThis.__courseIpc=[];for(const [channel,fn]of ipcMain._invokeHandlers){ipcMain._invokeHandlers.set(channel,async(event,...args)=>{try{const value=await fn(event,...args);globalThis.__courseIpc.push({channel,ok:true});return value;}catch(error){globalThis.__courseIpc.push({channel,ok:false,error:String(error)});throw error;}});}});await page.waitForLoadState('domcontentloaded');
      await page.getByRole('heading',{name:'Knowledge Base',exact:true}).waitFor({timeout:15000});
      assert.equal(await page.evaluate(()=>typeof window.knowledgeBase.documents.import),'function');
      assert.equal(await page.evaluate(()=>typeof window.require),'undefined');
      if(['project-01','project-02'].includes(task)) {
        await app.evaluate(({dialog},file)=>{globalThis.__coursePickerCalls=0;dialog.showOpenDialog=async()=>{globalThis.__coursePickerCalls++;return {canceled:false,filePaths:[file]};};},fixture);
        let fileChooserCalls=0;page.on('filechooser',async chooser=>{fileChooserCalls++;await chooser.setFiles(fixture);});
        await page.getByRole('button',{name:/import/i}).first().click();
        const input=page.locator('input[type=file]');
        if(await input.count()&&await input.first().isVisible())await input.first().click();
        await poll(()=>page.evaluate(async()=> (await window.knowledgeBase.documents.list()).length>0));
        const pickerCalls=await app.evaluate(()=>globalThis.__coursePickerCalls);uiEvents.push({type:'picker',nativeCalls:pickerCalls,fileChooserCalls});
        assert.ok(pickerCalls+fileChooserCalls>0,'import did not pass through a file picker');
        if(task==='project-02'){const result=await page.evaluate(async()=>{const d=(await window.knowledgeBase.documents.list())[0];return window.knowledgeBase.documents.getContent(d.id);});assert.equal(result,content);}
      } else await page.evaluate(file=>window.knowledgeBase.documents.import(file),fixture);
      await page.evaluate(()=>window.knowledgeBase.indexing.start());
      await page.getByRole('button',{name:'Refresh',exact:true}).click();
      await page.getByText('heldout',{exact:true}).first().waitFor({timeout:10000});
      const questions=['How does indexing preserve paragraphs?','What architecture is used?'];
      for(const q of questions){
        await page.locator('input[type=text]').first().fill(q);
        await page.getByRole('button',{name:'Ask',exact:true}).click();
        await poll(()=>page.evaluate(async question=>(await window.knowledgeBase.qa.history()).some(h=>h.question===question),q));
        const answer=await page.evaluate(async question=>(await window.knowledgeBase.qa.history()).find(h=>h.question===question).response.answer,q);
        await page.getByText(answer,{exact:true}).first().waitFor({timeout:10000});
        await page.screenshot({path:path.join(output,'visible-answer.png')});
        fs.writeFileSync(path.join(output,'visible-answer.json'),JSON.stringify({question:q,answer,body:await page.locator('body').innerText()},null,2));
      }
      if(['project-01','project-02'].includes(task)){
        const imported=await page.evaluate(async()=>(await window.knowledgeBase.documents.list())[0]);
        await app.close();
        assert.equal(fs.readFileSync(path.join(data,'electron','knowledge-base-data','content',`${imported.id}.txt`),'utf8'),content);
        app=await _electron.launch({executablePath:require('/opt/app/node_modules/electron'),args:['--no-sandbox',path.join(cwd,'dist/main/main.js'),`--user-data-dir=${path.join(data,'electron')}`],timeout:30000});
        page=await app.firstWindow();await page.waitForLoadState('domcontentloaded');
        await page.getByRole('button',{name:'Refresh',exact:true}).click();await page.getByText('heldout',{exact:true}).first().waitFor({timeout:10000});
        assert.equal((await page.evaluate(()=>window.knowledgeBase.qa.history())).length,2);
        await page.screenshot({path:path.join(output,'restart.png')});
      }
      if(task==='project-05') {
        await page.getByRole('button',{name:/conversation|history/i}).first().click();
        const history=await page.evaluate(()=>window.knowledgeBase.qa.history());
        const body=await page.locator('body').innerText();
        for(const h of history){assert.ok(body.includes(h.question),'missing question');assert.ok(body.includes(h.response.answer),'truncated answer');}
        assert.ok(body.indexOf(questions[0])<body.indexOf(questions[1]),'history ordering');
        assert.match(body,/confidence|85%|0\.85/i);
        const citationControl=page.locator('button, summary, [role="button"]').filter({hasText:/citations?/i}).first();await citationControl.click();
        await poll(async()=> (await page.locator('body').innerText()).includes(history[0].response.citations[0].excerpt));
        assert.ok((await page.locator('body').innerText()).includes(history[0].response.citations[0].excerpt));
        let confirmationMode='cancel', nativeConfirmation=false;
        page.on('dialog',async d=>{assert.equal(d.type(),'confirm');nativeConfirmation=true;if(confirmationMode==='cancel')await d.dismiss();else await d.accept();});
        const clear=page.getByRole('button',{name:/clear.*history/i}).first();
        await clear.click();
        const cancel=page.getByRole('button',{name:/^(cancel|no)$/i}).last();
        if(!nativeConfirmation){await cancel.waitFor({state:'visible',timeout:5000});await cancel.click();}
        assert.equal((await page.evaluate(()=>window.knowledgeBase.qa.history())).length,history.length,'cancel must retain history');
        confirmationMode='accept';nativeConfirmation=false;
        await clear.click();
        if(!nativeConfirmation){
          await cancel.waitFor({state:'visible',timeout:5000});
          assert.equal((await page.evaluate(()=>window.knowledgeBase.qa.history())).length,history.length,'history must remain until confirmation');
          await cancel.locator('..').getByRole('button',{name:/clear|confirm|yes|delete/i}).click();
        }
        await poll(()=>page.evaluate(async()=>(await window.knowledgeBase.qa.history()).length===0),5000);
      }
      if(task==='project-06') {
        await page.evaluate(async()=>{const h=(await window.knowledgeBase.qa.history())[0];await window.knowledgeBase.feedback.submit({question:h.question,answer:h.response.answer,rating:'positive',comment:'sample course feedback'});});
        const feedback=await page.evaluate(()=>window.knowledgeBase.feedback.list());
        assert.equal(feedback.length,1);assert.equal(feedback[0].rating,'positive');assert.equal(feedback[0].comment,'sample course feedback');
        const submitted=await page.evaluate(async()=>(await window.knowledgeBase.qa.history())[0]);
        assert.equal(feedback[0].question,submitted.question);assert.equal(feedback[0].answer,submitted.response.answer);
        await app.close();
        app=await _electron.launch({executablePath:require('/opt/app/node_modules/electron'),args:['--no-sandbox',path.join(cwd,'dist/main/main.js'),`--user-data-dir=${path.join(data,'electron')}`],timeout:30000});
        page=await app.firstWindow();await page.waitForLoadState('domcontentloaded');
        assert.deepEqual(await page.evaluate(()=>window.knowledgeBase.feedback.list()),feedback,'feedback must survive process restart');
        await page.getByRole('button',{name:'Refresh',exact:true}).click();
        await page.getByText('heldout',{exact:true}).first().click();
        page.on('dialog',d=>d.accept());
        await page.getByRole('button',{name:/reset/i}).first().click();
        const confirm=page.getByRole('button',{name:/^(confirm|yes|reset data)$/i}).last();if(await confirm.isVisible().catch(()=>false))await confirm.click();
        await poll(()=>page.evaluate(async()=>(await window.knowledgeBase.documents.list()).length===0));
        assert.equal((await page.evaluate(()=>window.knowledgeBase.documents.list())).length,0);
        assert.equal((await page.evaluate(()=>window.knowledgeBase.qa.history())).length,0);
        assert.equal((await page.evaluate(()=>window.knowledgeBase.feedback.list())).length,0);
        const body=await page.locator('body').innerText();
        assert.ok(!body.includes('heldout'),'stale document remains visible');
        assert.ok(!body.includes(submitted.response.answer),'stale answer remains visible');
        for(const citation of submitted.response.citations)assert.ok(!body.includes(citation.excerpt),'stale citation remains visible');
        await page.screenshot({path:path.join(output,'after-reset.png')});
        const afterReset=await page.evaluate(()=>window.knowledgeBase.qa.ask('What architecture is used?'));
        assert.equal(afterReset.citations.length,0,'reset must clear retrievable index chunks');
      }
      await page.screenshot({path:path.join(output,'electron.png')});
    } catch(error){if(page)await page.screenshot({path:path.join(output,'ui-failure.png')}).catch(()=>{});throw error;}
    finally {
      uiEvents.push({type:'ipc',calls:await app.evaluate(()=>globalThis.__courseIpc??[]).catch(()=>[])});
      if(page)uiEvents.push({type:'final-body',text:await page.locator('body').innerText().catch(()=>'(unavailable)')});
      fs.writeFileSync(path.join(output,'ui-events.json'),JSON.stringify(uiEvents,null,2));
      await app.close();
    }
  });
  if(task==='project-04')await check('structured logs include import, indexing and failure events',()=>{
    const entries=serviceLogs.flatMap(line=>{try{return [JSON.parse(line)];}catch{return [];}});
    fs.writeFileSync(path.join(output,'logs.json'),JSON.stringify(entries,null,2));
    assert.ok(entries.some(e=>e.level&&e.message&&/import/i.test(e.message)));
    assert.ok(entries.some(e=>e.level&&e.message&&/index/i.test(e.message)));
    try{documents.importDocument('/tmp/does-not-exist-course-fixture.txt');}catch{}
    const failures=serviceLogs.flatMap(line=>{try{return [JSON.parse(line)];}catch{return [];}});
    assert.ok(failures.some(e=>/error|warn/i.test(e.level)&&e.message),'missing structured failure event');
  });
  save();
})().catch(error=>{checks.push({name:'grader infrastructure',passed:false,error:String(error)});save();process.exitCode=2;});
