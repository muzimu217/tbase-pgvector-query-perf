# Reproduce the Main Experiment

Use an isolated OpenTenBase test cluster. The administrative SIMD ablation
temporarily swaps the installed `vector.so` for newly created backend sessions
and restores the original checksum on exit.

Generate the fixed dataset with `ROWS=100000`, `DIMS=128`, `QUERIES=200`, item
seed 17 and query seed 97 from `bench/run_ivfflat_benchmark.sh`, then create:

```sql
CREATE INDEX profile_items_cos_idx ON profile_items
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 1000);
```

Run the scalar/SIMD ABBA matrix:

```bash
export PGHOST=127.0.0.1 PGPORT=22301 PGUSER=otbtest DBNAME=ivfflat_test
SCALAR_LIBRARY=/path/to/scalar/vector.so \
VECTORIZED_LIBRARY=/path/to/vectorized/vector.so \
ACTIVE_LIBRARY=/path/to/install/lib/postgresql/vector.so \
ALLOW_LIBRARY_SWAP=true WORK_MEM=4MB PROBES=1000 REPETITIONS=5 \
RESULT_DIR=/path/to/results/simd-matrix \
  bench/run_ivfflat_simd_ablation.sh
```

Run query-sort memory and exact top-10 checks:

```bash
WORK_MEM=4MB QUERY_WORK_MEM=64MB PROBES=1000 REPETITIONS=5 \
RESULT_DIR=/path/to/results/vectorized-matrix \
  bench/run_ivfflat_high_probes.sh
```

Capture the post-SIMD CPU profile:

```bash
WORK_MEM=4MB QUERY_WORK_MEM=0 PROBES=1000 PERF_SECONDS=30 \
RESULT_DIR=/path/to/results/vectorized-perf \
  bench/run_ivfflat_perf_profile.sh
```

Validate generated CSV files against `performance/data/dataset-manifest.md`,
and compare aggregate values with `metrics.json`.
