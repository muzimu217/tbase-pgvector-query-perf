# OpenTenBase pgvector 查询路径优化与完整交付计划

## 1. 项目目标

本项目以 OpenTenBase 内置 pgvector 的 IVFFlat 查询路径为对象，先修复可复现的查询路径问题，再通过 profiling 选择高 `probes` 场景下的性能优化点。所有性能结论必须同时具备源码、固定数据生成方法、原始日志、执行计划、指标文件和图表，不以单次运行或人工摘录的数据作为结论。

### 用户要求与交付边界

1. 第一阶段：完成源码开发、回归测试和可复现实践测试。
2. 第二阶段：交付完整数据链、证明材料、图表和 PDF 技术报告。
3. 第三阶段：制作约 20 页的项目汇报 PPT，并放入仓库文档目录。
4. 第四阶段（可选）：提供录制视频所需的逐镜头脚本，视频由申请人录制。
5. 当前只执行第一阶段。后续阶段不得提前编造性能数据或结论。

## 2. 实验契约

- run id：`ivfflat-query-path-v1`
- 实验层级：rescan 可靠性修复为 `auxiliary/dev`，后续 before/after 性能矩阵为 `main/test`。
- 开发分支：`muzimu217/ivfflat-query-path-optimization`
- 主问题：OpenTenBase pgvector 0.8.0 的 IVFFlat 查询路径能否在保证结果与 recall 不变的前提下，提高反复 rescan 的稳定性，并降低高 `probes` 查询开销？
- 零假设：源码修改不会带来可重复的内存或延迟改善。
- 备择假设：修复 rescan 生命周期后，嵌套循环场景内存不再随 rescan 次数持续增长；后续基于 profiling 的单点优化可降低高 `probes` 延迟且不降低 recall。
- 第一项最小改动：回移 pgvector 0.8.6 的 IVFFlat rescan 查询向量释放修复，并用 OpenTenBase 可用的 tuplesort 重建补齐上游 `tuplesort_reset()` 语义，再补充嵌套循环回归用例。
- 上游出处：pgvector commit [`93a5b4a16d699eaf890970777c19f19b9d545782`](https://github.com/pgvector/pgvector/commit/93a5b4a16d699eaf890970777c19f19b9d545782)，`Fix memory leak in ivfrescan`。该提交初始化 `so->value`，并在重新归一化查询值前释放上一轮分配。
- OpenTenBase 适配边界：归一化查询值清理沿用上述上游修复语义；排序生命周期部分为平台独立适配，因为 OpenTenBase PG10 基座没有上游使用的 `tuplesort_reset()`，本项目采用销毁并重建 tuplesort 状态恢复等价批次语义。
- 放弃条件：无法证明问题存在于 OpenTenBase 当前代码，或者修改改变距离结果、索引计划或 recall。
- 最强备选解释：RSS 增长可能主要来自 tuplesort/内存分配器保留，而非归一化查询向量泄漏；因此必须同时保存 IVFFlat loops 和 RSS 时序，并在同主机进行 baseline/patched 对照。

## 3. 基线与可比性

### 已接受基线

- 基线源码：`OpenTenBase-source` 分支 `feature/pgvector-bench-diagnostics-tools`，提交 `0915c04`。
- 上游基础：OpenTenBase `origin/master` 加一项 benchmark/diagnostics 提交。
- 数据文件：`docs/benchmark-data/ivfflat_benchmark_20260621_110256.csv`。
- 数据规模：100000 行、128 维、30 条查询、`top-k=10`。
- 索引参数：`lists=1000`，`probes=1/5/10/50/100/500/1000`。
- 距离类型：L2、Inner Product、Cosine。

### 必须保持不变的比较条件

- 固定数据生成种子、数据规模、维度、query 集合和预热方法。
- before/after 使用同一机器、编译参数、OpenTenBase 拓扑和数据库参数。
- 每个场景至少 1 次预热、5 次正式重复；报告均值、P50、P95、P99 和离散程度。
- 每次保存 `EXPLAIN (ANALYZE, BUFFERS)`，确认走同一 IVFFlat Index Scan。
- 必须同时报告 `recall@10`；性能改善不能以 recall 下降换取。

### 第一阶段指标键

- `backend_rss_before_kb`
- `backend_rss_after_kb`
- `backend_rss_delta_kb`
- `avg_latency_ms`
- `p95_latency_ms`
- `p99_latency_ms`
- `qps`
- `recall_at_10`
- `plan_uses_ivfflat`
- `regression_status`

## 4. 代码实施计划

| 路径 | 当前作用 | 第一阶段改动 | 验证方式 | 风险 |
|---|---|---|---|---|
| `OpenTenBase-source/contrib/pgvector/src/ivfscan.c` | IVFFlat list 选择、候选扫描、排序和 rescan | 初始化归一化查询值，并在 rescan 时释放上一轮分配 | 嵌套循环 SQL、RSS/内存上下文对比、回归测试 | 错误释放非自有 Datum |
| `OpenTenBase-source/contrib/pgvector/test/sql/ivfflat_vector.sql` | IVFFlat vector 回归输入 | 增加 Cosine LATERAL/nested-loop rescan 场景 | `make installcheck REGRESS=ivfflat_vector` | 查询计划未触发 rescan |
| `OpenTenBase-source/contrib/pgvector/test/expected/ivfflat_vector.out` | 回归预期输出 | 固化嵌套循环查询正确结果 | regression diff 为零 | 输出顺序不稳定 |
| `contrib/pgvector/bench/` | 现有可复现 benchmark | 增加 rescan 内存场景和分阶段耗时采集 | shell 语法检查、OpenTenBase 实跑 | 平台观测接口差异 |
| `patches/` | 可移植源码交付 | 导出最小补丁并记录基线 commit | `git apply --check` | 与后续上游更新冲突 |

### 后续 profiling 候选

这些候选必须在 `perf` 证据出来后才能进入代码，不预先全部实现：

1. `GetScanLists`：中心距离计算和 pairing heap 维护。
2. `GetScanItems`：候选距离计算、虚拟 tuple 构造和 `tuplesort` 写入。
3. 距离函数：现有编译器自动向量化是否生效，以及 L2/IP/Cosine 的 CPU 占比。
4. OpenTenBase 分布式路径：Coordinator/Datanode 与 Remote Fast Query Execution 开销。

### Profiling 结论与已选性能改动

- 数据：100000 行、128 维、Cosine、`lists=1000`、`probes=1000`、200 条固定查询。
- 基线计划：约 21.03 秒，临时块读 69000、写 69400。
- perf 热点：向量内积约 32.2%，排序比较与排序主体至少约 22.6%，且存在明显临时文件 I/O。
- 汇编核查：`VectorInnerProduct.fma.0` 仍为标量 `vfmadd231ss` 循环；OpenTenBase in-tree 构建未消费 pgvector 的 `PG_CFLAGS`，导致自动向量化参数被静默丢失。
- 上限 pilot：`work_mem=64MB` 消除临时块 I/O，同负载约 15.80 秒，改善约 24.9%。
- 实现 A：修复 in-tree Makefile 参数传递，让现有 pgvector 自动向量化设计真正生效。
- 实现 B：新增 `ivfflat.query_work_mem`，默认 `0` 继承 `work_mem`，只在用户显式配置时提高 IVFFlat 内部 tuplesort 预算。

## 5. 执行路线

### 5.1 Smoke

1. 编译 `contrib/pgvector`。
2. 执行 `ivfflat_vector` 单项 regression。
3. 执行新增 nested-loop 查询，确认结果稳定并实际触发 IVFFlat rescan。
4. 对脚本执行 `bash -n`。

Smoke 预计时间预算为 30 分钟，远端构建和最小集群部署预算为 2 小时。第一次内存观测使用 `RESCANS=1000`，只检查脚本、计划与 loops；不用它支撑修复效果结论。

### 5.2 正式测试

1. 在同一 OpenTenBase 环境分别运行 baseline commit 与优化 commit。
2. rescan 矩阵：外表行数 `100/1000/10000`，维度 `128/384/768`，每组 5 次。
3. 查询矩阵：三种 metric，原有 7 档 `probes`，每组 5 次。
4. 高 `probes` profiling：重点采集 `500/1000`，保存 `perf.data`、折叠栈和 SVG 火焰图。
5. 原始输出写入带时间戳的运行目录，不覆盖历史运行。

### 5.3 成功门槛

- 第一项修复：nested-loop/rescan 场景内存增长不再随执行次数线性累积，回归测试通过。
- 主性能优化：`probes=500/1000` 至少一个核心 metric 的 avg 或 P95 改善达到 10%，5 次重复方向一致。
- L2/IP/Cosine 正确性通过，`recall@10` 不下降，执行计划保持 IVFFlat。
- 若性能收益不足 10%，如实归类为 `inconclusive`，保留 profiling 和负结果，不包装成成功。

## 6. 证据与目录合同

```text
artifacts/experiment/<run_id>/
  artifact_manifest.json
  run_manifest.json
  environment/
  commands/
  logs/
  plans/
  raw-data/
  metrics.json
  metrics.md
  claim_validation.md
  summary.md
docs/final-report/
  report-source.md
  figures/
  OpenTenBase-pgvector-query-optimization-report.pdf
docs/presentation/
  outline.md
  OpenTenBase-pgvector-query-optimization.pptx
  OpenTenBase-pgvector-query-optimization.pdf
docs/video/
  recording-script.md
```

所有图表必须能够由 `raw-data/` 中的 CSV/JSON 和仓库脚本重新生成。PDF、PPT 不作为数据真相源，只引用经过验证的指标文件。

## 7. 最终报告结构

1. 摘要与贡献点。
2. OpenTenBase 与 pgvector 查询链路背景。
3. 问题定义与基线。
4. 实验环境和可复现方法。
5. 源码审计与 profiling 证据。
6. rescan 生命周期修复。
7. 高 `probes` 性能优化实现。
8. 正确性、recall 和性能结果。
9. 消融、异常场景和限制。
10. 复现步骤、PR 信息和结论。

## 8. 约 20 页 PPT 结构

1. 封面
2. 项目与课题背景
3. 用户问题
4. OpenTenBase/pgvector 架构
5. IVFFlat 查询流程
6. 基线实验设计
7. 数据与指标
8. 原始基线结果
9. 问题一：rescan 生命周期
10. 问题复现证据
11. 修复设计
12. 回归验证
13. profiling 方法
14. 热点证据
15. 性能优化设计
16. before/after 结果
17. recall 与延迟权衡
18. 可复现交付链
19. 局限与后续工作
20. 总结与社区贡献

## 9. 视频脚本范围

视频脚本在代码、数据和报告稳定后生成，包含环境介绍、问题复现、源码讲解、测试执行、结果图表和结论。脚本只描述仓库中可以实际复现的操作，不加入未完成演示。

## 10. 回退与恢复

- 本地无法完整构建 OpenTenBase：先完成代码静态验证和补丁检查，正式指标标记为待远端运行。
- 远端资源不足：保持数据与指标定义不变，先运行缩小规模的 smoke，不用小规模结果替代正式结论。
- profiling 显示热点不在 pgvector：保留证据，将优化目标收敛到 OpenTenBase 分布式执行层或终止该候选。
- 第一次性能改动不增益：回到可执行的 rescan 修复 checkpoint，依据热点选择下一项单变量修改。

## 11. 修订记录

| 日期 | 变更 | 原因 | 对可比性的影响 |
|---|---|---|---|
| 2026-08-17 | 创建完整交付与第一阶段实验计划 | 从申请阶段进入源码开发 | 无，沿用 2026-06-21 基线数据合同 |
| 2026-08-17 | 新增单后端 rescan RSS 时序工具 | 隔离 CN/DN 远程执行干扰并证明实际 index loops | 正式对照必须在同主机、同参数、同拓扑下运行 |
| 2026-08-17 | 远端全量构建第一次失败后补装 `libcurl-devel` 并增量重跑 | `url_curl.c` 缺少 `curl/curl.h` | 仅环境修复，未改变源码和编译参数 |
| 2026-08-17 | 为 4 GB 开发机显式下调 OpenTenBase 测试集群的 forward buffer、workfile、SPM 和 worker 配置 | 默认 `fn_shared_buffers=300000`、`pg_workfile_max_entries=8192` 且 `max_wal_senders=64`，不适合单机最小拓扑 | 只影响环境资源上限；baseline/patched 将共用同一配置 |
| 2026-08-17 | 将第一项修复扩展为 tuplesort 批次重置 + Cosine 查询向量释放 | 真实 regression 触发 rescan 与 iterative scan 的 `invalid tuplesort state`；OpenTenBase 无上游 `tuplesort_reset()` | 不改变数据、距离函数或 probes，仅恢复每批独立排序状态 |
| 2026-08-17 | 新增 sort-reset/no-cleanup 消融对照，用 peak RSS 而非 end RSS 作为内存生命周期主指标 | 原始基线无法完成 rescan，且 scan 结束会释放 tmp context，端点 RSS 会隐藏执行期峰值 | 消融版与完整版仅相差 normalized value cleanup；同种子、同主机、每格 5 次 |
| 2026-08-17 | 新增 `ivfflat.query_work_mem` 并完成 4MB/64MB 五次配对 | profiling 显示 tuplesort 临时 I/O，需要不改全局 `work_mem` 的控制面 | 临时块归零，但 7.32% 改善低于 10% 门槛，不作主加速结论 |
| 2026-08-17 | 修复 in-tree Makefile 对 pgvector 自动向量化参数的传递 | 标量 perf 中内积占 32.20%，汇编证明现有 `PG_CFLAGS` 未生效 | 不改算法、数据、probes 或 recall；仅恢复 pgvector 已有编译设计 |
| 2026-08-17 | 废弃第一轮 SIMD 正式矩阵并保留原始文件 | 主机负载档位跳变跨过一个 ABBA pair | 该轮不进入主指标；稳定性复跑新增每次系统快照 |
| 2026-08-17 | 完成 SIMD 稳定性复跑、top-10 校验和后置 perf | 需同时证明改善幅度、方向一致、结果不变与机制命中 | 5/5 同向、平均 -18.30%、recall@10=1.0；内积 perf 份额从 32.80% 降至 17.37% |
| 2026-08-18 | 补充 rescan 内存泄漏修复的 pgvector 官方 commit URL 与平台适配边界 | R006-L4 要求每项上游来源可点击核验 | 不改变实现或实验，仅补全来源追溯 |
