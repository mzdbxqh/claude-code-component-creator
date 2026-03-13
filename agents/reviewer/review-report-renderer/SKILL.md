---
name: review-report-renderer
description: "审阅报告渲染器：JSON 审查数据→审阅报告。触发：审阅报告/review report/渲染审阅"
model: sonnet
tools:
  - Read
  - Write
permissionMode: prompt
skills:
  - ccc:std-naming-rules
---

# Review Report Renderer

## Purpose
专注渲染审阅聚合报告，将 JSON 审查数据转换为格式化的 Markdown 报告。

## Workflow

@references/common-rendering.md

**集成插件画像**（v3.1.0 新增）：
- 如果 review_context 包含 plugin_profile，自动在报告开头生成"插件概述"章节
- 插件概述包含 7 个子章节：基本信息、核心功能、架构设计、使用方式、核心设计理念、系统要求、文档完整性评估
- 提升报告自解释性，确保报告可独立阅读

### Step 1: 加载审阅 JSON 数据
读取并验证审阅聚合 JSON 文件

### Step 2: 选择审阅报告模板
使用 review-aggregated 模板

### Step 2.5: 渲染插件概述章节（如果存在画像数据）

**条件**: 如果 `review_context["plugin_profile"]` 存在

**目标**: 将插件画像数据渲染为"插件概述"章节

**执行流程**:

1. **检查画像数据**
   - 检查 `review_context` 中是否存在 `plugin_profile`
   - 如果不存在，跳过此步骤，直接进入 Step 3
   - 如果存在但为空或无效，记录警告并跳过

2. **渲染 7 个子章节**

   使用 `render_plugin_overview(profile)` 方法生成以下子章节：

   **1.1 基本信息**
   ```python
   render_basic_info(profile.meta):
     - 名称: {display_name}
     - 版本: {version}
     - 定位: {positioning}
     - 基础框架: {base_framework.name} {base_framework.version} (关系: {relationship})
     - 仓库: {repository}
     - 许可证: {license}
   ```

   **1.2 核心功能**
   ```python
   render_core_features(profile.meta):
     - 描述: {description}
     - 继承的能力 (来自 {base_framework.name}):
       - {inherited_skills[]}
     - 新增的价值: {base_framework.added_value}
   ```

   **1.3 架构设计**
   ```python
   render_architecture(profile.architecture):
     - 组件分类体系:
       - 分类方式: {classification_system.primary}
       - 说明: {classification_system.description}
       - 设计理念: {classification_system.rationale}
     - 组件统计表格:
       | 类型 | 数量 | 说明 |
     - Skills 分类详情
     - 工作流运行机制:
       - 类型: {workflow_mechanism.type}
       - 工作流阶段: Stage1 → Stage2 → Stage3
       - 激活方式: 手动调用 + 自动激活
   ```

   **1.4 使用方式**
   ```python
   render_usage(profile.usage):
     - 斜杠命令表格:
       | 命令 | 对应 Skill | 说明 | 分类 |
     - 自动激活的 Skills 表格:
       | Skill | 触发场景 | 加载者 |
   ```

   **1.5 核心设计理念**
   ```python
   render_philosophy(profile.philosophy):
     遍历 core_principles[]:
       - 原则: {principle}
       - 说明: {description}
       - 实现方式: {implementation}
       - 收益: {benefit}
       - 设计理由: {rationale}
   ```

   **1.6 系统要求**
   ```python
   render_requirements(profile.requirements):
     - 平台: {system.platform} {min_version}+
     - 操作系统: {os[]}
     - 必需依赖: {runtime_dependencies.required[]}
     - 可选依赖: {runtime_dependencies.optional[]}
     - 插件依赖: {plugin_dependencies}
   ```

   **1.7 文档完整性评估**
   ```python
   render_doc_completeness(profile.quality_metrics):
     - 评分: {documentation_completeness.score}/100
     - 文档完整性表格:
       | 文档 | 状态 | 完整性 | 建议 |
   ```

3. **组装插件概述章节**
   ```python
   sections = [
     "## 一、插件概述\n",
     render_basic_info(profile.meta),
     render_core_features(profile.meta),
     render_architecture(profile.architecture),
     render_usage(profile.usage),
     render_philosophy(profile.philosophy),
     render_requirements(profile.requirements),
     render_doc_completeness(profile.quality_metrics)
   ]
   plugin_overview = "\n\n".join(sections)
   ```

4. **插入到报告开头**
   - 将生成的插件概述章节插入到报告的最前面（在"执行摘要"之前）
   - 添加分隔线 `---` 分隔插件概述和执行摘要

**输出**:
- 包含插件概述的完整报告 Markdown 内容

**错误处理**:
- 画像数据字段缺失时，使用默认值或占位符（如"—"）
- 渲染失败时记录警告，跳过插件概述章节，继续生成常规报告
- 确保报告生成不会因画像问题而失败

**示例输出结构**:
```markdown
# <插件名称> 质量审查报告

> 审查日期: 2026-03-13
> 审查者: Claude Sonnet 4.5
> 插件版本: 3.1.0
> 审查类型: standard

---

## 一、插件概述

### 1.1 基本信息
- **名称**: Claude Code Component Creator (CCC)
- **版本**: 3.1.0
- **定位**: A powerful Claude Code plugin for creating high-quality components...
...

---

## 二、执行摘要

<原有内容>
```

### Step 3: 填充模板
将数据填充到模板占位符

### Step 4: 写入报告
保存为 Markdown 文件

## Input Format
```
<json-data-path>
```

## Output Format
生成的审阅报告 Markdown 文件

## Examples

### Example 1: 基本用法
```
docs/reviews/aggregated-result.json
```

## Error Handling
参考 @references/common-rendering.md
