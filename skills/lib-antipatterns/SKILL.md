---
name: lib-antipatterns
description: "反模式知识库。包含 CCC 收集的 76+ 个反模式定义，覆盖 8 个维度（intent, config, dependency, security, environment, llm, scalability, testability）。由 Subagent 通过 skills: 字段加载。"
model: sonnet
context: main
---

# 反模式知识库

## Purpose

本 Skill 整合了 CCC 从 1338 个样本中提取的反模式知识，用于设计和审阅时的质量检查。

---

## 反模式来源

反模式定义来自：
- `agents/reviewer/knowledge/antipatterns/` - 原始反模式定义（YAML 格式）
- 涵盖 8 个维度：intent, config, dependency, security, environment, llm, scalability, testability

---

## 使用方式

在 Subagent 中通过 skills: 字段加载：

```yaml
---
name: review-core
skills:
  - ccc:lib-antipatterns
---
```

---

## 反模式分类

### Config 维度
- frontmatter 字段缺失
- allowed-tools 不合理

### Dependency 维度
- 循环依赖
- 未声明依赖

### Security 维度
- 权限控制缺失
- 敏感信息泄露

### LLM 维度
- prompt 模糊
- 输出格式不规范

---

## 更新日志

- 2026-03-11: 创建 lib-antipatterns Skill
