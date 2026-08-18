# 项目一技术报告

本目录是“OpenTenBase pgvector 查询路径优化”的报告源文件。最终 PDF、图表和 PPT 必须从本目录与 `artifacts/experiment/ivfflat-query-path-v1/` 的原始证据生成；指标文件和原始日志优先于报告文字。

## 当前状态

- 报告骨架：十章已建立。
- 初稿：`01-摘要.md`、`02-背景与任务对齐.md` 已完成。
- 主要证据：稳定 SIMD 矩阵、正确性输出、回归日志、rescan 内存消融、perf 报告。
- 主门禁：G12 已通过；七图与 PDF 初版已生成，仍需完成最终内容自审。

## 章节与证据绑定

| 章节 | 主要证据 | 状态 |
|---|---|---|
| 01 摘要 | `artifacts/experiment/ivfflat-query-path-v1/summary.md`、`metrics.json` | 初稿 |
| 02 背景与任务对齐 | `PLAN.md`、`README.md`、补丁系列 | 初稿 |
| 03 环境与可复现声明 | `environment/remote-environment.txt`、`run_manifest.json` | 骨架 |
| 04 方法学 | `commands/`、`metrics.md`、固定数据清单 | 骨架 |
| 05 实现与架构 | `patches/series/`、`claim_validation.md` | 骨架 |
| 06 实验设计 | `PLAN.md` 第 3、5 节 | 骨架 |
| 07 结果与图表 | `metrics.json`、`report/figures/data/`、`report/figures/output/` | 图表初稿 |
| 08 局限与风险 | `metrics.md`、`DECISION.md`、TAP 日志 | 骨架 |
| 09 贡献与后续计划 | `claim_validation.md`、PR #1 | 骨架 |
| 10 附录与复现命令 | `commands/reproduce-main.md`、`reproduce-smoke.md` | 骨架 |

## 写作边界

`ivfflat.query_work_mem` 的 7.32% 改善低于预设 10% 门槛，只作为辅助结果；生命周期实验的执行时间是 mixed，不宣称延迟收益；自动向量化来自现有编译器能力恢复，不是手写 SIMD intrinsics；本轮未采集逐查询 P95/P99。

旧版 `docs/figures/` 图已移入 `report/appendix/legacy-figures/`，并明确标记为仅工程连通性验证；正文图表不得引用旧图。

构建命令为 `PYTHON_BIN=python3 bash report/build.sh`。`PYTHON_BIN` 只用于选择本机已有的 Python 3 运行时；该运行时需要提供 Pillow 和 ReportLab，脚本本身不依赖仓库外的固定绝对路径。
