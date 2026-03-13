# 插件画像信息提取策略

本文档定义了 plugin-profiler 从文档和代码提取信息的详细策略。

## 一、提取优先级

### 信息源优先级

1. **README.md** (置信度: 0.95)
   - 最权威的插件说明文档
   - 优先提取: positioning, base_framework, workflow_mechanism, slash_commands

2. **CLAUDE.md** (置信度: 0.90)
   - 项目特定指令和理念
   - 优先提取: core_principles, special_instructions

3. **ARCHITECTURE.md** (置信度: 0.85)
   - 架构设计文档
   - 优先提取: workflow_mechanism, classification_system

4. **代码结构** (置信度: 1.0)
   - 最可靠的组件统计来源
   - 提取: component_types, classification_system (推断)

### 字段提取优先级

| 字段 | 优先提取源 | 备选提取源 | 推断规则 |
|------|-----------|-----------|---------|
| meta.name | README.md (标题) | 目录名 | 目录名 |
| meta.version | README.md (徽章) | git tag | "0.0.0" |
| meta.positioning | README.md (第一段) | - | 从目录名生成 |
| meta.base_framework | README.md (关键词搜索) | - | "independent" |
| architecture.component_types | 代码扫描 | - | - |
| architecture.classification_system | README.md + 代码验证 | 代码模式推断 | 基于前缀统计 |
| workflow_mechanism | README.md / ARCHITECTURE.md | - | null |
| usage.slash_commands | README.md | 代码推断 | 从 cmd-* skills 生成 |
| philosophy.core_principles | README.md / CLAUDE.md | - | null |
| requirements.system | README.md | 默认值 | Claude Code 0.1.0+ |

## 二、关键字段提取规则

### 2.1 meta.positioning（插件定位）

**提取策略**:
```
1. 定位 README.md 第一行标题（# 开头）
2. 提取标题后的第一段文本（非空行，非徽章）
3. 如果第一段是徽章行（包含 ![，则跳过取第二段
4. 截取前200字符作为定位描述

示例:
  输入:
    # Claude Code Component Creator (CCC)

    [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]

    A powerful Claude Code plugin for creating high-quality components with a structured workflow.

  输出:
    positioning = "A powerful Claude Code plugin for creating high-quality components with a structured workflow."
```

**推断规则**（README.md 不存在时）:
```
从目录名生成:
  目录名: "claude-code-component-creator"
  positioning = "Claude Code Component Creator plugin"
```

---

### 2.2 meta.base_framework（基础框架）

**提取策略**:
```
在 README.md 中搜索关键模式（不区分大小写）:

1. "based on <name>"
   示例: "This plugin is based on Superpowers 5.0.2"
   提取: {name: "Superpowers", version: "5.0.2", relationship: "extends"}

2. "extends <name>"
   示例: "Extends the official superpowers plugin"
   提取: {name: "superpowers", relationship: "extends"}

3. "built on top of <name>"
   示例: "Built on top of Superpowers framework"
   提取: {name: "Superpowers", relationship: "uses"}

4. "继承自 <name>" (中文)
   示例: "继承自 Superpowers 5.0.2"
   提取: {name: "Superpowers", version: "5.0.2", relationship: "extends"}

版本号提取:
  正则: r'(\d+\.\d+\.\d+)'
  示例: "based on Superpowers 5.0.2" → version = "5.0.2"
```

**推断规则**（未找到关键词时）:
```
base_framework = null
或
base_framework = {name: null, relationship: "independent"}
```

---

### 2.3 architecture.classification_system（分类体系）

**提取策略**:
```
1. 在 README.md 中搜索章节:
   - "## Skills 分类" / "## Skill Categories"
   - "## 组件分类" / "## Component Classification"

2. 提取分类说明:
   示例:
     ## Skills 分类
     本插件使用基于角色的分类体系：
     - cmd-*: 用户命令
     - std-*: 标准规范
     - lib-*: 知识库

   提取:
     classification_system = {
       primary: "role-based",
       description: "本插件使用基于角色的分类体系：cmd-(用户命令) / std-(标准规范) / lib-(知识库)",
       rationale: "角色分类比技术分层更符合组件的实际用途"
     }
```

**推断规则**（README.md 未说明时）:
```
基于代码扫描结果推断:

IF cmd- 占比 > 50% AND (std- 存在 OR lib- 存在) THEN
  primary = "role-based"
  description = "基于组件角色分类：cmd-(入口命令) / std-(标准规范) / lib-(知识库)"
  rationale = "从命名模式推断"

ELSE IF 存在模式 "frontend-*", "backend-*", "database-*" THEN
  primary = "technical-layered"
  description = "基于技术层次分类"
  rationale = "从命名模式推断"

ELSE THEN
  primary = "flat"
  description = "扁平化组织，无明显分类"
  rationale = "未发现明确的分类模式"
```

---

### 2.4 architecture.workflow_mechanism（工作流机制）

**提取策略**:
```
1. 在 README.md / ARCHITECTURE.md 中搜索工作流图示:
   模式1: 箭头流程图
     Intent → Blueprint → Delivery

   模式2: 列表描述
     ## Workflow
     1. Intent: Create intent artifact
     2. Blueprint: Generate blueprint
     3. Delivery: Build deliverable

2. 提取工作流阶段:
   - 阶段名称（Intent, Blueprint, Delivery）
   - 对应命令（/cmd-init, /cmd-design, /cmd-build）
   - 阶段描述

3. 提取激活方式:
   搜索关键词:
     - "SessionStart hook"
     - "automatic activation"
     - "slash commands"

   示例:
     "Commands can be triggered via slash commands like /cmd-init or automatically via SessionStart hook"

   提取:
     activation = {
       manual: {type: "slash_commands", commands: ["/cmd-init", ...]},
       automatic: {type: "SessionStart hook", trigger: "检测到工作流状态文件"}
     }
```

**推断规则**（README.md 未说明时）:
```
IF 存在 cmd-* skills THEN
  workflow_mechanism = {
    type: "command-based",
    activation: {
      manual: {type: "slash_commands", commands: 从 cmd-* 推断}
    }
  }
ELSE
  workflow_mechanism = null
```

---

### 2.5 usage.slash_commands（斜杠命令）

**提取策略**:
```
1. 在 README.md 中搜索斜杠命令模式:
   正则: r'/[a-z0-9:-]+'

   示例:
     "Use `/cmd-init` to create intent"
     "Run `/glaf4:brainstorm` for planning"

   提取:
     slash_commands = [
       {command: "/cmd-init", skill: "cmd-init", description: "create intent"},
       {command: "/glaf4:brainstorm", skill: "brainstorm", description: "for planning"}
     ]

2. 从 skills/ 目录验证命令存在性:
   FOR EACH extracted_command:
     skill_name = extract_skill_name(command)  # /cmd-init → cmd-init
     IF skill 文件存在:
       确认命令有效
     ELSE:
       记录警告: "命令 {command} 引用的 skill {skill_name} 不存在"
```

**推断规则**（README.md 未列出命令时）:
```
从 cmd-* skills 推断:
  FOR EACH skill IN Glob("skills/cmd-*/SKILL.md"):
    skill_name = extract_name(skill)  # skills/cmd-init/ → init
    command = f"/plugin:{skill_name}"  # /plugin:init

    # 读取 skill description
    description = extract_description_from_skill(skill)

    slash_commands.append({
      command: command,
      skill: skill_name,
      description: description
    })
```

---

### 2.6 philosophy.core_principles（核心理念）

**提取策略**:
```
1. 在 README.md / CLAUDE.md 中搜索章节:
   - "## Core Principles"
   - "## 核心理念"
   - "## Design Philosophy"
   - "## 设计哲学"

2. 提取列表项（- 开头或 1. 开头）:
   示例:
     ## Core Principles
     - **Test-Driven Development**: Write tests before implementation
     - **YAGNI**: You Aren't Gonna Need It
     - **DRY**: Don't Repeat Yourself

   提取:
     core_principles = [
       {
         principle: "Test-Driven Development",
         description: "Write tests before implementation"
       },
       {
         principle: "YAGNI",
         description: "You Aren't Gonna Need It"
       },
       ...
     ]

3. 如果章节包含段落说明，提取 rationale 和 benefit:
   示例:
     - **外部状态管理**: 工作流状态存储在 YAML 文件而非会话中。
       这样做的好处是可中断、可恢复、可审计。

   提取:
     {
       principle: "外部状态管理",
       description: "工作流状态存储在 YAML 文件而非会话中",
       benefit: "可中断、可恢复、可审计"
     }
```

**推断规则**（README.md 未说明时）:
```
core_principles = null
或
core_principles = []  # 空数组
```

---

### 2.7 requirements.system（系统要求）

**提取策略**:
```
1. 在 README.md 中搜索章节:
   - "## Requirements" / "## 系统要求"
   - "## Prerequisites" / "## 前置要求"
   - "## Installation" (内部可能包含要求)

2. 提取平台、版本、操作系统:
   示例:
     ## Prerequisites
     - **Claude Code**: Version 0.1.0 or higher
     - **Operating System**: macOS, Linux, or Windows (via WSL)
     - **Git**: For cloning and version control
     - **Node.js**: (Optional) For some advanced features

   提取:
     system = {
       platform: "Claude Code",
       min_version: "0.1.0",
       os: ["macOS", "Linux", "Windows (via WSL)"]
     }
     runtime_dependencies = {
       required: [
         {name: "git", version: "any", purpose: "cloning and version control"}
       ],
       optional: [
         {name: "node.js", version: "any", purpose: "some advanced features"}
       ]
     }
```

**推断规则**（README.md 未说明时）:
```
使用默认值:
  system = {
    platform: "Claude Code",
    min_version: "0.1.0",  # CCC 的最低要求
    os: ["macOS", "Linux", "Windows"]
  }

记录警告:
  "系统要求未在 README.md 中明确说明，使用默认值"
```

---

## 三、文档完整性评分规则

### 评分维度

1. **README.md 存在性** (40 分)
   - 存在: +40
   - 不存在: 0

2. **README.md 章节完整性** (40 分)
   - "Installation" / "安装": +10
   - "Usage" / "使用": +10
   - "Features" / "功能": +10
   - "Requirements" / "要求": +10

3. **CLAUDE.md 存在性** (30 分)
   - 存在: +30
   - 不存在: 0

4. **CLAUDE.md 内容质量** (10 分)
   - 包含项目特定指令: +10

5. **ARCHITECTURE.md 存在性** (20 分)
   - 存在: +20
   - 不存在: 0

6. **CHANGELOG.md 存在性** (10 分)
   - 存在: +10
   - 不存在: 0

### 评分示例

**示例 1: 完整文档**
```
文件:
  ✅ README.md (包含 Installation, Usage, Features, Requirements)
  ✅ CLAUDE.md (包含项目指令)
  ✅ ARCHITECTURE.md
  ✅ CHANGELOG.md

评分:
  README.md 存在: 40
  README.md 章节: 40 (10+10+10+10)
  CLAUDE.md 存在: 30
  CLAUDE.md 质量: 10
  ARCHITECTURE.md: 20
  CHANGELOG.md: 10

  总分: 150 → 归一化: 100 (满分)
```

**示例 2: 仅 README.md**
```
文件:
  ✅ README.md (包含 Installation, Usage, Features，缺 Requirements)
  ❌ CLAUDE.md
  ❌ ARCHITECTURE.md
  ❌ CHANGELOG.md

评分:
  README.md 存在: 40
  README.md 章节: 30 (10+10+10)
  CLAUDE.md: 0
  ARCHITECTURE.md: 0
  CHANGELOG.md: 0

  总分: 70 → 归一化: 70/150*100 = 46.7 ≈ 47
```

---

## 四、置信度评估

### 置信度计算规则

| 信息源 | 基础置信度 | 调整因子 |
|--------|-----------|---------|
| README.md 明确说明 | 0.95 | 无 |
| CLAUDE.md 明确说明 | 0.90 | 无 |
| ARCHITECTURE.md 明确说明 | 0.85 | 无 |
| 代码扫描（统计） | 1.0 | 无 |
| 代码推断（模式匹配） | 0.70 | 模式复杂度 |
| 目录名推断 | 0.50 | 无 |
| 默认值 | 0.30 | 无 |

### 调整因子示例

**代码推断置信度调整**:
```
基础置信度: 0.70

IF 模式非常明确（如 100% 的 skills 都是 cmd-*）THEN
  置信度 = 0.70 + 0.20 = 0.90

ELSE IF 模式模糊（如 cmd-* 占 51%）THEN
  置信度 = 0.70 - 0.10 = 0.60
```

---

## 五、常见问题处理

### Q1: README.md 格式不规范怎么办？

**情况**: README.md 第一段不是描述，而是目录或其他内容

**处理**:
```
策略1: 跳过非描述性段落
  - 跳过以 "Table of Contents" 开头的段落
  - 跳过纯链接段落
  - 取第一个包含实质内容的段落

策略2: 搜索 "## About" / "## 关于" 章节
  - 如果存在该章节，提取其内容作为 positioning

策略3: 降级到目录名推断
  - 记录警告: "README.md 格式不规范，无法提取 positioning"
```

### Q2: 插件没有 README.md 怎么办？

**处理**:
```
1. 记录严重警告:
   "README.md 缺失，无法充分理解插件定位和功能"

2. 启用纯代码推断模式:
   - meta.name: 从目录名
   - meta.version: 从 git tag 或 "0.0.0"
   - meta.positioning: "{name} plugin"
   - architecture.*: 全部从代码扫描
   - usage.slash_commands: 从 cmd-* skills 推断
   - philosophy.core_principles: null
   - requirements.system: 默认值

3. 文档完整性评分: 0-30 分（严重不足）

4. 在 extraction_metadata.warnings 中记录:
   [
     {
       level: "error",
       message: "README.md 缺失，强烈建议添加",
       recommendation: "创建 README.md 说明插件定位、功能和使用方式"
     }
   ]
```

### Q3: 组件命名不规范怎么办？

**情况**: skills 目录下既有 cmd-* 又有没有前缀的

**处理**:
```
1. 分别统计:
   cmd_skills: 15
   std_skills: 3
   lib_skills: 2
   other_skills: 5  # 没有前缀的

2. 在 classification_system 中标记混合模式:
   {
     primary: "mixed",
     description: "混合命名模式：部分使用角色前缀（cmd-/std-/lib-），部分未使用",
     rationale: "建议统一命名规范"
   }

3. 记录警告:
   "检测到混合命名模式，建议统一使用 cmd-/std-/lib- 前缀"
```

---

## 六、扩展字段提取（未来）

预留的扩展字段及其提取策略：

### 6.1 performance_characteristics

**提取来源**: PERFORMANCE.md 或 README.md "## Performance" 章节

**提取内容**:
```
{
  average_execution_time: "< 10s",
  token_usage: "5K-10K tokens per run",
  caching_support: true,
  parallel_execution: true
}
```

### 6.2 security_features

**提取来源**: SECURITY.md 或 README.md "## Security" 章节

**提取内容**:
```
{
  permission_model: "prompt-based",
  sensitive_data_handling: "never stored",
  audit_logging: true
}
```

---

## 七、总结

本文档定义了 plugin-profiler 的信息提取策略，包括：
1. 7 个关键字段的详细提取规则
2. 文档完整性评分算法
3. 置信度评估机制
4. 常见问题处理方案

**核心原则**:
- 多源结合：优先文档，代码验证
- 降级策略：文档缺失时启用推断
- 透明度：记录所有推断和警告
- 可扩展：预留扩展字段接口
