const {spawnSync}=require('node:child_process');
const {pathToFileURL}=require('node:url');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const built=spawnSync(process.execPath,[path.join(__dirname,'build.cjs')],{cwd:root,stdio:'inherit'});
if(built.error)throw built.error;if(built.status)process.exit(built.status);
const live=process.argv.includes('--live');
if(live&&(!process.env.WANDB_API_KEY||!process.env.WANDB_ENTITY))throw new Error('Forge mode requires WANDB_API_KEY and WANDB_ENTITY in your shell environment. Never put the key in source.');
const env={...process.env,WORKSHOP_DATA_DIR:path.join(root,'.workshop-data'),FORGE_BUDGET_USD:process.env.FORGE_BUDGET_USD||'20'};
if(live){env.FORGE_APP_MODE='live';env.FORGE_APP_ADAPTER=pathToFileURL(path.join(root,'dist/forge-adapter.cjs')).href;}
else {delete env.FORGE_APP_MODE;delete env.FORGE_APP_ADAPTER;}
console.log(live?'Forge mode: requests use your own project and budget.':'Offline mode: fixture answers; no inference requests.');
const result=spawnSync(require('electron'),['.'],{cwd:root,stdio:'inherit',env});
if(result.error)throw result.error;process.exitCode=result.status??1;
