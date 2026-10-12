const fs=require('fs'), path=require('path'), {pathToFileURL}=require('url');
const {chromium}=require(process.env.PLAYWRIGHT_PATH);
(async()=>{
const root=process.argv[2]||'original', out=process.argv[3]||'app.json';
const corpus=JSON.parse(fs.readFileSync('corpus.json','utf8'));
const browser=await chromium.launch({channel:'chrome',headless:true});
const page=await browser.newPage();
const errors=[]; page.on('pageerror',e=>errors.push(String(e)));
const url=pathToFileURL(path.resolve(root,'proportion-ma/index.html')).href;
const cdp=await page.context().newCDPSession(page); await cdp.send('Debugger.enable');
const lines=fs.readFileSync(path.join(root,'proportion-ma/index.html'),'utf8').split('\n');
// Conditional debugger probes read local variables without rewriting/extracting the shipped script.
await cdp.send('Debugger.setBreakpointByUrl',{url,lineNumber:lines.findIndex(l=>l.includes('var body = document.getElementById')),condition:'(window.__auditStudies = rows, false)'});
await cdp.send('Debugger.setBreakpointByUrl',{url,lineNumber:lines.findIndex(l=>l.includes('var w = rows.map')),condition:'(window.__auditTransformed = rows, false)'});
await cdp.send('Debugger.setBreakpointByUrl',{url,lineNumber:lines.findIndex(l=>l.includes('_lastResults = {')),condition:'(window.__auditLimits = {lo:lo,hi:hi,piLo:piT ? piT.lo : null,piHi:piT ? piT.hi : null}, false)'});
await page.goto(url); await page.waitForFunction(()=>typeof window._almLastPropMA==='function');
const result={}; let count=0;
for(const ca of corpus)for(const tr of ['logit','ft','raw'])for(const method of ['PM','DL','FE']){
 const key=ca.id+'|'+tr+'|'+method;
 result[key]=await page.evaluate(({ca,tr,method})=>{
  window.__auditStudies=null;window.__auditTransformed=null;window.__auditLimits=null;
  document.getElementById('src').value=ca.rows.map(r=>[r.x,r.n,r.label].join(',')).join('\n');
  document.getElementById('trans').value=tr; document.getElementById('tau-est').value=method;
  document.getElementById('btn-run').click();
  const r=window._almLastPropMA();
  if(!r)return {status:'refused',error:document.getElementById('res-body').innerText};
  if(!window.__auditLimits)throw new Error('Transformed interval probe did not fire');
  return {status:'ok',values:{...r,...window.__auditLimits},yi:window.__auditTransformed?.map(r=>r.y),vi:window.__auditTransformed?.map(r=>r.v),studies:window.__auditStudies,display:{pooled:document.querySelector('.pooled-row').innerText,heterogeneity:document.getElementById('het').innerText,rows:document.querySelectorAll('#res-body tr').length,forest:document.querySelectorAll('#forest polygon').length}};
 },{ca,tr,method});
 if(++count%300===0)console.log(count+' browser configurations');
}
fs.writeFileSync(out,JSON.stringify(result,null,2));fs.writeFileSync(out.replace('.json','-browser.json'),JSON.stringify({errors,browser:browser.version(),url,configurations:count},null,2));
await browser.close();console.log(count+' app configurations written; '+errors.length+' page errors');
})().catch(e=>{console.error(e);process.exit(1)});
