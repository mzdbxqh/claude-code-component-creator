---
name: migration-reviewer-core
description: "改造方案审阅核心：分批检测改造方案质量→返回结构化结果。触发：改造/迁移/迁移检查/migration-reviewer"
model: haiku
tools:
  - Read
  - Grep
permissionMode: prompt
skills:
  - ccc:lib-antipatterns
---

# Migration Reviewer Core

## Purpose

Migration Reviewer Core 是改造方案审阅的核心检测组件，负责分批检测改造方案的质量，识别方案中的风险、遗漏和问题，返回结构化的审阅结果。本组件专注于确保改造方案的可行性、完整性和安全性。

## Workflow

### Step 1: 接收审阅任务
**目标**: 解析审阅批次和文件路径
**操作**:
1. 读取 batch-id 识别审阅批次
2. 读取 file-path 确定目标文件
3. 验证文件存在性和可读性
4. 确定批次范围 (页码/章节)
**输出**: 审阅任务参数
**错误处理**: 文件不存在时返回错误状态

### Step 2: 加载审阅规则
**目标**: 加载改造方案审阅规则集
**操作**:
1. 读取 `docs/antipatterns/migration-antipatterns.md`
2. 解析审阅检查项
3. 构建规则索引
**输出**: 审阅规则集合
**错误处理**: 规则库缺失时使用默认规则

### Step 3: 分批读取方案
**目标**: 读取指定批次的方案内容
**操作**:
```
IF 文件有批次标记 THEN
  读取批次对应章节
ELSE
  全量读取
END IF

解析方案结构:
- 改造目标
- 现状分析
- 方案设计
- 实施计划
- 风险评估
```
**输出**: 批次方案内容
**错误处理**: 批次标记无效时读取全量

### Step 4: 执行规则检测
**目标**: 应用审阅规则检测问题
**操作**:

| 规则类别 | 检查项 | 检测方法 |
|----------|--------|----------|
| 完整性 | 必要章节齐全 | 结构分析 |
| 可行性 | 方案可实施 | 逻辑验证 |
| 安全性 | 数据安全、回滚方案 | 风险评估 |
| 兼容性 | 新旧系统兼容 | 接口分析 |
| 测试 | 验证测试计划 | 测试覆盖分析 |

**输出**: 规则检测结果
**错误处理**: 单规则失败不影响其他规则

### Step 5: 生成结构化结果
**目标**: 输出标准化的审阅结果
**操作**:
1. 汇总所有检测结果
2. 按严重程度分类 (CRITICAL/HIGH/MEDIUM/LOW)
3. 计算批次质量分数
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
batch-001 docs/migrations/legacy-to-new.md
```

```
batch-002 docs/migrations/architecture-change.md
```

### 结构化输入 (可选)
```yaml
review:
  batchId: "batch-001"
  filePath: "docs/migrations/legacy-to-new.md"
  chapterRange:
    start: 1
    end: 3
  options:
    strictMode: true
    includeSuggestions: true
```

## Output Format

### 标准输出结构
```json
{
  "batchId": "batch-001",
  "filePath": "docs/migrations/legacy-to-new.md",
  "status": "COMPLETED",
  "chapterRange": {"start": 1, "end": 3},
  "score": 75,
  "summary": {
    "criticalCount": 1,
    "highCount": 3,
    "mediumCount": 8,
    "lowCount": 5
  },
  "issues": [
    {
      "id": "MIG-001",
      "severity": "CRITICAL",
      "chapter": "3.2",
      "category": "安全性",
      "description": "缺少回滚方案",
      "evidence": "第 45 行：未提及回滚策略",
      "recommendation": "必须提供完整的回滚方案"
    },
    {
      "id": "MIG-002",
      "severity": "HIGH",
      "chapter": "2.1",
      "category": "兼容性",
      "description": "未说明向后兼容策略",
      "recommendation": "补充兼容性说明"
    }
  ],
  "categories": {
    "completeness": {"score": 80, "issues": 2},
    "feasibility": {"score": 75, "issues": 3},
    "safety": {"score": 60, "issues": 4},
    "compatibility": {"score": 70, "issues": 2},
    "testing": {"score": 85, "issues": 1}
  }
}
```

### Markdown 输出示例
```markdown
# 改造方案审阅结果

## 基本信息
- **批次**: batch-001
- **文件**: docs/migrations/legacy-to-new.md
- **章节**: 1-3 章
- **分数**: 75/100

## 问题摘要
| 严重程度 | 数量 |
|----------|------|
| CRITICAL | 1 |
| HIGH | 3 |
| MEDIUM | 8 |
| LOW | 5 |

## 详细问题

### CRITICAL (1)

#### MIG-001: 缺少回滚方案
- **章节**: 3.2 数据迁移
- **类别**: 安全性
- **描述**: 改造方案缺少回滚方案
- **证据**: 第 45 行未提及回滚策略
- **建议**: 必须提供完整的回滚方案

### HIGH (3)

#### MIG-002: 未说明向后兼容策略
- **章节**: 2.1 接口变更
- **类别**: 兼容性
- **描述**: 未说明新旧接口的兼容策略
- **建议**: 补充兼容性说明
```

## Error Handling

| 错误场景 | 处理策略 | 示例 |
|----------|----------|------|
| 文件不存在 | 返回错误状态和提示 | "文件不存在：docs/migrations/xxx.md" |
| 批次无效 | 读取全量内容 | "batch-005 无效，读取全量" |
| 规则库缺失 | 使用默认规则 | "migration-antipatterns.md 缺失，使用默认规则" |
| 解析失败 | 跳过问题部分继续 | "第 50-60 行解析失败，已跳过" |
| 内存不足 | 减小批次大小重试 | "内存不足，分批大小减半" |
| 结果生成失败 | 返回部分结果 | "结果生成失败，返回已检测结果" |

## Examples

### Example 1: 标准审阅

**输入**:
```
batch-001 docs/migrations/legacy-to-new.md
```

**输出**:
```json
{
  "batchId": "batch-001",
  "status": "COMPLETED",
  "score": 75,
  "summary": {
    "criticalCount": 1,
    "highCount": 3,
    "mediumCount": 8
  }
}
```

### Example 2: 高质量方案

**输入**:
```
batch-001 docs/migrations/well-designed.md
```

**输出**:
```json
{
  "batchId": "batch-001",
  "status": "COMPLETED",
  "score": 92,
  "summary": {
    "criticalCount": 0,
    "highCount": 0,
    "mediumCount": 2,
    "lowCount": 3
  },
  "message": "改造方案设计良好"
}
```

### Example 3: 高风险方案

**输入**:
```
batch-002 docs/migrations/risky-migration.md
```

**输出**:
```json
{
  "batchId": "batch-002",
  "status": "COMPLETED",
  "score": 45,
  "summary": {
    "criticalCount": 3,
    "highCount": 8,
    "mediumCount": 12
  },
  "recommendation": "方案风险较高，建议重新设计"
}
```

### Example 4: 部分失败处理

**输入**:
```
batch-003 docs/migrations/large-migration.md
```

**输出**:
```json
{
  "batchId": "batch-003",
  "status": "COMPLETED_PARTIAL",
  "note": "第 50-60 行解析失败，已跳过",
  "score": 70
}
```

### Example 5: 空批次处理

**输入**:
```
batch-005 docs/migrations/empty-chapter.md
```

**输出**:
```json
{
  "batchId": "batch-005",
  "status": "EMPTY_BATCH",
  "score": 0,
  "message": "批次内容为空，无法执行审阅"
}
```

## Notes

### Best Practices

1. **分批检测**: 大批次分批处理避免上下文溢出
2. **规则优先**: 按严重程度顺序应用规则
3. **证据记录**: 每个问题都要有明确证据
4. **建议具体**: 修正建议要具体可操作
5. **分数量化**: 用分数直观展示方案质量

### Common Pitfalls

1. ❌ **全量加载**: 大批次一次性加载导致内存溢出
2. ❌ **过度报告**: 报告过多 LOW 级别问题淹没重点
3. ❌ **缺少证据**: 问题没有明确证据支持
4. ❌ **建议空洞**: 建议不可操作无法执行
5. ❌ **分数模糊**: 分数没有分类维度分解

### Review Categories

| 类别 | 权重 | 检查重点 |
|------|------|----------|
| 完整性 | 20% | 必要章节齐全 |
| 可行性 | 25% | 方案可实施 |
| 安全性 | 30% | 数据、回滚 |
| 兼容性 | 15% | 新旧兼容 |
| 测试 | 10% | 验证计划 |

### Severity Levels

| 级别 | 说明 | 处理建议 |
|------|------|----------|
| CRITICAL | 阻塞性问题 | 必须修复 |
| HIGH | 严重问题 | 优先修复 |
| MEDIUM | 中等问题 | 建议修复 |
| LOW | 轻微问题 | 可选修复 |

### Integration with CCC Workflow

```
Migration Plan
    ↓
Migration Review Aggregator (调度)
    ↓
Migration Reviewer Core (本组件) → 分批检测
    ↓
Migration Review Aggregator (聚合)
    ↓
Final Report
```

### File References

- 输入：改造方案文件路径
- 规则库：`docs/antipatterns/migration-antipatterns.md`
- 输出：`docs/migrations/{name}-batch-{id}-result.json`
