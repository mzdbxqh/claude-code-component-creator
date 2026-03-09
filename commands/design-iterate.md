---
name: ccc:design-iterate
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
