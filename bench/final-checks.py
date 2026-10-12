from pathlib import Path
import json,subprocess,sys
for name,args in [('original',['compare.py','app.json','original']),('patched',['compare.py','app-patched.json','patched']),('meta',['compare-meta.py'])]:
 p=subprocess.run([sys.executable,*args],text=True,capture_output=True)
 Path(name+'-console.txt').write_text(p.stdout+p.stderr,encoding='utf8')
 print(p.stdout,end='');assert p.returncode==0,p.stderr
o=json.loads(Path('original-results.json').read_text());p=json.loads(Path('patched-results.json').read_text());m=json.loads(Path('meta-results.json').read_text())
assert p['failed']==0,'Patched primary comparison failed'
assert all('|raw|' in x['configuration'] for x in m['failures']),'Unexpected secondary discrepancy'
corpus={c['id']:c for c in json.loads(Path('corpus.json').read_text())}
assert all(any(z['x'] in (0,z['n']) for z in corpus[x['configuration'].rsplit('|',2)[0]]['rows']) for x in m['failures']),'Secondary discrepancy without boundary counts'
Path('results.json').write_text(json.dumps(dict(status='primary_pass_secondary_conventions_reviewed',secondary_note='Native meta PRAW corrects variance only; the app/metafor PR correct both yi and vi at boundaries.',original=o,patched=p,meta=m),indent=2,allow_nan=False),encoding='utf8')
print('Final validation PASS (primary); secondary raw-boundary convention differences documented')
