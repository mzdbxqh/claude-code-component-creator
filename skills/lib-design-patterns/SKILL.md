---
name: lib-design-patterns
description: "设计模式知识库，CCC 5阶段设计流程模式。由Subagent通过skills字段加载。"
model: sonnet
allowed-tools: []
context: main
---

# 设计模式知识库

## 模型要求

- **推荐**: Claude Sonnet 4.5+ (高效能,最佳性价比)
- **可用**: Claude Haiku 3.5+ (快速加载,知识库类 Skill)
- **最小**: Claude Haiku 3.5+ (最低要求)

### 功能需求
- 作为知识库 Skill,无需 Tool Use
- 通过 skills 字段加载到 Subagent 中
- 建议上下文窗口 >= 50K tokens

## Purpose

本 Skill 整合了 CCC 5 阶段设计流程的模式库，用于指导组件设计。

---

## 设计模式来源

设计模式定义来自：
- `agents/advisor/knowledge/design-patterns/` - 原始设计模式（JSON 格式）
- 涵盖 5 个阶段：需求分析、架构选型、详细设计、验证、规划

---

## 使用方式

在 Subagent 中通过 skills: 字段加载：

```yaml
---
name: advisor-core
skills:
  - ccc:lib-design-patterns
---
```

---

## 5 阶段设计流程

### 阶段 1：需求分析（Requirement）
- 问为什么直到根因
- 澄清技术需求和约束

### 阶段 2：架构选型（Architect）
- 基于需求选择组件类型
- 选择架构设计模式

### 阶段 3：详细设计（Design）
- 创建 YAML 配置
- 定义工作流步骤

### 阶段 4：验证（Validator）
- 验证合规性
- 检查配置完整性

### 阶段 5：实施规划（Planner）
- 生成详细实施计划
- 任务分解

---

## 更新日志

- 2026-03-11: 创建 lib-design-patterns Skill
