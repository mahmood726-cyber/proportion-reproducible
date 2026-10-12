from pathlib import Path
import shutil,difflib
src=Path('original');dst=Path('patched')
shutil.copytree(src,dst,dirs_exist_ok=True)
p=Path('proportion-ma/index.html')
a=(src/p).read_text(encoding='utf8');b=a
b=b.replace('var MAX = 200, EPS = 3e-7, FPMIN = 1e-30;','var MAX = 200, EPS = 1e-14, FPMIN = 1e-30;')
b=b.replace('if (hi - lo < 1e-8) break;','if (hi - lo < 1e-14) break;')
b=b.replace('    function ftBack(y, n) {\n      var s', '''    function ftBack(y, n) {
      if (!Number.isFinite(y) || !Number.isFinite(n) || n <= 0) return NaN;
      // Match metafor::transf.ipft.hm outside the finite-n transform domain.
      if (y < ftTransform(0, n).y) return 0;
      if (y > ftTransform(n, n).y) return 1;
      var s''')
assert b!=a
(dst/p).write_text(b,encoding='utf8',newline='\n')
Path('fix.patch').write_text(''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+p.as_posix(),tofile='b/'+p.as_posix())),encoding='utf8')
print('Wrote local patched copy and fix.patch; original source unchanged')
