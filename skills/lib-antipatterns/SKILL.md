---
name: lib-antipatterns
description: "反模式知识库，76+定义覆盖8维度。由Subagent通过skills字段加载。用于质量检查。"
model: sonnet
allowed-tools: []
context: main
---

# 反模式知识库

## 模型要求

- **推荐**: Claude Sonnet 4.5+ (高效能,最佳性价比)
- **可用**: Claude Haiku 3.5+ (快速加载,知识库类 Skill)
- **最小**: Claude Haiku 3.5+ (最低要求)

### 功能需求
- 作为知识库 Skill,无需 Tool Use
- 通过 skills 字段加载到 Subagent 中
- 建议上下文窗口 >= 50K tokens

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
