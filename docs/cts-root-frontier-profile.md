# Root-boundary and frontier diagnostics

The current clock-only reproducer still fails root-boundary closure on the approved [PR319 source](https://github.com/openecos-projects/ecc-tools/pull/319), even with sink clustering actually disabled. First-rejected samples alone cannot describe the rest of the candidate population. Full 0.20/0.25 pF trials also reached external limits without identifying which composition level dominated runtime.

`patches/cts-root-frontier-profile.patch` adds diagnostic statements to the pinned `TopologyPruning.cc` **after** the existing root-boundary logging patch. It leaves existing predicates, constraints, loop order, dominance operations and selected-pattern statements intact. The source-only PR319 branch is not modified. This is instrumentation, not a feasibility fix.

The preflight check verifies sequential application against the reviewed source, exact expected resulting text, 54 added lines and zero removed lines. That is not native compilation or proof of output equivalence. Native iCTS regressions and control-output comparisons remain required before using this build for design experiments.

## Recorded evidence

- Each root closure logs input/closed/rejected counts and per-call deltas of invalid-compensation, cap-mismatch and slew-mismatch counters already maintained by the native pass. Cap and slew events **can overlap**; never sum them as mutually exclusive rejection categories. They measure boundary consistency, not an independent Liberty-limit/signoff check.
- Root timing separates total closure wall time, direct cost-query time, load-resolution time and cache hits. These are function-local measurements, not a full CPU profile.
- Each frontier composition reports keyed candidate pairs, semantic rejections, cost-dominated pairs, committed entries, removed prior entries, state buckets, largest bucket and final frontier size. Summary counters can be checked for conservation. Progress messages occur at exponentially spaced pair counts starting at one million, limiting log growth; a progress snapshot may include one attempted pair whose classification is not yet recorded.
- Per-level begin/end messages identify depth, reverse level, aligned length, frontier sizes, retained pattern nodes and elapsed wall time. An external timeout can therefore retain a useful last-active level without being relabeled as a native failure.

Counters and logging add overhead. Runtime differences must be measured on identical inputs and must not be represented as an optimization result.

## Build and validation gate

The manual diagnostic workflow's `root_frontier_profile=true` option requires `reviewed_pr319=true` and `source_trunk_membership_fix=false`; the correction is already in the reviewed commit. The workflow checks and applies both additive diagnostic patches, records their digests, builds/imports the wheel, and runs the native iCTS CTest targets. A successful build alone does not promote any processor checkpoint.

After provenance and regression checks, start with the identical nine-macro control and fast 4,096-DFF regular fixture. Compare native results and exported V/DEF identities to the previous reviewed-head build before considering larger trials. Full SRAM processor CTS, routing and signoff remain incomplete.
