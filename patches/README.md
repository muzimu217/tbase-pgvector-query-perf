# Patch Index

Apply `0001-ivfflat-query-path-optimization.patch` to OpenTenBase source baseline
`0915c04e457f9b5625bd2ae71938f13e5e451888`. It is the canonical complete
source-phase patch and includes lifecycle fixes, tests, benchmark harnesses,
the query-memory GUC and the in-tree vectorization fix.

The older lifecycle and benchmark patch files are retained as historical,
single-purpose artifacts. They predate the completed performance work and must
not be combined with the canonical patch.

The canonical patch SHA256 is:

```text
c758913d94d21f9fa80472c79a764ea58b4776f1cd8bfb591a6d940a62a9050d
```

It has been checked both as a forward application against an archive of the
baseline commit and as a reverse application against the current source tree.

`series/` contains the same final source delta as five ordered `git
format-patch` files. Use this series when commit-level review or `git am` is
required:

1. `23d5d8a` Fix IVFFlat scan lifecycle
2. `65b7534` Add IVFFlat query sort memory control
3. `a1721d8` Restore pgvector auto-vectorization flags
4. `15aaa20` Add IVFFlat rescan regression coverage
5. `a9192a7` Add IVFFlat profiling harnesses
