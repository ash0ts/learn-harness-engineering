const {spawnSync}=require('node:child_process');
const path=require('node:path');
const fs=require('node:fs');
const root=path.resolve(__dirname,'..');
for(const [pkg,entry,args]of [['typescript','bin/tsc',['-p','tsconfig.node.json']],['vite','bin/vite.js',['build']]]) {
  const binary=path.join(path.dirname(require.resolve(pkg+'/package.json')),entry);
  const result=spawnSync(process.execPath,[binary,...args],{cwd:root,stdio:'inherit'});
  if(result.error)throw result.error;if(result.status)process.exit(result.status);
}
require('esbuild').buildSync({entryPoints:[path.join(root,'src/preload/preload.ts')],outfile:path.join(root,'dist/preload/preload.js'),bundle:true,platform:'node',format:'cjs',external:['electron']});
// The protected coordinator prebundles this file when staging to the CPU image.
// A normal local npm ci supplies the SDK so the same source builds on laptops.
if(fs.existsSync(path.join(root,'node_modules/@coreweave/forge-sdk'))) {
  require('esbuild').buildSync({entryPoints:[path.join(root,'scripts/live-entry.ts')],outfile:path.join(root,'dist/forge-adapter.cjs'),bundle:true,platform:'node',format:'cjs',target:'node22',logLevel:'warning'});
}
