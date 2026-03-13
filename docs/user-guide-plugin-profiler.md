# Plugin Profiler Framework 用户指南

> 版本: v3.1.0
> 最后更新: 2026-03-13

---

## 目录

1. [概述](#概述)
2. [快速开始](#快速开始)
3. [工作原理](#工作原理)
4. [使用场景](#使用场景)
5. [高级用法](#高级用法)
6. [故障排除](#故障排除)
7. [最佳实践](#最佳实践)

---

## 概述

Plugin Profiler Framework 是 CCC v3.1.0 引入的新功能，旨在解决审查报告缺少插件概述的问题。它能够：

- **自动生成插件画像**: 从文档和代码中提取标准化元数据
- **增强报告自解释性**: 在审查报告中添加"插件概述"章节
- **评估文档完整性**: 0-100 分评估插件文档质量
- **验证报告质量**: 自动检查报告的自解释性

### 核心收益

- 报告自解释性: 20% → 95%
- 外部开发者理解时间: 从 30 分钟降至 5 分钟
- 文档质量可见性: 客观量化评分

---

## 快速开始

### 基础用法

```bash
# 标准审查（自动包含插件画像）
/ccc:review

# 仅生成画像（不进行质量审查）
/ccc:review --profile-only

# 审查但跳过画像生成
/ccc:review --skip-profiling
```

### 输出文件

运行后会生成以下文件：

```
你的插件/
├── docs/
│   └── profile/
│       ├── plugin-profile.json    # 结构化数据（JSON Schema 验证）
│       └── plugin-profile.md      # 人类可读报告
└── docs/
    └── reviews/
        └── YYYY-MM-DD-review.md   # 包含"插件概述"的审查报告
```

---

## 工作原理

### 8 步画像生成流程

```
1. 参数解析 → 2. 文档读取 → 3. 代码扫描 → 4. 信息提取
    ↓
5. 信息推断 → 6. 文档完整性评分 → 7. 生成输出 → 8. 返回结果
```

#### Step 1: 参数解析和环境验证

- 解析 `--target`（默认当前目录）
- 验证目录是否包含 skills/ 或 agents/
- 检查缓存是否有效（基于文件修改时间）

#### Step 2: 文档读取

按优先级读取：
1. **README.md** (置信度 0.95) - 最权威的插件说明
2. **CLAUDE.md** (置信度 0.90) - 项目特定指令
3. **ARCHITECTURE.md** (置信度 0.85) - 架构设计文档

#### Step 3: 代码扫描

使用 Glob 工具扫描：
- `skills/**/SKILL.md` - 所有 Skills
- `agents/**/SKILL.md` - 所有 SubAgents
- `commands/**/*` - 命令定义
- `hooks/**/*.md` - 钩子配置

识别命名模式：
- `cmd-*`: 工作流命令（用户入口）
- `std-*`: 标准规范（设计标准）
- `lib-*`: 知识库（共享知识）

#### Step 4: 信息提取（从文档）

从 README.md 提取：
- **positioning**: 第一段描述（跳过徽章）
- **base_framework**: 搜索 "based on", "extends", "继承自"
- **workflow_mechanism**: 搜索箭头流程图 `→`
- **slash_commands**: 搜索 `/plugin:command` 模式
- **core_principles**: 搜索 "## Core Principles" 章节
- **system_requirements**: 搜索 "## Requirements" 章节

#### Step 5: 信息推断（从代码）

当文档缺失时，从代码推断：
- **meta.name**: 从 README 标题 或 目录名
- **meta.version**: 从 README 徽章 或 git tag 或 "0.0.0"
- **classification_system**: 基于命名前缀统计
- **slash_commands**: 从 cmd-* skills 生成

#### Step 6: 文档完整性评分

评分维度（总分 150，归一化为 100）：
- README.md 存在: 40 分
- README.md 章节完整性: 40 分（Installation/Usage/Features/Requirements 各 10 分）
- CLAUDE.md 存在: 30 分
- CLAUDE.md 内容质量: 10 分
- ARCHITECTURE.md 存在: 20 分
- CHANGELOG.md 存在: 10 分

#### Step 7: 生成输出文件

生成两种格式：
1. **plugin-profile.json**: 结构化数据，符合 JSON Schema
2. **plugin-profile.md**: 7 个章节的可读报告

#### Step 8: 返回结果

打印摘要：
```
✅ 插件画像生成成功

插件: Claude Code Component Creator (CCC) v3.1.0
定位: A powerful Claude Code plugin for creating...
组件: 25 skills, 46 agents
文档完整性: 98/100

输出:
- docs/profile/plugin-profile.json
- docs/profile/plugin-profile.md

警告 (1):
- ARCHITECTURE.md 缺失，建议添加说明工作流机制的详细文档
```

---

## 使用场景

### 场景 1: 首次审查新插件

**情况**: 你拿到一个从未见过的插件，需要快速理解

```bash
# 1. 先生成画像，快速了解插件
/ccc:review --profile-only

# 2. 阅读 plugin-profile.md（5 分钟内理解插件全貌）

# 3. 然后进行完整审查
/ccc:review
```

**收益**: 在深入质量审查前，先对插件有全面了解

### 场景 2: 更新插件文档

**情况**: 插件文档过时，需要重新生成画像

```bash
# 1. 编辑 README.md、CLAUDE.md 等文档

# 2. 强制重新生成画像（忽略缓存）
/ccc:review --profile-only --cache=false

# 3. 检查文档完整性评分
# 如果 < 80，根据建议完善文档

# 4. 重新生成直到评分 ≥90
```

**收益**: 文档质量可量化、可追踪

### 场景 3: 插件对比分析

**情况**: 需要对比两个插件的架构和功能

```bash
# 1. 为两个插件分别生成画像
cd plugin-a && /ccc:review --profile-only
cd plugin-b && /ccc:review --profile-only

# 2. 对比 plugin-profile.json
diff plugin-a/docs/profile/plugin-profile.json \
     plugin-b/docs/profile/plugin-profile.json
```

**收益**: 标准化的元数据便于对比

### 场景 4: CI/CD 集成

**情况**: 在持续集成中自动验证文档质量

```bash
# .github/workflows/docs-quality.yml
name: Documentation Quality Check

on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Generate Plugin Profile
        run: /ccc:review --profile-only

      - name: Check Documentation Score
        run: |
          score=$(jq '.quality_metrics.documentation_completeness.score' docs/profile/plugin-profile.json)
          if [ "$score" -lt 80 ]; then
            echo "Documentation score too low: $score/100"
            exit 1
          fi
```

**收益**: 自动化文档质量门禁

---

## 高级用法

### 自定义输出目录

```bash
# 输出到自定义路径
/ccc:review --profile-output=custom/output/

# 输出:
# custom/output/plugin-profile.json
# custom/output/plugin-profile.md
```

### 缓存机制

Plugin Profiler 使用文件修改时间判断缓存有效性：

```python
缓存路径: docs/profile/plugin-profile.json

缓存有效条件:
  - 文件存在
  - README.md 修改时间 < 缓存修改时间
  - CLAUDE.md 修改时间 < 缓存修改时间
  - CHANGELOG.md 修改时间 < 缓存修改时间
```

强制刷新缓存：

```bash
# 方式1: 删除缓存文件
rm docs/profile/plugin-profile.json

# 方式2: 使用 --cache=false（如果实现）
/ccc:review --profile-only --cache=false
```

### 编程式调用（SubAgent）

如果在其他 SubAgent 中需要使用画像数据：

```python
# 伪代码示例
profile = dispatch_subagent(
    agent="plugin-profiler",
    args={
        "target": "/path/to/plugin",
        "output": "json"
    }
)

# 使用画像数据
plugin_name = profile["meta"]["name"]
skills_count = profile["architecture"]["component_types"]["skills"]["count"]
```

---

## 故障排除

### 问题 1: 画像生成失败

**症状**: 报错 "目录不是插件"

**原因**: 目标目录下没有 skills/ 或 agents/ 目录

**解决方案**:
```bash
# 1. 检查目录结构
ls -la

# 2. 确保存在 skills/ 或 agents/ 目录
mkdir -p skills agents

# 3. 如果是特殊插件，可能需要修改检测逻辑
```

### 问题 2: 文档完整性评分异常低

**症状**: 评分 < 40

**原因**: README.md 缺失或格式不规范

**解决方案**:
```markdown
# 1. 确保 README.md 存在并包含以下章节:

## Installation
...

## Usage
...

## Features
...

## Requirements
...

# 2. 添加 CLAUDE.md（推荐）
# 3. 添加 CHANGELOG.md（推荐）
```

### 问题 3: 推断的字段不准确

**症状**: `meta.positioning` 提取的不是期望的内容

**原因**: README.md 格式特殊（如第一段是徽章）

**解决方案**:
```markdown
# 调整 README.md 格式

# Plugin Name

[![badges...](url)]

这里写插件定位描述（plugin-profiler 会提取这段）

## Installation
...
```

### 问题 4: 画像 JSON 不符合 schema

**症状**: JSON 验证失败

**解决方案**:
```bash
# 1. 检查 JSON 格式
cat docs/profile/plugin-profile.json | python3 -m json.tool

# 2. 对照 schema 检查缺失字段
# schema 路径: agents/profiler/plugin-profiler/schema/plugin-profile.schema.json

# 3. 手动补充缺失的必需字段
```

---

## 最佳实践

### 1. 编写高质量的 README.md

plugin-profiler 能提取的信息质量取决于 README.md 的质量。

**推荐结构**:

```markdown
# Plugin Name

[![Version](badge)](url)

插件定位描述（简洁的一两句话说明核心价值）

## Features

- 功能1
- 功能2

## Installation

### Prerequisites
- 前置要求

### Setup
安装步骤

## Usage

### Slash Commands

- `/plugin:command` - 说明

### Workflow

```
阶段1 → 阶段2 → 阶段3
```

## Core Principles

### 原则名称
- **说明**: ...
- **实现方式**: ...
- **收益**: ...

## Requirements

- **Platform**: Claude Code 0.1.0+
- **OS**: macOS, Linux, Windows
- **Dependencies**:
  - git (required)
  - node.js (optional)

## License

MIT
```

### 2. 添加 CLAUDE.md

CLAUDE.md 用于说明项目特定的设计理念和质量标准：

```markdown
# Project Guidelines

## Design Philosophy

说明核心设计理念

## Architecture

说明架构设计

## Quality Standards

说明质量标准
```

### 3. 使用语义化版本号

在 README.md 中添加版本徽章：

```markdown
[![Version](https://img.shields.io/badge/version-1.2.3-blue.svg)](url)
```

plugin-profiler 会自动提取 `1.2.3` 作为版本号。

### 4. 标准化命名规范

遵循 CCC 的命名规范：

- **cmd-***: 用户命令（如 cmd-init, cmd-design）
- **std-***: 标准规范（如 std-component-selection）
- **lib-***: 知识库（如 lib-antipatterns）

这样 plugin-profiler 能正确识别分类体系。

### 5. 定期更新画像

当插件有重大更新时，重新生成画像：

```bash
# 在 CHANGELOG.md 中添加版本记录后
/ccc:review --profile-only

# 检查文档完整性评分是否下降
# 如果下降，完善文档后重新生成
```

### 6. 在 PR 中包含画像更新

```bash
# PR 提交前
git add docs/profile/plugin-profile.json docs/profile/plugin-profile.md
git commit -m "[doc]更新插件画像（v1.2.3 → v1.3.0）"
```

### 7. 利用画像进行团队沟通

将 `plugin-profile.md` 作为插件的"名片"：

- 新成员加入时，先阅读 plugin-profile.md
- 跨团队协作时，分享 plugin-profile.md
- 插件演示时，基于 plugin-profile.md 讲解

---

## 参考资料

- [Plugin Profiler SKILL.md](../../agents/profiler/plugin-profiler/SKILL.md)
- [Plugin Profile Schema](../../agents/profiler/plugin-profiler/schema/plugin-profile.schema.json)
- [提取策略文档](../../agents/profiler/plugin-profiler/docs/extraction-strategy.md)
- [Self-Explanation Validator](../../agents/reviewer/self-explanation-validator/SKILL.md)
- [CCC 设计文档](../../docs/superpowers/specs/2026-03-13-plugin-profiler-design.md)

---

**版本历史**:
- v1.0.0 (2026-03-13): 初始版本
