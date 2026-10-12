import re,json,hashlib,subprocess,sys
from pathlib import Path
source=Path(sys.argv[1])
manifest=json.loads(Path('manifest.json').read_text());corpus=json.loads(Path('corpus.json').read_text())
evidence=[]
for c in corpus:
 nm=c['dataset'].split('$')[0]
 manual=re.sub('.\x08','',Path('manuals',nm+'.txt').read_text(errors='replace'))
 fields={}
 for field in re.findall(r'[A-Za-z][A-Za-z0-9_.]*',c['x']+'+'+c['n']):
  lines=[l.strip() for l in manual.splitlines() if '*'+field+'*' in l]
  assert lines,(c['id'],field)
  fields[field]=lines
 evidence.append(dict(id=c['id'],manual='manuals/'+nm+'.txt',fields=fields))
Path('schema-evidence.json').write_text(json.dumps(evidence,indent=2),encoding='utf8')
hashes={}
for p in Path('original').rglob('*'):
 if p.is_file():
  rel=p.relative_to('original'); original=source/rel
  assert original.is_file(),str(rel)
  sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
  assert sha(p)==sha(original),str(rel)
  hashes[rel.as_posix()]=sha(p)
commit=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
Path('source-provenance.json').write_text(json.dumps(dict(commit=commit,sha256=hashes),indent=2))
print(f'{len(evidence)} schema mappings verified against packaged manuals; {len(hashes)} copied source files byte-identical')
