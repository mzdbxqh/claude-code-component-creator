# /cmd-review-workflow 用户指南

**文档版本**: v1.0
**最后更新**: 2026-03-06
**适用版本**: CCC Plugin v3.1+

---

## 快速入门

### 什么是 /cmd-review-workflow？

`/cmd-review-workflow` 是 CCC 插件的工作流串联审查命令，按工作流顺序审查多个关联组件，生成工作流健康度报告。

### 基本用法

```bash
# 审查整个工作流
/cmd-review-workflow --artifact-id=BLP-001

# 指定审查深度
/cmd-review-workflow --artifact-id=BLP-001 --depth=full
```

---

## 参数详解

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--artifact-id` | 当前上下文 | 指定 Blueprint 工件 ID |
| `--depth` | full | 审查深度：shallow/full |

---

## 使用示例

### 示例 1: 标准工作流审查

```bash
/cmd-review-workflow --artifact-id=BLP-001
```

**输出**:
```
工作流健康度报告：BLP-001

工作流完整性评分：100% ✅
阶段交接清晰度评分：85% ⚠️
依赖健康度评分：90% ⚠️

总体评分：92/100 (Grade: A-)
```

---

## 工作流健康度指标

### 1. 工作流完整性

评估工作流各阶段是否完整定义。

| 评分 | 等级 | 说明 |
|------|------|------|
| 90-100 | A | 所有阶段定义完整 |
| 70-89 | B | 大部分阶段完整 |
| <70 | C | 存在阶段缺失 |

---

## 相关命令

| 命令 | 说明 |
|------|------|
| `/cmd-review` | 单组件质量审查 |
| `/cmd-fix` | 交互式修复 |
| `/cmd-status` | 查看项目状态 |

---

*文档生成于 2026-03-06 | CCC Plugin User Guide*
