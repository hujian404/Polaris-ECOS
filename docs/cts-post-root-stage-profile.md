# Post-root stage diagnostics

The bounded full-processor 0.25 pF profile reached a seven-level root pass with 8,881,686 closed entries, followed by an uninstrumented interval until the external two-hour stop. A fresh identical-input run captured two native backtraces and 20 seconds of CPU samples after that root pass, then deliberately stopped. All four sampling commands succeeded; native flow remains Ongoing/-15 with no clock-tree commit.

The short sampling window contains 987 cycle samples with zero reported lost samples. About two thirds of weighted self overhead belongs to libc allocation/free routines. This is a short-window observation, not attribution of the entire earlier 47-minute interval. The wheel retains only its Python entry in the dynamic symbol table and lacks `.symtab`/debug information, leaving C++ frames unresolved. No specific C++ function or algorithmic repair is established by these samples.

`patches/cts-post-root-stage-profile.patch` applies **after** the existing root-boundary and root/frontier patches on the same approved PR319 source. Preflight verifies all three patches in sequence against pinned source, exact resulting text, **23 added lines and zero removed lines**. It adds begin/end checkpoints and scoped durations for:

- state-frontier rebuilding, root fanout filtering, candidate library copying and final best-character selection;
- sink-region entry filtering and each previously uncached legality evaluation;
- boundary-group collection and electrical configuration inside a legality evaluation.

Existing predicates, data operations and their order remain intact. Timings are nested and logging adds overhead. The patch requires native compilation, regression and control checks; it is instrumentation, not a functional fix or CTS-quality pass. No SRAM/PDK views are included.

The diagnostic build's optional stage-profile mode keeps the original 23 native iCTS regression targets. When available, an additional symbol artifact retains an unstripped build module **only if its `.text` address, size and SHA256 match the wheel's native module**, so future samples can be mapped without substituting an unrelated binary. No symbol match may be inferred from version strings alone. The frozen cacheless release and narrow PR319 source branch are independent of this diagnostic proposal.
