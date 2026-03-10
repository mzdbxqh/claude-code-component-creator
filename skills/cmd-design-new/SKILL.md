---
name: ccc:cmd-design-new
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
