"""Check public structure and frozen result identities without installing a PDK."""
import ast
import hashlib
import json
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
for p in ROOT.rglob('*.py'):
    if not any(x in p.parts for x in ('local','build','generated','.git')):ast.parse(p.read_text())
manifest=json.loads((ROOT/'results/input-manifest.json').read_text())
assert hashlib.sha256((ROOT/'rtl/Polaris.v').read_bytes()).hexdigest()==manifest['rtl_sha256']
assert hashlib.sha256((ROOT/'flow/Polaris.sdc').read_bytes()).hexdigest()==manifest['sdc_sha256']
variant=(ROOT/'VARIANT').read_text().strip();assert variant in ('cacheless','sram-ip')
rows=list((ROOT/'results/cacheless/corners').glob('*/*/qor_summary.json'));assert len(rows)==13
for path in rows:
    summary=json.loads(path.read_text())['summary']
    assert all(summary[k]['nvp']==0 and summary[k]['tns']==0 and summary[k]['wns']>=0 for k in ('setup','hold'))
assert (ROOT/'LICENSE').exists() and (ROOT/'NOTICE.md').exists()
for p in ROOT.rglob('*'):
    if not p.is_file() or any(x in p.parts for x in ('.git','local','build','generated','runs','artifacts','ip')):continue
    assert p.stat().st_size<50*1024*1024,p
    if p.suffix in ('.py','.sh','.md','.toml','.json','.v','.scala','.sdc'):
        text=p.read_text(errors='replace')
        assert not re.search(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)',text),p
        assert not re.search(r'(?:192[.]168[.]\d+[.]\d+|/(?:data/)?home/(?:jian[.]hu|herbert)|[CD]:[/\\](?:Users|WorkSpace)[/\\])',text),p
print('Public structure and frozen thirteen-corner result passed; this does not run EDA or certify new physical results.')
