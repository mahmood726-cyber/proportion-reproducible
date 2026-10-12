// Serve app/ at the explicit local origin before running; never download packages.
const fs=require('fs'),path=require('path');
const {chromium}=require(process.env.PLAYWRIGHT_PATH||'playwright');
(async()=>{
 const browser=await chromium.launch({channel:process.env.PW_CHANNEL||'chrome',headless:true});
 try {
  const context=await browser.newContext();const errors=[],missing=[],requests=[],served=[];
  if(process.env.ARCHIVE_ROUTE_FILES==='1') {
   const root=path.resolve(__dirname,'../app');
   await context.route('**/*',async route=>{
    const url=new URL(route.request().url());
    if(url.origin!=='http://127.0.0.1:8000')return route.abort('blockedbyclient');
    const name=decodeURIComponent(url.pathname).slice(1),file=path.resolve(root,name);
    if(!file.startsWith(root+path.sep)||!fs.existsSync(file)||!fs.statSync(file).isFile()){served.push({path:url.pathname,status:404});return route.fulfill({status:404,body:'Missing archive asset'});}
    const types={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.css':'text/css','.json':'application/json','.wasm':'application/wasm','.ico':'image/x-icon'};
    served.push({path:url.pathname,status:200});
    return route.fulfill({status:200,contentType:types[path.extname(file)]||'application/octet-stream',body:fs.readFileSync(file)});
   });
  }
  const page=await context.newPage();
  page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>requests.push(r.url()));page.on('response',r=>{if(r.status()>=400)missing.push({url:r.url(),status:r.status()});});
  const response=await page.goto('http://127.0.0.1:8000/proportion-ma/index.html',{waitUntil:'networkidle'});
  if(!response || response.status()!==200)throw new Error('Unexpected navigation response: '+response?.status());
  await page.waitForFunction(()=>typeof window.AlmProportionValidation?.runLive==='function',{},{timeout:30000});
  const live=await page.evaluate(()=>AlmProportionValidation.runLive());
  const corpus=await page.evaluate(()=>AlmProportionValidation.runCorpus());
  const outside=requests.filter(u=>/^https?:/.test(u)&&new URL(u).origin!=='http://127.0.0.1:8000');
  const result={transport:process.env.ARCHIVE_ROUTE_FILES==='1'?'Playwright same-origin routes serving exact archive file bytes; no listening server':'HTTP server',serverRequests:served,liveChecks:live.rows.length,livePassed:live.rows.filter(r=>r.pass).length,versions:live.versions,corpusChecks:corpus.checks,corpusPassed:corpus.passed,errors,missing,outside,assetPaths:[...new Set(requests.filter(u=>/^https?:/.test(u)).map(u=>new URL(u).pathname.slice(1)))].sort()};
  fs.writeFileSync('results/ui-smoke.json',JSON.stringify(result,null,2)+'\n');
  if(live.rows.length!==16||live.rows.some(r=>!r.pass)||corpus.checks!==298116||corpus.passed!==298116||errors.length||missing.length||outside.length)throw new Error(JSON.stringify(result));
 } finally {
  for(const context of browser.contexts())await context.close();
  await browser.close();
 }
 console.log('ARCHIVE UI PASS: 16/16 live R quantities; 298116/298116 corpus checks; no missing assets, off-origin requests or page errors.');
})().then(()=>process.exit(0),e=>{console.error(e);process.exit(1);});
