# Repository Guidelines

## Project Structure & Module Organization

This repository contains the project-one deliverables for pgvector query performance work. `README.md` summarizes the project, and `SOP.md` defines the repeatable workflow. Reports live in `docs/`, benchmark evidence is under `docs/benchmark-data/` and `docs/figures/`, and source-level changes are stored as patches in `patches/`. Keep generated benchmark files tied to the command and environment that produced them.

## Build, Test, and Development Commands

Apply the benchmark patch from an OpenTenBase source tree:

```bash
git apply patches/pgvector-ivfflat-benchmark-tools.patch
```

Run the benchmark after applying the patch:

```bash
cd contrib/pgvector
ROWS=100000 DIMS=128 LISTS=1000 PROBES_LIST="1 5 10 50 100 500 1000" \
  METRICS="l2 ip cosine" bench/run_ivfflat_benchmark.sh
```

Validate shell scripts with `bash -n` before reporting results.

## Coding Style & Naming Conventions

Use shell scripts with `set -euo pipefail`. SQL helper names should be lowercase and schema-qualified under `pgvector_bench`. Name result files descriptively, for example `ivfflat_benchmark_<timestamp>.csv` and `*_plans.txt`.

## Testing Guidelines

Every performance claim must include recall, latency, and `EXPLAIN` plan evidence. Smoke tests may use small data, but formal results must use a documented benchmark matrix across L2, IP, and Cosine.

## Commit & Pull Request Guidelines

Use concise imperative commit messages, such as `Add pgvector benchmark report`. PRs must include summary, validation commands, data paths, and any limitations. Link related issues or upstream PRs when available.

## Security & Configuration Tips

Do not commit secrets, SSH keys, or database passwords. Record connection variables as placeholders, for example `PGHOST=<host>` and `PGUSER=<user>`.

