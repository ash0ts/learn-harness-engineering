const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict');
const Module=require('node:module');
const root=path.resolve(__dirname,'..');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'workshop.json'),'utf8'));
const checks=[];
const check=async(name,fn)=>{try{await fn();checks.push({name,passed:true});}catch(error){checks.push({name,passed:false,detail:String(error)});}};
function load(file){
  const filename=path.join(root,file),module=new Module(filename);module.paths=Module._nodeModulePaths(path.dirname(filename));
  const code=require('esbuild').buildSync({entryPoints:[filename],bundle:true,platform:'node',format:'cjs',packages:'external',write:false}).outputFiles[0].text;
  module._compile(code,filename);return module.exports;
}
async function main(){
  const data=fs.mkdtempSync(path.join(os.tmpdir(),'workshop-check-'));
  try{
    const {PersistenceService}=require('../dist/services/persistence-service.js');
    const {DocumentService}=require('../dist/services/document-service.js');
    const {IndexingService}=require('../dist/services/indexing-service.js');
    const p=new PersistenceService(data),documents=new DocumentService(p),index=new IndexingService(p);
    await check('Import button uses the typed picker and imports its chosen path',async()=>{
      let imported=null;global.window={knowledgeBase:{documents:{choose:async()=>'/fixture.txt',import:async name=>{imported=name;}}}};
      await load('src/renderer/workshop-import.ts').importFromPicker();assert.equal(imported,'/fixture.txt');
      imported=null;global.window.knowledgeBase.documents.choose=async()=>null;
      await load('src/renderer/workshop-import.ts').importFromPicker();assert.equal(imported,null);
    });
    await check('Inference request includes question, excerpts, model and bounded output',()=>{
      const request=load('workshop/inference.ts').makeRequest('unique-question',[{excerpt:'unique-excerpt'}],'fixed-model');
      assert.equal(request.model,'fixed-model');assert.ok(request.max_tokens>0&&request.max_tokens<=1024);
      assert.equal(request.chat_template_kwargs?.enable_thinking,false,'Use the documented non-thinking setting for this bounded exercise');
      assert.ok(request.messages.some(m=>m.role==='system'&&m.content.length>20));
      assert.match(JSON.stringify(request.messages),/unique-question/);assert.match(JSON.stringify(request.messages),/unique-excerpt/);
    });
    const imported=documents.importDocument(path.join(root,'fixtures/long.txt'));
    await index.startIndexing();
    await check('Long documents retain nonempty indexed text',()=>{
      const chunks=index.getAllChunks();assert.ok(chunks.length>1);assert.ok(chunks.every(c=>c.content.trim()));
    });
    await check('Document metadata survives a service restart',()=>{
      const restored=new DocumentService(new PersistenceService(data)).getDocument(imported.id);
      const text=fs.readFileSync(path.join(root,'fixtures/long.txt'),'utf8');
      assert.equal(restored.metadata.wordCount,text.trim().split(/\s+/).length);
    });
    if(manifest.project==='project-02'){
      await check('Workspace guidance names the real entry point and an acceptance command',()=>{
        const docs=fs.readFileSync(path.join(root,'AGENTS.md'),'utf8')+fs.readFileSync(path.join(root,'docs/ARCHITECTURE.md'),'utf8');
        assert.match(docs,/src\/main\/ipc-handlers.ts/);assert.match(docs,/npm (?:run )?(?:test|check)/);
        const feature=JSON.parse(fs.readFileSync(path.join(root,'feature_list.json'),'utf8'));
        assert.ok(feature.features.some(f=>f.id==='document-detail'&&f.acceptance?.length>30));
      });
      await check('Sandbox SDK exercise executes a bounded workspace check',async()=>{
        let observed;await load('workshop/sandbox-task.ts').inspectWorkspace({commands:{run:async(...args)=>{observed=args;return {stdout:'checked'};}}});
        assert.ok(observed);assert.deepEqual(observed[0],['npm','run','check']);assert.equal(observed[1].cwd,'/workspace/task');assert.ok(observed[1].timeoutMs<=60000);
      });
      await check('Detail bridge returns the persisted document content',()=>{
        const handlers=new Map();
        const source=fs.readFileSync(path.join(root,'dist/main/ipc-handlers.js'),'utf8');
        const module={exports:{}};
        const localRequire=name=>name==='electron'?{dialog:{}}:Module.createRequire(path.join(root,'dist/main/ipc-handlers.js'))(name);
        new Function('require','module','exports',source)(localRequire,module,module.exports);
        module.exports.registerIpcHandlers({handle:(name,fn)=>handlers.set(name,fn)}, {documentService:documents,indexingService:index,qaService:{},persistence:p});
        return Promise.resolve(handlers.get('documents:content')({},imported.id)).then(value=>assert.equal(value,fs.readFileSync(path.join(root,'fixtures/long.txt'),'utf8')));
      });
    }
    if(manifest.project==='project-03')await check('Feature record and handoff name observed checks and a next step',()=>{
      const features=JSON.parse(fs.readFileSync(path.join(root,'feature_list.json'),'utf8'));
      assert.ok(features.features.some(f=>f.id==='metadata'&&f.command==='npm test'));
      const handoff=fs.readFileSync(path.join(root,'session-handoff.md'),'utf8');
      for(const heading of ['Completed','Checks','Unfinished','Next'])assert.match(handoff,new RegExp(heading));
      assert.ok(handoff.length>180);assert.match(handoff,/workshop-metadata.ts/);
    });
    if(manifest.project==='project-04')await check('Student instrumentation closes successful and failed tool spans',async()=>{
      const {observe}=load('workshop/instrumentation.ts'),events=[];
      const sdk={startTool:args=>{const event={args};events.push(event);return {end:value=>event.end=value};}};
      const chunks=[{content:'visible text'},{content:''}];
      assert.equal(await observe(sdk,'retrieval.chunks',{question:'q'},async()=>chunks),chunks);
      assert.equal(events[0]?.args.name,'student.retrieval.chunks');
      const result=JSON.parse(events[0].end.result);assert.equal(result.chunkCount,2);assert.equal(result.nonemptyCount,1);
      await assert.rejects(()=>observe(sdk,'indexing.start',{},async()=>{throw new Error('controlled');}));
      assert.ok(events[1]?.end.error);
    });
    if(manifest.project==='project-07'){
      const policy=load('workshop/loop.ts');
      const observation={round:0,maxRounds:2,now:10,deadline:100,outcome:'task_failed',checks:[{name:'Persist word count',passed:false},{name:'Import',passed:true}]};
      await check('Loop stops on success, round limit and the saved deadline',()=>{
        assert.equal(policy.nextAction(observation),'run');
        assert.equal(policy.nextAction({...observation,outcome:'passed'}),'stop');
        assert.equal(policy.nextAction({...observation,round:2}),'stop');
        assert.equal(policy.nextAction({...observation,now:100}),'stop');
      });
      await check('Loop feedback names the actual failed check',()=>assert.match(policy.nextPrompt(observation),/Persist word count/));
    }
    if(manifest.project==='project-06'){
      const {QaService}=require('../dist/services/qa-service.js');
      const qa=new QaService(p,index);
      await check('Feedback is persisted and survives a fresh service instance',()=>{
        const entry=qa.submitFeedback('test-timestamp','test-question','negative','missing excerpt');
        assert.ok(new QaService(new PersistenceService(data)).getFeedback().some(row=>row.id===entry.id&&row.comment==='missing excerpt'));
      });
      await check('Benchmark executes import, index and question against real services',async()=>{
        p.resetAll();
        const observed=await load('workshop/benchmark.ts').benchmark({documents,index,qa},path.join(root,'fixtures/short.txt'),'What units are documents indexed into?');
        assert.ok(observed.chunkCount>0);assert.equal(observed.chunkCount,index.getChunksForDocument(observed.documentId).length);
        assert.equal(qa.getHistory().length,1);assert.equal(observed.answer,qa.getHistory()[0].response.answer);
        assert.ok(observed.citationCount>0);assert.equal(observed.citationCount,qa.getHistory()[0].response.citations.length);
        p.resetAll();assert.equal(documents.listDocuments().length,0);assert.equal(index.getAllChunks().length,0);assert.equal(qa.getHistory().length,0);assert.equal(qa.getFeedback().length,0);
      });
    }
    if(manifest.project==='project-05'){
      await check('Role prompts require a concrete review and protect renderer boundaries',()=>{
        const maker=fs.readFileSync(path.join(root,'prompts/maker.md'),'utf8'),checker=fs.readFileSync(path.join(root,'prompts/checker.md'),'utf8');
        assert.match(maker,/ConversationHistory/);assert.match(checker,/npm (?:run )?(?:test|check)/);assert.match(checker,/REVIEW/);
        const rubric=JSON.parse(fs.readFileSync(path.join(root,'rubric.json'),'utf8'));assert.ok(rubric.criteria.length>=3);
      });
      await check('History keeps the complete answer',()=>{
        const source=fs.readFileSync(path.join(root,'src/renderer/components/ConversationHistory.tsx'),'utf8');
        assert.doesNotMatch(source,/item\.response\.answer\.slice/);
      });
    }
  }finally{fs.rmSync(data,{recursive:true,force:true});delete global.window;}
  const result={schemaVersion:1,protocol:'workshop-v1',project:manifest.project,mode:'local-deterministic',checks,passed:checks.every(c=>c.passed)};
  fs.mkdirSync(path.join(root,'.workshop-evidence'),{recursive:true});fs.writeFileSync(path.join(root,'.workshop-evidence/local-check.json'),JSON.stringify(result,null,2));
  console.log(JSON.stringify(result,null,2));process.exitCode=result.passed?0:1;
}
main().catch(error=>{console.error(error);process.exitCode=1;});
