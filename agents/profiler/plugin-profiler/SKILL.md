---
name: plugin-profiler
description: "生成插件标准化画像，提取元信息、架构、使用方式和核心理念。触发：插件画像/plugin profile/profiler"
model: sonnet
context: fork
tools:
  - Read
  - Glob
  - Grep
permissionMode: prompt
skills:
  - ccc:std-component-selection
  - ccc:std-naming-rules
argument-hint: "--target=<plugin_root> [--output=json|markdown|both] [--cache=true|false]"
---

# Plugin Profiler

## 功能

从插件根目录提取完整画像,生成标准化的 plugin-profile.json 和 plugin-profile.md。

**输入**:
- 插件根目录路径
- README.md / CLAUDE.md / ARCHITECTURE.md(如存在)
- 代码结构(skills/, agents/, commands/, hooks/)

**输出**:
- `plugin-profile.json`: 符合 schema 的结构化数据
- `plugin-profile.md`: 人类可读的画像报告
- 文档完整性评分 (0-100)

**职责边界**:
- ✅ 负责: 提取元信息、统计组件、推断架构
- ❌ 不负责: 质量评估、反模式检测(由 review-core 负责)

## 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| --target | 路径 | 当前目录 | 插件根目录(包含 skills/, agents/ 等) |
| --output | 枚举 | both | 输出格式: json, markdown, both |
| --cache | 布尔 | true | 是否使用缓存(基于文件修改时间) |
| --output-dir | 路径 | docs/profile/ | 输出目录 |

## 工作流

### Step 1: 参数解析和环境验证

**目标**: 解析参数、验证插件根目录、检查缓存

**操作**:
1. 解析 --target 参数(默认当前目录)
2. 验证目录存在且包含 skills/ 或 agents/
3. 检查缓存是否存在且有效
   ```
   缓存路径: {target}/docs/profile/plugin-profile.json
   缓存有效条件:
     - 文件存在
     - README.md 修改时间 < 缓存修改时间
     - CLAUDE.md 修改时间 < 缓存修改时间
   ```
4. 如果缓存有效且 --cache=true,加载缓存并跳到 Step 5

**输出**: 目标目录路径、是否使用缓存

**错误处理**:
- 目录不存在 → 退出并提示错误
- 目录不是插件(无 skills/ 和 agents/) → 警告并继续

---

### Step 2: 文档读取

**目标**: 读取 README.md, CLAUDE.md, ARCHITECTURE.md

**操作**:
1. 尝试读取 README.md
   - 成功: 记录到 sources.README.md = {read: true, confidence: 0.95}
   - 失败: 记录警告 "README.md 不存在,将从代码推断"

2. 尝试读取 CLAUDE.md
   - 成功: 记录到 sources.CLAUDE.md = {read: true, confidence: 0.90}
   - 失败: 记录 sources.CLAUDE.md = {read: false}

3. 尝试读取 ARCHITECTURE.md
   - 成功: 记录到 sources.ARCHITECTURE.md = {read: true, confidence: 0.85}
   - 失败: 记录 sources.ARCHITECTURE.md = {read: false}

**输出**:
- readme_content (或 null)
- claude_md_content (或 null)
- architecture_md_content (或 null)
- sources 字典

**错误处理**: 文档读取失败不影响流程,继续从代码推断

---

### Step 3: 代码扫描

**目标**: 扫描插件目录结构,统计组件数量和类型

**操作**:
1. 扫描 skills/ 目录
   - 使用 Glob("skills/**/SKILL.md") 查找所有 SKILL.md 文件
   - 统计总数
   - 按命名前缀分类:
     - cmd-*: 工作流命令 skills
     - std-*: 标准规范 skills
     - lib-*: 知识库 skills
     - 其他: 未分类 skills

2. 扫描 agents/ 目录
   - 使用 Glob("agents/**/SKILL.md") 查找所有 SubAgent SKILL.md 文件
   - 统计数量
   - 识别分类(基于目录名):
     - 例如: agents/reviewer/review-core/ → category: reviewer
     - 提取目录层级: agents/<category>/<name>/
     - 按 category 分组统计

3. 扫描 commands/ 和 hooks/ 目录(可选)
   - 使用 Glob("commands/**/*") 统计 commands 数量
   - 使用 Glob("hooks/**/*.md") 统计 hooks 数量

**输出**:
- component_types 字典(skills, agents, commands, hooks 的统计)
- skills_categories 列表(cmd-, std-, lib- 分类详情)
- agents_categories 列表(按目录分类)

**错误处理**: Glob 失败时返回空列表,继续流程

---

### Step 4: 信息提取(从文档)

**目标**: 从 README.md 和 CLAUDE.md 提取关键字段

**操作**:
1. **提取 meta.positioning**(插件定位)
   ```
   策略:
     1. 从 README.md 第一段提取(# 标题后的第一段描述)
     2. 如果第一段是徽章,取第二段
     3. 如果没有 README,从目录名推断: "<name> plugin"

   示例:
     README.md:
       # Claude Code Component Creator (CCC)

       A powerful Claude Code plugin for creating high-quality components...

     提取结果:
       positioning = "A powerful Claude Code plugin for creating high-quality components"
   ```

2. **提取 meta.base_framework**(基础框架)
   ```
   策略:
     1. 在 README.md 中搜索关键词:
        - "based on <name>"
        - "extends <name>"
        - "继承自 <name>"
        - "built on top of <name>"
     2. 如果找到,提取框架名称和关系
     3. 如果没找到,标记为 "independent"

   示例:
     README.md:
       "This plugin is based on Superpowers 5.0.2"

     提取结果:
       base_framework = {
         name: "superpowers",
         version: "5.0.2",
         relationship: "extends"
       }
   ```

3. **提取 architecture.classification_system**(分类体系)
   ```
   策略:
     1. 在 README.md 中搜索 "Skills 分类" / "组件分类"
     2. 识别分类方式(角色 vs 技术层次)
     3. 从代码扫描结果验证(cmd-/std-/lib- 前缀比例)

   示例:
     如果 cmd- 占比 > 50% → 分类方式: "role-based"
     如果有 "Architecture Skills", "Design Skills" → 分类方式: "technical-layered"
   ```

4. **提取 architecture.workflow_mechanism**(工作流机制)
   ```
   策略:
     1. 在 README.md 中搜索关键词:
        - "workflow" / "工作流"
        - "SessionStart" / "hook"
        - "→" (箭头符号,表示流程)
     2. 提取工作流阶段描述

   示例:
     README.md:
       ```
       Intent → Blueprint → Delivery
       ```

     提取结果:
       workflow_mechanism = {
         type: "three-stage",
         stages: [
           {name: "Intent", ...},
           {name: "Blueprint", ...},
           {name: "Delivery", ...}
         ]
       }
   ```

5. **提取 usage.slash_commands**(斜杠命令)
   ```
   策略:
     1. 在 README.md 中搜索 "/" 开头的命令
     2. 匹配模式: `/plugin:command` 或 `/command`
     3. 从 skills/ 目录验证命令存在性

   示例:
     README.md:
       "Use `/cmd-init` to create intent"

     提取结果:
       slash_commands = [
         {command: "/cmd-init", skill: "cmd-init", ...}
       ]
   ```

6. **提取 philosophy.core_principles**(核心理念)
   ```
   策略:
     1. 在 README.md / CLAUDE.md 中搜索:
        - "## Core Principles" / "## 核心理念"
        - "## Philosophy" / "## 设计哲学"
     2. 提取列表项(- 开头)

   示例:
     README.md:
       ## Core Principles
       - Test-Driven Development
       - YAGNI

     提取结果:
       core_principles = [
         {principle: "Test-Driven Development", ...},
         {principle: "YAGNI", ...}
       ]
   ```

7. **提取 requirements.system**(系统要求)
   ```
   策略:
     1. 在 README.md 中搜索:
        - "## Requirements" / "## 系统要求"
        - "Prerequisites"
     2. 提取平台、版本、操作系统

   示例:
     README.md:
       - Platform: Claude Code 0.1.0+
       - OS: macOS, Linux, Windows (via WSL)

     提取结果:
       system = {
         platform: "Claude Code",
         min_version: "0.1.0",
         os: ["macOS", "Linux", "Windows (via WSL)"]
       }
   ```

**输出**: 填充的 profile 字典(部分字段)

**错误处理**: 提取失败的字段标记为 null,记录到 warnings

---

### Step 5: 信息推断(从代码)

**目标**: 对文档缺失的字段从代码推断

**操作**:
1. **推断 meta.name**
   ```
   IF README.md 存在 THEN
     从 README.md 第一行 # 标题提取
   ELSE
     从目录名推断
   ```

2. **推断 meta.version**
   ```
   策略优先级:
     1. 从 README.md 徽章提取 (![Version](badge-3.1.0))
     2. 从 git tag 提取 (git describe --tags)
     3. 默认: "0.0.0"
   ```

3. **推断 architecture.classification_system**
   ```
   基于 skills_categories 统计:
     IF cmd- 占比 > 50% AND std- 存在 THEN
       primary = "role-based"
       description = "基于组件角色分类:cmd-(用户命令) / std-(标准规范) / lib-(知识库)"
     ELSE IF 存在 "frontend-*", "backend-*" 模式 THEN
       primary = "technical-layered"
       description = "基于技术层次分类"
     ELSE
       primary = "flat"
       description = "扁平化组织"
   ```

4. **推断 usage.slash_commands**
   ```
   从 skills/ 目录名推断:
     FOR EACH skill IN cmd-* skills:
       skill_name = extract_name(skill)  # cmd-init → init
       command = f"/plugin:{skill_name}"
       slash_commands.append({command, skill: skill, ...})
   ```

**输出**: 完整的 profile 字典

**记录**: 所有推断的字段记录到 extraction_metadata.inference_applied

---

### Step 6: 文档完整性评分

**目标**: 评估插件文档的完整性(0-100 分)

**操作**:
1. 检查 README.md
   ```
   score = 0
   IF README.md 存在:
     score += 40
     IF 包含 "Installation" 章节: score += 10
     IF 包含 "Usage" 章节: score += 10
     IF 包含 "Features" 章节: score += 10
     IF 包含 "Requirements" 章节: score += 10
   ELSE:
     score += 0
     warnings.append("README.md 缺失(严重影响理解)")
   ```

2. 检查 CLAUDE.md
   ```
   IF CLAUDE.md 存在:
     score += 30
     IF 包含项目特定指令: score += 10
   ELSE:
     score += 0
     warnings.append("CLAUDE.md 缺失(推荐添加)")
   ```

3. 检查 ARCHITECTURE.md
   ```
   IF ARCHITECTURE.md 存在:
     score += 20
   ELSE:
     score += 0
     warnings.append("ARCHITECTURE.md 缺失(建议添加说明工作流机制)")
   ```

4. 检查 CHANGELOG.md
   ```
   IF CHANGELOG.md 存在:
     score += 10
   ```

**输出**: documentation_completeness.score (0-100)

---

### Step 7: 生成输出文件

**目标**: 生成 plugin-profile.json 和 plugin-profile.md

**操作**:
1. 生成 JSON
   ```python
   profile_json = {
     "meta": {
       "name": extracted_name,
       "version": extracted_version,
       "positioning": extracted_positioning,
       "base_framework": extracted_base_framework,
       ...
     },
     "architecture": {
       "component_types": {
         "skills": {
           "count": skills_count,
           "categories": skills_categories
         },
         "agents": {...},
         ...
       },
       "classification_system": inferred_classification,
       "workflow_mechanism": extracted_workflow
     },
     "usage": {
       "slash_commands": extracted_commands,
       "auto_activation_skills": extracted_auto_activation
     },
     "philosophy": {
       "core_principles": extracted_principles
     },
     "requirements": {
       "system": extracted_system_requirements,
       ...
     },
     "quality_metrics": {
       "documentation_completeness": {
         "score": doc_score,
         "breakdown": {
           "README.md": {exists: true, completeness: 100},
           "CLAUDE.md": {exists: false, recommendation: "建议添加"},
           ...
         }
       }
     },
     "extraction_metadata": {
       "sources": sources,
       "inference_applied": inference_log,
       "warnings": warnings
     }
   }

   # 写入文件
   output_path = f"{target}/docs/profile/plugin-profile.json"
   mkdir -p $(dirname output_path)
   write_file(output_path, json.dumps(profile_json, indent=2))
   ```

2. 生成 Markdown(可选)
   ```markdown
   # {meta.display_name} 插件画像

   > 生成时间: {timestamp}
   > 文档完整性评分: {doc_score}/100

   ## 基本信息
   - **名称**: {meta.name}
   - **版本**: {meta.version}
   - **定位**: {meta.positioning}
   - **基础框架**: {meta.base_framework.name} {meta.base_framework.version}

   ## 架构设计
   ### 组件统计
   - Skills: {skills.count} 个
   - Agents: {agents.count} 个

   ### 分类体系
   {classification_system.description}

   ...(其他章节)
   ```

**输出**:
- `{target}/docs/profile/plugin-profile.json`
- `{target}/docs/profile/plugin-profile.md` (如果 --output=markdown 或 both)

---

### Step 7.5: Schema 验证（可选）

**目标**: 验证生成的 JSON 符合 plugin-profile.schema.json

**操作**:
1. 加载 schema/plugin-profile.schema.json
2. 使用 JSON Schema 验证器验证 profile_json
3. 如果验证失败:
   - 记录警告到 warnings
   - 标记为"降级模式"
   - 继续生成输出(不中断流程)

**输出**: 验证结果(通过/警告/降级模式)

**错误处理**: 验证失败不影响输出,仅记录警告

---

### Step 8: 返回结果

**目标**: 返回画像数据和元信息

**操作**:
1. 打印摘要
   ```
   ✅ 插件画像生成成功

   插件: {meta.display_name} v{meta.version}
   定位: {meta.positioning}
   组件: {skills.count} skills, {agents.count} agents
   文档完整性: {doc_score}/100

   输出:
   - {output_path}/plugin-profile.json
   - {output_path}/plugin-profile.md

   警告 ({len(warnings)}):
   {warnings}
   ```

2. 返回数据结构
   ```python
   return {
     "profile": profile_json,
     "doc_score": doc_score,
     "warnings": warnings,
     "output_files": [json_path, md_path]
   }
   ```

**错误处理**: 如果关键字段缺失(meta.name, meta.version),返回错误状态

---

## 高级场景示例

### 场景1: 多层级插件分析

**使用场景**: 分析包含嵌套插件或子模块的复杂项目

**示例**:
```bash
# 项目结构
complex-plugin/
├── core/                    # 核心插件
│   ├── skills/
│   ├── agents/
│   └── .claude-plugin/
├── extensions/              # 扩展插件
│   ├── ui-extension/
│   │   ├── skills/
│   │   └── .claude-plugin/
│   └── api-extension/
│       ├── skills/
│       └── .claude-plugin/
└── shared/                  # 共享库
    └── lib-*/ skills

# 分析主插件
Task(
  agent="plugin-profiler",
  args={
    "target": "complex-plugin/core",
    "output": "both"
  }
)

# 分析扩展插件
Task(
  agent="plugin-profiler",
  args={
    "target": "complex-plugin/extensions/ui-extension",
    "output": "both"
  }
)

# 关键点
- 主插件的 base_framework 为 null (独立)
- 扩展插件的 base_framework 指向主插件
- 共享库会被多个插件的 plugin_dependencies.requires 引用
```

**预期输出**:
```json
{
  "meta": {
    "name": "ui-extension",
    "base_framework": {
      "name": "complex-plugin-core",
      "version": "2.1.0",
      "relationship": "extends"
    }
  },
  "requirements": {
    "plugin_dependencies": {
      "extends": ["complex-plugin-core"],
      "requires": ["shared-lib-common"],
      "conflicts": []
    }
  }
}
```

---

### 场景2: 大型项目性能优化

**使用场景**: 1000+ 文件的大型插件项目，初次扫描耗时长

**示例**:
```bash
# 第一次扫描（完整扫描）
Task(
  agent="plugin-profiler",
  args={
    "target": "large-plugin",
    "output": "both",
    "cache": true
  }
)
# 预计耗时: 2-3 分钟

# 后续增量扫描（使用缓存）
Task(
  agent="plugin-profiler",
  args={
    "target": "large-plugin",
    "output": "both",
    "cache": true
  }
)
# 预计耗时: <5 秒（缓存命中）

# 关键点
- 缓存基于文件修改时间判断有效性
- 只有 README.md、CLAUDE.md 修改时才失效
- 代码结构变更不影响缓存（需要手动 --cache=false 刷新）

# 强制刷新
Task(
  agent="plugin-profiler",
  args={
    "target": "large-plugin",
    "cache": false
  }
)
```

**优化建议**:
- 对于大型项目，初次扫描后保持缓存开启
- 仅在添加/删除组件后手动刷新缓存
- 使用 --output=json 减少 Markdown 生成开销

---

### 场景3: CI/CD 集成

**使用场景**: 在持续集成流程中自动生成插件画像

**示例**:
```yaml
# .github/workflows/profile-update.yml
name: Update Plugin Profile

on:
  push:
    branches: [main]
    paths:
      - 'skills/**'
      - 'agents/**'
      - 'README.md'
      - 'CLAUDE.md'

jobs:
  update-profile:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Generate Plugin Profile
        run: |
          claude-code execute plugin-profiler \
            --target=. \
            --output=both \
            --cache=false

      - name: Commit Profile
        run: |
          git add docs/profile/
          git commit -m "[ci]自动更新插件画像"
          git push
```

**关键点**:
- CI 环境中始终使用 --cache=false 确保最新数据
- 画像文件提交到仓库，便于历史对比
- 可结合 PR 审查流程，要求画像完整性评分 ≥90

---

### 场景4: 插件迁移兼容性分析

**使用场景**: 评估从其他框架（如 Superpowers）迁移到 CCC 的工作量

**示例**:
```bash
# 分析原插件
Task(
  agent="plugin-profiler",
  args={
    "target": "old-superpowers-plugin",
    "output": "both"
  }
)

# 预期输出
{
  "meta": {
    "base_framework": {
      "name": "superpowers",
      "version": "5.0.2",
      "relationship": "extends"
    }
  },
  "architecture": {
    "component_types": {
      "skills": {
        "count": 15,
        "categories": [
          {"prefix": "cmd-", "count": 12},
          {"prefix": "lib-", "count": 3}
        ]
      }
    }
  }
}

# 迁移评估
# 1. Skills 命名已符合 CCC 规范（cmd-/lib- 前缀）
# 2. 需要添加 std- Skills（如 std-component-selection）
# 3. base_framework 可保留，表明继承关系
# 4. 预计迁移工作量：低（主要是补充规范类 Skills）
```

**迁移检查清单**:
- Skills 命名是否符合 cmd-/std-/lib- 规范
- 是否存在 CLAUDE.md（迁移后强烈推荐）
- 是否使用了 CCC 的三阶段工作流
- plugin_dependencies 是否声明正确

---

### 场景5: 多版本对比分析

**使用场景**: 比较插件不同版本的架构演变

**示例**:
```bash
# 分析 v1.0.0
git checkout v1.0.0
Task(
  agent="plugin-profiler",
  args={
    "target": ".",
    "output": "json",
    "output-dir": "docs/profile/v1.0.0/"
  }
)

# 分析 v2.0.0
git checkout v2.0.0
Task(
  agent="plugin-profiler",
  args={
    "target": ".",
    "output": "json",
    "output-dir": "docs/profile/v2.0.0/"
  }
)

# 分析 v3.0.0 (当前)
git checkout main
Task(
  agent="plugin-profiler",
  args={
    "target": ".",
    "output": "json",
    "output-dir": "docs/profile/v3.0.0/"
  }
)

# 对比分析脚本（使用 jq）
jq -s '
  {
    "version_evolution": [
      {
        "version": "v1.0.0",
        "skills_count": .[0].architecture.component_types.skills.count,
        "agents_count": .[0].architecture.component_types.agents.count,
        "doc_score": .[0].quality_metrics.documentation_completeness.score
      },
      {
        "version": "v2.0.0",
        "skills_count": .[1].architecture.component_types.skills.count,
        "agents_count": .[1].architecture.component_types.agents.count,
        "doc_score": .[1].quality_metrics.documentation_completeness.score
      },
      {
        "version": "v3.0.0",
        "skills_count": .[2].architecture.component_types.skills.count,
        "agents_count": .[2].architecture.component_types.agents.count,
        "doc_score": .[2].quality_metrics.documentation_completeness.score
      }
    ]
  }
' docs/profile/v*/plugin-profile.json
```

**预期输出**:
```json
{
  "version_evolution": [
    {"version": "v1.0.0", "skills_count": 5, "agents_count": 10, "doc_score": 60},
    {"version": "v2.0.0", "skills_count": 15, "agents_count": 30, "doc_score": 85},
    {"version": "v3.0.0", "skills_count": 25, "agents_count": 51, "doc_score": 98}
  ]
}
```

**关键指标**:
- Skills/Agents 增长趋势
- 文档完整性改进
- 分类体系演变（从扁平到角色分类）
- 核心理念的变化

---

## 示例调用

```bash
# 生成 CCC 自身的画像
Task(
  agent="plugin-profiler",
  args={
    "target": "claude-code-component-creator",
    "output": "both"
  }
)

# 预期输出
{
  "profile": {
    "meta": {
      "name": "claude-code-component-creator",
      "display_name": "Claude Code Component Creator (CCC)",
      "version": "3.1.0",
      "positioning": "A powerful Claude Code plugin for creating high-quality components...",
      "base_framework": null
    },
    "architecture": {
      "component_types": {
        "skills": {
          "count": 24,
          "categories": [
            {"prefix": "cmd-", "count": 19, "description": "工作流命令"},
            {"prefix": "std-", "count": 3, "description": "标准规范"},
            {"prefix": "lib-", "count": 2, "description": "知识库"}
          ]
        },
        "agents": {
          "count": 44
        }
      },
      "classification_system": {
        "primary": "role-based",
        "description": "基于组件角色分类:cmd-(用户命令) / std-(标准规范) / lib-(知识库)"
      }
    },
    ...
  },
  "doc_score": 98,
  "warnings": []
}
```

## 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| 目标目录不存在 | 退出并提示错误 |
| README.md 缺失 | 警告,继续从代码推断 |
| Glob/Grep 失败 | 记录警告,返回空结果 |
| JSON Schema 验证失败 | 记录警告,继续生成(降级模式) |

## 性能优化

1. **缓存机制**: 基于文件修改时间判断缓存有效性
2. **惰性加载**: 仅在需要时读取 ARCHITECTURE.md
3. **并行扫描**: skills/ 和 agents/ 可并行扫描(如支持)

## 扩展性

未来可添加的字段:
- `performance_characteristics`: 性能特征
- `security_features`: 安全特性
- `compatibility_matrix`: 兼容性矩阵
