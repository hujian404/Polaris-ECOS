"""Copy a matched native checkpoint into a new project, with optional physical gate."""
import argparse
import gzip
import json
from pathlib import Path
import re
import shutil
p=argparse.ArgumentParser();p.add_argument('--source',required=True,type=Path);p.add_argument('--stage',required=True);p.add_argument('--out',required=True,type=Path);p.add_argument('--source-project',required=True,type=Path);p.add_argument('--require-clean',action='store_true');a=p.parse_args()
assert not a.out.exists()
state=json.loads((a.source/'home/flow.json').read_text())['steps']
assert state and all(x['state']=='Success' for x in state),'Source workspace has incomplete/failed steps; do not silently certify a recovered derivative'
if a.require_clean:
    for stage in ('drc','lvs'):
        metrics=json.loads((a.source/(stage+'_ecc/analysis/qor_metrics.json')).read_text())['metrics']
        assert next(m['value'] for m in metrics if m['id']==stage+'_count')==0
folder=a.source/a.stage/'output'
nets=[x for x in folder.glob('*.v.gz') if '_sim' not in x.name];assert len(nets)==1
with gzip.open(nets[0],'rb') as stream:assert stream.read(4096).strip(),'Empty native netlist (Issue350)'
defs=list(folder.glob('*.def.gz'));assert len(defs)<=1
config=(a.source_project/'ecc.toml').read_text()
runtime=json.loads((a.source_project/'runtime.json').read_text())
inputs=a.out/'inputs';inputs.mkdir(parents=True)
shutil.copy2(nets[0],inputs/'Polaris.v.gz')
golden=a.source_project/'inputs/golden.v.gz'
shutil.copy2(golden if golden.exists() else nets[0],inputs/'golden.v.gz')
shutil.copy2(a.source_project/'inputs/Polaris.sdc',inputs/'Polaris.sdc')
config=re.sub(r'^rtl = .*\n','',config,flags=re.M)
config=re.sub(r'^(netlist|golden_netlist|def) = .*\n','',config,flags=re.M)
config=config.replace('top = "Polaris"','top = "Polaris"\nnetlist = "inputs/Polaris.v.gz"\ngolden_netlist = "inputs/golden.v.gz"')
if defs:
    shutil.copy2(defs[0],inputs/'Polaris.def.gz');config=config.replace('top = "Polaris"','top = "Polaris"\ndef = "inputs/Polaris.def.gz"')
(a.out/'ecc.toml').write_text(config);(a.out/'runtime.json').write_text(json.dumps(runtime,indent=2)+'\n')
print(a.out)
