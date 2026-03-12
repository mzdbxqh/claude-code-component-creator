---
name: std-workflow-attribution
description: "工作流归属标注规范。检查组件的工作流定位标注。用于设计和审查插件流程定位。"
context: main
allowed-tools: []
model: sonnet
---

# 工作流归属标注规范

## 模型要求

- **推荐**: Claude Sonnet 4.5+ (高效能,最佳性价比)
- **可用**: Claude Haiku 3.5+ (快速加载,知识库类 Skill)
- **最小**: Claude Haiku 3.5+ (最低要求)

### 功能需求
- 作为知识库 Skill,无需 Tool Use
- 通过 skills 字段加载到 Subagent 中
- 建议上下文窗口 >= 50K tokens

## 目的

为入口型Skill（cmd-前缀）提供明确的工作流归属信息，帮助用户和审核者理解：
1. 该Skill是独立使用还是某工作流的一部分
2. 如果是工作流的一部分，完整流程是什么
3. 该Skill在流程中的位置

## 标注规范

### 规则1: description中标注归属

**格式**:
```yaml
description: "[功能描述] | 场景: [归属类型]"
```

**归属类型**:
- `独立工具` - 可单独使用，无上下游依赖
- `主工作流的第X步` - 属于主要工作流程
- `代码迭代流程的第X步` - 属于代码改进流程
- `制品迭代流程的核心` - 属于制品优化流程
- `多流程的检查点/修复点` - 多个流程共用
- `快捷工具（集成多个流程）` - 封装多个步骤

**示例**:
```yaml
# 独立工具
description: "查询项目状态 | 场景: 独立工具"

# 集成场景
description: "生成Blueprint | 场景: 主工作流的第2步"
description: "执行迭代计划 | 场景: 代码迭代流程的第2步"
description: "质量审查 | 场景: 多流程的检查点"
```

---

### 规则2: SKILL.md第一行补充完整流程（仅集成场景）

**独立工具**：无需补充

**集成场景格式**:
```markdown
# /ccc:xxx

**完整流程**: 步骤1 → 步骤2 → **当前** → 步骤4 → 步骤5

[原有功能描述]
```

**多流程交汇点格式**:
```markdown
# /ccc:xxx

**适用流程**:
- **主工作流**: `design` → **review** → `fix` → `validate` → `build`
- **代码迭代**: `implement` → **review** → `fix`
- **制品迭代**: `iterate` → **review** → `fix` → `build`

[原有功能描述]
```

**标注约定**:
- 用反引号包裹其他skill: `design`
- 用加粗标注当前位置: **implement**
- 用普通文本描述非skill节点: 现有代码、Blueprint-v1

---

### 规则3: 检查标准

**设计新插件时**，确保：
- [ ] 所有cmd-前缀skill的description包含"| 场景: ..."标注
- [ ] 集成场景skill在SKILL.md第一行有完整流程图
- [ ] 流程图中当前位置用加粗标注
- [ ] 独立工具不需要流程图

**审查现有插件时**，检查：
- [ ] description是否包含归属标注
- [ ] 归属标注是否准确（是否真的独立/集成）
- [ ] 集成场景是否有完整流程图
- [ ] 流程图是否标注当前位置

---

## 反模式

### ❌ 反模式1: description中展开完整流程

```yaml
# 错误示例
description: "生成Blueprint | 流程: init → design → review → fix → validate → build"
```

**问题**: description过长，挤占提示词空间

**正确做法**:
```yaml
description: "生成Blueprint | 场景: 主工作流的第2步"
```

---

### ❌ 反模式2: 独立工具添加流程图

```markdown
# 错误示例
# /ccc:status

**完整流程**: 项目目录 → **status** → 状态报告

[...]
```

**问题**: 独立工具没有上下游依赖，不需要流程图

**正确做法**:
```markdown
# /ccc:status

Displays current project workflow state and artifact status.
```

---

### ❌ 反模式3: 集成场景缺少流程图

```markdown
# 错误示例
# /ccc:implement

Implements iteration plans from design-iterate.

## Usage
```

**问题**: 用户不知道implement前后应该做什么

**正确做法**:
```markdown
# /ccc:implement

**完整流程**: `design-iterate` → **implement** → `review` → `fix`

Implements iteration plans from design-iterate.

## Usage
```

---

### ❌ 反模式4: 流程图不标注当前位置

```markdown
# 错误示例
**完整流程**: design-iterate → implement → review → fix
```

**问题**: 无法快速识别当前位置

**正确做法**:
```markdown
**完整流程**: `design-iterate` → **implement** → `review` → `fix`
```

---

## 应用场景

### 场景1: CCC设计新插件

当 `cmd-design` 生成新插件的Skill时：
1. 询问用户：这是独立工具还是某工作流的一部分？
2. 如果是工作流一部分，询问完整流程
3. 自动在description中添加归属标注
4. 自动在SKILL.md第一行添加流程图

---

### 场景2: CCC审查现有插件

当 `cmd-review` 审查插件时：
1. 检查所有cmd-skill的description是否包含归属标注
2. 检查集成场景skill是否有流程图
3. 验证归属标注与实际上下游关系是否一致
4. 生成审查报告，标注不符合规范的skill

---

## 示例库

### 主工作流（6个）

完整流程: `init` → `design` → `review` → `fix` → `validate` → `build`

#### 示例: cmd-init

```yaml
---
name: ccc:cmd-init
description: "创建Intent制品 | 场景: 主工作流的起点"
---

# /ccc:init

**完整流程**: **init** → `design` → `review` → `fix` → `validate` → `build`

Create Intent artifact using 4-question framework.
```

#### 示例: cmd-design

```yaml
---
name: ccc:cmd-design
description: "生成Blueprint | 场景: 主工作流的第2步"
---

# /ccc:design

**完整流程**: `init` → **design** → `review` → `fix` → `validate` → `build`

Creates comprehensive blueprint artifacts from intent specifications.
```

#### 示例: cmd-review (多流程交汇点)

```yaml
---
name: ccc:cmd-review
description: "质量审查 | 场景: 多流程的检查点"
---

# /ccc:review

**适用流程**:
- **主工作流**: `design` → **review** → `fix` → `validate` → `build`
- **代码迭代**: `implement` → **review** → `fix`
- **制品迭代**: `iterate` → **review** → `fix` → `build`

Performs comprehensive component quality review.
```

---

### 迭代工作流A：代码迭代（2个）

完整流程: 现有代码 → `design-iterate` → `implement` → `review` → `fix`

#### 示例: cmd-design-iterate

```yaml
---
name: cmd-design-iterate
description: "生成迭代方案 | 场景: 代码迭代流程的起点"
---

# /ccc:design-iterate

**完整流程**: 现有代码 → **design-iterate** → `implement` → `review` → `fix`

Iterate on existing components - analyze current vs target state.
```

#### 示例: cmd-implement

```yaml
---
name: cmd-implement
description: "执行迭代计划 | 场景: 代码迭代流程的第2步"
---

# /ccc:implement

**完整流程**: `design-iterate` → **implement** → `review` → `fix`

Implements iteration plans from design-iterate.
```

---

### 迭代工作流B：制品迭代（1个）

完整流程: Blueprint-v1 → `iterate` → Blueprint-v2 → `review` → `fix` → `build`

#### 示例: cmd-iterate

```yaml
---
name: ccc:cmd-iterate
description: "迭代Blueprint | 场景: 制品迭代流程的核心"
---

# /ccc:iterate

**完整流程**: Blueprint-v1 → **iterate** → Blueprint-v2 → `review` → `fix` → `build`

Iterates on existing blueprint artifacts to create improved versions.
```

---

### 独立工具（8个）

#### 示例: cmd-status

```yaml
---
name: cmd-status
description: "查询项目状态 | 场景: 独立工具"
---

# /ccc:status

Displays current project workflow state and artifact status.
```

#### 示例: cmd-diff

```yaml
---
name: cmd-diff
description: "对比制品差异 | 场景: 独立工具"
---

# /ccc:diff

Compares differences between two artifact versions.
```

#### 示例: cmd-quick (快捷工具)

```yaml
---
name: cmd-quick
description: "快速完整流程 | 场景: 快捷工具（集成多个流程）"
---

# /ccc:quick

**等价流程**: **quick** ≈ `init` → `design` → `build`（自动化执行）

Executes complete workflow from intent to delivery in a single command.
```

---

## 总结

通过简洁的归属标注（description）+ 精准的流程图（第一行），在最小token消耗（~500 tokens）的情况下，让每个skill都能清晰表达自己的工作流定位，同时作为CCC的设计和审查标准，推动整个Claude Code插件生态的规范化。
