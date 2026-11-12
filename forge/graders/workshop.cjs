// Protected runner, delivered separately from the editable student snapshot.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {spawnSync}=require('node:child_process');
const {createRequire}=require('node:module');
const root=process.cwd(),out=process.env.WORKSHOP_GRADE_DIR||'/tmp/workshop-grade';
const scenario=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const requireApp=createRequire(path.join(root,'package.json'));
fs.mkdirSync(out,{recursive:true});
const checks=[],events=[],images=[];
const save=(name,value)=>fs.writeFileSync(path.join(out,name),JSON.stringify(value,null,2));
async function check(name,action){try{await action();checks.push({name,passed:true});return true;}catch(error){checks.push({name,passed:false,detail:String(error)});return false;}}
function command(args){const result=spawnSync(process.execPath,args,{cwd:root,encoding:'utf8',timeout:90000});fs.appendFileSync(path.join(out,'build.log'),[args.join(' '),result.stdout,result.stderr].join('\n'));if(result.error)throw result.error;assert.equal(result.status,0,'command failed; see build.log');return result.stdout;}
async function until(fn,timeout=15000){const end=Date.now()+timeout;while(Date.now()<end){if(await fn())return;await new Promise(r=>setTimeout(r,150));}throw new Error('Timed out waiting for observed app state');}
async function main(){
  if(!await check('TypeScript and Electron build',()=>{command([requireApp.resolve('typescript/bin/tsc'),'--noEmit','-p','tsconfig.json']);command(['scripts/build.cjs']);}))return;
  await check('Focused lesson checks',()=>command(['scripts/check.cjs']));
  try{save('local-check.json',JSON.parse(fs.readFileSync(path.join(root,'.workshop-evidence/local-check.json'),'utf8')));}catch{}
  const {_electron}=requireApp('playwright');
  const data=path.join(out,'app-data');let app,page;
  const capture=async step=>{if(!page)return;const file=step+'.png';await page.screenshot({path:path.join(out,file)});images.push({file,step,snapshot:scenario.snapshotId,sha256:scenario.snapshotSha256});};
  const launch=async(live)=>{
    app=await _electron.launch({executablePath:requireApp('electron'),args:[...(process.platform==='linux'?['--no-sandbox']:[]),path.join(root,'dist/main/main.js')],env:{...process.env,WORKSHOP_DATA_DIR:data,FORGE_APP_MODE:live?'live':'offline'},timeout:30000});
    page=await app.firstWindow();page.on('pageerror',e=>events.push({type:'renderer-error',message:String(e)}));page.on('console',m=>events.push({type:'console',level:m.type(),text:m.text()}));
    await page.getByRole('heading',{name:'Knowledge Base · workshop',exact:true}).waitFor({timeout:20000});
    await app.evaluate(({ipcMain})=>{globalThis.__workshopIPC=[];for(const [name,fn]of ipcMain._invokeHandlers)ipcMain._invokeHandlers.set(name,async(...args)=>{try{const value=await fn(...args);globalThis.__workshopIPC.push({channel:name,ok:true});return value;}catch(error){globalThis.__workshopIPC.push({channel:name,ok:false,error:String(error)});throw error;}});});
  };
  try{
    await launch(scenario.live);await capture('00-start');
    const fixture=path.join(root,'fixtures',scenario.fixture==='short'?'short.txt':'long.txt');
    const title=path.basename(fixture,'.txt');
    await app.evaluate(({dialog},file)=>{globalThis.__workshopPickers=0;dialog.showOpenDialog=async()=>{globalThis.__workshopPickers++;return {canceled:false,filePaths:[file]};};},fixture);
    const imported=await check('Import button invokes picker and displays its document',async()=>{
      await page.getByRole('button',{name:'+ Import',exact:true}).click();
      await page.getByText(title,{exact:true}).first().waitFor({timeout:10000});
      assert.equal(await app.evaluate(()=>globalThis.__workshopPickers),1);
      assert.equal(await page.evaluate(()=>typeof window.require),'undefined');
    });
    await capture('01-import');if(!imported)return;
    await page.getByText(title,{exact:true}).first().click();
    await check('Detail view displays the actual imported content',async()=>{
      const content=await page.getByTestId('document-content').innerText({timeout:5000});assert.equal(content.trim(),fs.readFileSync(fixture,'utf8').trim());
    });
    await capture('02-detail');if(scenario.scenario==='import')return;
    await check('Index button creates nonempty visible chunks',async()=>{
      await page.getByRole('button',{name:'Index Document',exact:true}).click();
      await page.getByRole('button',{name:/Show Chunks \([1-9]/}).waitFor({timeout:10000});
      await page.getByRole('button',{name:/Show Chunks/}).click();
      const files=fs.readdirSync(path.join(data,'chunks')).filter(f=>f.endsWith('.json'));
      const chunks=files.flatMap(file=>JSON.parse(fs.readFileSync(path.join(data,'chunks',file),'utf8')));
      save('chunks.json',chunks);assert.ok(chunks.length);assert.ok(chunks.every(c=>c.content.trim()));
      await page.getByText(/^Chunk 0 \(/).first().scrollIntoViewIfNeeded();
    });
    await capture('03-index');if(scenario.scenario==='index')return;
    const questions=[scenario.question||'What units are documents indexed into?','What is the orbital period of the invented planet Glorp?'];
    for(let i=0;i<questions.length;i++){
      await check('Visible answer '+(i+1),async()=>{
        await page.getByPlaceholder('Ask a question about your documents...').fill(questions[i]);
        await page.getByRole('button',{name:'Ask',exact:true}).click();
        await until(()=>fs.existsSync(path.join(data,'qa-history.json'))&&JSON.parse(fs.readFileSync(path.join(data,'qa-history.json'),'utf8')).some(h=>h.question===questions[i]),scenario.live?140000:15000);
        const history=JSON.parse(fs.readFileSync(path.join(data,'qa-history.json'),'utf8'));
        const answer=history.find(h=>h.question===questions[i]).response.answer;
        const visibleAnswer=page.getByText(answer,{exact:true}).first();
        await visibleAnswer.waitFor({timeout:10000});await visibleAnswer.scrollIntoViewIfNeeded();save('answers.json',history);
      });
      await capture('04-answer-'+(i+1));
    }
    if(scenario.scenario==='ask')return;
    if(scenario.scenario==='reset'){
      await check('Feedback button persists the observed rating',async()=>{
        await page.getByRole('button',{name:'History',exact:true}).click();
        await page.getByTitle('Poor answer').first().click();
        await until(()=>fs.existsSync(path.join(data,'feedback.json'))&&JSON.parse(fs.readFileSync(path.join(data,'feedback.json'),'utf8')).length>0);
        await page.getByRole('button',{name:'Documents',exact:true}).click();
      });
      await capture('05-feedback');
      await check('Reset removes visible documents, answers and citations',async()=>{
        const oldAnswers=JSON.parse(fs.readFileSync(path.join(data,'qa-history.json'),'utf8')).map(h=>h.response.answer);
        page.once('dialog',d=>d.accept());await page.getByRole('button',{name:'Reset',exact:true}).click();
        await until(()=>!fs.existsSync(path.join(data,'qa-history.json')));
        const body=await page.locator('body').innerText();
        for(const answer of oldAnswers)assert.ok(!body.includes(answer),'A stale answer survived reset');
        assert.equal(await page.getByTestId('document-content').count(),0);
        assert.equal(await page.getByText(title,{exact:true}).count(),0);
        await page.getByRole('button',{name:'History',exact:true}).click();
        assert.equal(await page.getByTitle('Poor answer').count(),0);
      });
      await capture('06-reset');await app.close();app=null;await launch(false);
      await check('Reset remains empty after restart',async()=>{
        assert.equal(await page.getByText(title,{exact:true}).count(),0);
        await page.getByRole('button',{name:'History',exact:true}).click();assert.equal(await page.getByTitle('Poor answer').count(),0);
        for(const name of ['documents-meta.json','qa-history.json','feedback.json'])if(fs.existsSync(path.join(data,name)))assert.equal(JSON.parse(fs.readFileSync(path.join(data,name),'utf8')).length,0);
      });
      await capture('07-reset-restart');return;
    }
    events.push(...await app.evaluate(()=>globalThis.__workshopIPC));await app.close();app=null;
    // Restart checks persistence only. It never issues replacement inference.
    await launch(false);
    await check('Documents and complete answers survive restart',async()=>{
      await page.getByText(title,{exact:true}).first().waitFor({timeout:10000});
      await page.getByRole('button',{name:'History',exact:true}).click();
      const history=JSON.parse(fs.readFileSync(path.join(data,'qa-history.json'),'utf8'));
      assert.equal(history.length,2);
      for(const item of history){
        await page.getByText(item.question,{exact:true}).first().waitFor({timeout:10000});
        // Playwright normalizes HTML whitespace, but still requires the entire
        // answer. A truncated history entry cannot satisfy this exact match.
        await page.getByText(item.response.answer,{exact:true}).first().waitFor({timeout:10000});
      }
    });
    await capture('05-restart-history');
    if(scenario.scenario==='clear-history')await check('Clear history removes visible and persisted answers',async()=>{
      page.once('dialog',d=>d.accept());await page.getByRole('button',{name:'Clear History',exact:true}).click();
      await until(()=>JSON.parse(fs.readFileSync(path.join(data,'qa-history.json'),'utf8')).length===0);
      const body=await page.locator('body').innerText();assert.ok(!body.includes(questions[0]));await capture('06-clear-history');
    });
  }catch(error){checks.push({name:'Electron scenario',passed:false,detail:String(error)});try{await capture('failure');}catch{}}
  finally{if(app){try{events.push(...await app.evaluate(()=>globalThis.__workshopIPC??[]));await app.close();}catch(error){checks.push({name:'Electron shutdown',passed:false,detail:String(error)});}}save('ui-events.json',events);save('images.json',images);}
}
main().catch(error=>checks.push({name:'runner',passed:false,detail:String(error)})).finally(()=>{
  const result={schemaVersion:1,protocol:'workshop-v1',...scenario,checks,images,passed:checks.length>0&&checks.every(c=>c.passed),pickerMode:'actual Import button; automated native dialog selection'};
  save('result.json',result);process.exitCode=result.passed?0:1;
});
