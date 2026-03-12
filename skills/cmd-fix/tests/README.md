# cmd-fix 测试指南

## 运行测试

```bash
/ccc:test-sandbox --target=skills/cmd-fix --with-eval
```

## 测试用例

| 测试 | 描述 | 优先级 |
|------|------|--------|
| single_issue_fix | 单问题修复 | critical |
| batch_fix | 批量修复 | high |
| evals_creation_fix | 创建测试定义 | high |
| plugin_manifest_fix | 修复plugin.json | critical |
| circular_dependency_fix | 解除循环依赖 | high |

## 测试夹具

- 审查报告夹具: `../evals/test-fixtures/review-report-*.md`
- 组件夹具: `../evals/test-fixtures/skill-without-evals/`

## 通过标准

- 修复准确率 ≥ 95%
- 无回归问题
- 所有修改可验证
