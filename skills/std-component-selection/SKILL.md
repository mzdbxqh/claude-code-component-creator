---
name: ccc:std-component-selection
description: "组件选型决策规则。适用于设计和审阅 Claude Code 插件时的组件类型选择。提供 Skill 三种角色（cmd-/std-/lib-）决策树和典型组合模式。Use when designing or reviewing Claude Code plugins."
model: sonnet
context: main
---

# 组件选型决策规则

## Purpose

本 Skill 定义了 Claude Code 插件中组件选型的标准决策流程，包括：
1. **Skill 三种角色**的定义和选择标准（cmd-/std-/lib-）
2. **Subagent 和 Hook** 的适用场景
3. **典型组合模式**和最佳实践

本规则既用于 CCC 自身架构设计，也用于 CCC 设计/审阅其他插件时的选型判断。

---

## Skill 三种角色定义

| 角色 | 命名前缀 | 触发方式 | 用途 | 示例 |
|------|---------|---------|------|------|
| **入口型 Skill** | `cmd-` | `/plugin:cmd-xxx` 用户手动触发 | 工作流入口，可调度 Subagent | `cmd-design`, `cmd-review` |
| **自动发现型 Skill** | `std-` | Claude 自动匹配 description | 通用规范、知识，Claude 自动加载 | `std-api-conventions`, `std-naming-rules` |
| **参考型 Skill** | `lib-` | Subagent `skills: []` 显式加载 | 专业知识库，给特定 Subagent 用 | `lib-security-rules`, `lib-antipatterns` |

---

## 选型决策树

```
组件性质分析
│
├─ 🎯 需要用户通过 / 手动触发工作流？
│   → **入口型 Skill** (cmd- 前缀)
│   - 命名：cmd-<workflow-name>
│   - 可调度 Subagent
│   - 可引用其他 Skill
│   - 典型场景：设计、审阅、部署、测试等工作流
│   - 示例：cmd-design, cmd-review, cmd-deploy
│
├─ 📖 纯知识/流程/规范/检查清单？
│   │
│   ├─ 通用知识，Claude 能自动判断何时需要
│   │   → **自动发现型 Skill** (std- 前缀)
│   │   - 命名：std-<topic-name>
│   │   - description 要清晰说明适用场景
│   │   - 典型场景：API 规范、命名规则、架构模式
│   │   - 示例：std-api-conventions, std-naming-rules, std-component-selection
│   │
│   └─ 专业知识，给特定 Subagent 用的参考资料
│       → **参考型 Skill** (lib- 前缀)
│       - 命名：lib-<knowledge-domain>
│       - 由 Subagent 通过 skills: 字段加载
│       - 典型场景：反模式库、设计模式库、安全规则
│       - 示例：lib-security-rules, lib-antipatterns, lib-design-patterns
│
├─ 🤖 需要独立执行复杂任务？
│   - 需要隔离上下文 / 限制工具 / 并行 / 不同模型
│   → **Subagent**
│   - 通过 skills: [plugin:lib-xxx] 预装知识
│   - context: fork 隔离上下文
│   - 典型场景：审阅、设计、测试执行、报告生成
│   - 示例：review-core, advisor-core, blueprint-core
│
└─ ⚡ 需要在事件发生时自动执行确定性逻辑？
    → **Hook**
    - PreToolUse / PostToolUse / Notification / Stop
    - 不经过 LLM，100% 确定性
    - 典型场景：权限检查、环境验证、参数校验
    - 示例：pre-deploy-check.sh, validate-config.sh
```

---

## 命名规则

### Skill 命名规则

```
格式：<role-prefix>-<descriptive-name>
      │              │
      │              └─ 描述性名称（kebab-case）
      └─ 角色前缀（cmd/std/lib）

示例：
  cmd-design          → 入口型 Skill，触发设计工作流
  std-naming-rules    → 自动发现型 Skill，命名规则知识
  lib-antipatterns    → 参考型 Skill，反模式知识库
```

### Subagent 命名规则

```
格式：<domain>-<role>-core 或 <domain>-<specific-function>

示例：
  review-core              → 审阅领域核心组件
  advisor-core             → 顾问领域核心组件
  architecture-analyzer    → 架构分析组件
```

---

## Subagent 配置规范

Subagent 应通过 `skills:` 字段显式声明依赖的参考型 Skill：

```yaml
---
name: review-core
skills:
  - ccc:std-component-selection
  - ccc:std-naming-rules
  - ccc:lib-antipatterns
context: fork
model: sonnet
---
```

**关键要点**：
- 使用完整的命名空间：`plugin:skill-name`
- 参考型 Skill 必须通过 skills: 字段加载
- 依赖关系显性化，易于维护

---

## 设计时的选型问题

在设计插件组件时，按顺序回答以下问题：

1. **需要用户手动触发吗？** → 是 → 入口型 Skill (cmd-)
2. **是纯知识/规范吗？** → 是，且通用 → 自动发现型 Skill (std-) / 是，且专业 → 参考型 Skill (lib-)
3. **需要独立执行复杂任务吗？** → 是 → Subagent（配置 skills: 字段）
4. **需要事件驱动的确定性逻辑吗？** → 是 → Hook

---

## 审阅时的检查项

### 命名规范检查

- [ ] 所有入口型 Skill 使用 `cmd-` 前缀
- [ ] 所有自动发现型 Skill 使用 `std-` 前缀
- [ ] 所有参考型 Skill 使用 `lib-` 前缀
- [ ] Skill 名称使用 kebab-case
- [ ] 触发路径格式正确：`/plugin:skill-name`

### 选型合理性检查

- [ ] 入口型 Skill 的功能确实需要用户手动触发
- [ ] 自动发现型 Skill 的 description 清晰说明适用场景
- [ ] 参考型 Skill 确实是专业知识库
- [ ] Subagent 确实需要隔离上下文或复杂任务执行

### Subagent 配置检查

- [ ] Subagent 使用 skills: 字段声明依赖
- [ ] skills: 字段使用完整命名空间（plugin:skill-name）
- [ ] 引用的 Skill 确实存在

---

## 更新日志

- 2026-03-11: 创建 std-component-selection Skill，定义 Skill 三种角色和选型决策树
