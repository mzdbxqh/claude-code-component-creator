---
name: ccc:cmd-design-new
model: sonnet
context: fork
disable-model-invocation: true
allowed-tools: [Read, Write, Edit, Glob, Grep]
description: "5阶段交互式设计新组件。触发：新建/创建组件，复杂设计。输出Blueprint。等同design的交互版。"
argument-hint: "[component-name] [--lang=zh-cn|en-us|ja-jp]"
---

# /ccc:design-new

**完整流程**: **design-new** → `review` → `fix` → `validate` → `build`

Design new component from scratch - 5-stage workflow (requirements→architecture→design→validation→planning) to create complete component design.

## 模型要求

- **推荐**: Claude Opus 4.5+ (最高质量,复杂架构设计)
- **可用**: Claude Sonnet 4.5+ (高效能,标准设计)
- **最小**: Claude Sonnet 4.5+ (最低要求)

### 功能需求
- 需要支持 Tool Use (Read, Write, Edit, Glob, Grep)
- 需要支持多轮对话和复杂推理
- 需要高级架构决策能力
- 建议上下文窗口 >= 200K tokens (处理完整设计流程和模式库)

## SubAgents 协作

本工作流使用以下 SubAgents 进行任务分解和执行：

### 核心 Agents
- **ccc:design-new-core**: 新设计核心，负责引导交互式设计流程和生成完整证据链

### 调度策略
- **串行执行**: cmd-design-new → ccc:design-new-core → 5 阶段设计流程
- **并行执行**: 无（设计阶段有依赖关系）
- **错误处理**: 任何阶段失败时允许用户返回上一阶段重新设计

### Agent 输入输出
| Agent | 输入 | 输出 |
|-------|------|------|
| ccc:design-new-core | 用户交互输入 + lang 参数 | 设计文档 + Blueprint 制品 |

### 调用示例
```
用户: /ccc:design-new
  ↓
cmd-design-new 启动交互式流程
  ↓
调用 ccc:design-new-core (5 阶段设计):
  Phase 1: 需求分析 (交互式提问)
  Phase 2: 架构设计 (组件选型)
  Phase 3: 详细设计 (工作流定义)
  Phase 4: 验证 (证据链生成)
  Phase 5: 规划 (实施步骤)
  ↓
cmd-design-new 生成设计文档和 Blueprint 制品
```

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

## Workflow

### 输入要求
- **必需参数**: 无（交互式引导设计）
- **可选参数**: `--lang=zh-cn|en-us|ja-jp` 输出语言（默认 zh-cn）
- **前置条件**: 无特殊前置条件，适合从零开始设计新组件

### 执行步骤

**Step 1: 交互式需求收集**
- 引导用户描述组件需求
- 通过交互式问答收集关键信息
- 识别组件类型（Command、Skill、Subagent、Workflow）
- 确定核心功能和目标
- **错误处理**: 用户取消输入时保存已收集信息并退出；输入不完整时继续追问直到获取足够信息

**Step 2: 需求分析（阶段 1）**
- 分解功能需求和非功能需求
- 识别硬约束和软约束
- 确定优先级和范围
- 评估复杂度等级（simple、moderate、complex）
- **错误处理**: 需求冲突时提示用户澄清；需求过于复杂时建议拆分为多个组件

**Step 3: 架构设计（阶段 2）**
- 确定组件架构模式
- 选择合适的工具组合
- 设计组件间协作关系（如需要多个组件）
- 评估性能和扩展性需求
- **错误处理**: 架构选择冲突时提供多个方案供用户选择；工具组合不合理时自动优化

**Step 4: 详细设计（阶段 3）**
- 设计工作流步骤（详细的执行流程）
- 定义输入输出规范
- 设计错误处理策略
- 配置工具权限和资源限制
- 生成完整证据链（能力需求表、Skill 映射、验证清单）
- **错误处理**: 工作流过于复杂时建议简化；证据链不完整时标记并继续

**Step 5: 验证结果（阶段 4）**
- 验证需求覆盖完整性
- 检查架构合理性
- 评估设计质量（0-100 评分）
- 识别潜在问题和风险
- **错误处理**: 验证失败时返回相应阶段重新设计；质量过低（<60）时建议重新设计

**Step 6: 生成制品和报告（阶段 5）**
- 生成 Blueprint YAML 制品
- 创建完整设计文档（包含 5 个阶段的详细结果）
- 制定实施计划和里程碑
- 保存所有制品到对应目录
- **错误处理**: 制品生成失败时显示错误并保留设计数据；目录不存在时自动创建

### 预期输出
- **主要制品**:
  - `docs/ccc/blueprint/YYYY-MM-DD-<artifact-id>.yaml` Blueprint 制品
  - `docs/designs/YYYY-MM-DD-<component-name>-design-new.md` 完整设计文档
- **设计文档结构**:
  - 阶段 1: 需求分析（功能需求、非功能需求、约束）
  - 阶段 2: 架构设计（组件架构、工具选择、协作关系）
  - 阶段 3: 详细设计（工作流步骤、I/O 规范、错误处理、完整证据链）
  - 阶段 4: 验证结果（需求覆盖检查、架构评估、质量评分）
  - 阶段 5: 实施规划（开发步骤、测试策略、交付计划）
- **控制台输出**: 各阶段完成提示、关键决策摘要、Blueprint ID、质量评分

### 错误处理
- **用户中断输入** → 保存已收集的设计信息，提供恢复命令
- **需求冲突** → 暂停并提示用户澄清，提供选项供选择
- **架构验证失败** → 返回架构设计阶段，提供改进建议
- **质量评分过低** → 显示问题清单，建议重新设计或简化需求
- **文件生成失败** → 保留设计数据，提供备用保存路径
- **通用错误** → 保存各阶段的设计结果，提供从失败点继续的命令

---

## Global Parameter

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--lang` | `zh-cn`, `en-us`, `ja-jp` | `zh-cn` | 输出语言 (Output language) |

## 使用示例 (Examples)

### Example 1: 简单命令设计

```bash
/design-new
```

**输入**: 交互式提示引导，例如设计一个简单的代码格式化命令

**输出**: 完整的5阶段设计文档：
- 阶段1：需求分析（格式化 Python/JavaScript 代码）
- 阶段2：架构设计（Command 组件，调用外部格式化工具）
- 阶段3：详细设计（参数定义、工具选择、错误处理）
- 阶段4：验证结果（需求覆盖检查、架构合理性评估）
- 阶段5：实施规划（开发步骤、测试策略、交付计划）
- Blueprint artifact: `docs/ccc/blueprint/YYYY-MM-DD-BLP-XXX.yaml`

### Example 2: 复杂 Subagent 设计

```bash
/design-new --lang=en-us
```

**输入**: 英文交互流程，设计一个 API 测试自动化 Subagent

**输出**: 英文完整设计方案：
- Requirements: API testing capabilities, report generation, integration with CI/CD
- Architecture: Subagent with forked context, tools (Bash, Read, Write, Grep)
- Design: Test discovery, execution workflow, result aggregation
- Validation: Architecture compliance checklist, tool permission verification
- Planning: Multi-phase implementation with milestones
- Complete evidence chain: capability requirements table, Skill mapping, validation checklist
- Blueprint artifact with full specifications

### Example 3: 端到端工作流设计

```bash
/design-new
```

**输入**: 设计一个完整的数据迁移工作流（包含多个 Skill 和 Subagent）

**输出**: 复杂工作流的完整设计：
- 阶段1：需求分解（数据抽取、转换、加载、验证）
- 阶段2：多组件架构（Coordinator Command + 3个 Subagent：Extractor、Transformer、Loader）
- 阶段3：详细设计（每个组件的职责、接口、数据流、错误处理策略）
- 阶段4：工作流验证（依赖关系检查、并行机会识别、工具权限审核）
- 阶段5：分阶段实施计划（第一阶段核心流程、第二阶段错误处理、第三阶段性能优化）
- 完整证据链（20+ 条能力需求、Skill 映射表、验证清单）
- Blueprint artifact 包含完整工作流定义和组件规格
