# Claim Validation

| Claim | Acceptance gate | Observed | Verdict |
|---|---|---|---|
| Repeated IVFFlat scans no longer enter an invalid tuplesort state | regression pass | 1/1 pass; original baseline has three errors | supported |
| The lifecycle test exercises rescan | more than one IVFFlat loop | 1,000 loops in smoke; up to 50,000 in ablation | supported |
| Existing L2/IP/Cosine and iterative scans remain correct | regression pass | pass | supported |
| Normalized-value cleanup reduces execution-time peak RSS | lower peak growth in same-host ablation | 5.84%, 48.35%, 59.97% lower as rescans increase | supported |
| OpenTenBase in-tree pgvector uses its intended auto-vectorization flags | packed SIMD in compiled assembly | `vfmadd231ps` present; scalar build uses `vfmadd231ss` | supported |
| SIMD lowers high-probes latency | at least 10%, five repeats same direction | 18.30% mean; 5/5 faster; minimum paired gain 11.64% | supported |
| SIMD preserves full-probes recall | recall@10 unchanged | 1.000000, 0 differing rows out of 2,000 | supported |
| SIMD reduces the inner-product hotspot | lower perf self-time share | 32.80% to 17.37% combined share | supported |
| Query-specific memory alone is a main speedup | at least 10% | 7.32%, despite eliminating temp I/O | not supported |
| Lifecycle cleanup alone improves latency | consistent lower execution time | mixed | not supported |

The first SIMD matrix is retained as an invalidated attempt because a host-load
regime change crossed one pair. The stability rerun added per-run load snapshots
and is the only SIMD matrix used for the headline latency claim.
