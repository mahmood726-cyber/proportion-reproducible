"""Fail-closed source inventory, metadata, table, image and output verification."""
import hashlib,json,re,tempfile
from pathlib import Path
from PIL import Image
import yaml
from recut_integrity import verify_pins, source_files
from make_outputs import ROOT,read,csvread,build
def main():
    provenance=verify_pins()
    actual={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files()}
    assert actual==read(ROOT/'SOURCE_SHA256.json'),'Source inventory/hash mismatch'
    app=read(ROOT/'app/app-sha256.json')
    assert set(app)=={p.relative_to(ROOT/'app').as_posix() for p in (ROOT/'app').rglob('*') if p.is_file() and p.name!='app-sha256.json'}
    for name,sha in app.items():assert hashlib.sha256((ROOT/'app'/name).read_bytes()).hexdigest()==sha,name
    assert set(read(ROOT/'results/browser-asset-paths.json'))<=set(app)
    assert read(ROOT/'results/asset-availability.json')['missing_local_assets']==[]
    assert 'favicon.ico' in app, 'Automatic browser favicon request must be served'
    smoke=read(ROOT/'results/ui-smoke.json')
    assert smoke['liveChecks']==smoke['livePassed']==16
    assert smoke['corpusChecks']==smoke['corpusPassed']==298116
    assert smoke['errors']==smoke['missing']==smoke['outside']==[]
    assert set(smoke['assetPaths'])<=set(app)
    assert smoke['serverRequests'] and all(r['status']<400 for r in smoke['serverRequests'])
    assert all(r['path'].split('?')[0].lstrip('/') in app for r in smoke['serverRequests'])
    assert smoke['versions']['metafor']=='4.8-0' and smoke['versions']['webR']=='0.5.5'
    runtime=read(ROOT/'results/validation-r-runtime.json')
    assert runtime['metafor']=='5.2.1' and runtime['checks']==runtime['passed']==298116
    for p in source_files():
        assert p.name not in ['paper.md','paper_v2_dictated_text.md'],'Manuscript draft included'
        if p.suffix.lower() in ['.json','.js','.mjs','.cjs','.py','.r','.md','.csv','.txt','.html','.cff','.patch','.css']:
            raw=p.read_bytes();assert not raw.startswith(b'\xef\xbb\xbf'),f'BOM: {p.name}'
            text=raw.decode('utf-8')
            assert not re.search(r'\b[A-Za-z]:[\\/](?:Users|Projects|claude-temp|E156|ProjectIndex)[\\/]',text),f'Machine path: {p.relative_to(ROOT)}'
    m=read(ROOT/'app/proportion-ma/validate/MANIFEST.json')
    for f in m['files']:
        p=ROOT/'app/proportion-ma'/f['path'];assert p.stat().st_size==f['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256'];assert b'\r' not in p.read_bytes()
        original=ROOT/('data' if p.name=='corpus.json' else 'results')/p.name
        assert hashlib.sha256(original.read_bytes()).hexdigest()==f['source_sha256']
        assert p.read_bytes()==original.read_bytes().replace(b'\r\n',b'\n')
    t=csvread(ROOT/'outputs/table1_by_quantity.csv');total=t[-1]
    for col,want in [('checks',298116),('passed_before',237911),('passed_after',298116)]:assert int(total[col])==sum(int(r[col]) for r in t[:-1])==want
    datasets=csvread(ROOT/'outputs/table2_datasets.csv');assert len(datasets)==114 and len({d['dataset'] for d in datasets})==114
    for col,want in [('analyses',240),('rows',4768),('zero_event_rows',478),('all_event_rows',23),('configurations',2160)]:assert sum(int(r[col]) for r in datasets)==want
    with tempfile.TemporaryDirectory(prefix='.verify-',dir=ROOT) as d:
        temp=Path(d);build(temp)
        assert {p.name for p in temp.iterdir()}=={p.name for p in (ROOT/'outputs').iterdir() if p.name!='validate_R_table.csv'}
        for p in temp.iterdir():assert p.read_bytes()==(ROOT/'outputs'/p.name).read_bytes(),f'Non-reproducible output: {p.name}'
    rt=ROOT/'outputs/validate_R_table.csv'
    if rt.exists():
        rows=csvread(rt);assert {r['quantity'] for r in rows}=={r['quantity'] for r in t[:-1]}
        assert sum(int(r['checks']) for r in rows)==sum(int(r['passed']) for r in rows)==298116
        for r in rows:
            prior=next(x for x in t if x['quantity']==r['quantity']);assert int(r['checks'])==int(prior['checks'])
            assert float(r['largest_difference'])<=max(map(float,r['tolerance'].split(';')))
            assert ('replayed' in r['Mode'])==r['quantity'].startswith('ui_')
    sizes=read(ROOT/'outputs/sizes.json')
    assert set(sizes)=={s+'.'+e for s in ['figure2_agreement','visual_abstract'] for e in ['png','tif']}
    for name,info in sizes.items():
        with Image.open(ROOT/'outputs'/name) as im:
            assert (im.width,im.height)==(info['width_pixels'],info['height_pixels'])
            assert abs(im.width/300*25.4-170)<.1
            assert all(abs(float(v)-300)<.001 for v in im.info['dpi'])
    for stem in ['figure2_agreement','visual_abstract']:
        with Image.open(ROOT/'outputs'/f'{stem}.png') as a,Image.open(ROOT/'outputs'/f'{stem}.tif') as b:assert a.convert('RGB').tobytes()==b.convert('RGB').tobytes()
    z=read(ROOT/'.zenodo.json');cff=yaml.safe_load((ROOT/'CITATION.cff').read_text(encoding='utf-8'))
    assert z['title']==cff['title']=='Meta-analysis of proportions in the browser: a tool validated against the R packages metafor and meta'
    assert z['creators']==[{'name':'Ahmad, Mahmood'}] and cff['authors']==[{'family-names':'Ahmad','given-names':'Mahmood'}]
    assert z['license']==cff['license']=='MIT' and z['version']==cff['version']=='1.1.0'
    assert str(cff['date-released'])=='2026-10-20'
    assert {(r['identifier'],r['relation']) for r in z['related_identifiers']}=={('https://github.com/mahmood726-cyber/allmeta','isDerivedFrom'),('10.5281/zenodo.23288388','isDerivedFrom'),(provenance['allmeta_doi'],'isDerivedFrom')}
    assert any(r.get('doi')=='10.5281/zenodo.23288388' and r.get('notes')=='isDerivedFrom' for r in cff['references'])
    assert (ROOT/'.gitattributes').read_text().strip()=='* -text'
    print(f'ARCHIVE PASS: {len(app)} app hashes; {len(actual)} source hashes; 298116/298116 historical checks; tables, metadata, reproducible outputs and image pixels verified.')
if __name__=='__main__':main()
