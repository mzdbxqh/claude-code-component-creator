---
name: reviewer-core
description: "架构审阅核心：分批加载反模式→执行检测→返回结构化结果。触发：审阅/架构检查/reviewer-core"
context: fork
model: haiku
allowed-tools:
  - Read
  - Grep
argument-hint: "<batch-id> <file-path>"
---

# Reviewer Core

## Purpose

Reviewer Core 是架构审阅系统的核心检测组件，负责分批加载架构反模式库，对目标文件执行深度质量检查，返回结构化的审阅结果。作为审阅流程的执行引擎，本组件专注于高效、准确地识别代码和架构中的质量问题。

## Workflow

### Step 1: 接收审阅任务
**目标**: 解析审阅请求参数
**操作**:
1. 读取 batch-id 识别审阅批次
2. 读取 file-path 确定目标文件
3. 验证文件存在性和可读性
**输出**: 审阅任务参数
**错误处理**: 文件不存在时返回错误状态

### Step 2: 加载反模式库
**目标**: 根据组件类型加载对应的反模式定义
**操作**:
1. 分析目标文件的组件类型 (Skill/SubAgent)
2. 从 `docs/antipatterns/` 加载对应的反模式定义
3. 解析反模式规则和检测逻辑
**输出**: 反模式规则集合
**错误处理**: 反模式库缺失时使用通用规则

### Step 3: 分批处理文件
**目标**: 大文件分批处理避免上下文溢出
**操作**:
```
IF 文件行数 > 500 THEN
  分批大小 = 200 行
  分批数 = ceil(总行数 / 分批大小)
  FOR 每批 DO
    执行反模式检测
    合并检测结果
  END FOR
ELSE
  全量处理
END IF
```
**输出**: 分批处理结果
**错误处理**: 分批失败时降级为全量处理

### Step 4: 执行反模式检测
**目标**: 应用反模式规则检测问题
**操作**: 对每类反模式执行检测：

| 反模式类别 | 检测项 | 检测方法 |
|------------|--------|----------|
| 命名规范 | name 格式、description 长度 | 正则匹配、长度检查 |
| 权限设计 | context/tools 一致性、最小权限 | 规则匹配 |
| 工作流设计 | 步骤完整性、错误处理 | 结构分析 |
| 工具使用 | 冗余工具、缺失工具 | 必要性分析 |
| 文档质量 | 注释完整性、示例质量 | 内容分析 |

**输出**: 反模式检测结果列表
**错误处理**: 单个规则失败不影响其他规则

### Step 5: 生成结构化结果
**目标**: 输出标准化的审阅结果
**操作**:
1. 汇总所有检测结果
2. 按严重程度分类 (ERROR/WARNING/INFO)
3. 计算质量分数
4. 生成 JSON 格式结果
**输出**: 结构化审阅结果
**错误处理**: 结果生成失败时返回部分结果

## Input Format

### 基本输入
```
<batch-id> <file-path>
```

### 输入示例
```
batch-001 agents/advisor/advisor-core/SKILL.md
```

```
batch-002 src/components/data-processor.ts
```

### 结构化输入 (可选)
```yaml
batch:
  id: "batch-001"
  files:
    - path: "agents/advisor/advisor-core/SKILL.md"
      type: "skill"
    - path: "agents/reviewer/review-core/SKILL.md"
      type: "subagent"
  options:
    depth: "full"
    includeInfo: false
```

## Output Format

### 标准输出结构
```json
{
  "batchId": "batch-001",
  "filePath": "agents/advisor/advisor-core/SKILL.md",
  "status": "COMPLETED",
  "score": 85,
  "summary": {
    "errorCount": 0,
    "warningCount": 2,
    "infoCount": 3
  },
  "issues": [
    {
      "id": "SKILL-001",
      "severity": "WARNING",
      "category": "命名规范",
      "location": {"line": 3, "column": 1},
      "description": "description 长度不足 50 字符",
      "suggestion": "扩展到 50-200 字符以清晰描述功能"
    }
  ],
  "antipatterns": {
    "checked": ["命名规范", "权限设计", "工作流设计"],
    "violated": ["命名规范"]
  },
  "metrics": {
    "linesOfCode": 150,
    "complexity": "low",
    "coverage": "complete"
  }
}
```

### Markdown 输出示例
```markdown
# 审阅结果报告

## 基本信息
- **文件**: agents/advisor/advisor-core/SKILL.md
- **批次**: batch-001
- **状态**: COMPLETED
- **分数**: 85/100

## 问题摘要
| 严重程度 | 数量 |
|----------|------|
| ERROR | 0 |
| WARNING | 2 |
| INFO | 3 |

## 详细问题

### WARNING (2)

#### SKILL-001: description 长度不足
- **位置**: 第 3 行
- **描述**: description 长度不足 50 字符
- **建议**: 扩展到 50-200 字符以清晰描述功能

#### SKILL-003: 缺少错误处理文档
- **位置**: 工作流部分
- **描述**: 部分步骤缺少错误处理说明
- **建议**: 为每个步骤添加错误处理策略

## 反模式检查
- ✅ 命名规范
- ✅ 权限设计
- ⚠️ 工作流设计 (2 个问题)
```

## Error Handling

| 错误场景 | 处理策略 | 示例 |
|----------|----------|------|
| 文件不存在 | 返回错误状态和友好提示 | "文件 xxx 不存在，请检查路径" |
| 文件不可读 | 检查权限并返回错误 | "文件权限不足，请检查读取权限" |
| 反模式库缺失 | 使用内置通用规则 | "专用反模式库缺失，使用通用规则" |
| 文件过大 | 分批处理，超阈值时截断 | "文件超过 2000 行，仅处理前 1000 行" |
| 解析失败 | 跳过问题部分继续处理 | "第 50-60 行解析失败，已跳过" |
| 内存不足 | 降低分批大小重试 | "内存不足，减小分批大小到 100 行" |

## Examples

### Example 1: Skill 文件审阅

**输入**:
```
batch-001 agents/advisor/advisor-core/SKILL.md
```

**输出**:
```json
{
  "batchId": "batch-001",
  "filePath": "agents/advisor/advisor-core/SKILL.md",
  "status": "COMPLETED",
  "score": 92,
  "summary": {"errorCount": 0, "warningCount": 1, "infoCount": 2},
  "issues": [
    {
      "id": "SKILL-005",
      "severity": "WARNING",
      "description": "部分工具缺少用途注释",
      "suggestion": "为每个 allowed-tools 添加用途说明"
    }
  ]
}
```

### Example 2: SubAgent 文件审阅

**输入**:
```
batch-002 agents/reviewer/review-core/SKILL.md
```

**输出**:
```json
{
  "batchId": "batch-002",
  "filePath": "agents/reviewer/review-core/SKILL.md",
  "status": "COMPLETED",
  "score": 78,
  "summary": {"errorCount": 0, "warningCount": 3, "infoCount": 1},
  "issues": [
    {
      "id": "SUBAGENT-002",
      "severity": "WARNING",
      "description": "Task 调用缺少超时设置",
      "suggestion": "为 Task 调用添加 timeout 参数"
    }
  ]
}
```

### Example 3: 大批文件分批处理

**输入**:
```
batch-003 docs/large-specification.md
```

**输出**:
```json
{
  "batchId": "batch-003",
  "filePath": "docs/large-specification.md",
  "status": "COMPLETED_PARTIAL",
  "score": 88,
  "batchesProcessed": 5,
  "totalBatches": 5,
  "summary": {"errorCount": 1, "warningCount": 2, "infoCount": 5}
}
```

### Example 4: 多问题检测

**输入**:
```
batch-004 agents/advisor/test-core/SKILL.md
```

**输出**:
```json
{
  "batchId": "batch-004",
  "status": "COMPLETED",
  "score": 65,
  "summary": {"errorCount": 2, "warningCount": 5, "infoCount": 3},
  "issues": [
    {
      "id": "SKILL-001",
      "severity": "ERROR",
      "description": "name 使用了驼峰命名而非 kebab-case"
    },
    {
      "id": "SKILL-002",
      "severity": "ERROR",
      "description": "main context 包含了 Write 工具"
    }
  ]
}
```

### Example 5: 空文件处理

**输入**:
```
batch-005 empty-file.md
```

**输出**:
```json
{
  "batchId": "batch-005",
  "status": "EMPTY_FILE",
  "score": 0,
  "summary": {"errorCount": 0, "warningCount": 0, "infoCount": 0},
  "message": "文件为空，无法执行审阅"
}
```

## Notes

### Best Practices

1. **分批处理**: 大文件分批避免上下文溢出
2. **增量报告**: 发现问题立即报告，不要等待全部完成
3. **分级处理**: ERROR 优先，WARNING 次之，INFO 可选
4. **规则隔离**: 单个规则失败不影响整体流程
5. **结果缓存**: 相同文件使用缓存结果

### Common Pitfalls

1. ❌ **全量加载**: 大文件一次性加载导致内存溢出
2. ❌ **过度报告**: 报告过多 INFO 级别问题淹没重点
3. ❌ **规则耦合**: 一个规则失败导致整个流程中断
4. ❌ **缺少上下文**: 问题报告没有行号等定位信息
5. ❌ **重复检测**: 同一问题被多个规则重复报告

### Antipattern Categories

#### Skill 反模式
| ID | 名称 | 描述 |
|----|------|------|
| SKILL-001 | 命名不规范 | name 未使用 kebab-case |
| SKILL-002 | 权限冲突 | context 与 tools 不一致 |
| SKILL-003 | 缺少错误处理 | 步骤缺少错误处理说明 |
| SKILL-004 | 工具冗余 | 包含未使用的工具 |
| SKILL-005 | 文档不完整 | 缺少必要文档章节 |

#### SubAgent 反模式
| ID | 名称 | 描述 |
|----|------|------|
| SUBAGENT-001 | 任务协调混乱 | Task 调用缺少清晰流程 |
| SUBAGENT-002 | 缺少超时设置 | 异步调用无超时保护 |
| SUBAGENT-003 | 上下文污染 | fork context 未清理临时文件 |
| SUBAGENT-004 | 依赖隐式 | 调用其他 agent 未明确声明 |

### Integration with Review System

```
用户请求审阅
    ↓
Review Aggregator (调度器)
    ↓
Reviewer Core (本组件) → 分批检测
    ↓
Review Aggregator (聚合器) → 结果聚合
    ↓
Report Renderer (渲染器) → 生成报告
```

### File References

- 反模式库：`docs/antipatterns/skill-antipatterns.md`
- 反模式库：`docs/antipatterns/subagent-antipatterns.md`
- 输出目录：`docs/reviews/{batch-id}/results.json`
