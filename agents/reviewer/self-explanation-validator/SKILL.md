---
name: self-explanation-validator
description: "报告自解释性验证器：检查报告是否包含必需章节、无外部引用、结构清晰、信息准确。触发：自解释/验证报告/report validation"
model: sonnet
tools:
  - Read
  - Grep
permissionMode: prompt
argument-hint: "--report=<report_path> --profile=<profile_path> [--threshold=80]"
---

# Self-Explanation Validator

## Purpose

验证审查报告的自解释性，确保报告可独立阅读，不依赖外部文档即可理解被扫描插件。

## Validation Dimensions

4 个验证维度（100分制）：

| 维度 | 权重 | 检查项 | 评分标准 |
|------|------|--------|---------|
| **完整性** | 40% | 必需章节是否存在 | 10 个必需章节全部存在得满分 |
| **自包含性** | 30% | 是否需要参考外部文档 | 不需要参考任何外部文档得满分 |
| **结构清晰度** | 20% | 章节层次和逻辑 | 遵循标准结构得满分 |
| **信息准确性** | 10% | 画像信息与实际一致 | 一致性验证通过得满分 |

## Required Sections

报告必须包含以下 10 个章节/小节：

1. **插件概述 > 基本信息** (`### 1.1 基本信息`)
2. **插件概述 > 核心功能** (`### 1.2 核心功能`)
3. **插件概述 > 架构设计 > 组件分类体系** (`#### 组件分类体系`)
4. **插件概述 > 架构设计 > 工作流运行机制** (`#### 工作流运行机制`)
5. **插件概述 > 使用方式 > 斜杠命令** (`#### 斜杠命令`)
6. **插件概述 > 核心设计理念** (`### 1.5 核心设计理念`)
7. **插件概述 > 系统要求** (`### 1.6 系统要求`)
8. **执行摘要** (`## 二、执行摘要`)
9. **组件扫描结果** (`## 三、组件扫描结果`)
10. **质量评估** (`## 四、质量评估`)

## Parameters

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--report` | 路径 | 必需 | 待验证的报告 Markdown 文件路径 |
| `--profile` | 路径 | 可选 | 插件画像 JSON 文件路径（用于信息准确性检查） |
| `--threshold` | 数字 | `80` | 合格阈值（0-100），低于阈值输出警告 |

## Workflow

### Step 1: 读取报告文件

**目标**: 加载待验证的报告内容

**操作**:
1. 读取 `--report` 参数指定的 Markdown 文件
2. 验证文件存在性和可读性
3. 加载报告内容到内存

**输出**: 报告内容字符串

**错误处理**: 文件不存在或不可读时退出并提示错误

---

### Step 2: 读取画像文件（可选）

**条件**: 如果提供了 `--profile` 参数

**目标**: 加载插件画像数据用于准确性检查

**操作**:
1. 读取 `--profile` 参数指定的 JSON 文件
2. 解析 JSON 内容
3. 提取组件统计数据（skills.count, agents.count 等）

**输出**: 画像数据对象

**错误处理**: 文件不存在或格式错误时记录警告，跳过准确性检查

---

### Step 3: 完整性检查（40%）

**目标**: 检查 10 个必需章节是否全部存在

**操作**:
1. 定义必需章节列表（使用 Markdown 标题格式）:
   ```python
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
   ```

2. 使用 Grep 工具逐一检查每个章节:
   ```bash
   for section in required_sections:
       if Grep(pattern=section, path=report_file, output_mode="files_with_matches"):
           # 章节存在
       else:
           missing_sections.append(section)
           score -= 40 / len(required_sections)
   ```

3. 如果有缺失章节，记录问题:
   ```python
   if missing_sections:
       issues.append({
           "severity": "error",
           "type": "missing_section",
           "sections": missing_sections,
           "message": f"缺失 {len(missing_sections)} 个必需章节"
       })
   ```

**输出**: 缺失章节列表、扣分

**错误处理**: Grep 失败时记录警告

---

### Step 4: 自包含性检查（30%）

**目标**: 检查报告是否引用外部文档

**操作**:
1. 定义外部引用模式:
   ```python
   external_refs = [
       "参见 README.md",
       "详见文档",
       "参考 ARCHITECTURE.md",
       "see documentation",
       "refer to README"
   ]
   ```

2. 使用 Grep 检查每个模式（不区分大小写）:
   ```bash
   for ref in external_refs:
       matches = Grep(pattern=ref, path=report_file, output_mode="count", -i=true)
       if matches > 0:
           score -= 10  # 每发现一个外部引用扣10分
           issues.append({
               "severity": "warning",
               "type": "external_reference",
               "text": ref,
               "count": matches,
               "message": f"报告引用外部文档 '{ref}' ({matches}次)，降低了自解释性"
           })
   ```

**输出**: 外部引用列表、扣分

**错误处理**: Grep 失败时记录警告

---

### Step 5: 结构清晰度检查（20%）

**目标**: 检查报告章节结构是否清晰

**操作**:
1. 使用 Grep 统计所有标题（# 开头的行）:
   ```bash
   headings = Grep(pattern="^#{1,4}\s+", path=report_file, output_mode="count")
   ```

2. 检查标题数量是否充足:
   ```python
   if headings < 10:
       score -= 20
       issues.append({
           "severity": "warning",
           "type": "insufficient_structure",
           "message": f"章节数量不足（当前: {headings}, 预期: ≥10）"
       })
   ```

3. （可选）检查章节编号是否连续（使用正则）

**输出**: 标题数量、扣分

**错误处理**: Grep 失败时记录警告

---

### Step 6: 信息准确性检查（10%）

**条件**: 如果提供了 `--profile` 参数

**目标**: 验证报告中的组件数量与画像一致

**操作**:
1. 从报告中提取 Skills 数量:
   ```bash
   # 匹配模式: "| Skills | 24 |" 或 "Skills: 24"
   skills_match = Grep(pattern="Skills.*\\|.*(\d+)", path=report_file, output_mode="content")
   reported_skills_count = extract_number(skills_match)
   ```

2. 从画像中提取实际数量:
   ```python
   actual_skills_count = profile.architecture.component_types.skills.count
   ```

3. 对比并扣分:
   ```python
   if reported_skills_count != actual_skills_count:
       score -= 10
       issues.append({
           "severity": "error",
           "type": "data_inconsistency",
           "field": "skills_count",
           "reported": reported_skills_count,
           "actual": actual_skills_count,
           "message": f"报告中的 Skills 数量与画像不一致"
       })
   ```

4. （可选）对 Agents 数量进行同样检查

**输出**: 一致性问题列表、扣分

**错误处理**: 提取失败时跳过此检查

---

### Step 7: 生成验证结果

**目标**: 汇总检查结果，生成验证报告

**操作**:
1. 计算最终评分:
   ```python
   final_score = max(0, min(100, score))  # 限制在 0-100 之间
   ```

2. 根据 issues 生成改进建议:
   ```python
   recommendations = []
   for issue in issues:
       if issue["type"] == "missing_section":
           recommendations.append(f"补充缺失的章节: {', '.join(issue['sections'])}")
       elif issue["type"] == "external_reference":
           recommendations.append(f"将外部引用的内容内联到报告中，避免引用 '{issue['text']}'")
       elif issue["type"] == "insufficient_structure":
           recommendations.append("增加章节深度，按照标准模板组织内容")
       elif issue["type"] == "data_inconsistency":
           recommendations.append(f"修正 {issue['field']} 的值（应为 {issue['actual']}）")
   ```

3. 输出验证结果:
   ```
   ========================================
   报告自解释性验证结果
   ========================================

   报告: {report_path}
   评分: {final_score}/100

   维度评分:
   - 完整性: {completeness_score}/40
   - 自包含性: {self_contained_score}/30
   - 结构清晰度: {structure_score}/20
   - 信息准确性: {accuracy_score}/10

   {if final_score < threshold}
   ⚠️ 评分低于阈值 ({threshold})，需要改进

   发现的问题 ({len(issues)}):
   {for issue in issues}
   - [{issue.severity}] {issue.message}
   {endfor}

   改进建议:
   {for rec in recommendations}
   - {rec}
   {endfor}
   {else}
   ✅ 报告自解释性良好
   {endif}
   ```

**输出**: 验证结果报告

**错误处理**: 无

---

### Step 8: 返回退出码

**目标**: 根据评分返回合适的退出码

**操作**:
```python
if final_score >= threshold:
    exit(0)  # 成功
else:
    exit(1)  # 失败（评分低于阈值）
```

**输出**: 退出码

---

## Output Format

验证结果包含：
- **评分**: 0-100 的整数
- **维度评分**: 4 个维度的详细得分
- **问题列表**: 发现的所有问题（severity, type, message）
- **改进建议**: 针对问题的具体改进建议
- **退出码**: 0（通过）或 1（未通过阈值）

## Examples

### Example 1: 验证报告（带画像）

```bash
# 验证报告，使用默认阈值 80
self-explanation-validator --report=docs/reviews/ccc-review.md --profile=docs/profile/plugin-profile.json

# 输出:
# 报告自解释性验证结果
# 评分: 95/100
# ✅ 报告自解释性良好
```

### Example 2: 验证报告（无画像）

```bash
# 验证报告，跳过准确性检查
self-explanation-validator --report=docs/reviews/plugin-review.md

# 输出:
# 报告自解释性验证结果
# 评分: 85/100 (准确性检查跳过)
# ✅ 报告自解释性良好
```

### Example 3: 验证失败

```bash
# 验证报告，设置更高阈值
self-explanation-validator --report=docs/reviews/incomplete-report.md --threshold=90

# 输出:
# 报告自解释性验证结果
# 评分: 75/100
# ⚠️ 评分低于阈值 (90)，需要改进
#
# 发现的问题:
# - [error] 缺失 2 个必需章节
# - [warning] 报告引用外部文档 '参见 README.md' (1次)
#
# 改进建议:
# - 补充缺失的章节: ### 1.5 核心设计理念, ### 1.6 系统要求
# - 将外部引用的内容内联到报告中，避免引用 '参见 README.md'
```

## Error Handling

| 错误类型 | 处理方式 |
|---------|---------|
| 报告文件不存在 | 退出并提示错误 |
| 画像文件不存在 | 记录警告，跳过准确性检查 |
| Grep 失败 | 记录警告，继续其他检查 |
| 提取数据失败 | 跳过对应检查项 |

## Performance

- 典型报告（50KB）验证耗时: <5 秒
- Token 使用: 约 5K-10K tokens
- 支持大型报告（500KB+）

## Extension Points

未来可扩展的检查项：
- 图表质量（Mermaid 图是否正确）
- 代码示例完整性
- 链接有效性
- 多语言支持验证
