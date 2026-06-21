# 项目一 SOP：pgvector 查询性能优化

## 目标

在 L2、Inner Product、Cosine 场景下，保证结果正确性和 recall 稳定，同时降低查询耗时或提升吞吐。

## 阶段 1：环境确认

1. 确认 OpenTenBase 可启动。
2. 确认 `CREATE EXTENSION vector` 成功。
3. 记录 CPU、内存、磁盘、OpenTenBase 版本。
4. 确认 `contrib/pgvector` 目录存在。

退出条件：能创建 vector 表并执行基础距离查询。

## 阶段 2：基线工具

1. 准备 benchmark 脚本。
2. 参数必须通过环境变量配置：
   - `ROWS`
   - `DIMS`
   - `QUERIES`
   - `TOPK`
   - `LISTS`
   - `PROBES_LIST`
   - `METRICS`
   - `MAINTENANCE_WORK_MEM`
3. 自动输出 CSV 和 `EXPLAIN` plan。

退出条件：smoke benchmark 通过，且 plan 显示 IVFFlat Index Scan。

## 阶段 3：正式 benchmark

按资源预算生成矩阵，不固定单一参数。

推荐矩阵：

```text
METRICS="l2 ip cosine"
PROBES_LIST="1 5 10 50 100 <lists/2> <lists>"
```

退出条件：

- 每个 metric 至少 5 档 probes。
- 同时保存 avg latency、p95 latency、recall@k。
- 每个 metric 有 plan 证据。

## 阶段 4：热点定位

优先分析：

- 距离计算函数。
- IVFFlat list 扫描。
- tuple fetch。
- OpenTenBase 分布式执行开销。

可使用 `perf`、`gprof` 或火焰图工具。

## 阶段 5：优化验证

任何优化必须满足：

- recall 不下降。
- 查询计划仍走 IVFFlat。
- 至少 avg latency、p95 latency 或吞吐之一改善。
- 保留 before/after CSV 和图表。

## 禁止事项

- 禁止只报告延迟，不报告 recall。
- 禁止没有 `EXPLAIN` 就声称走 IVFFlat。
- 禁止把 smoke benchmark 当正式结论。
- 禁止把某一台机器上的参数写成全局默认值。

