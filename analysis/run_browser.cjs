// Human-runner E2E contract. Serves exact archive bytes on the required local origin.
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),http=require('node:http');
const {pathToFileURL}=require('node:url');
const {chromium}=require(process.env.PLAYWRIGHT_PATH||'playwright');
const root=path.resolve(__dirname,'..'),app=path.join(root,'app'),out=path.join(root,'rerun');
const mode=process.argv[2],origin='http://127.0.0.1:8000';
assert.ok(['original','extras','live-plus'].includes(mode),'Specify original, extras or live-plus');
fs.mkdirSync(out,{recursive:true});
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const save=(name,value)=>fs.writeFileSync(path.join(out,name),JSON.stringify(value,null,2)+'\n','utf8');
const state=page=>page.evaluate(()=>({
 src:document.getElementById('src').value,trans:document.getElementById('trans').value,
 tau:document.getElementById('tau-est').value,result:window._almLastPropMA(),
 body:document.getElementById('res-body').innerHTML,forest:document.getElementById('forest').outerHTML,
 het:document.getElementById('het').innerHTML,href:location.href,history:history.state
}));
(async()=>{
 const requests=[],errors=[],missing=[],outside=[];
 const types={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.css':'text/css','.json':'application/json','.wasm':'application/wasm','.ico':'image/x-icon'};
 const server=http.createServer((req,res)=>{
  try {
   const u=new URL(req.url,origin),name=decodeURIComponent(u.pathname).replace(/^\/+/,''),p=path.resolve(app,name);
   if(!p.startsWith(app+path.sep)||!fs.existsSync(p)||!fs.statSync(p).isFile()) {
    missing.push(u.pathname);res.writeHead(404);res.end('Missing archive asset');return;
   }
   requests.push(u.pathname);res.writeHead(200,{'Content-Type':types[path.extname(p)]||'application/octet-stream'});
   res.end(fs.readFileSync(p));
  } catch(e) {errors.push(String(e));res.writeHead(500);res.end('Archive server error');}
 });
 let browser;
 const timeout=setTimeout(()=>{console.error('Browser validation exceeded 30 minutes');process.exitCode=1;browser?.close();server.close();},1800000);
 try {
  await new Promise((resolve,reject)=>{server.once('error',reject);server.listen(8000,'127.0.0.1',resolve);});
  browser=await chromium.launch({channel:process.env.PW_CHANNEL||'chrome',headless:true});
  const context=await browser.newContext();
  await context.route('**/*',route=>{
   const u=new URL(route.request().url());
   if(/^https?:$/.test(u.protocol)&&u.origin!==origin){outside.push(u.href);return route.abort('blockedbyclient');}
   return route.continue();
  });
  const page=await context.newPage();
  page.on('pageerror',e=>errors.push(String(e)));
  await page.goto(origin+'/proportion-ma/index.html',{waitUntil:'networkidle'});
  await page.waitForFunction(()=>window.AlmProportionValidation&&window.AlmPropPlusValidation);
  if(mode==='original'){
   const before=await state(page),r=await page.evaluate(()=>AlmProportionValidation.runCorpus());
   save('original-browser.json',r);
   assert.equal(r.checks,298116);assert.equal(r.passed,298116);assert.deepEqual(r.failed,[]);
   assert.equal(r.refusals.length,198);assert.deepEqual(await state(page),before);
   console.log('ORIGINAL CURRENT PAGE: '+r.passed+'/'+r.checks+' checks pass; '+r.refusals.length+' matched refusals');
   const live=await page.evaluate(()=>AlmProportionValidation.runLive());
   save('original-live.json',live);
   assert.equal(live.rows.length,16);assert.ok(live.rows.every(r=>r.pass));
   assert.equal(live.versions.metafor,'4.8-0');assert.equal(live.versions.webR,'0.5.5');
   console.log('ORIGINAL LIVE R: '+live.rows.filter(r=>r.pass).length+'/'+live.rows.length+' quantities pass');
   // Capture fresh observations for the unchanged original compare.py and validate.R.
   const corpus=read('data/corpus.json');
   const observed=await page.evaluate(corpus=>{
    const observations={};
    for(const ca of corpus)for(const tr of ['logit','ft','raw'])for(const method of ['PM','DL','FE']){
     document.getElementById('src').value=ca.rows.map(r=>[r.x,r.n,r.label].join(',')).join('\n');
     document.getElementById('trans').value=tr;document.getElementById('tau-est').value=method;
     __almPropValidation.run();const a=__almPropValidation.snapshot();
     observations[ca.id+'|'+tr+'|'+method]=a?{status:'ok',...a,display:{
      pooled:document.querySelector('.pooled-row').innerText,heterogeneity:document.getElementById('het').innerText,
      rows:document.querySelectorAll('#res-body tr').length,forest:document.querySelectorAll('#forest polygon').length
     }}:{status:'refused'};
    }
    return observations;
   },corpus);
   assert.equal(Object.keys(observed).length,2160);
   const target=path.join(out,'original/results');fs.mkdirSync(target,{recursive:true});
   fs.writeFileSync(path.join(target,'app-patched.json'),JSON.stringify(observed,null,2)+'\n','utf8');
  } else if(mode==='extras'){
   const before=await state(page);
   await page.evaluate(()=>AlmPropPlusValidation.prepare());await context.setOffline(true);
   const r=await page.evaluate(()=>AlmPropPlusValidation.runCorpus());save('extras-offline.json',r);
   assert.equal(r.checks,7248);assert.equal(r.passed,7248);assert.deepEqual(r.failed,[]);
   assert.equal(r.refusals.length,28);assert.deepEqual(await state(page),before);
   console.log('EXTRAS PRESENTATION/EXPORT: '+r.passed+'/'+r.checks+' checks pass; '+r.refusals.length+' refusals; offline replay and state restoration');
   await context.setOffline(false);
   // A corrupted export must be detected by the real adapter.
   const negatives=await page.evaluate(async()=>{
    const original=AlmPropPlus.exported;
    try {
     AlmPropPlus.exported=()=>{const v=JSON.parse(original());v.inputs=[];v.source='corrupted negative control';return JSON.stringify(v);};
     const r=await AlmPropPlusValidation.runCorpus();
     return {inputs:r.failed.some(f=>f.quantity==='export_inputs'),provenance:r.failed.some(f=>f.quantity==='provenance')};
    } finally {AlmPropPlus.exported=original;}
   });
   assert.equal(negatives.inputs,true);assert.equal(negatives.provenance,true);
   // Reload to discard the pinned-file cache before deliberately corrupting one input.
   await page.reload({waitUntil:'networkidle'});
   await page.route('**/validate/plus-corpus/corpus.json',r=>r.fulfill({contentType:'application/json',body:'{}'}));
   await assert.rejects(()=>page.evaluate(()=>AlmPropPlusValidation.runCorpus()),/SHA-256/);
   console.log('EXTRAS NEGATIVE CONTROLS: 3/3 detections (input export, provenance, SHA-256)');
  } else {
   const {compareBrowser,assertDocumentedContract}=await import(pathToFileURL(path.join(out,'plus/proportion-ma/validate/compare-browser.mjs')).href);
   const corpus=read('validation-plus/plus-corpus/corpus.json'),refs=read('validation-plus/plus-corpus/reference-plus.json');
   const observed=[];
   try {
    for(const ca of corpus){
     await page.locator('#src').fill(ca.rows.map(r=>[r.x,r.n,r.label].join(',')).join('\n'));
     const result=await page.evaluate(async()=>{await AlmPropPlus.run();AlmPropPlus.audit();return AlmPropPlus.snapshot().result;});
     observed.push({id:ca.id,result});
     if(observed.length%20===0)console.log('GLMM live configurations: '+observed.length+'/'+corpus.length);
    }
    const comparison=compareBrowser(observed,corpus,refs);save('glmm-browser-comparison.json',comparison);
    console.log('EXTRAS CROSS-RUNTIME: '+comparison.passed+'/'+comparison.checks+' passing; '+comparison.failed.length+' failures retained');
    assertDocumentedContract(comparison);
    console.log('EXTRAS DOCUMENTED-EXCEPTIONS CONTRACT PASS (not whole-corpus parity)');
   } finally {save('glmm-browser-results.json',observed);}
  }
  assert.deepEqual(errors,[],'Page/server errors');assert.deepEqual(missing,[],'Missing assets');assert.deepEqual(outside,[],'Off-origin requests');
  console.log('ASSETS PASS: no page errors, missing assets or off-origin requests');
 } finally {
  save(mode+'-transport.json',{origin,requests:[...new Set(requests)].sort(),errors,missing,outside});
  clearTimeout(timeout);
  if(browser)await browser.close();
  await new Promise(resolve=>server.close(resolve));
 }
})().catch(e=>{console.error(e);process.exitCode=1;});
