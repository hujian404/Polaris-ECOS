# Local sink-capacitance table candidate

The post-root CPU sample shows heavy allocation activity but cannot identify a C++ function in the stripped wheel. Independent inspection of the approved [PR319 source](https://github.com/openecos-projects/ecc-tools/tree/3ba4d0ec58529a7bf890fb28ef9e427bb97f562a) identifies a concrete copy amplification in `RecoverSinkLoadRegionGroup`.

The caller supplies a capacitance table covering the design's sink groups. Each local group copies that entire table into its electrical configuration, then copies the configuration for a capacitance-only check. Across G groups and N globally cached pins, these table copies can require O(G*N) entries even though electrical evaluation uses each group's own pins and recursively derived subsets.

`patches/cts-local-cap-subset-candidate.patch` populates the local configuration using only `ordered_loads`. The existing precheck still rejects a missing local-pin capacitance. `ClusterConstraintEvaluator::queryPinCap` performs a keyed lookup for each active pin; it does not aggregate unrelated table entries. Recursive split nodes contain subsets of the same local loads. The table's values for all queried pins, exact electrical evaluation, split limits, fallback rules and fanout/capacitance checks are retained. `FastClustering::buildElectricalBaseConfig` returns a fresh configuration with an empty pin table.

Three native regression cases use the real `RecoverSinkLoadRegionGroup` path, adding thousands of unrelated pin-cap entries and checking:

- identical already-legal and split-recovery outputs;
- unchanged rejection of a missing local-pin capacitance;
- identical capacitance failure and optional fallback outcomes.

They compare typed failures, selected pins/groups/centers, tree counts, capacitances and split/fallback metadata. These are semantic guards, not timing assertions or a surrogate implementation of the recovery algorithm.

The proposal applies after the two existing root/frontier logging patches and the post-root stage patch. Sequential source application has been checked. **Native compilation, regressions, real-library control-output comparisons and full-scale timing measurements remain pending.** This candidate does not yet establish the cause of the entire silent interval, a measured speedup, processor CTS closure or a signoff pass. PR319 remains a separate, narrow connection fix.
