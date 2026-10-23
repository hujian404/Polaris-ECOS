"""Run an explicit native stage range; native results remain authoritative."""
import argparse
import json
import os
from pathlib import Path
import subprocess

def main():
    p=argparse.ArgumentParser();p.add_argument('--project',required=True,type=Path);p.add_argument('--workspace',required=True,type=Path);p.add_argument('--from',dest='start',required=True);p.add_argument('--to',dest='end',required=True);p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    project=a.project.resolve();workspace=a.workspace.resolve()
    config=json.loads((project/'runtime.json').read_text());bundle=Path(config['bundle'])
    env=os.environ.copy();env.update(CHIPCOMPILER_OSS_CAD_DIR=config['oss_cad'],CHIPCOMPILER_ICS55_PDK_ROOT=str(bundle/'pdk'),CHIPCOMPILER_ECC_SIZER_ROOT=str(bundle/'ecc-sizer'),CHIPCOMPILER_KEPLER_FORMAL_ROOT=str(bundle/'kepler-formal'),ECOS_COURSE_NO_GENERIC_ABC='1',ECOS_COURSE_HIER_MAP='1',ECOS_COURSE_SKIP_ONEHOT='1',YOSYS_SYNTH_STRATEGY='DELAY 0')
    env['PATH']=str(bundle/'ecc-sizer/bin')+os.pathsep+str(bundle/'kepler-formal')+os.pathsep+env['PATH']
    command=[str(bundle/'ecc/ecc'),'run','--project',str(project),'--workspace',str(workspace),'--from',a.start,'--to',a.end]
    if a.dry_run:print(json.dumps({'command':command,'variant':config['variant'],'scope':'Dry run only, no EDA stage executed'},indent=2));return
    assert not workspace.exists(), 'Use a fresh workspace; preserve previous native evidence'
    raise SystemExit(subprocess.run(command,env=env).returncode)
if __name__=='__main__':main()
