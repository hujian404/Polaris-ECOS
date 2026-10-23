"""Prepare the checkpoint-specific two-buffer ECO; no quality claim until rerun."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import shutil
p=argparse.ArgumentParser()
for name in ('netlist','def','sdc','golden','liberty','lef','out'):
    p.add_argument('--'+name,required=True,type=Path)
p.add_argument('--instances',nargs='+',default=['hold43545','hold43546'])
a=p.parse_args()
assert not a.out.exists(),'Use a fresh output directory'
assert len(a.instances)==len(set(a.instances))
def read(path):
    return gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes()
lib=a.liberty.read_text();lef=a.lef.read_text();cells={}
for master in ('DLY4X2H7R','BUFX4H7R'):
    match=re.search(r'\bcell\s*\(\s*'+master+r'\s*\)\s*\{',lib);assert match,master
    block=re.split(r'\n\s*cell\s*\(',lib[match.end():],maxsplit=1)[0]
    function=re.findall(r'\bfunction\s*:\s*"([^"]+)"',block)
    assert len(function)==1 and re.sub(r'[\s()]','',function[0])=='A'
    assert set(re.findall(r'\bpin\s*\(\s*(\w+)\s*\)',block))=={'A','Y'}
    geometry=re.search(r'\bMACRO\s+'+master+r'\b(.*?)\bEND\s+'+master+r'\b',lef,re.S);assert geometry
    cells[master]=tuple(map(float,re.search(r'\bSIZE\s+([\d.]+)\s+BY\s+([\d.]+)',geometry[1]).groups()))
assert cells['BUFX4H7R'][1]==cells['DLY4X2H7R'][1]
assert cells['BUFX4H7R'][0]<=cells['DLY4X2H7R'][0]
net=read(a.netlist);definition=read(a.__dict__['def'])
for instance in a.instances:
    token=re.escape(instance.encode())
    net,count=re.subn(rb'\bDLY4X2H7R(\s+\\?'+token+rb'\s*\()',rb'BUFX4H7R\1',net)
    assert count==1,(instance,'netlist',count)
    definition,count=re.subn(rb'(-\s+'+token+rb'\s+)DLY4X2H7R\b',rb'\1BUFX4H7R',definition)
    assert count==1,(instance,'DEF',count)
match=re.search(rb'(?ms)^NETS\s+\d+\s*;(.*?)^END NETS',definition);assert match
regular,wires=re.subn(rb'\+\s+(?:ROUTED|FIXED|COVER)\b[^;]*',b'',match[1]);assert wires>0
special_before=re.findall(rb'(?ms)^SPECIALNETS\b.*?^END SPECIALNETS',definition)
definition=definition[:match.start(1)]+regular+definition[match.end(1):]
assert re.findall(rb'(?ms)^SPECIALNETS\b.*?^END SPECIALNETS',definition)==special_before
a.out.mkdir(parents=True)
for name,data in (('Polaris.v.gz',net),('Polaris.def.gz',definition),('golden.v.gz',read(a.golden))):
    with gzip.open(a.out/name,'wb') as f:f.write(data)
shutil.copy2(a.sdc,a.out/'Polaris.sdc')
(a.out/'eco.json').write_text(json.dumps({'instances':a.instances,'from':'DLY4X2H7R','to':'BUFX4H7R','cleared_regular_wire_records':wires,'netlist_sha256':hashlib.sha256(net).hexdigest(),'scope':'Prepared only. Route, DRC/LVS, LEC, RCX and all setup/hold corners must be rerun.'},indent=2)+'\n')
print(a.out)
