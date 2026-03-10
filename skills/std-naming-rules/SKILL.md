---
name: ccc:std-naming-rules
description: "命名规则检查标准。适用于审阅 Claude Code 插件时的命名规范检查。包含 Skill 命名规则（cmd-/std-/lib-前缀）、Subagent 命名规则、触发路径规则。Use when reviewing Claude Code plugins."
model: sonnet
context: main
---

# 命名规则检查标准

## Skill 命名规则

### 角色前缀规则

| 前缀 | 角色 | 适用场景 |
|------|------|---------|
| `cmd-` | 入口型 Skill | 用户手动触发的工作流 |
| `std-` | 自动发现型 Skill | 通用规范、知识 |
| `lib-` | 参考型 Skill | 专业知识库 |

### 正确示例

```
✅ cmd-design           # 入口型：设计工作流
✅ std-naming-rules     # 自动发现型：命名规则
✅ lib-antipatterns     # 参考型：反模式库
```

### 错误示例

```
❌ design               # 缺少 cmd- 前缀
❌ cmd_design           # 应使用 kebab-case
```

---

## Subagent 命名规则

```
<domain>-<role>-core   # 核心组件
<domain>-<function>    # 功能组件
```

### 正确示例

```
✅ review-core
✅ architecture-analyzer
```

---

## 审阅检查清单

- [ ] 入口型 Skill 使用 `cmd-` 前缀
- [ ] 自动发现型 Skill 使用 `std-` 前缀
- [ ] 参考型 Skill 使用 `lib-` 前缀
- [ ] 所有 Skill 名称使用 kebab-case
- [ ] frontmatter name 字段格式正确

---

## 更新日志

- 2026-03-11: 创建 std-naming-rules Skill
