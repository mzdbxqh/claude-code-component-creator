# report-renderer 拆分分析

## 当前状态
- 总行数: 419 行
- 处理 6 种报告类型

## 共享逻辑 (约 80 行)
- 模板填充引擎 (占位符解析、替换)
- 后处理优化 (清理空行、格式修正)
- 错误处理 (JSON 解析、模板缺失、占位符未匹配)
- 文件写入逻辑

## 差异化逻辑
- review-aggregated: 120 行 (审阅聚合报告)
- architecture-analysis: 100 行 (架构分析报告)
- dependency-analysis: 90 行 (依赖分析报告)
- migration-review: 110 行 (改造方案报告)

## 拆分建议
按输入类型拆分为 4 个专用 renderer，共享逻辑提取到 references/
