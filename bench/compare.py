import json,sys,math,re
from collections import defaultdict
from pathlib import Path
app_path=sys.argv[1] if len(sys.argv)>1 else 'app.json'
prefix=sys.argv[2] if len(sys.argv)>2 else 'original'
ref=json.loads(Path('reference.json').read_text()); app=json.loads(Path(app_path).read_text())
assert set(ref)==set(app),'configuration keys differ'
stats=defaultdict(lambda:dict(checks=0,passed=0,max_difference=0,worst=None,tolerances=set()))
failures=[]
def check(key,q,a,b,tol):
    s=stats[q];s['checks']+=1;s['tolerances'].add(tol)
    if a is None or b is None: diff=0 if a is b else math.inf
    elif isinstance(b,bool):diff=0 if a==b else 1
    else:diff=abs(a-b)/(1 if q.endswith('Qp') else max(1,abs(b))) if math.isfinite(a) and math.isfinite(b) else math.inf
    ok=diff<=tol;s['passed']+=ok
    if diff>s['max_difference']:s['max_difference']=diff;s['worst']=key
    if not ok:failures.append(dict(configuration=key,quantity=q,app=a,reference=b,difference=diff,tolerance=tol))
for key,r in ref.items():
    a=app[key];check(key,'status',a['status']==r['status'],True,0)
    if r['status']!='ok' or a['status']!='ok':continue
    iterative=key.endswith('|PM')
    for q,b in r['values'].items():
        tol=1e-6 if iterative and q not in ('Q','df','i2','k') else 1e-9
        check(key,q,a['values'].get(q),b,tol)
    for q in ('yi','vi'):
        assert a[q] is not None,key
        assert len(a[q])==len(r[q]),key
        for i,b in enumerate(r[q]):check(key+f'#{i+1}',q,a[q][i],b,1e-9)
    assert len(a['studies'])==len(r['studies'])
    for i,(aa,rr) in enumerate(zip(a['studies'],r['studies'])):
        for q,b in rr.items():check(key+f'#{i+1}','study_'+q,aa[q],b,1e-6 if q=='rel' and iterative else 1e-9)
    check(key,'ui_row_count',a['display']['rows'],r['values']['k']+1,0)
    check(key,'ui_forest_diamond',a['display']['forest'],1,0)
    shown=re.findall(r'[-+]?\d+\.\d+%',a['display']['pooled'])
    expected=[f"{100*r['values'][q]:.1f}%" for q in ('poolP','poolLo','poolHi')]+['100%']
    # 100% weight has no decimal and is deliberately absent from this regex.
    check(key,'ui_pooled_text',shown==expected[:3],True,0)
    shown_pi=re.findall(r'prediction interval = (.*)',a['display']['heterogeneity'])
    expected_pi=[] if r['values']['poolPiLo'] is None else [f"{100*r['values'][q]:.1f}%" for q in ('poolPiLo','poolPiHi')]
    actual_pi=re.findall(r'[-+]?\d+\.\d+%',shown_pi[0]) if shown_pi else []
    check(key,'ui_prediction_text',actual_pi==expected_pi,True,0)
for q,s in stats.items():
    s['tolerances']=sorted(s['tolerances'])
    print(f"{q}: {s['passed']}/{s['checks']} pass; max difference={s['max_difference']:.17g}; tolerance={s['tolerances']}")
total=sum(s['checks'] for s in stats.values());passed=sum(s['passed'] for s in stats.values())
result=dict(app=app_path,checks=total,passed=passed,failed=total-passed,quantities=dict(stats),failures=failures)
Path(prefix+'-results.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(f'{passed}/{total} checks pass')
