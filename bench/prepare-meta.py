import json,csv
from pathlib import Path
text=Path('reference.R').read_text()
Path('json-writer.R').write_text(text[text.index('js <- function'):text.index('items<-')],encoding='utf8')
with open('meta-input.csv','w',newline='',encoding='utf8') as f:
 w=csv.writer(f);w.writerow(['id','x','n'])
 for c in json.loads(Path('corpus.json').read_text()):
  if not c['rows']:w.writerow([c['id'],'NA','NA'])
  for r in c['rows']:w.writerow([c['id'],r['x'],r['n']])
