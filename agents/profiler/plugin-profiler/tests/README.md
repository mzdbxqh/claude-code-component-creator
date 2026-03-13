# Plugin Profiler 测试用例

本目录包含 plugin-profiler 的测试 fixtures。

## 目录结构

```
tests/
├── README.md                    # 本文件
└── fixtures/
    ├── minimal-plugin/          # 最小化插件示例
    │   ├── README.md
    │   └── skills/
    │       └── hello-world/
    │           └── SKILL.md
    │
    ├── full-featured-plugin/    # 完整功能插件示例
    │   ├── README.md
    │   ├── CLAUDE.md
    │   ├── skills/
    │   │   ├── cmd-plan/
    │   │   ├── cmd-execute/
    │   │   └── cmd-review/
    │   └── agents/
    │       └── executor/
    │           └── plan-executor/
    │
    └── expected-profiles/       # 期望画像结果
        ├── minimal.json
        └── full-featured.json
```

## 测试用例说明

### minimal-plugin

**目的**: 测试 plugin-profiler 的推断能力

**特点**:
- 仅有最基本的 README.md
- 单个 skill（未使用标准命名前缀）
- 无 CLAUDE.md、ARCHITECTURE.md
- 无工作流机制

**期望画像**:
- 正确推断插件名称（从 README 标题）
- 正确识别扁平化分类体系
- 正确推断版本号为 "0.0.0"（默认值）
- 文档完整性评分: 40/100（低分警告）

### full-featured-plugin

**目的**: 测试 plugin-profiler 的完整提取能力

**特点**:
- 完整的 README.md（包含所有推荐章节）
- 包含 CLAUDE.md（项目特定指令）
- 3 个 cmd-* skills
- 1 个 SubAgent
- 三阶段工作流机制
- 基于 Superpowers 5.0.2
- 核心设计理念说明

**期望画像**:
- 正确提取版本号 "1.2.3"（从 README 徽章）
- 正确识别基于 Superpowers 的关系
- 正确提取三阶段工作流（Plan → Execute → Review）
- 正确提取 3 个核心设计理念
- 正确提取系统要求（Claude Code 0.1.0+）
- 文档完整性评分: 80/100（良好）

## 测试执行方式

### 方式 1: 手动调用 SubAgent

```bash
# 测试 minimal-plugin
Task(
  agent="plugin-profiler",
  args={
    "target": "tests/fixtures/minimal-plugin",
    "output": "json",
    "cache": false
  }
)

# 比较输出与期望画像
diff <actual-output> tests/fixtures/expected-profiles/minimal.json
```

### 方式 2: 自动化测试脚本（待实现）

```bash
# 运行所有测试用例
./run-tests.sh

# 期望输出:
# ✓ minimal-plugin: 画像匹配
# ✓ full-featured-plugin: 画像匹配
# ✓ 所有测试通过
```

## 验证要点

### minimal-plugin 验证清单

- [ ] meta.name 正确提取（"minimal-test-plugin"）
- [ ] meta.version 推断为 "0.0.0"
- [ ] meta.positioning 从 README 第一段提取
- [ ] meta.base_framework 为 null
- [ ] architecture.component_types.skills.count = 1
- [ ] architecture.classification_system.primary = "flat"
- [ ] usage.slash_commands 从 README 提取（"/minimal:hello"）
- [ ] quality_metrics.documentation_completeness.score = 40
- [ ] extraction_metadata.warnings 包含文档缺失警告

### full-featured-plugin 验证清单

- [ ] meta.name 正确提取（"full-featured-test-plugin"）
- [ ] meta.version 从徽章提取（"1.2.3"）
- [ ] meta.base_framework.name = "Superpowers"
- [ ] meta.base_framework.version = "5.0.2"
- [ ] architecture.component_types.skills.count = 3
- [ ] architecture.component_types.agents.count = 1
- [ ] architecture.classification_system.primary = "role-based"
- [ ] architecture.workflow_mechanism.type = "three-stage"
- [ ] architecture.workflow_mechanism.stages 包含 3 个阶段
- [ ] usage.slash_commands 包含 3 个命令
- [ ] philosophy.core_principles 包含 3 个理念
- [ ] requirements.system.platform = "Claude Code"
- [ ] requirements.runtime_dependencies.required 包含 git
- [ ] quality_metrics.documentation_completeness.score = 80

## 常见问题

### Q: 为什么需要两个测试用例？

**A**:
- **minimal-plugin**: 测试推断逻辑（当文档不完整时）
- **full-featured-plugin**: 测试完整提取（当文档齐全时）

### Q: 如何添加新的测试用例？

**A**:
1. 在 `fixtures/` 下创建新插件目录
2. 编写 README.md 和 skills/agents
3. 在 `expected-profiles/` 下创建对应的 JSON 文件
4. 更新本 README 的验证清单

### Q: 期望画像如何生成？

**A**: 期望画像是手工编写的，基于：
1. 设计文档中的提取策略
2. 推断规则
3. Schema 定义

确保期望画像符合 `plugin-profile.schema.json`。

## 相关文档

- [Plugin Profile Schema](../schema/plugin-profile.schema.json)
- [提取策略文档](../docs/extraction-strategy.md)
- [推断规则文档](../docs/inference-rules.md)
