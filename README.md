# 项目一：pgvector 查询性能优化

## 任务定位

围绕 `contrib/pgvector` 的向量距离计算、IVFFlat 索引扫描、`lists/probes` 参数选择、召回率与查询延迟平衡开展优化。

## 当前状态

已完成 `muzimu217/ivfflat-query-path-optimization` 分支的源码开发、
分步提交与实验收口：

- 修复 IVFFlat rescan/iterative scan 的 tuplesort 生命周期问题。
- 释放 Cosine rescan 的旧归一化查询向量，50,000 rescans 峰值 RSS 增长降低 59.97%。
- 修复 OpenTenBase in-tree Makefile 的 pgvector 自动向量化参数传递，高 `probes` 负载平均耗时降低 18.30%。该优化由编译器自动向量化完成，不包含手写 SIMD intrinsics。
- 新增 `ivfflat.query_work_mem`，可独立消除 IVFFlat 查询排序的临时 I/O。
- 200 条查询的 2,000 个 top-10 结果全部一致，`recall@10=1.0`。

## 交付物

```text
docs/pgvector-performance-development-report.md
docs/pgvector-optimization-roadmap-engineering-plan.md
docs/benchmark-data/
docs/figures/
patches/pgvector-ivfflat-benchmark-tools.patch
patches/0001-ivfflat-query-path-optimization.patch
patches/series/
artifacts/experiment/ivfflat-query-path-v1/
SOP.md
```

## 核心验证

- 原始参数基线：100000 行、128 维、30 查询，L2/IP/Cosine，`probes=1/5/10/50/100/500/1000`。
- 主优化实验：100000 行、128 维、200 查询，Cosine，`lists=probes=1000`。
- `EXPLAIN` 确认查询走 IVFFlat Index Scan，exact/IVFFlat top-10 共 2000 行全部一致。
- scalar/SIMD 五次 ABBA 配对矩阵、perf 数据、内存消融和固定种子数据校验链均已归档。

主实验的详细数字、结论边界和复现命令见
[`artifacts/experiment/ivfflat-query-path-v1/`](artifacts/experiment/ivfflat-query-path-v1/)。
