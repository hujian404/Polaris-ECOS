"""Install the recorded opt-in controls; preserve the unmodified default path.

Tcl context originates in Efabless/OpenLane-derived scripts, Apache-2.0.
Copyright 2020 Efabless Corporation. See LICENSES/Apache-2.0.txt.
New wrapper Copyright (c) 2026 Hu Jian, MulanPSL-2.0.
"""
import argparse
import difflib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--script',required=True,type=Path);a=p.parse_args()
original=a.script.read_text()
markers=('ECOS_COURSE_NO_GENERIC_ABC','ECOS_COURSE_HIER_MAP','ECOS_COURSE_SKIP_ONEHOT')
if all(m in original for m in markers):print('All opt-in controls already present');raise SystemExit(0)
assert not any(m in original for m in markers),'Partially patched runtime: inspect before continuing'
text=original
old='synth -run fine:\n';assert text.count(old)==1
text=text.replace(old,'''if {[info exists ::env(ECOS_COURSE_NO_GENERIC_ABC)] && $::env(ECOS_COURSE_NO_GENERIC_ABC) eq "1"} {
  synth -noabc -run fine:
} else {
  synth -run fine:
}
''')
old='synth -top $top_design -run :fine\n';assert text.count(old)==1
text=text.replace(old,'''if {[info exists ::env(ECOS_COURSE_HIER_MAP)] && $::env(ECOS_COURSE_HIER_MAP) eq "1"} {
  set keep_hierarchy "true"
}
'''+old)
old='  -showtmp\n';assert text.count(old)==1
text=text.replace(old,old+'''
if {[info exists ::env(ECOS_COURSE_HIER_MAP)] && $::env(ECOS_COURSE_HIER_MAP) eq "1"} {
  opt_clean -purge
  flatten -noscopeinfo
  opt_clean -purge
  hierarchy -check -top $top_design
}
''')
old='\nonehot\n';assert text.count(old)==1
text=text.replace(old,'''
if {![info exists ::env(ECOS_COURSE_SKIP_ONEHOT)] || $::env(ECOS_COURSE_SKIP_ONEHOT) ne "1"} {
  onehot
} else {
  log "Polaris-ECOS diagnostic: onehot explicitly skipped"
}
''')
backup=a.script.with_suffix(a.script.suffix+'.polaris-ecos-original')
assert not backup.exists(),'Preserve the existing runtime backup'
backup.write_text(original);a.script.write_text(text)
a.script.with_suffix('.polaris-ecos.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True),text.splitlines(True),fromfile='original',tofile='opt-in')))
print('Installed opt-in controls; default path retained; original saved beside script')
