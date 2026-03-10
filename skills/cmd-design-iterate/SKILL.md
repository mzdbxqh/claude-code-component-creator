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

## 使用示例 (Examples)

### Example 1: 基础组件迭代

```bash
/design-iterate commands/deploy.md
```

**输入**: 现有的部署命令组件文档

**输出**: 生成迭代设计文档，包含：
- 当前组件能力分析
- 与最新设计标准的差异对比
- 增量优化方案（如添加回滚能力、多环境支持）
- 变更证据链（为何需要这些变更、影响哪些 skill）

### Example 2: Subagent 组件优化

```bash
/design-iterate subagents/docker-builder.md --lang=en-us
```

**输入**: 现有 Docker 构建器 Subagent 文档，英文输出

**输出**: 英文迭代设计文档，分析：
- 当前架构与三角色系统的符合度
- 工具权限配置优化建议
- 性能改进方案（如并行构建支持）
- 迁移路径和风险评估

### Example 3: 复杂组件重构迭代

```bash
/design-iterate skills/reviewer/migration-reviewer-core.md
```

**输入**: 复杂的审查器核心 Skill 组件

**输出**: 全面的重构方案：
- 现状分析（代码复杂度、依赖关系）
- 目标架构（模块化、可扩展性）
- 分阶段迭代计划（第一阶段重构检测模式、第二阶段优化性能）
- 完整变更证据链（每个变更的业务价值和技术理由）
- 回滚策略和测试方案
