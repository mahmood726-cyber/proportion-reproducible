import json
from pathlib import Path
p=Path('meta-reference.json')
initial=json.loads(p.read_text());refined=json.loads(Path('meta-reference-refined.json').read_text())
if not Path('meta-reference-initial.json').exists():Path('meta-reference-initial.json').write_bytes(p.read_bytes())
initial.update(refined)
p.write_text(json.dumps(initial,indent=2),encoding='utf8')
print(f'{len(initial)} meta reference configurations after precision refinement and empty-corpus refusal checks')
