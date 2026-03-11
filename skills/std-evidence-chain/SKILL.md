---
name: ccc:std-evidence-chain
description: "证据链规范。确保工作流需求到实现的完整追溯性。用于设计和审阅组件。"
model: sonnet
allowed-tools: []
context: main
---

# 证据链规范

## 模型要求

- **推荐**: Claude Sonnet 4.5+ (高效能,最佳性价比)
- **可用**: Claude Haiku 3.5+ (快速加载,知识库类 Skill)
- **最小**: Claude Haiku 3.5+ (最低要求)

### 功能需求
- 作为知识库 Skill,无需 Tool Use
- 通过 skills 字段加载到 Subagent 中
- 建议上下文窗口 >= 50K tokens

## 核心原则

1. **可追溯性**：每个设计决策都能追溯到需求来源
2. **可验证性**：提供明确的检查点
3. **完整性**：覆盖从需求到实现的所有环节

## 证据链结构

### 层次1：工作流设计
- 工作流各阶段的职责
- 阶段间的输入输出关系

### 层次2：能力需求
- 每个阶段需要什么能力
- 能力的具体表现形式

### 层次3：Skill映射
- 能力由哪个skill提供
- Skill的当前状态（现有/迭代/新建）

### 层次4：验证清单
- 可检查的断言列表
- 每个断言的验证方法

---

## 更新日志

- 2026-03-11: 创建 std-evidence-chain Skill
