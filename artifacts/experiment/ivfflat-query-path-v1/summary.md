# Main Experiment Summary

The source phase produced two supported contributions for OpenTenBase's bundled
pgvector IVFFlat path.

First, an OpenTenBase-compatible scan reset rebuilds tuplesort state and frees
the previous normalized Cosine query value. The original code fails the target
regression with three `invalid tuplesort state` errors. The patched regression
passes, and a five-repeat lifecycle ablation reduces mean peak RSS growth by
48.35% at 10,000 rescans and 59.97% at 50,000 rescans. Lifecycle latency is
mixed, so no latency claim is attached to this fix.

Second, the in-tree build now carries pgvector's existing auto-vectorization
flags into OpenTenBase's actual `CFLAGS`. Assembly changes from scalar
`vfmadd231ss` to packed `vfmadd231ps`. On the fixed 100,000-row, 128-dimensional,
200-query Cosine workload at `lists=probes=1000`, five ABBA-ordered pairs show
an 18.30% lower mean workload time, with all five SIMD runs faster. Exact and
full-probes IVFFlat top-10 sets match for all 2,000 rows (`recall@10=1.0`).

The optional `ivfflat.query_work_mem` setting isolates IVFFlat query-sort memory
from global `work_mem`. Setting it to 64 MB removes 69,000 temporary reads and
69,400 temporary writes per workload, but the 7.32% latency improvement is below
the 10% main threshold. It remains a useful tuning control rather than a main
speedup result.

Post-SIMD perf confirms the mechanism: inner-product self-time share drops from
about 32.8% to 17.37%, and sorting becomes the leading hotspot. The source,
plans, raw matrices, checksums, perf data, correctness outputs and fixed-seed
data contract are archived under this run directory.
