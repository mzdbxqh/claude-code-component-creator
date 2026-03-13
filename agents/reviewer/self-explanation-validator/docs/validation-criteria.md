# 报告自解释性验证标准

## 概述

本文档详细说明 self-explanation-validator 的 4 个验证维度的评分标准、检查逻辑和示例。

## 验证维度

### 1. 完整性检查（40%）

**评分标准**:
- 满分 40 分
- 每缺失一个必需章节扣 4 分（10 个必需章节）

**必需章节列表**:

| 序号 | 章节标题 | Markdown 格式 | 说明 |
|-----|---------|--------------|------|
| 1 | 插件概述 | `## 一、插件概述` | 顶级章节 |
| 2 | 基本信息 | `### 1.1 基本信息` | 插件名称、版本、作者等 |
| 3 | 核心功能 | `### 1.2 核心功能` | 主要功能列表 |
| 4 | 架构设计 | `### 1.3 架构设计` | 架构描述的父章节 |
| 5 | 组件分类体系 | `#### 组件分类体系` | Skills/Agents 分类 |
| 6 | 工作流运行机制 | `#### 工作流运行机制` | 工作流执行逻辑 |
| 7 | 使用方式 | `### 1.4 使用方式` | 使用说明的父章节 |
| 8 | 斜杠命令 | `#### 斜杠命令` | 命令列表和用法 |
| 9 | 核心设计理念 | `### 1.5 核心设计理念` | 设计原则和哲学 |
| 10 | 系统要求 | `### 1.6 系统要求` | 依赖和环境要求 |

**检查逻辑**:

```python
def check_completeness(report_content: str) -> tuple[int, list]:
    """检查报告完整性

    Args:
        report_content: 报告 Markdown 内容

    Returns:
        (score, missing_sections): 得分和缺失章节列表
    """
    required_sections = [
        "## 一、插件概述",
        "### 1.1 基本信息",
        "### 1.2 核心功能",
        "### 1.3 架构设计",
        "#### 组件分类体系",
        "#### 工作流运行机制",
        "### 1.4 使用方式",
        "#### 斜杠命令",
        "### 1.5 核心设计理念",
        "### 1.6 系统要求"
    ]

    score = 40
    missing = []

    for section in required_sections:
        if section not in report_content:
            missing.append(section)
            score -= 4  # 每个章节 4 分

    return score, missing
```

**示例**:

**完整报告**（满分 40/40）:
```markdown
## 一、插件概述

### 1.1 基本信息
- 插件名称: CCC
- 版本: v3.1.0

### 1.2 核心功能
- 组件设计
- 质量审查

### 1.3 架构设计

#### 组件分类体系
三种组件类型: cmd/std/lib

#### 工作流运行机制
阶段式设计流程

### 1.4 使用方式

#### 斜杠命令
- /design-new-component
- /cmd-review

### 1.5 核心设计理念
质量优先、用户友好

### 1.6 系统要求
- Claude Code v1.0+
- Node.js 16+
```

**不完整报告**（扣分 8/40 = 32/40）:
```markdown
## 一、插件概述

### 1.1 基本信息
- 插件名称: CCC

### 1.2 核心功能
- 组件设计

### 1.3 架构设计

#### 组件分类体系
三种组件类型

### 1.4 使用方式

# 缺失:
# - #### 工作流运行机制 (-4)
# - #### 斜杠命令 (-4)
# - ### 1.5 核心设计理念 (-4)
# - ### 1.6 系统要求 (-4)
```

---

### 2. 自包含性检查（30%）

**评分标准**:
- 满分 30 分
- 每发现一个外部引用扣 10 分（最多扣 30 分）

**外部引用模式列表**:

| 模式 | 说明 | 示例 |
|-----|------|------|
| `参见 README.md` | 中文引用 README | "详细配置参见 README.md" |
| `详见文档` | 通用中文引用 | "详见文档第 3 章" |
| `参考 ARCHITECTURE.md` | 引用架构文档 | "参考 ARCHITECTURE.md 了解设计" |
| `see documentation` | 英文引用文档 | "see documentation for details" |
| `refer to README` | 英文引用 README | "refer to README section 2" |

**检查逻辑**:

```python
def check_self_contained(report_content: str) -> tuple[int, list]:
    """检查报告自包含性

    Args:
        report_content: 报告 Markdown 内容

    Returns:
        (score, external_refs): 得分和外部引用列表
    """
    patterns = [
        "参见 README.md",
        "详见文档",
        "参考 ARCHITECTURE.md",
        "see documentation",
        "refer to README"
    ]

    score = 30
    external_refs = []

    for pattern in patterns:
        # 不区分大小写匹配
        if re.search(pattern, report_content, re.IGNORECASE):
            external_refs.append(pattern)
            score -= 10

    return max(0, score), external_refs
```

**示例**:

**自包含报告**（满分 30/30）:
```markdown
## 一、插件概述

### 1.1 基本信息
- 插件名称: Component Creator for Claude (CCC)
- 版本: v3.1.0
- 作者: mzdbxqh
- 描述: 用于 Claude Code 的组件创建和审查插件

### 1.2 核心功能
1. **组件设计**: 提供三种组件类型（cmd/std/lib）的设计模板
2. **质量审查**: 多维度质量评估和改进建议
3. **工作流管理**: 阶段式设计流程和检查点机制

### 1.3 架构设计

#### 组件分类体系
插件采用三层组件分类：
- **cmd 类型**: 斜杠命令，用户交互入口
- **std 类型**: 标准组件，封装通用逻辑
- **lib 类型**: 基础库，提供底层能力

#### 工作流运行机制
采用阶段式设计流程：
1. 需求分析
2. 架构设计
3. 详细设计
4. 质量审查
```

**有外部引用的报告**（扣分 10/30 = 20/30）:
```markdown
## 一、插件概述

### 1.1 基本信息
- 插件名称: CCC
- 版本: v3.1.0

### 1.2 核心功能
详细功能列表参见 README.md 第 2 章。  # 外部引用，扣 10 分

### 1.3 架构设计
架构图和详细说明详见文档。  # 虽然也是外部引用，但已经扣过分了
```

---

### 3. 结构清晰度检查（20%）

**评分标准**:
- 满分 20 分
- 标题数量 < 10：扣 20 分
- 标题数量 ≥ 10：满分

**检查逻辑**:

```python
def check_structure_clarity(report_content: str) -> tuple[int, dict]:
    """检查报告结构清晰度

    Args:
        report_content: 报告 Markdown 内容

    Returns:
        (score, stats): 得分和统计信息
    """
    # 统计各级标题数量
    h1_count = len(re.findall(r'^#\s+', report_content, re.MULTILINE))
    h2_count = len(re.findall(r'^##\s+', report_content, re.MULTILINE))
    h3_count = len(re.findall(r'^###\s+', report_content, re.MULTILINE))
    h4_count = len(re.findall(r'^####\s+', report_content, re.MULTILINE))

    total_headings = h1_count + h2_count + h3_count + h4_count

    score = 20 if total_headings >= 10 else 0

    stats = {
        "total": total_headings,
        "h1": h1_count,
        "h2": h2_count,
        "h3": h3_count,
        "h4": h4_count
    }

    return score, stats
```

**示例**:

**结构清晰的报告**（满分 20/20）:
```markdown
# CCC 插件审查报告  # H1

## 一、插件概述  # H2

### 1.1 基本信息  # H3
### 1.2 核心功能  # H3
### 1.3 架构设计  # H3

#### 组件分类体系  # H4
#### 工作流运行机制  # H4

### 1.4 使用方式  # H3

#### 斜杠命令  # H4

### 1.5 核心设计理念  # H3
### 1.6 系统要求  # H3

## 二、执行摘要  # H2

# 统计: H1=1, H2=2, H3=7, H4=3, 总计=13 ≥ 10 → 满分
```

**结构不足的报告**（扣分 20/20 = 0/20）:
```markdown
# CCC 插件审查报告  # H1

## 插件概述  # H2

一些基本信息...

## 质量评估  # H2

一些评估内容...

# 统计: H1=1, H2=2, H3=0, H4=0, 总计=3 < 10 → 0 分
```

---

### 4. 信息准确性检查（10%）

**评分标准**:
- 满分 10 分
- 需要提供 `--profile` 参数才进行检查
- 未提供画像文件时跳过此检查（不扣分）
- Skills 数量不一致：扣 5 分
- Agents 数量不一致：扣 5 分

**检查项**:

| 数据项 | 提取模式（报告） | 提取路径（画像） | 权重 |
|-------|-----------------|-----------------|------|
| Skills 数量 | `Skills.*\|.*(\d+)` | `architecture.component_types.skills.count` | 5 分 |
| Agents 数量 | `Agents.*\|.*(\d+)` | `architecture.component_types.agents.count` | 5 分 |

**检查逻辑**:

```python
def check_accuracy(report_content: str, profile_data: dict) -> tuple[int, list]:
    """检查信息准确性

    Args:
        report_content: 报告 Markdown 内容
        profile_data: 画像 JSON 数据

    Returns:
        (score, issues): 得分和问题列表
    """
    score = 10
    issues = []

    # 检查 Skills 数量
    skills_match = re.search(r'Skills.*?\|.*?(\d+)', report_content)
    if skills_match:
        reported_skills = int(skills_match.group(1))
        actual_skills = profile_data["architecture"]["component_types"]["skills"]["count"]

        if reported_skills != actual_skills:
            score -= 5
            issues.append({
                "field": "skills_count",
                "reported": reported_skills,
                "actual": actual_skills
            })

    # 检查 Agents 数量
    agents_match = re.search(r'Agents.*?\|.*?(\d+)', report_content)
    if agents_match:
        reported_agents = int(agents_match.group(1))
        actual_agents = profile_data["architecture"]["component_types"]["agents"]["count"]

        if reported_agents != actual_agents:
            score -= 5
            issues.append({
                "field": "agents_count",
                "reported": reported_agents,
                "actual": actual_agents
            })

    return score, issues
```

**示例**:

**画像数据**（profile.json）:
```json
{
  "architecture": {
    "component_types": {
      "skills": {
        "count": 24
      },
      "agents": {
        "count": 8
      }
    }
  }
}
```

**准确的报告**（满分 10/10）:
```markdown
## 组件统计

| 类型 | 数量 |
|-----|-----|
| Skills | 24 |
| Agents | 8 |
```

**不准确的报告**（扣分 5/10 = 5/10）:
```markdown
## 组件统计

| 类型 | 数量 |
|-----|-----|
| Skills | 20 |  # 错误，实际是 24，扣 5 分
| Agents | 8 |   # 正确
```

---

## 评分汇总

### 总分计算

```python
final_score = (
    completeness_score +     # 0-40
    self_contained_score +   # 0-30
    structure_score +        # 0-20
    accuracy_score          # 0-10
)  # 总计 0-100
```

### 评级标准

| 分数区间 | 评级 | 说明 |
|---------|------|------|
| 90-100 | 优秀 | 自解释性极佳，可直接作为独立文档使用 |
| 80-89 | 良好 | 自解释性较好，仅需少量改进 |
| 70-79 | 合格 | 基本满足自解释性要求，需适度改进 |
| 60-69 | 不足 | 自解释性欠佳，需较大改进 |
| <60 | 差 | 严重依赖外部文档，需重写 |

### 阈值设置建议

| 场景 | 推荐阈值 | 说明 |
|-----|---------|------|
| 生产环境发布 | 85 | 确保报告质量 |
| 开发阶段审查 | 75 | 允许一定改进空间 |
| 快速验证 | 60 | 仅检查基本要求 |

---

## 改进建议生成

### 建议模板

```python
RECOMMENDATION_TEMPLATES = {
    "missing_section": "补充缺失的章节: {sections}",
    "external_reference": "将外部引用的内容内联到报告中，避免引用 '{text}'",
    "insufficient_structure": "增加章节深度，按照标准模板组织内容（当前 {count} 个标题，建议 ≥10）",
    "data_inconsistency": "修正 {field} 的值（报告中: {reported}, 实际: {actual}）"
}
```

### 优先级排序

1. **ERROR 级别**: missing_section, data_inconsistency
2. **WARNING 级别**: external_reference, insufficient_structure

---

## 扩展检查项（未来）

### 图表质量检查

```python
def check_mermaid_diagrams(report_content: str) -> tuple[int, list]:
    """检查 Mermaid 图表质量"""
    # 检查图表语法正确性
    # 检查图表完整性（节点、边）
    # 检查图表可读性
    pass
```

### 代码示例完整性

```python
def check_code_examples(report_content: str) -> tuple[int, list]:
    """检查代码示例完整性"""
    # 检查代码块语法高亮
    # 检查代码块是否可运行
    # 检查代码注释完整性
    pass
```

### 链接有效性

```python
def check_links(report_content: str) -> tuple[int, list]:
    """检查链接有效性"""
    # 检查内部锚点是否存在
    # 检查外部链接是否可访问
    pass
```
