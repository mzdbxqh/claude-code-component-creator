# CCC 测试框架

## 概述

CCC（Claude Code Component Creator）测试框架提供全面的质量保证机制，确保所有组件在交付前满足质量标准。

## 测试层级

### L1: 单元测试 (Unit Tests)
- **范围**: 单个组件的功能测试
- **工具**: evals.json 测试定义
- **执行**: eval-executor
- **评分**: eval-grader
- **覆盖率目标**: 80%+

### L2: 集成测试 (Integration Tests)
- **范围**: 组件间协作测试
- **工具**: 工作流测试脚本
- **执行**: test-sandbox-core
- **覆盖率目标**: 70%+

### L3: 端到端测试 (E2E Tests)
- **范围**: 完整工作流测试
- **工具**: 综合测试场景
- **执行**: 自动化测试流程
- **覆盖率目标**: 60%+

## 测试类型

### 1. 功能测试 (Functional Tests)

**目标**: 验证组件功能正确性

**测试用例示例**:
```json
{
  "id": "FT-001",
  "name": "意图澄清测试",
  "component": "intent-core",
  "input": "我想要一个TODO查找器",
  "assertions": [
    {
      "type": "output_contains",
      "value": "Intent 制品已创建"
    },
    {
      "type": "file_exists",
      "path": "docs/ccc/intent/INT-*.yaml"
    },
    {
      "type": "yaml_field",
      "path": "docs/ccc/intent/INT-*.yaml",
      "field": "what",
      "contains": "TODO"
    }
  ]
}
```

### 2. 质量测试 (Quality Tests)

**目标**: 验证输出质量达标

**测试用例示例**:
```json
{
  "id": "QT-001",
  "name": "Blueprint 质量测试",
  "component": "blueprint-core",
  "input": {
    "intent_id": "INT-001",
    "requirement": "创建TODO查找器"
  },
  "assertions": [
    {
      "type": "quality_score",
      "metric": "completeness",
      "threshold": 85
    },
    {
      "type": "quality_score",
      "metric": "clarity",
      "threshold": 80
    }
  ]
}
```

### 3. 性能测试 (Performance Tests)

**目标**: 验证执行效率

**测试用例示例**:
```json
{
  "id": "PT-001",
  "name": "审查性能测试",
  "component": "review-core",
  "input": "10个组件",
  "assertions": [
    {
      "type": "execution_time",
      "max_seconds": 120
    },
    {
      "type": "token_usage",
      "max_tokens": 50000
    }
  ]
}
```

### 4. 安全测试 (Security Tests)

**目标**: 验证安全防护措施

**测试用例示例**:
```json
{
  "id": "ST-001",
  "name": "命令注入防护测试",
  "component": "fix-orchestrator",
  "input": {
    "artifact_id": "../../etc/passwd"
  },
  "assertions": [
    {
      "type": "throws_error",
      "error_type": "SecurityError",
      "message_contains": "Invalid artifact-id"
    }
  ]
}
```

## evals.json 结构规范

### 标准格式

```json
{
  "version": "1.0.0",
  "component": "component-name",
  "description": "组件测试套件",
  "testCases": [
    {
      "id": "TC-001",
      "name": "测试用例名称",
      "category": "功能|质量|性能|安全",
      "priority": "P0|P1|P2",
      "prompt": "测试输入提示词",
      "expectedWorkflow": ["step1", "step2"],
      "expectedArtifacts": ["path/to/output"],
      "qualityThresholds": {
        "metricName": 80
      },
      "assertions": [
        {
          "type": "assertion_type",
          "value": "expected_value"
        }
      ]
    }
  ]
}
```

### Assertion 类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `output_contains` | 输出包含指定文本 | `{"type": "output_contains", "value": "成功"}` |
| `file_exists` | 文件存在 | `{"type": "file_exists", "path": "docs/*.yaml"}` |
| `yaml_field` | YAML字段验证 | `{"type": "yaml_field", "field": "name", "value": "xxx"}` |
| `quality_score` | 质量评分 | `{"type": "quality_score", "metric": "completeness", "threshold": 80}` |
| `execution_time` | 执行时间 | `{"type": "execution_time", "max_seconds": 120}` |
| `token_usage` | Token使用量 | `{"type": "token_usage", "max_tokens": 50000}` |
| `throws_error` | 抛出错误 | `{"type": "throws_error", "error_type": "ValueError"}` |
| `regex_match` | 正则匹配 | `{"type": "regex_match", "pattern": "^[A-Z]+-\\d+$"}` |

## 测试执行

### 手动执行

```bash
# 执行单个组件测试
# /ccc:eval-executor (SubAgent - 通过 /cmd-test-sandbox 调用) --component=intent-core

# 执行所有测试
# /ccc:eval-executor (SubAgent - 通过 /cmd-test-sandbox 调用) --all

# 执行特定类别测试
# /ccc:eval-executor (SubAgent - 通过 /cmd-test-sandbox 调用) --category=security
```

### 自动执行（CI/CD）

```yaml
# .github/workflows/test.yml
name: CCC Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run CCC Tests
        run: |
          # /ccc:eval-executor (SubAgent - 通过 /cmd-test-sandbox 调用) --all --report=junit
      - name: Upload Results
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: test-results.xml
```

## 测试覆盖率目标

| 组件类型 | 目标覆盖率 | 优先级 |
|---------|-----------|-------|
| cmd-* (命令) | 90% | P0 |
| std-* (标准) | 80% | P1 |
| lib-* (知识库) | 60% | P2 |
| 核心 Subagents | 85% | P0 |
| 辅助 Subagents | 70% | P1 |
| 工具组件 | 75% | P1 |

## 测试数据管理

### Fixtures 目录结构

```
tests/
├── fixtures/
│   ├── intents/          # 意图测试数据
│   │   ├── simple-skill.yaml
│   │   └── complex-subagent.yaml
│   ├── blueprints/       # 蓝图测试数据
│   │   ├── minimal.yaml
│   │   └── comprehensive.yaml
│   ├── reviews/          # 审查报告测试数据
│   │   └── sample-review.md
│   └── artifacts/        # 其他测试制品
├── mocks/                # Mock 数据
│   ├── llm-responses/    # LLM 响应 mock
│   └── api-responses/    # API 响应 mock
└── utils/                # 测试工具
    ├── assertions.py     # 自定义断言
    └── helpers.py        # 测试辅助函数
```

### Fixture 示例

```yaml
# tests/fixtures/intents/simple-skill.yaml
what: "TODO 查找器"
why: "快速找到项目中的待办事项"
target_users: ["开发者", "项目经理"]
constraints:
  - "不修改代码"
  - "支持多种注释格式"
acceptance_criteria:
  - "找到所有 TODO 注释"
  - "按文件分组显示"
```

## 测试报告

### 报告格式

```json
{
  "test_run_id": "TR-2026-03-12-001",
  "timestamp": "2026-03-12T10:00:00Z",
  "duration_seconds": 450,
  "summary": {
    "total": 50,
    "passed": 45,
    "failed": 3,
    "skipped": 2,
    "pass_rate": 90.0
  },
  "results": [
    {
      "test_id": "TC-001",
      "status": "PASSED",
      "duration": 12.5,
      "tokens_used": 3200
    }
  ],
  "metrics": {
    "total_tokens": 45000,
    "total_cost": 0.85,
    "avg_test_time": 9.0
  }
}
```

### Benchmark 报告

```markdown
# CCC Benchmark Report

## Summary
- **Date**: 2026-03-12
- **Test Suite**: Full Suite (50 tests)
- **Pass Rate**: 90% (45/50)
- **Total Duration**: 7m 30s
- **Total Cost**: $0.85

## Performance Metrics

| Metric | with-skill | baseline | Improvement |
|--------|-----------|----------|-------------|
| Avg Time | 9.0s | 15.2s | 40.8% faster |
| Token Usage | 45K | 68K | 33.8% less |
| Cost | $0.85 | $1.25 | 32.0% cheaper |

## Failed Tests

1. **TC-023**: Security injection test
   - Error: Timeout after 120s
   - Action: Increase timeout threshold

2. **TC-034**: Large project review
   - Error: Out of memory
   - Action: Implement batching

3. **TC-045**: Parallel execution
   - Error: Race condition
   - Action: Add synchronization
```

## 最佳实践

### 1. 测试独立性
- 每个测试用例独立运行
- 不依赖其他测试的状态
- 使用 fixtures 准备测试数据

### 2. 测试可重复性
- 固定随机种子
- Mock 外部依赖
- 清理测试环境

### 3. 测试可维护性
- 清晰的测试命名
- 完整的测试文档
- 模块化测试代码

### 4. 测试效率
- 并行执行独立测试
- 缓存重复数据
- 增量测试（仅测试变更部分）

### 5. 测试覆盖
- 正常流程测试
- 异常流程测试
- 边界条件测试
- 安全性测试

## 组件测试优先级

### P0 (必须有测试)
1. cmd-design
2. cmd-review
3. cmd-fix
4. advisor-core
5. blueprint-core
6. review-core
7. fix-orchestrator

### P1 (建议有测试)
1. cmd-init
2. cmd-validate
3. cmd-build
4. delivery-core
5. reviewer-core
6. architecture-analyzer

### P2 (可选测试)
1. 所有辅助 Subagents
2. 报告渲染器
3. 工具类组件

## 测试维护

### 定期任务
- **每周**: 运行完整测试套件
- **每月**: 更新测试数据
- **每季度**: 审查测试覆盖率
- **每半年**: 重构测试代码

### 测试更新触发条件
1. 组件功能变更
2. 新增功能特性
3. 发现新的 bug
4. 性能优化后
5. 安全加固后

## 工具链

### 使用的工具
- **eval-executor**: 执行测试用例
- **eval-grader**: 评估测试结果
- **eval-parser**: 解析测试定义
- **benchmark-aggregator**: 聚合性能数据
- **test-sandbox-core**: 沙箱测试环境

### CI/CD 集成
- GitHub Actions
- GitLab CI/CD
- Jenkins
- Travis CI

## 附录

### A. 测试模板

参见: `tests/templates/`

### B. 常见问题

参见: `docs/testing-faq.md`

### C. 贡献指南

参见: `docs/contributing-tests.md`
