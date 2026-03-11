---
name: ccc:std-component-selection
description: "组件选型决策规则。定义Skill三角色(cmd-/std-/lib-)决策树。用于设计和审阅插件。"
model: sonnet
allowed-tools: []
context: main
---

# 组件选型决策规则

## 模型要求

- **推荐**: Claude Sonnet 4.5+ (高效能,最佳性价比)
- **可用**: Claude Haiku 3.5+ (快速加载,知识库类 Skill)
- **最小**: Claude Haiku 3.5+ (最低要求)

### 功能需求
- 作为知识库 Skill,无需 Tool Use
- 通过 skills 字段加载到 Subagent 中
- 建议上下文窗口 >= 50K tokens

## Purpose

本 Skill 定义了 Claude Code 插件中组件选型的标准决策流程，包括：
1. **Skill 三种角色**的定义和选择标准（cmd-/std-/lib-）
2. **Subagent 和 Hook** 的适用场景
3. **典型组合模式**和最佳实践

本规则既用于 CCC 自身架构设计，也用于 CCC 设计/审阅其他插件时的选型判断。

---

## Skill 三种角色定义

| 组件类型 | 命名/配置 | 触发方式 | 用途 | 示例 |
|---------|----------|---------|------|------|
| **入口型 Skill** | `cmd-` 前缀 | `/plugin:cmd-xxx` 用户手动触发 | 工作流入口，可调度 Subagent | `cmd-design`, `cmd-review` |
| **自动发现型 Skill** | `std-` 前缀 | Claude 自动匹配 description | 通用规范、知识，Claude 自动加载 | `std-api-conventions`, `std-naming-rules` |
| **参考型 Skill** | `lib-` 前缀 | Subagent `skills: []` 显式加载 | 专业知识库，给特定 Subagent 用 | `lib-security-rules`, `lib-antipatterns` |
| **Subagent** | 无前缀 | 通过 Skill 调度或直接调用 | 独立执行复杂任务，隔离上下文 | `review-core`, `advisor-core` |
| **Hook** | `.sh` 脚本 | 事件自动触发 | 确定性逻辑，权限检查、参数验证 | `pre-deploy-check.sh` |
| **MCP Server** | `.mcp.json` | 自动加载 | 扩展工具集，外部服务集成 | GitHub、Slack、Filesystem |
| **LSP Server** | `.lsp.json` | 自动加载 | IDE功能：补全、跳转、重命名 | TypeScript LS、Python LS |

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
├─ ⚡ 需要在事件发生时自动执行确定性逻辑？
│   → **Hook**
│   - PreToolUse / PostToolUse / Notification / Stop
│   - 不经过 LLM，100% 确定性
│   - 典型场景：权限检查、环境验证、参数校验
│   - 示例：pre-deploy-check.sh, validate-config.sh
│
├─ 🔌 需要扩展 Claude Code 的工具集？
│   - 集成外部服务（GitHub、Slack、数据库等）
│   → **MCP Server** (.mcp.json 配置)
│   - 配置文件：.mcp.json（插件根目录）
│   - 传输方式：http（推荐）、stdio
│   - 典型场景：GitHub 集成、Slack 通知、文件系统访问
│   - 示例：github MCP、slack MCP、filesystem MCP
│   - 注意：需要用户配置环境变量和权限
│
└─ 🔧 需要提供 IDE 级别的代码支持？
    - 代码补全、跳转定义、重命名、诊断
    → **LSP Server** (.lsp.json 配置)
    - 配置文件：.lsp.json（插件根目录）
    - 语言支持：JavaScript、Python、Rust、Go 等
    - 典型场景：TypeScript 补全、Python 类型检查、Rust 分析
    - 示例：typescript-language-server、pylsp、rust-analyzer
    - 注意：需要用户安装对应的语言服务器二进制文件
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
  ccc:review-core              → 审阅领域核心组件
  ccc:advisor-core             → 顾问领域核心组件
  ccc:architecture-analyzer    → 架构分析组件
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
5. **需要集成外部服务吗？** → 是 → MCP Server（配置 .mcp.json）
6. **需要提供 IDE 级别的代码支持吗？** → 是 → LSP Server（配置 .lsp.json）

### MCP vs LSP 选择指南

| 需求 | 选择 | 配置文件 | 示例 |
|------|------|----------|------|
| 需要调用外部 API（GitHub、Slack） | MCP | .mcp.json | github MCP, slack MCP |
| 需要访问文件系统、数据库 | MCP | .mcp.json | filesystem MCP, postgres MCP |
| 需要代码补全、跳转定义 | LSP | .lsp.json | typescript-language-server |
| 需要类型检查、诊断 | LSP | .lsp.json | pylsp, rust-analyzer |
| 需要重命名、查找引用 | LSP | .lsp.json | gopls, clangd |

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

### MCP Server 配置检查

- [ ] MCP 配置文件位于插件根目录的 `.mcp.json`
- [ ] mcpServers 字段格式正确（name、command、args、env）
- [ ] 使用 http 传输（推荐），避免使用已弃用的 sse
- [ ] allowedEnvVars 声明了所有需要的环境变量
- [ ] README 文档说明了 MCP 配置和环境变量设置

### LSP Server 配置检查

- [ ] LSP 配置文件位于插件根目录的 `.lsp.json`
- [ ] lspServers 字段格式正确（command、args、languages）
- [ ] 指定了支持的编程语言（languages 字段）
- [ ] README 文档说明了 LSP 依赖的二进制文件安装
- [ ] 没有与 .mcp.json 混淆（分离关注点）

---

## 更新日志

- 2026-03-12: **Task 2.3** - 补充 MCP Servers 和 LSP Servers 组件类型到选型决策树
- 2026-03-11: 创建 std-component-selection Skill，定义 Skill 三种角色和选型决策树
