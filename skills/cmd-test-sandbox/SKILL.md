---
name: ccc:cmd-test-sandbox
model: sonnet
context: fork
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep]
description: "运行自动化沙箱测试验证 CCC 插件功能。适用场景：集成测试、工作流验证、质量门禁。输出包含测试用例结果、通过率统计、质量评分和失败诊断的测试报告。支持 5 个测试类别（Simple Skill、Complex SubAgent、Data Transform、Review、Quick Workflow）和 Dry Run 模式。关键动作：测试、验证、评估、诊断。独立工具。 [支持平台: macOS, Linux, Windows (via WSL)]"
argument-hint: "[--test-case=<id>] [--dry-run] [--verbose]"
---

# /ccc:test-sandbox

Runs automated sandbox tests to verify CCC plugin functionality including intent→blueprint→delivery workflow and review features.

## 模型要求

- **推荐**: Claude Sonnet 4.5+ (高效能,最佳性价比)
- **可用**: Claude Opus 4.5+ (最高质量,完整测试)
- **最小**: Claude Sonnet 4.5+ (最低要求)

### 功能需求
- 需要支持 Tool Use (Bash, Read, Write, Edit, Glob, Grep)
- 需要支持多轮对话和测试执行
- 需要处理完整工作流测试
- 建议上下文窗口 >= 200K tokens (处理多个测试用例)

## SubAgents 协作

本工作流使用以下 SubAgents 进行任务执行：

### 核心 Agents
- **ccc:test-sandbox-core**: 沙箱测试核心，负责测试环境准备、用例执行和结果收集

### 调度策略
- **串行执行**: cmd-test-sandbox → ccc:test-sandbox-core → 逐个执行测试用例
- **并行执行**: 无（测试用例顺序执行以避免干扰）
- **错误处理**: 单个测试失败时记录结果，继续执行其他测试

### Agent 输入输出
| Agent | 输入 | 输出 |
|-------|------|------|
| ccc:test-sandbox-core | 测试用例 ID 列表 + 运行参数 | 测试报告（通过率、失败诊断）|

### 调用示例
```
用户: /ccc:test-sandbox
  ↓
cmd-test-sandbox 准备测试环境
  ↓
调用 ccc:test-sandbox-core (执行所有测试用例):
  TC-001: TODO 查找器 (Simple Skill)
  TC-002: 代码审查器 (Complex SubAgent)
  TC-003: YAML 转 JSON (Data Transform)
  TC-004: 全面项目审查 (Review)
  TC-005: 一键快速工作流 (Quick Workflow)
  ↓
收集测试结果并生成报告
  ↓
cmd-test-sandbox 输出测试摘要和通过率
```

## Usage

```bash
# 运行所有测试用例
/ccc:test-sandbox

# 运行特定测试用例
/ccc:test-sandbox --test-case=TC-001

# 干运行（不实际创建文件）
/ccc:test-sandbox --dry-run

# 详细输出模式
/ccc:test-sandbox --verbose
```

## Test Cases

| ID | 名称 | 类型 | 预计耗时 |
|------|------|------|---------|
| TC-001 | TODO 查找器 | Simple Skill | 2 分钟 |
| TC-002 | 代码审查器 | Complex SubAgent | 3 分钟 |
| TC-003 | YAML 转 JSON | Data Transform | 2 分钟 |
| TC-004 | 全面项目审查 | Comprehensive Review | 4 分钟 |
| TC-005 | 一键快速工作流 | Quick Workflow | 3 分钟 |

## Workflow

### Step 1: 准备测试环境
**目标**: 创建隔离的测试目录
**操作**:
1. 创建临时测试目录 `docs/ccc/sandbox-test-{timestamp}/`
2. 复制测试夹具文件
3. 初始化测试上下文
**输出**: 测试环境就绪
**错误处理**: 目录创建失败时使用内存模拟

### Step 2: 运行测试用例
**目标**: 执行每个测试用例
**操作**:
```
FOR each test case IN evals/evals.json DO
  1. 运行测试 prompt
  2. 捕获实际工作流
  3. 验证输出文件
  4. 记录测试结果
END FOR
```
**输出**: 测试结果集合
**错误处理**: 单个测试失败不影响其他测试

### Step 3: 验证完整链路
**目标**: 验证 intent → blueprint → delivery 链路
**操作**:
1. 检查 Intent 文件创建
2. 检查 Blueprint 文件创建
3. 检查 Delivery 文件创建
4. 验证追溯性矩阵
**输出**: 链路验证报告
**错误处理**: 链路中断时标注断点位置

### Step 4: 生成测试报告
**目标**: 输出结构化测试结果
**操作**:
1. 汇总所有测试结果
2. 计算通过率
3. 识别失败原因
4. 生成改进建议
5. 写入报告文件
**输出**: 测试报告文件
**错误处理**: 写入失败时输出到控制台

## Output Specification

### Console Output

```
🧪 CCC Sandbox Test Report

Test Environment: docs/ccc/sandbox-test-20260307-143022/
Test Cases: 5
Start Time: 2026-03-07 14:30:22

Running Tests...
┌─────────────────────────────────────────────────────┐
│ TC-001: TODO 查找器                    ✅ PASSED    │
│   Intent Quality: 89/100 (threshold: 80)           │
│   Blueprint Quality: 92/100 (threshold: 85)        │
│   Delivery Compliance: 88/100 (threshold: 80)      │
│   Execution Time: 1m 45s                           │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ TC-002: 代码审查器                   ✅ PASSED    │
│   Intent Quality: 85/100 (threshold: 80)           │
│   Blueprint Quality: 88/100 (threshold: 85)        │
│   Delivery Compliance: 90/100 (threshold: 80)      │
│   Execution Time: 2m 30s                           │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ TC-003: YAML 转 JSON                 ⚠️ WARN      │
│   Intent Quality: 82/100 (threshold: 80)           │
│   Blueprint Quality: 84/100 (threshold: 85) ❌     │
│   Delivery Compliance: 86/100 (threshold: 85)      │
│   Execution Time: 1m 52s                           │
│   Warning: Blueprint 质量略低于阈值                  │
└─────────────────────────────────────────────────────┘

Summary:
┌─────────────────────────────────────────────────────┐
│ Total: 5  |  Passed: 4  |  Warn: 1  |  Failed: 0   │
│ Pass Rate: 100% (warning不计入失败)                  │
│ Average Execution Time: 2m 18s                      │
└─────────────────────────────────────────────────────┘

Full Report: docs/ccc/sandbox-test-20260307-143022/report.md
```

### File Output

| 属性 | 值 |
|------|-----|
| **目录** | `docs/ccc/sandbox-test-{timestamp}/` |
| **报告文件** | `report.md` |
| **JSON 结果** | `results.json` |
| **保留策略** | 保留 7 天，自动清理 |

## Options

| 参数 | 值 | 默认值 | 说明 |
|------|-----|--------|------|
| `--test-case` | TC-001~TC-005 | 全部 | 运行特定测试用例 |
| `--dry-run` | - | false | 不实际创建文件，仅验证逻辑 |
| `--verbose` | - | false | 输出详细调试信息 |

## Error Handling

| 错误场景 | 处理策略 | 用户可见消息 |
|----------|----------|-------------|
| 测试目录创建失败 | 使用内存模拟继续 | "无法创建测试目录，使用内存模式继续" |
| 测试用例执行超时 | 标记超时，继续下一测试 | "测试超时（>5 分钟），已标记并继续" |
| 输出文件未生成 | 记录失败，继续其他测试 | "未生成预期文件：{path}" |
| 质量阈值不达标 | 记录警告，不算失败 | "质量 {score}/100 低于阈值 {threshold}" |
| 测试中断 | 保存已完成的测试结果 | "测试中断，已完成 {n}/{total} 个测试" |

## Examples

### Example 1: 运行所有测试

```bash
/ccc:test-sandbox
```

**输出**: 执行 5 个测试用例，生成完整报告

### Example 2: 运行单个测试

```bash
/ccc:test-sandbox --test-case=TC-001
```

**输出**: 仅执行 TODO 查找器测试

### Example 3: 干运行验证

```bash
/ccc:test-sandbox --dry-run
```

**输出**: 验证测试逻辑，不实际创建文件

### Example 4: 详细模式调试

```bash
/ccc:test-sandbox --verbose
```

**输出**: 包含详细的调试信息和中间结果

## Notes

### Best Practices

1. **定期运行**: 每次重大修改后运行沙箱测试
2. **发布前验证**: 发布新版本前必须通过所有测试
3. **隔离环境**: 测试在独立目录运行，不影响主项目
4. **自动清理**: 测试完成后自动清理临时文件

### Common Pitfalls

1. ❌ **跳过测试**: 修改核心逻辑后不运行测试
2. ❌ **忽略警告**: 警告可能是潜在问题的前兆
3. ❌ **手动修改**: 不要手动修改测试结果文件
4. ❌ **长期保留**: 测试目录应在验证后清理

### Test Case Categories

| Category | Description | Test Cases |
|----------|-------------|------------|
| Simple Skill | 单步骤简单技能 | TC-001 |
| Complex SubAgent | 多步骤复杂代理 | TC-002 |
| Data Transform | 数据转换技能 | TC-003 |
| Review | 审查功能 | TC-004 |
| Quick Workflow | 一键快速流程 | TC-005 |

### Integration with CI/CD

```bash
# 在 CI/CD 流程中运行测试
/ccc:test-sandbox --dry-run --verbose

# 检查测试通过率
if [ $(cat results.json | jq '.passRate') -ge 90 ]; then
  echo "✅ Tests passed"
  exit 0
else
  echo "❌ Tests failed"
  exit 1
fi
```
