# review-core Agent 测试指南

## 运行测试

```bash
/ccc:test-sandbox --target=agents/reviewer/review-core
```

## 测试范围

- 反模式规则加载
- 组件质量检查
- 问题分类和评分
- 修复建议生成

## 测试夹具

位于 `test-fixtures/`:
- 各类组件示例
- 预期检测结果

## 通过标准

- 规则加载完整（76+条）
- 检测准确率 ≥ 95%
- 评分合理（与手工评估误差<5%）
