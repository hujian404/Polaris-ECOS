# SPDX-License-Identifier: MulanPSL-2.0
"""A synthetic clock-only spatial proxy, not an electrical reduction of Polaris."""
import argparse,hashlib,json,re,shutil
from pathlib import Path
p=argparse.ArgumentParser(description="Generate a synthetic clock-only regular-sink proxy")
p.add_argument('--template',type=Path,required=True,help="Existing nine-macro reproducer project")
p.add_argument('--pdk',type=Path,required=True,help="ICS55 PDK root")
p.add_argument('--out',type=Path,required=True,help="Fresh output project directory")
p.add_argument('--grid',type=int,default=64,choices=(16,32,64,128))
a=p.parse_args()
source=a.template.resolve();project=a.out.resolve();label=project.name
assert source.is_dir() and not project.exists(), "Use an existing template and fresh output"
lib=a.pdk.resolve()/'IP/STD_cell/ics55_LLSC_H7C_V1p10C100/ics55_LLSC_H7CR/liberty/ics55_LLSC_H7CR_ss_rcworst_1p08_125_nldm.lib'
def block(text,start):
 opening=text.index('{',start);depth=1;index=opening+1
 while depth:
  if text[index]=='{':depth+=1
  elif text[index]=='}':depth-=1
  index+=1
 return text[opening+1:index-1]
text=lib.read_text(encoding="utf-8");chosen=None
for match in re.finditer(r'\bcell\s*\(\s*([^\s)]+)\s*\)\s*\{',text):
 cell=match.group(1).strip('"');body=block(text,match.start())
 ff=re.search(r'\bff\s*\([^)]*\)\s*\{',body)
 if ff is None:continue
 sequential=block(body,ff.start())
 clock=re.search(r'\bclocked_on\s*:\s*"([A-Za-z_][A-Za-z0-9_]*)"',sequential)
 if clock is None or re.search(r'\b(?:clear|preset)\s*:',sequential):continue
 if not cell.startswith('DFF'):continue
 chosen=(cell,clock.group(1));break
assert chosen,'No ordinary positive-clock reset-free DFF found in the real library'
cell,clock_pin=chosen
definition=(source/'inputs/clock.def').read_text(encoding="utf-8")
die=tuple(map(int,re.search(r'DIEAREA\s*\(\s*(\d+)\s+(\d+)\s*\)\s*\(\s*(\d+)\s+(\d+)\s*\)',definition).groups()))
rows=re.findall(r'(?m)^ROW\s+\S+\s+(\S+)\s+(\d+)\s+(\d+)\s+\S+\s+DO\s+\d+\s+BY\s+1\s+STEP\s+(\d+)\s+0\s*;',definition)
assert rows
site=rows[0][0];x0=int(rows[0][1]);y0=int(rows[0][2]);xpitch=int(rows[0][3])
ys=sorted(set(int(x[2]) for x in rows));ypitch=ys[1]-ys[0]
assert all(y%ypitch==ys[0]%ypitch for y in ys)
new_rows=[]
for index,y in enumerate(range(y0,die[3]-ypitch,ypitch)):
 new_rows.append(f'ROW PROXY_ROW_{index} {site} {x0} {y} '+('FS' if index%2==0 else 'N')+f' DO {(die[2]-2*x0)//xpitch} BY 1 STEP {xpitch} 0 ;')
definition=re.sub(r'(?m)^ROW[^\n]*\n','',definition)
position=definition.index('COMPONENTS ')
definition=definition[:position]+'\n'.join(new_rows)+'\n'+definition[position:]
components=[];connections=[];instances=[]
for row in range(a.grid):
 y=y0+round(((die[3]-2*y0)*(row+1)/(a.grid+1))/ypitch)*ypitch
 orientation='FS' if ((y-y0)//ypitch)%2==0 else 'N'
 for column in range(a.grid):
  x=x0+round(((die[2]-2*x0)*(column+1)/(a.grid+1))/xpitch)*xpitch
  name=f'proxy_{row}_{column}'
  components.append(f'- {name} {cell} + FIXED ( {x} {y} ) {orientation} ;')
  connections.append(f' ( {name} {clock_pin} )')
  instances.append(f'  {cell} {name} (.{clock_pin}(clock));')
definition=re.sub(r'COMPONENTS\s+9\s*;.*?END COMPONENTS','COMPONENTS '+str(a.grid*a.grid)+' ;\n'+'\n'.join(components)+'\nEND COMPONENTS',definition,flags=re.S)
definition=re.sub(r'NETS\s+1\s*;.*?END NETS','NETS 1 ;\n- clock ( PIN clock )\n'+'\n'.join(connections)+'\n ;\nEND NETS',definition,flags=re.S)
definition=definition.replace('DESIGN SRAMClockRepro ;','DESIGN RegularClockProxy ;')
(project/'inputs').mkdir(parents=True)
(project/'inputs/clock.def').write_text(definition,encoding='utf-8')
(project/'inputs/clock.v').write_text('module RegularClockProxy(input clock);\n'+'\n'.join(instances)+'\nendmodule\n',encoding='utf-8')
shutil.copy2(source/'inputs/clock.sdc',project/'inputs/clock.sdc')
config=re.sub(r'(?m)^name\s*=\s*"[^\n]+?"', 'name = '+json.dumps(label), (source/'ecc.toml').read_text(encoding="utf-8"), count=1).replace('top = "SRAMClockRepro"','top = "RegularClockProxy"')
(project/'ecc.toml').write_text(config,encoding='utf-8')
record={'scope':'Synthetic clock-only spatial proxy; data pins omitted. Not electrically equivalent to Polaris and not signoff evidence. Inherits external PDK/IP paths and parameters from the supplied template.', 'grid':a.grid,'regular_sinks':a.grid*a.grid,'cell':cell,'clock_pin':clock_pin,'die_dbu':die,'input_sha256':{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in (project/'inputs').iterdir()}}
(project/'generation.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,indent=2))
