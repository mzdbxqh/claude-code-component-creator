# Claude Code Component Creator (CCC) 插件画像

> 生成时间: 2026-03-13T14:10:00Z
> 文档完整性评分: **98/100**

---

## 一、基本信息

- **名称**: claude-code-component-creator
- **显示名称**: Claude Code Component Creator (CCC)
- **版本**: 3.1.0
- **定位**: A powerful Claude Code plugin for creating high-quality components and skills with a structured Intent/Blueprint/Delivery workflow.
- **基础框架**: 独立插件（不基于任何框架）
- **仓库**: https://github.com/mzdbxqh/claude-code-component-creator
- **许可证**: MIT
- **作者**: mzdbxqh

---

## 二、核心功能

A powerful Claude Code plugin for creating high-quality components and skills with a structured Intent/Blueprint/Delivery workflow.

### 关键特性

- 三阶段工作流：Intent → Blueprint → Delivery 确保设计质量
- 77+ 反模式检查：8 维度全面质量审查
- 元反思框架：4 维度自我评估
- 双模型验证：Sonnet 生成，Haiku 验证
- 追溯矩阵：从需求到实现的完整追溯
- 外部状态管理：工作流状态存储在 YAML 文件中
- 并行处理支持：3.75x-6.8x 加速（v3.1.0 新增）
- Token 预算透明化：完整成本估算和优化指南（v3.1.0 新增）
- 检查点恢复：从中断点恢复长时间工作流（v3.1.0 新增）
- 性能基准测试：内置性能测试框架（v3.1.0 新增）

---

## 三、架构设计

### 3.1 组件分类体系

**分类方式**: 基于组件角色分类（role-based）

**说明**: 基于组件角色分类：cmd-(用户命令) / std-(标准规范) / lib-(知识库)

**设计理念**: 角色分类比技术分层更符合组件的实际用途，便于用户快速定位功能

### 3.2 组件统计

| 类型 | 数量 | 说明 |
|------|------|------|
| Skills | 25 | 19 cmd- + 4 std- + 2 lib- |
| Agents | 46 | 17 reviewer + 6 advisor + 1 profiler + 22 其他 |
| Commands | 0 | CCC 使用 Skills 代替 Commands |
| Hooks | 3 | SessionStart + PreToolUse |

#### Skills 分类详情

- **cmd-*** (19 个): 工作流命令 - 用户直接调用的斜杠命令
  - 示例: cmd-init, cmd-design, cmd-build, cmd-review, cmd-quick

- **std-*** (4 个): 标准规范 - 组件选型、命名、证据链等设计标准
  - 示例: std-component-selection, std-naming-rules, std-evidence-chain, std-workflow-attribution

- **lib-*** (2 个): 知识库 - 反模式库、设计模式库
  - 示例: lib-antipatterns, lib-design-patterns

### 3.3 工作流运行机制

**类型**: three-stage (三阶段工作流)

**工作流阶段**:
```
Intent → Blueprint → Delivery
```

详细说明:

1. **Intent** (`/cmd-init`)
   - 创建意图制品，使用 4 问题框架澄清需求
   - 输出: intent-*.yaml

2. **Blueprint** (`/cmd-design`)
   - 生成蓝图，5 阶段设计流程（需求→架构→设计→验证→规划）
   - 输出: blueprint-*.yaml

3. **Delivery** (`/cmd-build`)
   - 构建交付物，生成 SKILL.md、代码、测试和文档
   - 输出: delivery-*.yaml + 完整组件包

**激活方式**:

- **手动调用**: 用户通过斜杠命令手动调用工作流各阶段
  - 斜杠命令: /cmd-init, /cmd-design, /cmd-build, /cmd-review, /cmd-quick

- **自动激活**: SessionStart hook 自动加载
  - 触发条件: 检测到工作流状态文件（.ccc/artifacts/*.yaml）
  - 行为: 自动加载相关 Skills 和 SubAgents
  - 强制执行: 否（非强制工作流）

---

## 四、使用方式

### 4.1 斜杠命令

| 命令 | 对应 Skill | 说明 | 分类 |
|------|-----------|------|------|
| `/cmd-init` | cmd-init | 创建意图制品 | workflow |
| `/cmd-design` | cmd-design | 生成蓝图 | workflow |
| `/cmd-build` | cmd-build | 构建交付物 | workflow |
| `/cmd-implement` | cmd-implement | 实施迭代计划 | workflow |
| `/cmd-review` | cmd-review | 质量审查（76+ 检查项） | quality |
| `/cmd-quick` | cmd-quick | 快速完整工作流 | workflow |
| `/cmd-iterate` | cmd-iterate | 迭代蓝图 | workflow |
| `/cmd-design-iterate` | cmd-design-iterate | 迭代现有组件 | workflow |
| `/cmd-status` | cmd-status | 显示项目状态 | utility |
| `/cmd-trace` | cmd-trace | 生成追溯矩阵 | quality |
| `/cmd-validate` | cmd-validate | 外部工具验证 | quality |

### 4.2 自动激活的 Skills

| Skill | 触发场景 | 加载者 |
|-------|---------|--------|
| lib-antipatterns | 审查流程需要反模式检测 | cmd-review, review-core |
| lib-design-patterns | 设计流程需要模式参考 | cmd-design, blueprint-core |

---

## 五、核心设计理念

### 5.1 外部状态管理

- **说明**: 工作流状态存储在 YAML 文件而非会话中
- **实现方式**: .ccc/artifacts/ 目录下的 YAML 制品文件
- **收益**: 支持长时间工作流，状态可持久化和版本控制
- **设计理由**: 确保可中断、可恢复、可审计

### 5.2 完整追溯性

- **说明**: 从需求到实现的每一步都有清晰的追溯链
- **实现方式**: Intent → Blueprint → Delivery 的完整追溯矩阵
- **收益**: 质量可追溯，问题可定位
- **设计理由**: 确保需求不丢失，设计有依据

### 5.3 双模型验证

- **说明**: Sonnet 生成，Haiku 验证
- **实现方式**: 生成阶段使用 Sonnet，验证阶段使用 Haiku
- **收益**: 高质量输出 + 低成本验证
- **设计理由**: 平衡生成质量和验证成本

### 5.4 元反思框架

- **说明**: 4 维度自我评估（完整性、一致性、可测试性、可维护性）
- **实现方式**: Blueprint 阶段的 Meta-Reflection 检查
- **收益**: 设计时发现问题，而非实施后返工
- **设计理由**: 确保设计质量，减少返工

### 5.5 测试驱动开发

- **说明**: 测试先于实现
- **实现方式**: Delivery 阶段强制生成测试用例
- **收益**: 代码质量有保障，回归测试有基础
- **设计理由**: 确保代码可测试，需求可验证

### 5.6 YAGNI

- **说明**: 你不会需要它 - 只实现当前需要的功能
- **实现方式**: Intent 阶段明确排除不需要的功能
- **收益**: 代码简洁，维护成本低
- **设计理由**: 避免过度设计，降低复杂度

### 5.7 DRY

- **说明**: 不要重复自己 - 复用设计和代码
- **实现方式**: std- 和 lib- Skills 提供可复用的标准和知识
- **收益**: 统一标准，降低学习成本
- **设计理由**: 减少冗余，提升一致性

---

## 六、系统要求

- **平台**: Claude Code 0.1.0+
- **操作系统**: macOS, Linux, Windows (via WSL)

### 运行时依赖

**必需依赖**:
- git (any): 版本控制和提交管理

**可选依赖**:
- node.js (any): 某些高级功能

---

## 七、文档完整性评估

**评分**: 98/100

| 文档 | 状态 | 完整性 | 建议 |
|------|------|--------|------|
| README.md | ✓ 存在 | 100% | 优秀 |
| CLAUDE.md | ✓ 存在 | 100% | 优秀 |
| ARCHITECTURE.md | ✗ 缺失 | 0% | 建议添加架构文档说明工作流机制 |
| CHANGELOG.md | ✓ 存在 | 100% | 优秀 |
| CONFIGURATION.md | ✓ 存在 | 100% | 优秀 |
| SECURITY.md | ✓ 存在 | 100% | 优秀 |
| TROUBLESHOOTING.md | ✓ 存在 | 100% | 优秀 |

---

## 八、提取元数据

### 信息来源

- **README.md**: 已读取（置信度: 0.95）
- **CLAUDE.md**: 已读取（置信度: 0.90）
- **CHANGELOG.md**: 已读取（置信度: 0.95）
- **代码扫描**: 已完成（置信度: 1.0）

### 推断应用

- **字段**: architecture.classification_system
  - **方法**: 命名模式统计分析
  - **置信度**: 0.90
  - **理由**: cmd-* 占比 76% (19/25)，std- 和 lib- 存在

### 警告

- **级别**: info
  - **消息**: ARCHITECTURE.md 缺失，建议添加说明工作流机制的详细文档

---

**画像文件**: docs/profile/plugin-profile.json
