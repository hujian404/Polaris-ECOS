#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
if [ "$(cat "$root/VARIANT")" != cacheless ]; then
  echo 'Use sim/run_sram.py with official macro models on sram-ip.' >&2
  exit 2
fi
obj="$root/build/smoke"
mkdir -p "$obj"
verilator --cc --exe --build -j "${JOBS:-2}" -Wno-fatal --top-module Polaris \
  --output-split 10000 --output-split-cfuncs 200 --Mdir "$obj" \
  "$root/rtl/Polaris.v" "$root/sim/smoke.cpp" > "$obj/build.log" 2>&1
for stall in 0 3 7; do "$obj/VPolaris" "$stall"; done
