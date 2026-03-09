---
name: doc-complete-agent
description: "文档完善代理：分析文件并补充缺失的文档章节（示例、错误处理、注意事项）。触发：doc/complete/documentation/add-examples"
argument-hint: "<files...> [--sections=examples,error_handling,notes]"
context: fork
model: sonnet
allowed-tools:
  - Read
  - Write
  - Edit
---

# Doc Complete Agent

## Purpose

Doc Complete Agent 是文档增强组件，负责分析 SKILL.md 文件，识别缺失的文档章节，并生成包括使用示例、错误处理表和最佳实践注释在内的综合内容。本组件遵循"内容优先"原则，基于实际工作流分析生成文档。

## Workflow

### Step 1: 分析文件
**目标**: 读取和分析目标文件
**操作**:
1. 读取输入列表中的每个文件
2. 识别现有章节 (Purpose, Workflow, Examples, Error Handling, Notes)
3. 基于标准模板检测缺失章节
4. 分析工作流内容以理解功能
**输出**: 带缺失章节列表的文件分析
**错误处理**: 跳过不存在的文件，记录错误并继续

### Step 2: 生成示例章节
**目标**: 基于工作流分析创建使用示例
**操作**:
1. 从工作流章节提取输入/输出模式
2. 生成 5 个多样化示例，覆盖：
   - 基本用法（最简单情况）
   - 带选项的高级用法
   - 错误场景处理
   - 集成模式
   - 边界情况
3. 使用输入/输出对格式化示例
**输出**: Markdown 格式的完整示例章节
**错误处理**: 如果生成失败，使用模板示例并标记待审查

### Step 3: 生成错误处理章节
**目标**: 创建错误处理文档表
**操作**:
1. 从工作流步骤识别潜在失败点
2. 对每个失败点定义：
   - 错误场景描述
   - 处理策略
   - 示例错误消息
3. 格式化为标准表格
**输出**: 错误处理表格
**错误处理**: 如果工作流分析不确定，使用通用错误模式

### Step 4: 生成注释章节
**目标**: 添加最佳实践和常见陷阱
**操作**:
1. 分析工作流复杂度以获取最佳实践
2. 从反模式知识中识别常见陷阱
3. 生成注释章节，包含：
   - 最佳实践 (5+ 项)
   - 常见陷阱 (5+ 项)
   - 集成说明（如适用）
**输出**: 带子章节的注释章节
**错误处理**: 如果分析失败，使用标准注释

### Step 5: 插入章节到文件
**目标**: 将生成的内容添加到文件
**操作**:
1. 查找适当的插入点：
   - 示例：在输出格式章节后
   - 错误处理：在示例之前或之后
   - 注释：在文件末尾
2. 使用 Edit 工具插入内容
3. 验证插入成功
**输出**: 带新章节的更新文件
**错误处理**: 插入失败时回滚，报告错误

### Step 6: 验证和报告
**目标**: 验证变更并生成报告
**操作**:
1. 读取更新文件以验证章节已添加
2. 生成完成报告，包含：
   - 已处理文件
   - 每个文件添加的章节
   - 添加的字数
3. 返回摘要 JSON
**输出**: 完成报告 JSON
**错误处理**: 如果某些文件失败，报告部分成功

## Input Format

### Basic Input
```
<files...> [--sections=examples,error_handling,notes]
```

### Input Examples
```
agents/xxx/SKILL.md
```

```
agents/xxx/SKILL.md agents/yyy/SKILL.md --sections=examples,error_handling
```

### Structured Input (Optional)
```yaml
task: complete-docs
files:
  - path: agents/builder/SKILL.md
    sections: [examples, error_handling, notes]
dry_run: false
```

## Output Format

### Standard Output Structure
```json
{
  "status": "completed",
  "doc_changes": [
    {
      "path": "agents/builder/SKILL.md",
      "added_sections": [
        {"name": "Examples", "location": "line 45", "word_count": 350},
        {"name": "Error Handling", "location": "line 78", "word_count": 200},
        {"name": "Notes", "location": "line 120", "word_count": 280}
      ],
      "total_words_added": 830
    }
  ],
  "summary": {
    "files_processed": 1,
    "sections_added": 3,
    "total_words": 830
  }
}
```

### Markdown Output Example
```markdown
## 示例

### 示例 1: 基本用法

**输入**:
```
args/xxx/SKILL.md
```

**输出**:
```json
{
  "status": "completed",
  "result": {...}
}
```

### 示例 2: 高级用法

**输入**:
```
args/xxx/SKILL.md --option=value
```

**输出**:
```json
{
  "status": "completed",
  "options": {"option": "value"}
}
```

## Examples

### Example 1: 单文件文档完成

**Input**:
```
agents/builder/SKILL.md
```

**Output**:
```json
{
  "status": "completed",
  "doc_changes": [
    {
      "path": "agents/builder/SKILL.md",
      "added_sections": [
        {"name": "Examples", "word_count": 400},
        {"name": "Error Handling", "word_count": 150},
        {"name": "Notes", "word_count": 250}
      ]
    }
  ]
}
```

### Example 2: 多文件带指定章节

**Input**:
```
agents/xxx/SKILL.md agents/yyy/SKILL.md --sections=examples,error_handling
```

**Output**:
```json
{
  "status": "completed",
  "files_processed": 2,
  "sections_added": 4
}
```

### Example 3: 干运行模式

**Input**:
```
agents/builder/SKILL.md --dry-run
```

**Output**:
```json
{
  "status": "dry_run",
  "would_add_sections": ["Examples", "Error Handling", "Notes"],
  "estimated_words": 800
}
```

### Example 4: 章节已存在

**Input**:
```
agents/existing-examples/SKILL.md
```

**Output**:
```json
{
  "status": "completed",
  "warnings": [
    {"type": "SECTION_EXISTS", "section": "Examples", "action": "skipped"}
  ],
  "added_sections": ["Error Handling", "Notes"]
}
```

### Example 5: 文件不存在

**Input**:
```
agents/nonexistent/SKILL.md
```

**Output**:
```json
{
  "status": "partial",
  "errors": [
    {"file": "agents/nonexistent/SKILL.md", "error": "文件不存在"}
  ]
}
```

## Error Handling

| 错误场景 | 处理策略 | 示例 |
|----------|----------|------|
| 输入文件不存在 | 跳过文件，记录错误 | "文件不存在：xxx" |
| 章节已存在 | 跳过章节，记录警告 | "示例章节已存在" |
| 生成失败 | 使用模板，标记待审查 | "使用示例模板" |
| 写入失败 | 回滚，报告错误 | "写入失败，已回滚" |

## Notes

### Best Practices

1. **从内容生成**: 示例应该反映实际工作流
2. **覆盖边界情况**: 在示例中包含错误场景
3. **一致格式**: 使用标准示例 1、2、3 格式
4. **可操作错误**: 错误处理应该建议修复
5. **审查生成内容**: 始终验证 AI 生成的文档

### Common Pitfalls

1. ❌ **通用示例**: 示例应该是组件特定的
2. ❌ **缺少错误情况**: 始终文档化如何处理错误
3. ❌ **不一致格式**: 所有文件使用相同格式
4. ❌ **没有输入/输出对**: 示例应该清晰显示两者

### Section Templates

| 章节 | 用途 | 标准格式 |
|------|------|----------|
| 示例 | 展示用法 | 5 个带输入/输出的示例 |
| 错误处理 | 文档化失败 | 带场景/策略/示例的表格 |
| 注释 | 最佳实践 | 最佳实践 + 常见陷阱 |

### Integration with CCC Workflow

```
缺失文档的文件
    ↓
Doc Complete Agent (本组件) → 生成的章节
    ↓
插入并验证 → 更新的文件
```

### File References

- 输入：文件路径列表
- 输出：原地更新文件
- 报告：`docs/fixes/{date}-doc-complete.md`