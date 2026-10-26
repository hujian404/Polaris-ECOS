# Root-boundary and frontier diagnostics

The current clock-only reproducer still fails root-boundary closure on the approved [PR319 source](https://github.com/openecos-projects/ecc-tools/pull/319), even with sink clustering actually disabled. First-rejected samples alone cannot describe the rest of the candidate population. Full 0.20/0.25 pF trials also reached external limits without identifying which composition level dominated runtime.

`patches/cts-root-frontier-profile.patch` adds diagnostic statements to the pinned `TopologyPruning.cc` **after** the existing root-boundary logging patch. It leaves existing predicates, constraints, loop order, dominance operations and selected-pattern statements intact. The source-only PR319 branch is not modified. This is instrumentation, not a feasibility fix.

The preflight check verifies sequential application against the reviewed source, exact expected resulting text, 54 added lines and zero removed lines. The resulting build and control comparisons have now been audited as described below. Instrumentation has not repaired the full processor flow.

## Recorded evidence

- Each root closure logs input/closed/rejected counts and per-call deltas of invalid-compensation, cap-mismatch and slew-mismatch counters already maintained by the native pass. Cap and slew events **can overlap**; never sum them as mutually exclusive rejection categories. They measure boundary consistency, not an independent Liberty-limit/signoff check.
- Root timing separates total closure wall time, direct cost-query time, load-resolution time and cache hits. These are function-local measurements, not a full CPU profile.
- Each frontier composition reports keyed candidate pairs, semantic rejections, cost-dominated pairs, committed entries, removed prior entries, state buckets, largest bucket and final frontier size. Summary counters can be checked for conservation. Progress messages occur at exponentially spaced pair counts starting at one million, limiting log growth; a progress snapshot may include one attempted pair whose classification is not yet recorded.
- Per-level begin/end messages identify depth, reverse level, aligned length, frontier sizes, retained pattern nodes and elapsed wall time. An external timeout can therefore retain a useful last-active level without being relabeled as a native failure.

Counters and logging add overhead. Runtime differences must be measured on identical inputs and must not be represented as an optimization result.

## Build and validation gate

The manual diagnostic workflow's `root_frontier_profile=true` option requires `reviewed_pr319=true` and `source_trunk_membership_fix=false`; the correction is already in the reviewed commit. The workflow checks and applies both additive diagnostic patches, records their digests, builds/imports the wheel, and runs the native iCTS CTest targets. A successful build alone does not promote any processor checkpoint.

After provenance and regression checks, start with the identical nine-macro control and fast 4,096-DFF regular fixture. Compare native results and exported V/DEF identities to the previous reviewed-head build before considering larger trials. Full SRAM processor CTS, routing and signoff remain incomplete.

## Native observations

[Build 40214930653](https://github.com/hujian404/Polaris-ECOS/actions/runs/40214930653) passed native import and all **23 iCTS CTest targets**, with zero failures/skips in the downloaded JUnit records. Source deltas, patch digests, wheel identity and live native module mappings were verified. The shared stock runtime was unchanged.

| Case | Observation | Scope |
| --- | --- | --- |
| 4,096-DFF, 0.45 pF | Native Incomplete; 78,540 root evaluations, none closed; all 78,540 have a slew mismatch, zero cap mismatches or invalid compensations | Eight calls, including repeated executions; rejection-count sequence matches the uninstrumented reviewed-head control |
| Nine SRAM macros, 0.45 pF | 0.057312 ns skew; compressed Verilog/DEF hashes exactly match the earlier native Success run; gzip CRC valid | Deliberately stopped after matching outputs; current wrapper remains Ongoing/-15. Macro-only synthesis does not use the regular H-tree frontier |
| Nine macros + 4,014 DFFs, 0.25 pF | 2.35555 ns optimized skew, matching the uninstrumented same-head baseline | Still exceeds the unchanged 0.08 ns target; deliberately stopped at the optimization checkpoint, Ongoing/-15 |

All completed composition summaries satisfy both counter-conservation checks. The mixed proxy's largest composition attempts 163,387,544 keyed pairs and retains 12,556,115 entries, taking about 27.2 seconds inside the composition function. These scoped timings overlap with enclosing stages and are not a complete CPU profile.

### Full processor at 0.25 pF

After the controls matched, a single bounded CTS-only profile used the **identical original placed netlist, DEF and 50 MHz SDC** as the earlier 0.25 pF diagnostic. The seven-level plan's final composition attempted **10,824,862,860** keyed pairs, retaining 15,390,656 entries in about 842 seconds. Its root pass then closed **8,881,686** candidates and rejected 6,508,970 due to slew boundary mismatch; cap mismatches and invalid compensation were zero for that pass.

This is different from the original 0.45 pF all-rejected condition: some evaluated root boundaries close under the tighter search budget. It does **not** establish a legal committed clock tree, timing quality or processor signoff. The run reached its external 7,200-second limit, exited -15 and retained native Ongoing, with no tree commit. The last root log preceded the external stop by roughly 47 minutes; existing instrumentation does not distinguish state-frontier rebuilding, candidate copying, sink-region legality checks and subsequent work within that interval.

All **33 archived evidence files** were verified after local retrieval. [Machine-readable summary](../results/sram/cts-frontier-profile-summary.json) records identities, counters and native-state limits without including PDK/IP views. The full processor is not ready for routing or GDS export. Further native backtrace/CPU sampling targets the silent post-root interval; it is a diagnostic step, not another constraint waiver.
