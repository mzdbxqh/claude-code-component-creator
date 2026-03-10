---
name: ccc:design-new
description: |
  从零开始设计新组件 - 通过 5 阶段流程（需求→架构→设计→验证→规划）
  创建完整的组件设计方案。
  Design new component from scratch - 5-stage workflow (requirements→architecture→
  design→validation→planning) to create complete component design.
argument-hint: "[component-name] [--lang=zh-cn|en-us|ja-jp]"
---

# /design-new 命令

## 用法 (Usage)

```
/design-new
/design-new --lang=en-us
```

直接运行命令，Claude 将引导你完成交互式设计流程。

## 输出 (Output)

设计文档将包含：
- 5阶段设计结果（需求→架构→设计→验证→规划）
- **完整证据链**（能力需求表、Skill映射表、验证清单）
- Blueprint artifact

## Global Parameter

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--lang` | `zh-cn`, `en-us`, `ja-jp` | `zh-cn` | 输出语言 (Output language) |
