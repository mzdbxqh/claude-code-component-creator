# CCC 插件最佳实践指南

**文档版本**: v1.0
**最后更新**: 2026-03-06
**适用版本**: CCC Plugin v3.1+

---

## 修复最佳实践

### 1. 审查后立即修复

审查发现的问题应尽快修复，避免问题累积。

```bash
# 推荐工作流
/ccc:review --artifact-id=DLV-001
/ccc:fix --artifact-id=DLV-001
/ccc:review --artifact-id=DLV-002  # 验证修复效果
```

### 2. 首次使用交互式模式

首次使用 `/ccc:fix` 时，建议使用交互式模式了解修复内容。

```bash
# 首次使用
/ccc:fix --artifact-id=DLV-001

# 熟悉后可使用自动模式
/ccc:fix --artifact-id=DLV-002 --auto
```

### 3. 使用 dry-run 预览

在不确定修复内容时，先用 dry-run 模式预览。

```bash
/ccc:fix --artifact-id=DLV-001 --dry-run
```

---

## 工作流审查最佳实践

### 1. 定期执行工作流审查

建议每周或每次重大变更后执行工作流审查。

```bash
# 每周审查
/ccc:review-workflow --artifact-id=latest
```

### 2. 关注交接清晰度

工作流阶段间的交接是问题高发区域。

**检查要点**:
- 输入输出定义是否清晰
- 阶段间数据传递是否正确
- 异常处理是否连贯

---

## Skill Description 最佳实践

### 1. 四段式结构

```yaml
description: |
  [技能名称/类型]：[核心语义]
  [关键原则]
  触发：[触发词列表]
```

**示例**:
```yaml
description: |
  测试驱动开发 (TDD)：Bug 修复/功能实现时先写失败测试→写最小代码通过→重构
  铁律：无失败测试不写生产代码
  触发：测试/TDD/红绿重构/测试先行
```

### 2. 触发词设计原则

- **覆盖同义词**: 包含中文、英文、缩写
- **包含场景**: 描述使用场景
- **积极主动**: 使用"无论何时"、"即使"等词汇

**示例**:
```yaml
description: |
  代码审查工具，检查代码质量、编码规范和潜在问题。
  无论何时用户提交代码变更、请求代码审查或询问代码质量问题，都应该使用此技能。
  即使只是小的修改或简单的功能添加，也建议使用此技能确保代码一致性。
  触发：代码审查/code review/PR/代码质量/编码规范/最佳实践
```

---

## 性能优化建议

### 1. 批量审查时使用并行

```bash
# 使用 ccc:review-aggregator 并行审查多个组件
ccc-review --target=. --parallel
```

### 2. 跳过不必要的检查

```bash
# 仅需基础合规性检查时跳过架构分析
/ccc:review --target=. --no-arch
```

### 3. 使用缓存

```bash
# 复用已有审查结果
/ccc:review --artifact-id=DLV-001 --use-cache
```

---

## 常见问题模式

### 问题模式 1: 元数据缺失

**症状**: 组件缺少 name、description、argument-hint 等字段

**修复**:
```bash
/ccc:fix --artifact-id=DLV-001
# 或手动修复
# 编辑 SKILL.md 添加缺失的 frontmatter 字段
```

### 问题模式 2: 工具权限未声明

**症状**: 使用了工具但未在 allowed-tools 中声明

**修复**:
```bash
/ccc:fix --artifact-id=DLV-001
# 工具声明代理会自动分析实际使用的工具并添加声明
```

### 问题模式 3: 文档不完整

**症状**: 缺少示例、错误处理、注意事项章节

**修复**:
```bash
/ccc:fix --artifact-id=DLV-001
# 文档完善代理会补充缺失章节
```

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-03-06 | 初始版本 |

---

*文档生成于 2026-03-06 | CCC Plugin Best Practices*
