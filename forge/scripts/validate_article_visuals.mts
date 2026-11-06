import { chromium } from 'playwright';
import { promises as fs } from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import siteUtils from '../../scripts/export-site-utils.ts';
const { startStaticServer, toAbsoluteSiteUrl }=siteUtils;
const root=path.resolve('forge/local-results/article-editorial');
await fs.mkdir(root,{recursive:true});
await fs.rm(path.join(root,'visual-browser-validation.json'),{force:true});
const catalog=JSON.parse(await fs.readFile('docs/public/forge/evidence/catalog.json','utf8'));
const anchorMap=JSON.parse(await fs.readFile('docs/.vitepress/anchor-map.json','utf8'));
const server=await startStaticServer();
const browser=await chromium.launch({headless:true,channel:'chrome'});
const records=[];const checked=new Set();const errors=[];const images=new Set();
try {
 for(const width of [1440,390]) {
  const page=await browser.newPage({viewport:{width,height:width===390?844:1000},deviceScaleFactor:1});
  page.on('pageerror',e=>errors.push(e.message));
  for(const file of (await fs.readdir('docs/en/forge')).filter(f=>f.endsWith('.md')).sort()) {
   const response=await page.goto(toAbsoluteSiteUrl(server.origin,'/en/forge/'+(file==='index.md'?'':file.replace(/\.md$/,''))),{waitUntil:'networkidle'});
   assert.equal(response?.status(),200,file);
   const data=await page.evaluate(()=>({
    headings:[...document.querySelectorAll('.vp-doc h1,.vp-doc h2,.vp-doc h3')].map(e=>e.id),
    overflow:document.documentElement.scrollWidth>innerWidth,
    images:[...document.querySelectorAll('.vp-doc img')].map(e=>({link:e.closest('a')?.getAttribute('href'),src:(e as HTMLImageElement).src,alt:(e as HTMLImageElement).alt})),
    links:[...document.querySelectorAll('.vp-doc a,.VPSidebar a')].map(e=>(e as HTMLAnchorElement).href).filter(h=>h.startsWith(location.origin)),
    scrollable:[...document.querySelectorAll('.forge-figure')].map(e=>{e.scrollLeft=500;const scrolled=e.scrollLeft>0;e.scrollLeft=0;return {scrollable:e.scrollWidth>e.clientWidth,scrolled}})
   }));
   console.log(`Checked page ${file} at ${width}px`);
   assert(!data.overflow,`Page overflow ${file} ${width}`);
   assert.deepEqual(data.headings,anchorMap['forge/'+file].ids,`Headings ${file}`);
   for(const im of data.images){assert(im.alt,`Missing alt ${file}`);assert(!im.link?.startsWith('data:'),`Full-size image needs a navigable file URL: ${file}`);images.add(im.src);if(im.src.startsWith('data:image/'))continue;if(checked.has(im.src))continue;assert.equal((await page.request.get(im.src)).status(),200,im.src);checked.add(im.src)}
   for(const href of data.links){if(checked.has(href))continue;const url=new URL(href);const res=await page.request.get(url.origin+url.pathname);assert.equal(res.status(),200,href);if(url.hash){const html=await res.text();const exists=await page.evaluate(({html,id})=>!!new DOMParser().parseFromString(html,'text/html').getElementById(id),{html,id:decodeURIComponent(url.hash.slice(1))});assert(exists,href)}checked.add(href)}
   assert(data.scrollable.every(x=>!x.scrollable||x.scrolled),'Figure scroll');
   records.push({file,width,images:data.images.length,links:data.links.length});
   if(['index.md','06-capstone.md','08-state-machine.md','evidence.md'].includes(file)){
    await page.screenshot({path:path.join(root,`visual-${file.replace('.md','')}-${width}-top.png`)});
    const figure=page.locator('.forge-figure').first();if(await figure.count()){await figure.scrollIntoViewIfNeeded();await page.screenshot({path:path.join(root,`visual-${file.replace('.md','')}-${width}-figure.png`)})}
   }
  }
  const url=toAbsoluteSiteUrl(server.origin,'/en/forge/evidence');
  await page.goto(url,{waitUntil:'networkidle'});
  await page.getByRole('region',{name:'Recorded trial evidence'}).scrollIntoViewIfNeeded();
  await page.getByText('39 matching attempts · 19 recorded passes').waitFor();
  await page.getByLabel('Project',{exact:true}).selectOption('project-02');
  await page.getByText('6 matching attempts · 0 recorded passes').waitFor();
  await page.locator('.trial>summary').first().click();
  await page.locator('.trial[open]').getByText('No application screenshot was retained for this attempt.',{exact:false}).waitFor();
  const deepLink=page.url();assert(deepLink.includes('trial='));
  await page.reload({waitUntil:'networkidle'});assert.equal(await page.locator('.trial[open]').count(),1);
  await page.getByLabel('Cohort',{exact:true}).selectOption('all');
  await page.goBack({waitUntil:'networkidle'});assert.equal(await page.getByLabel('Cohort',{exact:true}).inputValue(),'primary');
  await page.goForward({waitUntil:'networkidle'});assert.equal(await page.getByLabel('Cohort',{exact:true}).inputValue(),'all');
  await page.getByRole('button',{name:'Reset filters'}).click();
  await page.getByRole('button',{name:'Next',exact:true}).click();await page.getByText('Page 2 of 4').waitFor();
  await page.getByRole('button',{name:'Previous',exact:true}).click();
  await page.getByLabel('Project',{exact:true}).selectOption('project-08');
  await page.getByText('No recorded attempt matches these filters.',{exact:false}).waitFor();
  await page.getByLabel('Cohort',{exact:true}).selectOption('all');
  await page.getByLabel('Find a trial, treatment, source revision, or error').fill('03ca01ca');
  await page.getByText('1 matching attempts · 1 recorded passes').waitFor();
  const summary=page.locator('.trial>summary').first();await summary.focus();await page.keyboard.press('Enter');assert.equal(await page.locator('.trial[open]').count(),1);
  await page.locator('.trial[open]').scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(root,`visual-evidence-${width}-trial.png`)});
  const table=page.locator('.trial[open] .checks');assert((await table.innerText()).includes('Passed'));
  await page.getByLabel('Find a trial, treatment, source revision, or error').fill('impossible-no-record-000');
  await page.getByText('No recorded attempt matches these filters.',{exact:false}).waitFor();
  assert(!(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth)));
  await page.close();
 }
 const requestPage=await browser.newPage();
 const response=await requestPage.request.get(toAbsoluteSiteUrl(server.origin,'/forge/evidence/catalog.json'));
 assert.deepEqual(await response.json(),catalog);
 const csv=await requestPage.request.get(toAbsoluteSiteUrl(server.origin,'/forge/evidence/trials.csv'));assert.equal(await csv.text(),await fs.readFile('docs/public/forge/evidence/trials.csv','utf8'));
 const zip=await requestPage.request.get(toAbsoluteSiteUrl(server.origin,'/forge/evidence/forge-visual-evidence.zip'));assert.equal(zip.status(),200);assert((await zip.body()).length>1e6);
 assert.deepEqual(errors,[],'Browser errors');
 const result={verified:true,pageRenders:records.length,uniqueLocalResources:checked.size,uniqueImageSources:images.size,viewports:[1440,390],checks:['links and anchors','image sources and alt text','responsive overflow','scrollable wide figures','primary counts','project filters','missing screenshot state','selected trial reload','browser back and forward','pagination','empty filters','keyboard trial expansion','CSV and catalog readback','portable ZIP download'],records};
 await fs.writeFile(path.join(root,'visual-browser-validation.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify({...result,records:undefined}));
} finally {await browser.close();await server.close()}
