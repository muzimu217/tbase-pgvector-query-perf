# Stage Decision

- Question: continue optimizing the current code line, or freeze the main
  experiment and move to the report phase?
- Verdict: `good`
- Action: `write`
- Decision: freeze the validated source and main experiment contract. Use the
  archived evidence for the PDF report and figures before considering another
  optimization branch.

## Reason

The incumbent line passes its predefined gate: the stable SIMD matrix improves
mean high-probes workload time by 18.30%, all five pairs are faster, top-10
recall is unchanged at 1.0, and the post-change perf profile confirms the
claimed mechanism. The independent lifecycle fix also has regression and
peak-memory evidence.

Continuing immediately into sort internals could produce additional speedup,
but it would expand the implementation and verification surface after the core
claim is already supported. Promoting `ivfflat.query_work_mem` as the main
result was rejected because its 7.32% latency gain is below the 10% gate.

## Evidence

- `performance/simd-matrix-stability/aggregate.csv`
- `performance/vectorized-matrix/correctness.txt`
- `performance/baseline/perf-report-symbol.txt`
- `performance/vectorized-perf/perf-report-symbol.txt`
- `ablation/memory-matrix-stats.csv`
- `performance/final-vectorized-regression.log`
- `claim_validation.md`

## Reopen Condition

Open a separate optimization branch only after the report package is complete,
and only if the next target is backed by a new acceptance contract for sorting
comparison, tuple materialization, or temporary-file overhead.
