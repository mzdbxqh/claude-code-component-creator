# CCC 性能基准测试

## 概述

CCC 性能基准测试框架用于测量和跟踪组件的性能指标，包括执行时间、Token 使用量、成本估算等，确保系统性能符合预期并持续优化。

## 测试维度

### 1. 执行时间 (Execution Time)
- **单组件执行时间**: 单个组件的端到端执行时间
- **工作流总时间**: 完整工作流的总执行时间
- **SubAgent 调用时间**: 各个 SubAgent 的执行时间
- **I/O 操作时间**: 文件读写、API 调用等 I/O 时间

### 2. Token 使用量 (Token Usage)
- **输入 Token**: 提示词和上下文的 Token 数
- **输出 Token**: 生成内容的 Token 数
- **总 Token**: 输入 + 输出 Token
- **Token 效率**: 每个功能点的平均 Token 消耗

### 3. 成本估算 (Cost Estimation)
- **单次执行成本**: 基于 Token 使用量计算
- **批量执行成本**: 大规模使用的成本估算
- **成本效益比**: 功能价值 vs 成本

### 4. 质量指标 (Quality Metrics)
- **输出质量分数**: 生成内容的质量评分
- **准确率**: 正确结果的比例
- **完整性**: 输出的完整程度

## 基准测试套件

### L1: 组件级基准测试

```json
{
  "benchmark_id": "BM-COMPONENT-001",
  "category": "component-level",
  "component": "intent-core",
  "test_cases": [
    {
      "id": "TC-001",
      "name": "简单意图澄清",
      "input": "我想要一个TODO查找器",
      "baseline": {
        "execution_time": 15.2,
        "tokens": {
          "input": 450,
          "output": 850,
          "total": 1300
        },
        "cost": 0.025
      },
      "target": {
        "execution_time": 12.0,
        "tokens": {
          "total": 1100
        },
        "cost": 0.020
      }
    }
  ]
}
```

### L2: 工作流级基准测试

```json
{
  "benchmark_id": "BM-WORKFLOW-001",
  "category": "workflow-level",
  "workflow": "design",
  "test_cases": [
    {
      "id": "TC-001",
      "name": "简单技能设计流程",
      "steps": [
        "intent-core",
        "advisor-core",
        "requirement-core",
        "architect-core",
        "blueprint-core"
      ],
      "baseline": {
        "execution_time": 180.5,
        "tokens": {
          "total": 45000
        },
        "cost": 0.85
      },
      "target": {
        "execution_time": 150.0,
        "tokens": {
          "total": 38000
        },
        "cost": 0.70
      }
    }
  ]
}
```

### L3: 端到端基准测试

```json
{
  "benchmark_id": "BM-E2E-001",
  "category": "end-to-end",
  "scenario": "从意图到交付",
  "test_cases": [
    {
      "id": "TC-001",
      "name": "完整技能创建流程",
      "workflow": "init → design → review → fix → build",
      "baseline": {
        "execution_time": 450.0,
        "tokens": {
          "total": 120000
        },
        "cost": 2.50
      },
      "target": {
        "execution_time": 380.0,
        "tokens": {
          "total": 100000
        },
        "cost": 2.10
      }
    }
  ]
}
```

## 基准数据收集

### 自动化收集

```python
class PerformanceBenchmark:
    """性能基准测试"""

    def __init__(self, component_name):
        self.component_name = component_name
        self.metrics = {
            'execution_time': [],
            'tokens': {
                'input': [],
                'output': [],
                'total': []
            },
            'cost': [],
            'quality_score': []
        }

    def measure_execution(self, test_case):
        """测量执行性能"""
        start_time = time.time()
        start_tokens = self._get_token_count()

        try:
            # 执行测试用例
            result = self._execute_test_case(test_case)

            # 收集指标
            end_time = time.time()
            end_tokens = self._get_token_count()

            metrics = {
                'execution_time': end_time - start_time,
                'tokens': {
                    'input': end_tokens['input'] - start_tokens['input'],
                    'output': end_tokens['output'] - start_tokens['output'],
                    'total': end_tokens['total'] - start_tokens['total']
                },
                'cost': self._calculate_cost(end_tokens - start_tokens),
                'quality_score': self._evaluate_quality(result)
            }

            self._record_metrics(metrics)
            return metrics

        except Exception as e:
            logging.error(f"Benchmark failed: {e}")
            return None

    def _calculate_cost(self, tokens):
        """计算成本"""
        # Claude Sonnet 4.5 定价
        input_cost_per_mtok = 3.0  # $3 per MTok
        output_cost_per_mtok = 15.0  # $15 per MTok

        input_cost = (tokens['input'] / 1_000_000) * input_cost_per_mtok
        output_cost = (tokens['output'] / 1_000_000) * output_cost_per_mtok

        return input_cost + output_cost

    def generate_report(self):
        """生成基准测试报告"""
        return {
            'component': self.component_name,
            'summary': {
                'avg_execution_time': np.mean(self.metrics['execution_time']),
                'p50_execution_time': np.median(self.metrics['execution_time']),
                'p95_execution_time': np.percentile(self.metrics['execution_time'], 95),
                'avg_tokens': np.mean(self.metrics['tokens']['total']),
                'avg_cost': np.mean(self.metrics['cost']),
                'avg_quality': np.mean(self.metrics['quality_score'])
            },
            'detailed_metrics': self.metrics
        }
```

## 基准测试报告

### 报告格式

```markdown
# CCC Performance Benchmark Report

**Generated**: 2026-03-12
**Test Suite**: Full Benchmark (50 tests)
**Environment**: Production

## Executive Summary

| Metric | Current | Baseline | Target | Status |
|--------|---------|----------|--------|--------|
| Avg Execution Time | 12.5s | 15.2s | 12.0s | ⚠️ -4.2% |
| Avg Token Usage | 42K | 50K | 40K | ✅ -16% |
| Avg Cost | $0.78 | $0.95 | $0.75 | ⚠️ +4% |
| Avg Quality Score | 87/100 | 85/100 | 88/100 | ⚠️ -1 |

**Overall Performance**: 🟡 Good (3/4 targets met)

## Component-Level Results

### intent-core

| Test Case | Time (s) | Tokens | Cost | Quality | Status |
|-----------|---------|--------|------|---------|--------|
| Simple Intent | 10.2 ⬇️ | 1100 ⬇️ | $0.019 ⬇️ | 88 ⬆️ | ✅ |
| Complex Intent | 18.5 ⬇️ | 2200 ⬇️ | $0.042 ⬇️ | 86 ⬆️ | ✅ |
| Multi-constraint | 25.3 ⬆️ | 3500 ⬇️ | $0.065 ⬇️ | 84 → | ⚠️ |

**Summary**: 2/3 tests improved, 1 regression (execution time)

### advisor-core

| Test Case | Time (s) | Tokens | Cost | Quality | Status |
|-----------|---------|--------|------|---------|--------|
| Simple Skill | 8.5 ⬇️ | 3200 ⬇️ | $0.055 ⬇️ | 90 ⬆️ | ✅ |
| Complex SubAgent | 15.8 ⬇️ | 5800 ⬇️ | $0.095 ⬇️ | 88 ⬆️ | ✅ |

**Summary**: All tests improved

### blueprint-core

| Test Case | Time (s) | Tokens | Cost | Quality | Status |
|-----------|---------|--------|------|---------|--------|
| Simple Blueprint | 12.3 ⬇️ | 4500 ⬇️ | $0.072 ⬇️ | 89 ⬆️ | ✅ |
| Complex Blueprint | 22.7 → | 8200 ⬇️ | $0.135 ⬇️ | 87 → | ⚠️ |

**Summary**: 1/2 tests fully met targets

## Workflow-Level Results

### Design Workflow

**Steps**: intent-core → advisor-core → requirement-core → architect-core → blueprint-core

| Metric | Current | Baseline | Delta | Target | Status |
|--------|---------|----------|-------|--------|--------|
| Total Time | 165s | 180s | -8.3% | 150s | ⚠️ |
| Total Tokens | 40K | 45K | -11.1% | 38K | ⚠️ |
| Total Cost | $0.75 | $0.85 | -11.8% | $0.70 | ⚠️ |
| Quality Score | 88 | 85 | +3.5% | 88 | ✅ |

**Summary**: Significant improvement but not yet hitting all targets

### Review Workflow

**Steps**: component-scan → review-core → architecture-analyzer → report-renderer

| Metric | Current | Baseline | Delta | Target | Status |
|--------|---------|----------|-------|--------|--------|
| Total Time (10 components) | 95s | 120s | -20.8% | 80s | ⚠️ |
| Total Tokens | 35K | 42K | -16.7% | 32K | ⚠️ |
| Total Cost | $0.68 | $0.82 | -17.1% | $0.60 | ⚠️ |
| Quality Score | 86 | 84 | +2.4% | 87 | ⚠️ |

**Summary**: Good progress, approaching targets

## Performance Trends

### Execution Time Trend (Last 30 Days)

```
20s │
    │     ●
    │   ●   ●
15s │ ●       ●
    │           ●
    │             ● ●
10s │                 ● ●
    │                     ●
 5s │________________________
    Jan    Feb    Mar
```

**Trend**: ⬇️ 35% improvement over 30 days

### Token Usage Trend

```
60K │ ●
    │   ●
50K │     ●
    │       ●
40K │         ● ●
    │             ● ●
30K │                 ●
    │________________________
    Jan    Feb    Mar
```

**Trend**: ⬇️ 30% reduction in token usage

## Cost Analysis

### Monthly Cost Projection

| Scenario | Tests/Month | Current Cost | Target Cost | Delta |
|----------|-------------|--------------|-------------|-------|
| Light Usage | 100 | $78 | $75 | +4% |
| Medium Usage | 500 | $390 | $375 | +4% |
| Heavy Usage | 2000 | $1560 | $1500 | +4% |

**Recommendation**: Optimize token usage to meet cost targets

## Bottleneck Analysis

### Top 5 Slowest Operations

1. **blueprint-core: Complex Blueprint** - 22.7s (24% of workflow time)
2. **architect-core: Architecture Design** - 18.5s (20% of workflow time)
3. **requirement-core: Requirement Analysis** - 15.3s (16% of workflow time)
4. **advisor-core: Complex SubAgent** - 15.8s (17% of workflow time)
5. **review-core: Full Review** - 12.5s (13% of workflow time)

### Optimization Opportunities

1. **blueprint-core**: Reduce template loading time (-5s potential)
2. **architect-core**: Cache design patterns (-3s potential)
3. **requirement-core**: Optimize requirement extraction (-2s potential)

## Recommendations

### High Priority (This Week)

1. **Optimize blueprint-core**
   - Action: Implement template caching
   - Impact: -5s execution time, -1000 tokens
   - Effort: 2 hours

2. **Reduce Token Usage in advisor-core**
   - Action: Simplify prompts, remove redundant context
   - Impact: -800 tokens per execution
   - Effort: 1 hour

### Medium Priority (This Month)

3. **Implement Parallel Review**
   - Action: Add --parallel option to review workflow
   - Impact: -40% execution time for large projects
   - Effort: 4 hours (already completed in Task #77)

4. **Add Response Caching**
   - Action: Cache common LLM responses
   - Impact: -30% token usage for repeated operations
   - Effort: 3 hours

### Low Priority (Next Quarter)

5. **Optimize Report Rendering**
   - Action: Stream report generation
   - Impact: -2s execution time
   - Effort: 2 hours

6. **Implement Token Budget Alerts**
   - Action: Warn when approaching budget limits
   - Impact: Better cost control
   - Effort: 1 hour

## Testing Environment

- **Model**: Claude Sonnet 4.5
- **Pricing**: $3/MTok input, $15/MTok output
- **Test Data**: Production-like scenarios
- **Iterations**: 10 runs per test case
- **Confidence Level**: 95%

## Appendix

### A. Detailed Test Results

See: `benchmarks/2026-03-12-full-results.json`

### B. Historical Data

See: `benchmarks/history/`

### C. Test Artifacts

See: `benchmarks/artifacts/`
```

## 基准测试工具

### benchmark 命令

```bash
# 运行所有基准测试
/ccc:benchmark --all

# 运行特定组件基准测试
/ccc:benchmark --component=intent-core

# 运行特定工作流基准测试
/ccc:benchmark --workflow=design

# 对比两个版本
/ccc:benchmark --compare v1.0.0 v1.1.0

# 生成报告
/ccc:benchmark --report --format=markdown

# 导出数据
/ccc:benchmark --export --output=benchmarks/results.json
```

## 持续监控

### CI/CD 集成

```yaml
# .github/workflows/benchmark.yml
name: Performance Benchmark

on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Run Benchmarks
        run: /ccc:benchmark --all --report

      - name: Compare with Baseline
        run: /ccc:benchmark --compare main HEAD

      - name: Upload Results
        uses: actions/upload-artifact@v2
        with:
          name: benchmark-results
          path: benchmarks/

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        run: |
          /ccc:benchmark --comment-pr
```

### 性能回归检测

```python
def detect_regression(current, baseline, threshold=0.1):
    """检测性能回归"""
    regressions = []

    # 检查执行时间
    if current['execution_time'] > baseline['execution_time'] * (1 + threshold):
        regressions.append({
            'metric': 'execution_time',
            'current': current['execution_time'],
            'baseline': baseline['execution_time'],
            'regression': ((current['execution_time'] / baseline['execution_time']) - 1) * 100
        })

    # 检查Token使用量
    if current['tokens']['total'] > baseline['tokens']['total'] * (1 + threshold):
        regressions.append({
            'metric': 'token_usage',
            'current': current['tokens']['total'],
            'baseline': baseline['tokens']['total'],
            'regression': ((current['tokens']['total'] / baseline['tokens']['total']) - 1) * 100
        })

    return regressions
```

## 最佳实践

1. **定期运行**: 每周运行完整基准测试
2. **版本对比**: 每次发布前对比性能
3. **趋势分析**: 跟踪性能趋势，及时发现问题
4. **目标设定**: 设定清晰的性能目标
5. **自动化**: 集成到 CI/CD 流程
6. **透明度**: 公开性能数据和改进计划

## 附录

### 性能优化清单

- [ ] 实现template缓存
- [ ] 优化prompt简化
- [ ] 添加并行处理
- [ ] 实现响应缓存
- [ ] 优化报告生成
- [ ] 添加Token预算告警
- [ ] 实现增量处理
- [ ] 优化I/O操作

### 参考资料

- [LLM Performance Optimization](https://example.com/llm-perf)
- [Token Usage Best Practices](https://example.com/token-usage)
- [Cost Optimization Guide](https://example.com/cost-opt)
