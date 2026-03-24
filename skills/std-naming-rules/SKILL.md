---
name: std-naming-rules
description: "命名规则检查标准。定义Skill/Subagent命名规范。用于审阅插件命名合规性。"
model: sonnet
allowed-tools: []
context: main
argument-hint: ""
---

# 命名规则检查标准

## 模型要求

- **推荐**: Claude Sonnet 4.5+ (高效能,最佳性价比)
- **可用**: Claude Haiku 3.5+ (快速加载,知识库类 Skill)
- **最小**: Claude Haiku 3.5+ (最低要求)

### 功能需求
- 作为知识库 Skill,无需 Tool Use
- 通过 skills 字段加载到 Subagent 中
- 建议上下文窗口 >= 50K tokens

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
