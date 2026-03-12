# cmd-review 测试指南

## 运行测试

```bash
/ccc:test-sandbox --target=skills/cmd-review --with-eval
```

## 测试用例

参见 `../evals/evals.json` 了解完整测试定义。

| 测试 | 描述 | 优先级 |
|------|------|--------|
| basic_component_review | 单组件审查 | critical |
| multi_component_review | 全项目审查 | critical |
| antipattern_detection | 反模式检测 | high |
| plugin_manifest_validation | Plugin配置验证 | critical |

## 测试夹具

测试夹具位于 `../evals/test-fixtures/`:
- `sample-skill/` - 示例skill组件
- `sample-plugin/` - 示例plugin项目
- `problematic-skill/` - 包含问题的skill
- `invalid-plugin/` - 配置错误的plugin

## 通过标准

- 所有critical测试通过
- 审查报告生成完整
- 问题检测准确率 ≥ 95%
- 修复建议可行
