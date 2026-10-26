# Local sink-capacitance table candidate

The post-root CPU sample shows heavy allocation activity but cannot identify a C++ function in the stripped wheel. Independent inspection of the approved [PR319 source](https://github.com/openecos-projects/ecc-tools/tree/3ba4d0ec58529a7bf890fb28ef9e427bb97f562a) identifies a concrete copy amplification in `RecoverSinkLoadRegionGroup`.

The caller supplies a capacitance table covering the design's sink groups. Each local group copies that entire table into its electrical configuration, then copies the configuration for a capacitance-only check. Across G groups and N globally cached pins, these table copies can require O(G*N) entries even though electrical evaluation uses each group's own pins and recursively derived subsets.

`patches/cts-local-cap-subset-candidate.patch` populates the local configuration using only `ordered_loads`. The existing precheck still rejects a missing local-pin capacitance. `ClusterConstraintEvaluator::queryPinCap` performs a keyed lookup for each active pin; it does not aggregate unrelated table entries. Recursive split nodes contain subsets of the same local loads. The table's values for all queried pins, exact electrical evaluation, split limits, fallback rules and fanout/capacitance checks are retained. `FastClustering::buildElectricalBaseConfig` returns a fresh configuration with an empty pin table.

Three native regression cases use the real `RecoverSinkLoadRegionGroup` path, adding thousands of unrelated pin-cap entries and checking:

- identical already-legal and split-recovery outputs;
- unchanged rejection of a missing local-pin capacitance;
- identical capacitance failure and optional fallback outcomes.

They compare typed failures, selected pins/groups/centers, tree counts, capacitances and split/fallback metadata. These are semantic guards, not timing assertions or a surrogate implementation of the recovery algorithm.

The proposal applies after the two existing root/frontier logging patches and the post-root stage patch. Sequential source application has been checked. [Build 40289508333](https://github.com/hujian404/Polaris-ECOS/actions/runs/40289508333) completed successfully; downloaded JUnit/discovery records verify **23/23 native iCTS targets**, zero failures/skips. `LastTest.log` confirms all three added regression cases executed and passed. The installed native module and source/wheel/patch identities were audited.

The regular 4096-DFF control preserves the reference root-rejection sequence. Nine official SRAM macros retain **0.057312 ns** skew and identical compressed V/DEF hashes. The mixed 9-macro + 4014-DFF control retains **2.35555 ns**, still above 0.08 ns. These last two controls deliberately stop at audited output/optimization checkpoints and remain native Ongoing/-15; they are not wrapper Success or processor quality passes.

## Full-scale observation

The candidate uses the same original placed netlist, DEF and 50 MHz SDC, default allocator and unchanged electrical targets. Its first seven-level composition counters and root closure counts match the previous default-allocator profile: **8,881,686 root entries close**. All completed composition summaries conserve their counters.

The seven-level post-root scopes now complete in **43.713 seconds** in total, including **36.122 seconds** of sink-region filtering. The run continues through six- and five-level plans and into four-level composition before its external 7200-second bound. The six-level region filter takes 17.214 seconds; the five-level filter takes 48.585 seconds. No clock tree is committed at that stop, so native Ongoing/-15 is preserved.

This demonstrates further search progress. It is not a controlled whole-flow speedup measurement: the original profile lacks post-root scope timers, and its silent interval cannot be attributed exclusively to region filtering. A separate existing-tcmalloc control also reached the two-hour external bound without a tree commit; changing the allocator has not established CTS closure.

The validated code candidate is now running with a six-hour wall limit to let the remaining plans finish. Only the resource budget changes; no timing, capacitance, fanout or skew target is waived. [Aggregate evidence](../results/sram/cts-local-cap-subset-summary.json) distinguishes completed diagnostics from this pending extended attempt.

## Upstream contribution

[Draft PR320](https://github.com/openecos-projects/ecc-tools/pull/320) contains only the recovery source and its native test file, based on current upstream `main`. It includes repository formatting; token comparisons verify no additional code changes from formatting. Native runtime allocation changes, while public APIs, ABI layout and packaging requirements are unchanged. Required upstream CI and full processor quality remain pending. PR319 remains the separate connection fix; no PDK/IP views, diagnostic instrumentation or generated build outputs are included in PR320.
