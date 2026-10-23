#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
if [ "$(cat "$root/VARIANT")" != cacheless ]; then
  echo 'Cached frozen RTL is provided; see docs/sram.md before regenerating memories.' >&2
  exit 2
fi
mkdir -p "$root/generated"
cd "$root/processor"
export NOOP_HOME="$PWD"
mill -i chiselModule.runMain top.ECOSMain -td "$root/generated/raw" --output-file Polaris.v
python3 - "$root" <<'PY'
from pathlib import Path
import re,sys
root=Path(sys.argv[1])
raw=(root/'generated/raw/Polaris.v').read_bytes()
(root/'generated/Polaris.v').write_bytes(re.sub(rb'_(aw|ar|w|r|b)_(?:bits_)?',rb'_\1',raw))
print('Generated separate candidate; revalidate before replacing frozen rtl/Polaris.v')
PY
