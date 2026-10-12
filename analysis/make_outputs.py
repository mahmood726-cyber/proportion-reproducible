"""Recompute publication tables and figures; expected numbers are assertions only."""
import csv, json, math, re
from collections import defaultdict
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
def csvread(p):
    with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def csvwrite(p,rows):
    with p.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def compare(ref,app):
    assert set(ref)==set(app),'Configuration keys differ'
    stats={}
    def check(key,q,a,b,tol):
        s=stats.setdefault(q,dict(checks=0,passed=0,max_difference=0,worst=None,tolerances=[]))
        s['checks']+=1
        if tol not in s['tolerances']:s['tolerances'].append(tol);s['tolerances'].sort()
        if a is None or b is None:diff=0 if a is b else math.inf
        elif isinstance(b,bool):diff=0 if a==b else 1
        else:diff=abs(a-b)/max(1,abs(b)) if math.isfinite(a) and math.isfinite(b) else math.inf
        s['passed']+=diff<=tol
        if diff>s['max_difference']:s['max_difference']=diff;s['worst']=key
    for key,r in ref.items():
        a=app[key];check(key,'status',a['status']==r['status'],True,0)
        if r['status']!='ok' or a['status']!='ok':continue
        pm=key.endswith('|PM')
        for q,b in r['values'].items():check(key,q,a['values'].get(q),b,1e-6 if pm and q not in ('Q','df','i2','k') else 1e-9)
        for q in ('yi','vi'):
            assert len(a[q])==len(r[q])
            for i,b in enumerate(r[q]):check(key+f'#{i+1}',q,a[q][i],b,1e-9)
        assert len(a['studies'])==len(r['studies'])
        for i,(aa,rr) in enumerate(zip(a['studies'],r['studies'])):
            for q,b in rr.items():check(key+f'#{i+1}','study_'+q,aa[q],b,1e-6 if q=='rel' and pm else 1e-9)
        check(key,'ui_row_count',a['display']['rows'],r['values']['k']+1,0)
        check(key,'ui_forest_diamond',a['display']['forest'],1,0)
        shown=re.findall(r'[-+]?\d+\.\d+%',a['display']['pooled'])
        expected=[f"{100*r['values'][q]:.1f}%" for q in ('poolP','poolLo','poolHi')]
        check(key,'ui_pooled_text',shown==expected,True,0)
        pi=re.findall(r'prediction interval = (.*)',a['display']['heterogeneity'])
        actual=re.findall(r'[-+]?\d+\.\d+%',pi[0]) if pi else []
        expected=[] if r['values']['poolPiLo'] is None else [f"{100*r['values'][q]:.1f}%" for q in ('poolPiLo','poolPiHi')]
        check(key,'ui_prediction_text',actual==expected,True,0)
    return stats

def secondary(app,ref):
    assert set(app)==set(ref)
    checks=passed=0
    for key,r in ref.items():
        a=app[key];checks+=1;passed+=a['status']==r['status']
        if a['status']!='ok' or r['status']!='ok':continue
        for q,b in r['values'].items():
            av=a['values'][q];d=abs(av-b)/max(1,abs(b)) if av is not None and b is not None else math.inf
            checks+=1;passed+=d<=(1e-6 if key.endswith('|PM') else 1e-9)
            if d>(1e-6 if key.endswith('|PM') else 1e-9):assert '|raw|' in key,'Unexpected secondary mismatch'
    return checks,passed

def figures(out,stats,before,n):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.titlesize':10,'axes.labelsize':8,'xtick.labelsize':8,'ytick.labelsize':8,'legend.fontsize':8})
    quantities=[q for q,s in stats.items() if s['tolerances']!=[0]]
    fig,ax=plt.subplots(figsize=(170/25.4,6.8))
    for i,q in enumerate(quantities):
        for group,offset,marker,color,label in [(before,.13,'x','#bd4b32','Before fixes'),(stats,-.13,'o','#24658a','After fixes')]:
            s=group[q];x=math.log10(max(1e-16,s['max_difference']))
            ax.scatter(x,i+offset,marker=marker,color=color,s=26,label=label if i==0 else None)
            if group is before and s['passed']<s['checks']:ax.annotate(f" {s['checks']-s['passed']:,} failed",(x,i+offset),fontsize=8,va='center')
    ax.axvline(-9,ls='--',color='#555',label='Closed form: 1e-9')
    ax.axvline(-6,ls=':',color='#555',label='PM dependent: 1e-6')
    ax.set_yticks(range(len(quantities)),quantities);ax.invert_yaxis();ax.set_xlim(-16.6,2.5)
    ax.set_xlabel('log10 maximum relative difference within quantity')
    ax.set_title('Browser versus metafor: before and after two fixes')
    ax.grid(axis='y',alpha=.15);ax.legend(loc='lower right')
    fig.text(.5,.015,'Difference = |App - R| / max(1, |R|). Zeros / <1e-16 at -16. Exact UI/status checks in Table 1.',ha='center',fontsize=8)
    fig.tight_layout(rect=(0,.04,1,1));savefig(fig,out,'figure2_agreement');plt.close(fig)
    fig=plt.figure(figsize=(170/25.4,3.65))
    boxes=[('Problem','Pooling binomial\nproportions requires\ncareful transforms\nand boundary rules.'),('Tool','allmeta in\nthe browser:\nlogit, PFT, raw;\nPM, DL, FE.'),('Validation',f"{n['datasets_used']['value']} datasets\n{n['configurations']['value']:,} configurations\nR: metafor\nand meta."),('Result',f"{n['passed']['value']:,} of {n['checks']['value']:,}\nchecks pass\n(after 2 fixes)")]
    for i,(head,body) in enumerate(boxes):
        x=.02+i*.245
        fig.patches.append(FancyBboxPatch((x,.25),.22,.52,boxstyle='round,pad=0.008',transform=fig.transFigure,facecolor=['#f4ece8','#e8f0f7','#eaf4ec','#fdf6e3'][i],edgecolor='#999'))
        fig.text(x+.11,.7,head,ha='center',weight='bold',fontsize=10)
        fig.text(x+.11,.49,body,ha='center',va='center',fontsize=8,linespacing=1.6)
    fig.text(.5,.89,'Meta-analysis of proportions in the browser',ha='center',fontsize=11,weight='bold')
    fig.text(.5,.13,'Primary: metafor. Secondary meta raw-boundary conventions differ.',ha='center',fontsize=8)
    fig.text(.5,.07,'Computational regroupings are not clinical analyses. No GLMM comparison.',ha='center',fontsize=8)
    savefig(fig,out,'visual_abstract');plt.close(fig)
def savefig(fig,out,name):
    for ext in ['png','tif']:fig.savefig(out/f'{name}.{ext}',dpi=300)

def build(out=ROOT/'outputs'):
    out.mkdir(parents=True,exist_ok=True)
    ref=read(ROOT/'results/reference.json');app=read(ROOT/'results/app-patched.json');old=read(ROOT/'results/app.json')
    corpus=read(ROOT/'data/corpus.json');manifest=read(ROOT/'data/manifest.json')
    ids={f"{ca['id']}|{tr}|{m}" for ca in corpus for tr in ['logit','ft','raw'] for m in ['PM','DL','FE']}
    assert ids==set(ref) and len(ids)==len(corpus)*9
    assert all(isinstance(r['x'],int) and isinstance(r['n'],int) and 0<=r['x']<=r['n'] and r['n']>0 for ca in corpus for r in ca['rows'])
    stats=compare(ref,app);before=compare(ref,old)
    for actual,name in [(stats,'patched-results.json'),(before,'original-results.json')]:
        ledger=read(ROOT/'results'/name)
        assert actual==ledger['quantities'],f'Quantity ledger differs: {name}'
        assert sum(x['checks'] for x in actual.values())==ledger['checks']
        assert sum(x['passed'] for x in actual.values())==ledger['passed']
    table=[dict(quantity=q,checks=s['checks'],passed_before=before[q]['passed'],passed_after=s['passed'],largest_difference=s['max_difference'],largest_difference_before=before[q]['max_difference'],tolerance=';'.join(map(str,s['tolerances']))) for q,s in stats.items()]
    table.append(dict(quantity='TOTAL',checks=sum(s['checks'] for s in stats.values()),passed_before=sum(s['passed'] for s in before.values()),passed_after=sum(s['passed'] for s in stats.values()),largest_difference='',largest_difference_before='',tolerance='quantity-specific'))
    csvwrite(out/'table1_by_quantity.csv',table)
    datasets=[]
    for dataset,m in manifest.items():
        cases=[ca for ca in corpus if ca['dataset'].split('$')[0]==dataset];rows=[r for ca in cases for r in ca['rows']]
        assert set(m['analyses'])=={ca['id'] for ca in cases}
        datasets.append(dict(dataset=dataset,status=m['status'],analyses=len(cases),rows=len(rows),zero_event_rows=sum(r['x']==0 for r in rows),all_event_rows=sum(r['x']==r['n'] for r in rows),configurations=9*len(cases)))
    csvwrite(out/'table2_datasets.csv',datasets)
    n={}
    def add(k,v,source,transform):n[k]=dict(value=v,source=source,transformation=transform)
    add('datasets_enumerated',len(manifest),'data/manifest.json','count entries')
    for status in ['used','excluded']:add('datasets_'+status,sum(m['status']==status for m in manifest.values()),'data/manifest.json','count status='+status)
    for q in ['analyses','rows','zero_event_rows','all_event_rows','configurations']:add(q,sum(d[q] for d in datasets),'data/corpus.json','sum '+q+'; analyses/arms may overlap')
    for k,status in [('successful','ok'),('refusals','refused')]:add(k,sum(r['status']==status for r in ref.values()),'results/reference.json','count status='+status)
    for k,col in [('checks','checks'),('passed','passed_after'),('before_passed','passed_before')]:add(k,table[-1][col],'results/reference.json + app-patched.json + app.json','recompute full primary comparison')
    mc,mp=secondary(app,read(ROOT/'results/meta-reference.json'))
    mr=read(ROOT/'results/meta-results.json');assert (mc,mp)==(mr['checks'],mr['passed'])
    add('meta_checks',mc,'results/meta-reference.json + app-patched.json','recompute secondary comparison')
    add('meta_passed',mp,'results/meta-reference.json + app-patched.json','recompute secondary comparison')
    for q,s in stats.items():add('max_'+q,s['max_difference'],'results/reference.json + app-patched.json','maximum relative difference for '+q)
    for k,v in read(ROOT/'results/versions.json').items():add('version_'+k,v,'results/versions.json','source runtime metadata')
    dump(out/'numbers.json',n);figures(out,stats,before,n)
    sizes={}
    for p in sorted(out.iterdir()):
        if p.suffix in ['.png','.tif']:
            with Image.open(p) as im:sizes[p.name]=dict(width_pixels=im.width,height_pixels=im.height,dpi=[float(v) for v in im.info['dpi']])
    dump(out/'sizes.json',sizes)
    expected=read(ROOT/'expected/paper_values.json');passed=0
    report=['# Reproduction report','','All findings recomputed from input/result records; expected values are assertions.','','| Claim | Expected | Reproduced | Verdict |','|---|---|---|---|']
    for k,e in expected.items():
        actual=n[k]['value'];ok=actual==e['value'];passed+=ok
        report.append(f"| {k} | {e['value']} | {actual} | {'PASS' if ok else 'FAIL'} |")
    final=f"{'PASS' if passed==len(expected) else 'FAIL'}: {passed}/{len(expected)} paper-value assertions; {n['passed']['value']}/{n['checks']['value']} final checks; {n['before_passed']['value']}/{n['checks']['value']} before fixes."
    report+=['','Figures: 300 dpi, 170 mm nominal width, text >=8 pt. Figure 2 shows per-quantity maxima; red crosses mark before-fix results and annotations identify failures. Exact status/UI checks are in Table 1. Table 2 includes all catalogue entries, with zero counts for excluded datasets.','','This command rechecks archived app/R records; validate.R recomputes R numerical fits and replays archived DOM evidence. No clinical interpretation, GLMM validation, deployment or Overmind certification is implied.','',final]
    (out/'reproduction_report.md').write_text('\n'.join(report)+'\n',encoding='utf-8',newline='\n')
    print(final)
    assert passed==len(expected) and n['passed']['value']==n['checks']['value']
    return stats
if __name__=='__main__':build()
