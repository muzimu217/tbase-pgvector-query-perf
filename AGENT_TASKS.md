# Agent Task Delegation: Project 1

## Mission

This agent owns `pgvector` query performance optimization for OpenTenBase/TBase. The work must keep L2, Inner Product, and Cosine results correct while improving query latency or throughput under measurable recall constraints.

## Inputs

- Repository: `tbase-pgvector-query-perf`
- Upstream package repo: `OpenTenBase-Packages`
- OpenTenBase source tree or container runtime
- Existing report: `docs/pgvector-performance-development-report.md`
- Existing SOP: `SOP.md`
- Public submission PR: `CDUESTC-OpenAtom-Open-Source-Club/OpenTenBase-Packages#27`

## Agent Roles

### Benchmark Agent

1. Reproduce the baseline with configurable `ROWS`, `DIMS`, `QUERIES`, `TOPK`, `LISTS`, and `PROBES_LIST`.
2. Record `avg_latency_ms`, `p95_latency_ms`, `recall@k`, and query plan evidence for every metric.
3. Save raw CSV, summarized tables, and chart-ready data under `docs/benchmark-data/`.

### Profiling Agent

1. Locate CPU hotspots in distance calculation, IVFFlat list scanning, tuple fetch, and distributed execution.
2. Use `perf`, `gprof`, flamegraph, or equivalent tools when available.
3. Produce a short hotspot note with function names, evidence, and optimization candidates.

### Optimization Agent

1. Implement only changes that can be validated against the baseline.
2. Prioritize low-risk improvements: parameter heuristics, benchmark tooling, scan diagnostics, and safe C-level micro-optimizations.
3. Keep branch names free of `codex`.

### Report Agent

1. Convert raw results into recall/latency comparison tables and figures.
2. Explain which `lists/probes` settings are recommended for which workload size.
3. Mark heuristic conclusions as heuristic, not guaranteed behavior.

## Required Commands

```bash
git status --short --branch
docker compose up -d
psql -d postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"
./scripts/run-pgvector-benchmark.sh
```

Adapt command names to the actual upstream package layout if scripts are moved.

## Deliverables

- Benchmark script or patch
- Before/after CSV files
- `EXPLAIN` evidence for L2/IP/Cosine
- Performance report with recall and latency curves
- Regression or TAP test where the change touches behavior
- PR link and validation log

## Acceptance Criteria

- All three metrics are covered.
- Recall does not regress at the selected target threshold.
- At least one of average latency, p95 latency, or throughput improves.
- The report includes machine specs, dataset size, dimensions, index parameters, and exact commands.

## Stop And Ask

Stop before proceeding if:

- OpenTenBase cannot load `vector`.
- Benchmark output lacks recall or plan evidence.
- A proposed C change affects distance semantics.
- Results vary enough that the conclusion depends on a single noisy run.
