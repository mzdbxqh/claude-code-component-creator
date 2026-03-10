---
name: ccc:cmd-design-iterate
description: |
  基于现有组件迭代优化 - 分析现状与目标差异，生成增量变更方案。
  Iterate on existing components - analyze current vs target state,
  generate incremental change proposals.
argument-hint: "<component-path> [--lang=zh-cn|en-us|ja-jp]"
---

# /design-iterate 命令

## 用法 (Usage)

```
/design-iterate <component-path>
/design-iterate <component-path> --lang=en-us
```

## Global Parameter

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--lang` | `zh-cn`, `en-us`, `ja-jp` | `zh-cn` | 输出语言 (Output language) |

## 参数 (Parameters)

- `component-path`: 现有组件文件路径
  - 示例：`commands/deploy.md`
  - 示例：`subagents/docker-builder.md`

## 输出 (Output)

迭代设计文档将包含：
- 差异分析
- 影响评估
- 增量方案
- **变更证据链**（变更的能力需求、影响的skill、变更原因）
