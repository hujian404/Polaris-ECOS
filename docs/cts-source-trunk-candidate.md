# Candidate source-trunk membership correction

The isolated diagnostic wheel built by Actions run 40097393166 can execute the nine-macro CTS fixture. Both its hard-macro domain and source-to-root segment finish, but commit is rejected with `foreign_net_membership` and `duplicate_pin_membership`: the hard-macro root input remains in `clock`'s load list after being connected to the last source-trunk net. Native CTS returns Incomplete (10 seconds); this is not a full CTS pass or an ABI import failure.

Pinned official source: [ecc-tools SourceTrunkSegment.cc](https://github.com/openecos-projects/ecc-tools/blob/dfb4a3b4f1181d81d0fec9f82d9abeaae942aec8/src/operation/iCTS/source/module/synthesis/topology/trunk/SourceTrunkSegment.cc).

`ConnectSourceNet` currently preserves every existing attached load. The buffered path subsequently connects `sink` to its last new net but leaves the same pointer in the source load list. The candidate excludes only that displaced sink while reconnecting the source. Other existing loads and the zero-buffer direct connection are preserved. No skew, capacitance, slew or frequency limit is relaxed.

The patch is **a candidate**, separate from the logging-only patch. Its focused tests extract the actual original/modified reconnection functions into a minimal Pin/Net model. The original test demonstrates the stale membership; the candidate test checks that it is removed, unrelated loads remain, and the direct path is unchanged:

```sh
c++ -std=c++20 tests/cts-source-trunk/original.cpp -o /tmp/cts-original
/tmp/cts-original
c++ -std=c++20 tests/cts-source-trunk/candidate.cpp -o /tmp/cts-candidate
/tmp/cts-candidate
```

Both focused checks pass in WSL Ubuntu 22.04. The native integration result below supplies the separate real-tool validation. The regular-sink H-tree root-boundary failure of the full processor remains unresolved; this change does not establish processor feasibility or signoff. Frozen cacheless artifacts are unaffected. Upstream investigation: [ECC #357](https://github.com/openecos-projects/ecc/issues/357).

## Native candidate execution

[Actions run 40156959057](https://github.com/hujian404/Polaris-ECOS/actions/runs/40156959057) successfully built and imported the candidate wheel. Its recorded source delta and digest were checked before installation; live process mappings confirmed the isolated candidate module. With identical nine-macro Verilog/DEF/SDC inputs to the failed control, native synthesis now reports `committed`, and optimization reaches **0.057312 ns** skew under the unchanged **0.08 ns** target. Native instantiation, evaluation and CTS output complete. Exported Verilog and DEF gzip CRC checks also pass.

The fresh nine-macro integration run completed **CTS Success**, return **0**, in **12 minutes 34 seconds**, including geometry export. Its inputs match the failed control; Verilog/DEF gzip checks pass, and both compressed output hashes match the earlier candidate attempt. That earlier attempt hit an external 600-second limit during geometry export and remains recorded as `Ongoing`/`-15`; it is not relabeled as success. The longer run confirms the complete small-flow integration without relaxing electrical limits.

The source-only correction is proposed upstream as [draft ecc-tools PR #319](https://github.com/openecos-projects/ecc-tools/pull/319). Its rebased connection functions match the native-tested candidate; the complete upstream test suite on the rebased commit has not been claimed as run. This pull request is separate from the logging-only diagnostic patch.

## Remaining processor root-boundary failure

The complete processor probe subsequently returned **Incomplete**: the nine-macro domain finished, but the 589,378 regular sinks could not close their H-tree root boundary. Across seven depths, 1,056,241 candidate evaluations were rejected and none closed. These are evaluations across depths, not unique physical designs. Each depth's first rejected sample has a matching source-boundary capacitance bucket but a mismatching slew bucket: total root load bucket 32, source-boundary branch bucket 8, and root output slew bucket 22. With the configured lattices, the first samples imply total estimated root load in (0.93, 0.96] pF and output slew in (0.70, 0.733333] ns. The capacitance-match flag compares a branch boundary estimate, so it does not establish that total load satisfies 0.45 pF. These first samples do not describe the cause distribution of every rejection or prove that pruning removed feasible solutions.

The [regular-clock spatial reproducer](../repro/regular-clock-spatial/README.md) uses 4,096 real standard-cell flip-flops on the original die and reproduces the same class of root failure in about 11 seconds. Its generated Verilog, DEF and SDC hashes match the executed fixture, and the native configuration check passes. It is a synthetic clock-only fixture, with no processor data paths or functional/signoff equivalence.

Mixed spatial proxies containing nine real macros and 4,014 flip-flops commit both sink domains with tighter search capacitance budgets, but still fail the unchanged 0.08 ns skew target:

| Search capacitance budget | Final optimized skew |
| --- | --- |
| 0.20 pF | 3.56164 ns |
| 0.25 pF | 2.32593 ns |
| 0.30 pF | 4.14697 ns |

Those proxy controllers explicitly terminate after final native optimization reports the missed target; their interrupted wrapper states are preserved. They are not CTS quality passes. Two full-processor, CTS-only diagnostics at 0.20/0.25 pF each reached the external **7,200-second limit**, returned **-15**, and retained native **Ongoing** state. Import and CTS initialization completed, but no tree commit or final optimization checkpoint was observed. These are externally interrupted searches, not native Incomplete outcomes or a proof of physical infeasibility. Original placement inputs, 50 MHz, slew limits, Liberty limits and the skew target remain unchanged. No routing or signoff promotion follows, and full SRAM processor closure remains incomplete.

The matched regular-only controls preserve all 4,014 mixed-fixture DFF records while omitting the macros, loads and obstacles. Their optimized skew at 0.20/0.25/0.30 pF is 0.257067/0.129273/0.479626 ns: regular-domain skew is also unresolved. Tightening the supported `[params.cts].max_fanout` from 32 to 16 at 0.25 pF takes effect in native logs, but yields 0.280700 ns regular-only and 2.790390 ns mixed skew. Both trees commit and both miss 0.08 ns; this does not improve their paired baseline. The [portable mixed/masked generator and table](../repro/regular-clock-spatial/README.md) reproduce these input layouts without including PDK/IP views. All three generated layout variants match executed input hashes and pass native project checking; configuration/reproducibility checks do not establish timing quality.
