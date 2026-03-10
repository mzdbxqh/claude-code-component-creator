---
name: ccc:lib-design-patterns
description: "设计模式知识库。包含 CCC 5 阶段设计流程的模式库（需求分析、架构选型、详细设计、验证、规划）。由 Subagent 通过 skills: 字段加载。"
model: sonnet
context: main
---

# 设计模式知识库

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
