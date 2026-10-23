"""Run official macro models and finite cached-system programs; no physical claim."""
import argparse
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--sram-root',required=True,type=Path);p.add_argument('--verilator',default='verilator');p.add_argument('--jobs',default='2');p.add_argument('--only',choices=['all','macros','mmio','memory'],default='all');a=p.parse_args()
assert (ROOT/'VARIANT').read_text().strip()=='sram-ip'
macros=('ics55_ecos_sram_128x74_m4','ics55_ecos_sram_512x76_m4','ics55_ecos_sram_4096x64_m4')
models=[a.sram_root.resolve()/n/'verilog'/(n+'_core.v') for n in macros]
assert all(x.is_file() for x in models),'Use the three official functional models'
wrapper=ROOT/'rtl/sram/ics55_openbpu_wrappers.v';soft=ROOT/'rtl/sram/ics55_soft_dualport.v'
build=ROOT/'build/sram';build.mkdir(parents=True,exist_ok=True)
if a.only in ('all','macros'):
    subprocess.run(['iverilog','-g2012','-s','sram_tb','-o',str(build/'macros'),str(ROOT/'sim/sram_tb.sv'),str(wrapper),*[str(x) for x in models]],check=True)
    subprocess.run(['vvp',str(build/'macros')],check=True,timeout=180)
for mode,harness in [('mmio','cached-smoke.cpp'),('memory','memory-smoke.cpp')]:
    if a.only not in ('all',mode):continue
    obj=build/mode;obj.mkdir(exist_ok=True)
    with (obj/'build.log').open('w') as log:
        subprocess.run([a.verilator,'--cc','--exe','--build','--no-timing','-j',a.jobs,'-Wno-fatal','--top-module','Polaris','--output-split','10000','--output-split-cfuncs','200','--Mdir',str(obj),'-CFLAGS','-O1',str(ROOT/'rtl/Polaris.v'),str(wrapper),str(soft),*[str(x) for x in models],str(ROOT/'sim'/harness)],stdout=log,stderr=subprocess.STDOUT,check=True)
    for stall in (0,3,7):subprocess.run([str(obj/'VPolaris'),str(stall)],check=True,timeout=180)
