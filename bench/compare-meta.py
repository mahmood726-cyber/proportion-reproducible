import json,math
from pathlib import Path
from collections import defaultdict
a=json.loads(Path('app-patched.json').read_text());r=json.loads(Path('meta-reference.json').read_text())
stats=defaultdict(lambda:dict(checks=0,passed=0,max_difference=0,worst=None)); failures=[]
assert set(a)==set(r),'Secondary reference configuration coverage differs'
for key,rr in r.items():
 aa=a[key];q='status';s=stats[q];s['checks']+=1;s['passed']+=aa['status']==rr['status']
 if aa['status']!=rr['status']: failures.append(dict(configuration=key,quantity='status',app=aa['status'],reference=rr['status']))
 if aa['status']!='ok' or rr['status']!='ok':continue
 for q,b in rr['values'].items():
  av=aa['values'][q];diff=abs(av-b)/max(1,abs(b)) if av is not None and b is not None else math.inf
  tol=1e-6 if key.endswith('|PM') else 1e-9
  s=stats[q];s['checks']+=1;s['passed']+=diff<=tol
  if diff>s['max_difference']:s['max_difference']=diff;s['worst']=key
  if diff>tol:failures.append(dict(configuration=key,quantity=q,app=av,reference=b,difference=diff,tolerance=tol))
for q,s in stats.items():print(f"{q}: {s['passed']}/{s['checks']} pass; max difference={s['max_difference']:.17g}")
checks=sum(s['checks'] for s in stats.values());passed=sum(s['passed'] for s in stats.values())
Path('meta-results.json').write_text(json.dumps(dict(checks=checks,passed=passed,failed=checks-passed,quantities=dict(stats),failures=failures),indent=2))
print(f'{passed}/{checks} checks pass')
