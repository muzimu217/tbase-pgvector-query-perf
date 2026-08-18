# Run Log Summary

1. Rebuilt OpenTenBase with GCC 11, debug symbols, frame pointers and `--disable-license`.
2. Started a one-GTM, one-CN, one-DN cluster and added the required default/sharding node group.
3. Verified writable distributed DDL/DML and `vector 0.8.0` loading.
4. First regression driver attempt failed before tests because OpenTenBase uses `MY_LOCAL_CN1PORT`; rerun used `22201`.
5. The real regression exposed `invalid tuplesort state` in LATERAL rescan and iterative scan.
6. Added OpenTenBase-compatible tuplesort rebuilding plus normalized-query cleanup and calibrated expected output.
7. Regression passed 1/1.
8. CN memory smoke was rejected because RFQE hid inner loops; the harness was extended to set up through CN and execute/sample through DN.
9. DN smoke passed with IVFFlat index loops=1000 and durable RSS, setup, plan and summary artifacts.
10. Built original, sort-reset/no-cleanup and full-patch libraries with recorded SHA256 hashes.
11. Original regression failed as expected with three invalid tuplesort-state errors.
12. Completed 30 paired ablation runs; full-patch peak growth dropped most strongly at 50,000 rescans.
13. Restored the full-patch library and passed the final regression 1/1.
14. Profiled the 100,000-row, 128-dimensional, 200-query high-probes workload; scalar inner product was the largest hotspot at 32.20% self time.
15. Added `ivfflat.query_work_mem`; 64 MB eliminated all recorded temporary blocks but improved paired workload time by only 7.32%, below the main gate.
16. Fixed OpenTenBase in-tree Makefile flag propagation and confirmed packed `vfmadd231ps` instructions in the installed library.
17. Rebuilt cleanly and passed the vectorized regression 1/1.
18. The first SIMD matrix was invalidated after a host-load regime change crossed one pair; raw evidence was retained.
19. Repeated the ABBA matrix with load snapshots; SIMD was faster in 5/5 pairs and lowered mean workload time by 18.30%.
20. Compared exact and full-probes IVFFlat top-10 sets for 200 queries; all 2,000 rows matched and recall@10 was 1.0.
21. Captured post-SIMD perf data; combined inner-product self-time share fell to 17.37%, making sort comparison the leading hotspot.
22. Verified fixed-seed streamed regeneration exactly matches both dataset SHA256 values and archived all non-regenerable evidence.
