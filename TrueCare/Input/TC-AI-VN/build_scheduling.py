"""Build True-Care-AI-Scheduling.html: inline screenshots from Input/TC-AI-VN into the template."""
import base64, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
TPL = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'template.html')
IMG = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'opt')
OUT = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, 'True-Care-AI-Scheduling.html')
tpl = open(TPL, encoding='utf-8').read()
used = set()
def rep(m):
    name = m.group(1); used.add(name)
    with open(os.path.join(IMG, name + '.png'), 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode()
out = re.sub(r'\{\{IMG:([\w-]+)\}\}', rep, tpl)
assert '{{' not in out, 'unreplaced placeholder'
open(OUT, 'w', encoding='utf-8').write(out)
print(f'{OUT}: {len(out):,} bytes, {len(used)} images')
