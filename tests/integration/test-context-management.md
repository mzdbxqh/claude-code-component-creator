# 上下文管理验证测试

**日期**: 2026-03-07
**目标**: 验证长上下文下的规则有效性和 SubAgent 边界

## 测试 1: SubAgent 边界识别

### 测试命令

```bash
python3 scripts/analyze-plugin-structure.py --check-context
```

### 预期输出

```
SubAgent Context Analysis:
- ccc:intent-core: fork (isolated) ✅
- ccc:blueprint-core: fork (isolated) ✅
- ccc:delivery-core: fork (isolated) ✅
- ccc:review-core: fork (isolated) ✅
```

## 测试 2: 长上下文规则有效性

### 测试方法

1. 构造不同大小的上下文 (10K, 50K, 100K tokens)
2. 在上下文不同位置放置规则 (开头、中间、结尾)
3. 运行审查，记录检出率

### 测试脚本

```python
# tests/integration/test_context_size.py
def test_long_context_effectiveness():
    results = []
    for size in [10000, 50000, 100000]:
        for position in ['beginning', 'middle', 'end']:
            result = run_review_with_context(size, position)
            results.append({
                'size': size,
                'position': position,
                'detection_rate': result.detection_rate
            })
    return results
```

### 预期结果

| 上下文大小 | 位置 | 预期检出率 |
|-----------|------|-----------|
| 10K tokens | 任意 | ≥ 95% |
| 50K tokens | 开头/结尾 | ≥ 90% |
| 50K tokens | 中间 | ≥ 80% |
| 100K tokens | 开头/结尾 | ≥ 85% |
| 100K tokens | 中间 | ≥ 70% |

## 测试 3: 上下文窗口监控

### 测试命令

```bash
python3 scripts/monitor-context-window.py
```

### 预期行为

- 上下文 < 60%: 正常审查
- 上下文 60-80%: 建议分批审查
- 上下文 > 80%: 自动切换分批审查模式
