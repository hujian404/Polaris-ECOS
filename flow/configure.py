"""Generate a local ECC project with explicit tool and optional SRAM paths."""
import argparse
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
def configure(args):
    bundle=args.bundle.resolve();suite=args.oss_cad.resolve();out=args.out.resolve()
    assert not out.exists(), 'Use a fresh project directory'
    assert (bundle/'ecc/ecc').is_file() and (suite/'bin/yosys').is_file(), 'Install the documented tool bundle first'
    pdk=bundle/'pdk'
    mapping=args.layermap.resolve() if args.layermap else pdk/'techfile/icsprout55.layermap'
    assert mapping.is_file(), 'Pass --layermap pointing to the official PDK mapping (Installer Issue35)'
    variant=(ROOT/'VARIANT').read_text().strip()
    cached=variant=='sram-ip'
    if cached:assert args.sram_root and args.sram_root.is_dir(), 'sram-ip requires --sram-root with the three official packages'
    (out/'inputs').mkdir(parents=True)
    shutil.copy2(ROOT/'rtl/Polaris.v',out/'inputs/Polaris.v')
    shutil.copy2(ROOT/'flow/Polaris.sdc',out/'inputs/Polaris.sdc')
    rtl=['inputs/Polaris.v']
    if cached:
        for name in ('ics55_openbpu_wrappers.v','ics55_soft_dualport.v'):
            shutil.copy2(ROOT/'rtl/sram'/name,out/'inputs'/name);rtl.append('inputs/'+name)
    name='openbpu-cached-sram' if cached else 'openbpu-cacheless'
    text='[design]\nname = '+json.dumps(name)+'\ntop = "Polaris"\nrtl = '+json.dumps(rtl)+'\nsdc = "inputs/Polaris.sdc"\nclock_port = "clock"\nfrequency_mhz = 50.0\n[pdk]\nname = "ics55"\n[pdk.overrides]\nmapping_file = '+json.dumps(str(mapping))+'\n'
    if cached:
        macros=('ics55_ecos_sram_128x74_m4','ics55_ecos_sram_512x76_m4','ics55_ecos_sram_4096x64_m4')
        stdlibs=[];lefs=[]
        for v in ('R','L'):
            matches=list(pdk.rglob('ics55_LLSC_H7C'+v+'_ss_rcworst_1p08_125_nldm.lib'));assert len(matches)==1;stdlibs+=matches
            matches=list(pdk.rglob('ics55_LLSC_H7C'+v+'_ecos.lef'));assert len(matches)==1;lefs+=matches
        libs=stdlibs[:]
        for macro in macros:
            lib=args.sram_root/macro/'lib'/(macro+'_ss1p08v125ccmax.lib')
            lef=args.sram_root/macro/'lef'/(macro+'.lef')
            assert lib.is_file() and lef.is_file(),macro
            libs.append(lib.resolve());lefs.append(lef.resolve())
        text+='libs = '+json.dumps([str(p) for p in libs])+'\nlefs = '+json.dumps([str(p) for p in lefs])+'\n'
    text+='''[flow]
preset = "rtl2gds"
[params.place]
num_threads = 16
routability_opt = 1
target_density = 0.3
[params.floorplan]
core_util = 0.3
[params.floorplan.ifp]
thread_number = 16
[params.route.RT]
"-thread_number" = "16"
[params.rcx]
thread_num = 16
'''
    if cached:
        text+='[params.cts]\nmax_cap = "0.45"\nroot_input_slew = "0.05"\nmax_sink_tran = "0.4"\nbuffer_type = ["BUFX8H7L", "BUFX12H7L", "BUFX16H7L", "BUFX20H7L"]\n'
        template=(ROOT/'flow/sram-corners.toml.in').read_text()
        text+=template.replace('__PDK__',str(pdk)).replace('__SRAM__',str(args.sram_root.resolve()))
    (out/'ecc.toml').write_text(text)
    (out/'runtime.json').write_text(json.dumps({'bundle':str(bundle),'oss_cad':str(suite),'variant':variant,'design_name':name},indent=2)+'\n')
    print(out/'ecc.toml')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--bundle',required=True,type=Path);p.add_argument('--oss-cad',required=True,type=Path);p.add_argument('--out',required=True,type=Path);p.add_argument('--layermap',type=Path);p.add_argument('--sram-root',type=Path)
    configure(p.parse_args())
