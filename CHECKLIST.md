# ivfflat-query-path-v1 执行清单

## 身份

- run id：`ivfflat-query-path-v1`
- idea：IVFFlat rescan 生命周期修复与高 probes 查询路径优化
- 分支：`muzimu217/ivfflat-query-path-optimization`
- 当前阶段：源码开发与实验已收口

## 规划

- [x] 主方向与仓库确定
- [x] 已接受 baseline 和指标合同确认
- [x] 源码问题与 profiling 热点定位
- [x] 完整交付目录与报告/PPT/视频边界确定
- [x] smoke 和正式运行路线写入 `PLAN.md`
- [x] 本地与远端运行环境快照完成

## Rescan 生命周期

- [x] 初始化 IVFFlat scan 保存的归一化查询值
- [x] rescan 前释放上一轮归一化查询值
- [x] 在 OpenTenBase 中重建 tuplesort 状态
- [x] 增加 Cosine nested-loop regression SQL 并更新 expected
- [x] 增加可重复的 rescan 内存观测场景
- [x] 原始基线 `invalid tuplesort state` 失败证据完成
- [x] sort-reset/no-cleanup 与完整修复 3x5 消融矩阵完成

## 性能优化

- [x] scalar 基线和 SIMD 优化构建完成
- [x] 修复 OpenTenBase in-tree Makefile 的 pgvector 向量化参数传递
- [x] 汇编确认标量 `vfmadd231ss` 变为 packed `vfmadd231ps`
- [x] 实现 `ivfflat.query_work_mem`
- [x] 完成 SIMD 五次 ABBA 稳定性矩阵与负载快照
- [x] 完成 query-work-mem 五次配对矩阵
- [x] 完成 scalar/SIMD perf data 与 symbol/children 报告
- [x] 保留且排除受负载跳变干扰的第一轮矩阵

## 验证与证据

- [x] 最终 `ivfflat_vector` regression 1/1 通过
- [x] L2/IP/Cosine 与 iterative scan 正确性通过
- [x] exact/IVFFlat 2,000 个 top-10 结果全部匹配，`recall@10=1.0`
- [x] SIMD 平均耗时改善 18.30%，5/5 同向
- [x] 生命周期可靠性和峰值内存改善为 supported
- [x] `ivfflat.query_work_mem` 消除临时 I/O，但 7.32% 改善未达主门槛
- [x] 固定种子数据 SHA256、原始计划、负载快照和 perf 数据归档
- [x] 生成仓库内可直接校验的 `ablation/SHA256SUMS.local`
- [x] 完整源码补丁在基线上 `git apply --check` 通过
- [x] 源码树拆分为 5 个渐进提交并生成标准 `git format-patch` 系列
- [x] 全部 benchmark/diagnostic shell 脚本通过 `bash -n`

## 后续交付

- [ ] PDF 技术报告与可复现图表完成
- [ ] 约 20 页 PPT 完成并逐页检查
- [ ] PPT 放入仓库文档目录
- [ ] 视频录制脚本完成
- [ ] 交付仓库分步 commit/push/draft PR
- [ ] 最终提交材料索引完成

## 当前下一项

源码开发与实验阶段已收口。下一阶段使用已归档指标制作完整 PDF 技术报告和可复现图表，不再改变主实验口径。
