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

Both focused checks pass in WSL Ubuntu 22.04. They do not replace rebuilding the real tool and rerunning the nine-macro integration fixture. The regular-sink H-tree root-boundary failure of the full processor remains unresolved; this change does not establish feasibility or signoff. Frozen cacheless artifacts are unaffected. Upstream investigation: [ECC #357](https://github.com/openecos-projects/ecc/issues/357).

## Native candidate execution

[Actions run 40156959057](https://github.com/hujian404/Polaris-ECOS/actions/runs/40156959057) successfully built and imported the candidate wheel. Its recorded source delta and digest were checked before installation; live process mappings confirmed the isolated candidate module. With identical nine-macro Verilog/DEF/SDC inputs to the failed control, native synthesis now reports `committed`, and optimization reaches **0.057312 ns** skew under the unchanged **0.08 ns** target. Native instantiation, evaluation and CTS output complete. Exported Verilog and DEF gzip CRC checks also pass.

The whole wrapper step is **not yet a complete pass**: geometry export exceeded the externally imposed 600-second limit, so its recorded state remains `Ongoing`, return `-15`. A fresh run allows 30 minutes for this tail; only complete step success plus an output audit permits processor CTS to start. The narrow connection correction is supported by native execution; full processor feasibility and signoff remain unproven.
