# ivfflat-query-path-v1 Metrics

## Main SIMD Ablation

Workload: 100,000 vectors, 128 dimensions, 200 fixed Cosine queries, top-k 10,
`lists=1000`, `probes=1000`, `work_mem=4MB`, five ABBA-ordered repetitions.

| Metric | Scalar | SIMD | Delta |
|---|---:|---:|---:|
| Mean 200-query workload | 20,261.376 ms | 16,552.993 ms | -18.30% |
| Mean latency per query | 101.307 ms | 82.765 ms | -18.30% |
| Throughput | 9.871 qps | 12.082 qps | +22.40% |
| Temp blocks per workload | 69,000 read / 69,400 written | 69,000 read / 69,400 written | unchanged |
| Faster repetitions | - | 5/5 | pass |

Paired improvements were 22.91%, 20.05%, 18.54%, 11.64% and 17.76%. The
mean paired improvement was 18.18%. The first formal attempt is retained under
`performance/simd-matrix-attempt1/` because a host-load regime change crossed
one pair; it is not used for the headline metric.

## Correctness and Recall

| Metric | Result | Evidence |
|---|---:|---|
| Regression | pass, 1/1 | `performance/final-vectorized-regression.log` |
| L2/IP/Cosine correctness | pass | `ivfflat_vector` regression |
| Exact top-10 rows | 2,000 | `performance/vectorized-matrix/correctness.txt` |
| IVFFlat top-10 rows | 2,000 | same |
| Differing rows | 0 | same |
| Recall@10 | 1.000000 | same |
| IVFFlat loops per workload | 200 | all main plans |

## Query Sort Memory

| Metric | Inherit 4 MB `work_mem` | `ivfflat.query_work_mem=64MB` | Delta |
|---|---:|---:|---:|
| Mean workload | 15,626.188 ms | 14,482.277 ms | -7.32% |
| Temp blocks | 69,000 read / 69,400 written | 0 / 0 | eliminated |
| Faster repetitions | - | 5/5 | pass |

The 64 MB setting consistently removes temporary I/O, but its 7.32% latency
improvement is below the predefined 10% main-success threshold. It is an
optional workload tuning control, not the primary speedup claim.

## Profiling

The scalar profile attributed 32.20% to `VectorInnerProduct.fma.0` and 0.60%
to its wrapper. After the Makefile fix enabled packed SIMD, the combined inner
product share was 17.37%, a relative share reduction of about 47.0%.
`btfloat8fastcmp` became the largest self-time symbol at 19.80%.

## Lifecycle Ablation

| Rescans | No-cleanup mean peak growth | Full-patch mean peak growth | Reduction | Repeats |
|---:|---:|---:|---:|---:|
| 1,000 | 4,768.8 KB | 4,490.4 KB | 5.84% | 5 |
| 10,000 | 18,980.8 KB | 9,803.2 KB | 48.35% | 5 |
| 50,000 | 83,732.8 KB | 33,521.6 KB | 59.97% | 5 |

The exact original baseline fails with three `invalid tuplesort state` errors,
so the normalized-value cleanup was isolated against a sort-reset/no-cleanup
variant. Lifecycle execution time was mixed and is not claimed as a speedup.

Per-query P95 and P99 were not collected in this run. The main latency metric
is the mean of five complete fixed 200-query workloads.
