---
name: cmd-design-iterate
model: sonnet
context: fork
disable-model-invocation: true
allowed-tools: [Read, Write, Edit, Glob, Grep]
description: "迭代流程第1步。分析现有组件差异，生成增量改进方案。触发：重构/升级/优化。输出迭代计划给implement。"
argument-hint: "<component-path> [--lang=zh-cn|en-us|ja-jp]"
---

# /cmd-design-iterate

**迭代流程**: 现有代码 → **design-iterate** → `implement` → `review` → `fix`

Iterate on existing components - analyze current vs target state, generate incremental change proposals.

## 模型要求

- **推荐**: Claude Sonnet 4.5+ (高效能,最佳性价比)
- **可用**: Claude Opus 4.5+ (最高质量,复杂重构设计)
- **最小**: Claude Sonnet 4.5+ (最低要求)

### 功能需求
- 需要支持 Tool Use (Read, Write, Edit, Glob, Grep)
- 需要支持多轮对话和复杂分析
- 需要处理差异分析和增量方案设计
- 建议上下文窗口 >= 200K tokens (处理完整组件分析)

## SubAgents 协作

本工作流使用以下 SubAgents 进行任务分解和执行：

### 核心 Agents
- **ccc:design-iterate-core**: 迭代设计核心，负责差异分析和增量方案生成

### 调度策略
- **串行执行**: cmd-design-iterate → ccc:design-iterate-core → 差异分析 → 增量方案设计
- **并行执行**: 无（分析和设计有依赖关系）
- **错误处理**: 组件文件不存在时提示用户确认路径

### Agent 输入输出
| Agent | 输入 | 输出 |
|-------|------|------|
| ccc:design-iterate-core | 现有组件路径 + 改进目标 | 迭代设计文档 + 增量实施计划 |

### 调用示例
```
用户: /cmd-design-iterate commands/deploy.md
  ↓
cmd-design-iterate 读取现有组件
  ↓
调用 ccc:design-iterate-core (差异分析和方案设计):
  Step 1: 加载现有组件
  Step 2: 分析当前状态 vs 目标状态
  Step 3: 识别改进点和影响范围
  Step 4: 设计增量变更方案（分阶段）
  Step 5: 生成变更证据链
  ↓
cmd-design-iterate 生成迭代设计文档
```

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

## Workflow

### 输入要求
- **必需参数**: `<component-path>` 现有组件文件路径
- **可选参数**: `--lang=zh-cn|en-us|ja-jp` 输出语言（默认 zh-cn）
- **前置条件**:
  - 目标组件文件必须存在（Skill、Subagent、Command 等）
  - 需要明确改进目标或当前组件存在的问题

### 执行步骤

**Step 1: 加载现有组件**
- 读取指定路径的组件文件
- 解析组件结构（frontmatter、workflow、配置等）
- 提取当前能力和设计要素
- **错误处理**: 文件不存在时提示检查路径；文件格式无效时显示解析错误位置

**Step 2: 分析差异和问题**
- 对比组件当前状态与设计标准
- 识别架构不符合项（如三角色系统）
- 检测性能瓶颈和优化机会
- 分析依赖关系和工具配置
- **错误处理**: 分析超时时使用已收集数据继续；无差异时报告"组件已达最优"并退出

**Step 3: 生成增量方案**
- 设计最小化变更路径
- 创建分阶段迭代计划（如分为第一阶段重构、第二阶段优化）
- 评估每个变更的影响范围
- 制定回滚策略
- **错误处理**: 变更方案过于复杂时自动拆分为多个阶段

**Step 4: 构建变更证据链**
- 记录每个变更的能力需求来源
- 标记受影响的相关 skills
- 记录变更原因和业务价值
- 建立可追溯性链条
- **错误处理**: 证据链缺失时标记为"需补充"并继续生成

**Step 5: 生成迭代设计文档**
- 编写差异分析章节
- 输出影响评估报告
- 制定增量方案文档
- 保存完整变更证据链
- **错误处理**: 文件写入失败时显示具体错误并提供备用路径

### 预期输出
- **主要制品**: `docs/designs/YYYY-MM-DD-<component-name>-iteration.md`
- **文档结构**:
  - 差异分析（当前状态 vs 目标状态）
  - 影响评估（变更范围、风险级别）
  - 增量方案（分阶段执行计划）
  - 变更证据链（能力需求表、Skill 映射、变更理由）
- **辅助信息**: 控制台显示关键差异摘要和优先级建议

### 错误处理
- **组件文件不存在** → 提示用户检查路径或使用 `/cmd-design-new` 创建新组件
- **无改进空间** → 报告"组件已达最优状态，无需迭代"并显示当前质量评分
- **分析失败** → 显示具体错误并建议简化组件或分解为多个小组件
- **输出路径冲突** → 使用时间戳确保唯一性或询问是否覆盖现有文件
- **通用错误** → 保存已分析的内容到临时文件，提供恢复命令

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
