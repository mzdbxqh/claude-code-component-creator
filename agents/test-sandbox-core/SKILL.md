---
name: test-sandbox-core
description: "沙箱测试核心：执行自动化测试验证 CCC 功能→运行测试用例→生成测试报告。触发：测试/sandbox/验证/test/verify"
argument-hint: "[--test-case=<id>] [--dry-run] [--verbose]"
context: fork
model: sonnet
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
---

# Test Sandbox Core

## Purpose

Test Sandbox Core 是自动化测试执行组件，负责：
1. **读取测试用例** - 从 `evals/evals.json` 加载测试定义
2. **执行测试流程** - 运行 intent→blueprint→delivery 完整链路
3. **验证输出文件** - 检查生成的制品是否符合预期
4. **生成测试报告** - 输出结构化的测试结果

## Workflow

### Step 1: 加载测试配置
**目标**: 读取并解析测试用例定义
**操作**:
1. 读取 `evals/evals.json` 文件
2. 解析测试用例结构
3. 验证测试配置完整性
**输出**: 测试用例列表
**错误处理**: 文件不存在时返回预定义测试用例

### Step 2: 准备测试环境
**目标**: 创建隔离的测试执行环境
**操作**:
1. 创建临时测试目录 `docs/ccc/sandbox-test-{timestamp}/`
2. 初始化测试状态文件
3. 设置测试超时配置（默认 5 分钟/用例）
**输出**: 测试环境就绪
**错误处理**: 目录创建失败时使用内存模拟

### Step 3: 执行测试用例
**目标**: 运行单个测试用例
**操作**:
```
FUNCTION executeTestCase(testCase):
  1. 记录开始时间
  2. 执行测试 prompt
  3. 等待工作流完成
  4. 捕获实际输出
  5. 验证质量阈值
  6. 记录测试结果
  RETURN testResult
END FUNCTION
```
**输出**: 单个测试结果
**错误处理**: 超时或失败时记录错误继续

### Step 4: 验证完整链路
**目标**: 验证 intent → blueprint → delivery 链路完整性
**操作**:
1. 检查 Intent 文件存在性和格式
2. 检查 Blueprint 文件存在性和格式
3. 检查 Delivery 文件存在性和格式
4. 验证追溯性（Blueprint 引用 Intent，Delivery 引用 Blueprint）
**输出**: 链路验证报告
**错误处理**: 链路中断时标注断点位置

### Step 5: 聚合测试结果
**目标**: 汇总所有测试结果
**操作**:
1. 统计通过/警告/失败数量
2. 计算通过率
3. 计算平均执行时间
4. 识别常见问题模式
**输出**: 测试结果聚合
**错误处理**: 聚合失败时输出原始结果

### Step 6: 生成测试报告
**目标**: 输出结构化的测试报告
**操作**:
1. 生成 Markdown 格式报告
2. 生成 JSON 格式结果
3. 可视化测试状态
4. 写入报告文件
**输出**: 测试报告文件
**错误处理**: 写入失败时输出到控制台

## Input Format

### 基本输入
```
[--test-case=<id>] [--dry-run] [--verbose]
```

### 输入示例
```
--test-case=TC-001
--dry-run --verbose
```

## Output Format

### 标准输出结构
```json
{
  "testRunId": "sandbox-20260307-143022",
  "status": "COMPLETED",
  "summary": {
    "totalTests": 5,
    "passed": 4,
    "warned": 1,
    "failed": 0,
    "passRate": 100,
    "averageExecutionTime": "2m 18s"
  },
  "testResults": [
    {
      "testCaseId": "TC-001",
      "name": "TODO 查找器",
      "status": "PASSED",
      "executionTime": "1m 45s",
      "metrics": {
        "intentQuality": 89,
        "blueprintQuality": 92,
        "deliveryCompliance": 88
      },
      "artifacts": ["INT-001.yaml", "BLP-001.yaml", "SKILL.md"]
    }
  ]
}
```

## Error Handling

| 错误场景 | 处理策略 | 用户可见消息 |
|----------|----------|-------------|
| 测试配置加载失败 | 使用预定义测试用例 | "测试配置加载失败，使用默认测试用例" |
| 测试环境创建失败 | 使用内存模拟继续 | "无法创建测试目录，使用内存模式" |
| 测试执行超时 | 标记超时，继续下一测试 | "测试超时，已标记并继续" |
| 输出文件验证失败 | 记录失败原因 | "验证失败：{reason}" |
| 报告写入失败 | 输出到控制台 | "报告写入失败，结果如下：" |

## Examples

### Example 1: 运行所有测试

**输入**:
```
无参数
```

**输出**:
```
🧪 执行 5 个测试用例...

TC-001: TODO 查找器 ✅ PASSED
TC-002: 代码审查器 ✅ PASSED
TC-003: YAML 转 JSON ⚠️ WARN
TC-004: 全面项目审查 ✅ PASSED
TC-005: 一键快速工作流 ✅ PASSED

通过率：100%
```

### Example 2: 运行单个测试

**输入**:
```
--test-case=TC-001
```

**输出**:
```
🧪 执行测试 TC-001: TODO 查找器

✅ PASSED - 执行时间：1m 45s
Intent Quality: 89/100
Blueprint Quality: 92/100
Delivery Compliance: 88/100
```

## Notes

### Best Practices

1. **隔离环境**: 测试在独立目录运行
2. **自动清理**: 测试完成后清理临时文件
3. **结果可重现**: 相同的测试用例产生一致的结果
4. **超时保护**: 每个测试用例设置超时限制

### Test Categories

| Category | Description |
|----------|-------------|
| Simple Skill | 单步骤简单技能测试 |
| Complex SubAgent | 多步骤复杂代理测试 |
| Data Transform | 数据转换技能测试 |
| Review | 审查功能测试 |
| Quick Workflow | 一键快速流程测试 |

### File References

- 输入：`evals/evals.json`
- 输出：`docs/ccc/sandbox-test-{timestamp}/report.md`
- 输出：`docs/ccc/sandbox-test-{timestamp}/results.json`
