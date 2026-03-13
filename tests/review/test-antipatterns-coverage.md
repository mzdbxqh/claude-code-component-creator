# Review 反模式覆盖度测试

**日期**: 2026-03-07
**目标**: 验证所有 76+ 反模式规则都能被正确触发

## 测试方法

1. 对每个规则类别，构造故意违反该规则的测试夹具
2. 运行 /cmd-review 对测试夹具进行审查
3. 验证规则是否正确检出违规行为

## 测试矩阵

| 维度 | 规则数 | 测试文件 | 状态 |
|------|--------|---------|------|
| 意图匹配 | 4 | `test-fixtures/intent-violations/` | ⏳ |
| 配置和使用方法 | 5 | `test-fixtures/config-violations/` | ⏳ |
| 外部基础设施依赖 | 12 | `test-fixtures/dependency-violations/` | ⏳ |
| 安全风险评估 | 5 | `test-fixtures/security-violations/` | ⏳ |
| 环境兼容性 | 3 | `test-fixtures/environment-violations/` | ⏳ |
| LLM 模型兼容性 | 3 | `test-fixtures/llm-violations/` | ⏳ |
| 扩展性 | 4 | `test-fixtures/scalability-violations/` | ⏳ |
| 架构分析 | 15 | `test-fixtures/architecture-violations/` | ⏳ |

## 测试命令

```bash
# 运行单个类别测试
/cmd-review --target=test-fixtures/intent-violations/

# 运行全部测试
/cmd-review --target=test-fixtures/review/
```

## 预期结果

- 覆盖率 ≥ 95%
- 无漏检
- 无误检
