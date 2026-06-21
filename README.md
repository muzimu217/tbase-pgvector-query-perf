# 项目一：pgvector 查询性能优化

## 任务定位

围绕 `contrib/pgvector` 的向量距离计算、IVFFlat 索引扫描、`lists/probes` 参数选择、召回率与查询延迟平衡开展优化。

## 当前状态

已完成阶段性交付，并提交到 OpenTenBase-Packages：

- PR #27: `Add pgvector benchmark report and diagnostics`

## 交付物

```text
docs/pgvector-performance-development-report.md
docs/pgvector-optimization-roadmap-engineering-plan.md
docs/benchmark-data/
docs/figures/
patches/pgvector-ivfflat-benchmark-tools.patch
SOP.md
```

## 核心验证

- 100000 行、128 维、30 查询。
- L2/IP/Cosine 三类 metric。
- IVFFlat `lists=1000`，`probes=1/5/10/50/100/500/1000`。
- `EXPLAIN` 确认三类查询均走 `Index Scan using items_embedding_ivfflat_idx`。
- 形成 recall/latency 曲线和参数建议。

