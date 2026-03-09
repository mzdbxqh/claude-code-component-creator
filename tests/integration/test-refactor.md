# 重构架构集成测试 (Refactored Architecture Integration Tests)

> 验证 v2.0 架构各组件协同工作

---

## 测试概述 (Test Overview)

| 测试项 | 目标 | 优先级 |
|--------|------|--------|
| /design-new 完整流程 | 验证 5 阶段设计流程 | P0 |
| /design-iterate 差异分析 | 验证增量设计能力 | P0 |
| /review 递归审阅 | 验证依赖分析和审阅 | P0 |
| 命令组合使用 | 验证工作流组合 | P1 |

---

## 测试 1: /design-new 完整流程

### 测试目标
验证 5 阶段设计流程完整执行，生成预期输出。

### 前置条件
- 所有 advisor/*-core Subagent 可用
- design-new-core 已配置
- 输出目录 `docs/designs/` 可写

### 测试步骤

#### Step 1: 启动设计流程

```bash
/design-new
```

#### Step 2: 回答需求收集问题

```
Claude: 这个组件要解决什么问题？
User: 创建一个自动部署工具，支持 Docker 和 Kubernetes

Claude: 目标用户是谁？
User: DevOps 工程师

Claude: 有什么约束条件吗？
User: 需要集成到现有 CI/CD 流程

Claude: 是否有现有系统上下文需要提供？
User: /commands/ci.md
```

#### Step 3: 验证各阶段执行

**Stage 1: requirement-core**
- [ ] 成功执行
- [ ] 生成需求规格说明书
- [ ] 展示关键决策：需求范围确认

**Stage 2: architect-core**
- [ ] 成功执行
- [ ] 推荐组件类型：Skill
- [ ] 展示关键决策：组件类型与清单

**Stage 3: design-core**
- [ ] 成功执行
- [ ] 生成详细设计
- [ ] 展示关键决策：执行流程设计

**Stage 4: validator-core**
- [ ] 成功执行
- [ ] 生成验证报告
- [ ] 合规性检查通过

**Stage 5: planner-core**
- [ ] 成功执行
- [ ] 生成实施计划
- [ ] 展示关键决策：里程碑与交付物

#### Step 4: 验证输出

**预期输出文件**: `docs/designs/2026-02-28-deploy-skill-design.md`

**文件结构检查**:
```markdown
# deploy-skill 设计方案

## 1. 需求分析
- [ ] 功能需求章节
- [ ] 关键决策：需求范围

## 2. 架构设计
- [ ] 组件类型选择
- [ ] 关键决策：组件类型与清单

## 3. 详细设计
- [ ] 元数据设计
- [ ] 关键决策：执行流程设计

## 4. 验证报告
- [ ] 规范符合性检查
- [ ] 关键信息：合规性与风险提示

## 5. 实施计划
- [ ] 任务分解
- [ ] 关键决策：里程碑与交付物
```

### 通过标准
- [ ] 5 个阶段全部成功完成
- [ ] 输出文档包含所有必需章节
- [ ] 每个阶段都有关键决策记录
- [ ] 文档保存到正确位置

---

## 测试 2: /design-iterate 差异分析

### 测试目标
验证基于现有组件的增量设计能力。

### 前置条件
- 存在测试组件: `commands/deploy.md`
- design-iterate-core 已配置
- dependency-analyzer 可用

### 测试步骤

#### Step 1: 准备测试组件

创建测试组件 `commands/deploy.md`:
```yaml
---
name: deploy
description: Deploy application to production
argument-hint: "<app-name> [--env production]"
---

# deploy

Deploy application using Docker or Kubernetes.

## Usage

```
/deploy my-app --env production
```
```

#### Step 2: 启动迭代流程

```bash
/design-iterate commands/deploy.md
```

#### Step 3: 回答迭代问题

```
Claude: 请描述你要新增或修改的功能：
User: 增加对 Helm chart 的支持

Claude: 有什么约束条件吗？
User: 保持现有 Docker 功能不变
```

#### Step 4: 验证分析步骤

**Step 4.1: 现状分析**
- [ ] 正确读取 deploy.md
- [ ] 识别当前功能：Docker ✅ K8s ✅ Helm ❌
- [ ] 生成依赖图

**Step 4.2: 差异分析**
- [ ] 识别新增功能：Helm 支持
- [ ] 标记 Breaking Changes：无
- [ ] 兼容性分析：向后兼容

**Step 4.3: 方案生成**
- [ ] 生成最小变更方案
- [ ] 提供备选方案
- [ ] 方案对比分析

**Step 4.4: 影响评估**
- [ ] 分析依赖组件影响
- [ ] 评估上游变更需求

**Step 4.5: 实施规划**
- [ ] 任务分解
- [ ] 里程碑设定
- [ ] 回滚策略

### 预期输出

**输出文件**: `docs/designs/2026-02-28-deploy-iteration-design.md`

**内容检查**:
```markdown
## 1. 现状分析
- [ ] 当前组件结构
- [ ] 依赖关系图
- [ ] 功能清单 (Docker ✅ K8s ✅ Helm ❌)

## 2. 需求差异分析
- [ ] 新增功能：Helm 支持
- [ ] Breaking Changes: 无

## 3. 迭代方案
- [ ] 推荐方案：创建 helm-deployer
- [ ] 备选方案对比
- [ ] 关键决策记录

## 4. 影响评估
- [ ] 依赖组件影响
- [ ] 兼容性分析

## 5. 实施计划
- [ ] 任务清单
- [ ] 回滚策略
```

### 通过标准
- [ ] 正确分析现有组件状态
- [ ] 准确识别需求差异
- [ ] 生成可行的变更方案
- [ ] 影响评估完整
- [ ] 实施计划包含回滚策略

---

## 测试 3: /review 递归审阅

### 测试目标
验证递归依赖分析和全量审阅功能。

### 前置条件
- 存在测试组件集
- dependency-analyzer 可用
- review-core 已配置
- review-aggregator 已配置

### 测试步骤

#### Step 1: 准备测试组件集

创建测试组件结构：
```
commands/
└── test-deploy.md      # 入口组件
subagents/
├── test-builder.md     # 依赖 1
└── test-validator.md   # 依赖 2
skills/
└── test-utils.md       # 深层依赖
```

**test-deploy.md**:
```yaml
---
name: test-deploy
description: Short
subagents:
  - test-builder
  - test-validator
---
```

**test-builder.md**:
```yaml
---
name: test-builder
description: Build component
skills:
  - test-utils
---
```

#### Step 2: 执行审阅

```bash
/review commands/test-deploy.md
```

#### Step 3: 验证依赖分析

- [ ] 识别所有 4 个组件
- [ ] 构建正确的依赖图
- [ ] 计算最大深度：3

**预期依赖图**:
```
test-deploy (Command)
├── test-builder (Subagent)
│   └── test-utils (Skill)
└── test-validator (Subagent)
```

#### Step 4: 验证并行审阅

- [ ] 为每个组件调用 review-core
- [ ] 按组件类型加载对应反模式
  - Command 反模式 → test-deploy
  - Subagent 反模式 → test-builder, test-validator
  - Skill 反模式 → test-utils

#### Step 5: 验证跨组件检查

- [ ] 检查工具权限一致性
- [ ] 检查模型兼容性
- [ ] 检测循环依赖

#### Step 6: 验证结果聚合

- [ ] 聚合所有组件的 issues
- [ ] 计算合规分数
- [ ] 生成修复优先级（P0/P1/P2/P3）

### 预期输出

**控制台摘要**:
```
智能审阅报告
================

入口：commands/test-deploy.md
组件总数：4
问题总数：X（Error: Y, Warning: Z, Info: W）
平均合规分数：XX%

依赖图：
test-deploy (Command) [XX%]
├── test-builder (Subagent) [XX%]
│   └── test-utils (Skill) [XX%]
└── test-validator (Subagent) [XX%]

详细报告已保存至：docs/reviews/2026-02-28-test-deploy-review.md
```

**报告文件检查**:
```markdown
# 智能审阅报告

## 审阅概览
- [ ] 组件总数：4
- [ ] 问题统计
- [ ] 平均合规分数

## 依赖图
- [ ] 可视化依赖关系
- [ ] 每个组件显示合规分数

## 按组件问题清单
- [ ] test-deploy (Command) - issues
- [ ] test-builder (Subagent) - issues
- [ ] test-validator (Subagent) - issues
- [ ] test-utils (Skill) - issues

## 跨组件依赖问题
- [ ] 工具权限问题（如有）
- [ ] 模型兼容性问题（如有）

## 修复优先级建议
- [ ] P0 问题列表
- [ ] P1 问题列表
- [ ] P2 问题列表

## 组件合规分数表
- [ ] 每个组件的分数
```

### 通过标准
- [ ] 正确识别所有依赖组件
- [ ] 依赖图准确
- [ ] 每个组件都被审阅
- [ ] 跨组件问题被检测
- [ ] 合规分数计算正确
- [ ] 报告保存到正确位置

---

## 测试 4: 命令组合使用

### 测试目标
验证多个命令组合使用的完整工作流。

### 场景 1: 设计 + 审阅

**工作流**:
```
/design-new → 生成设计 → /review → 验证质量
```

**步骤**:
1. 使用 `/design-new` 设计新组件
2. 实现组件（手动或自动）
3. 使用 `/review` 审阅实现结果
4. 验证设计 vs 实现的一致性

**检查点**:
- [ ] 设计文档中的架构决策在实现中得到体现
- [ ] 审阅发现的 issues 数量在可接受范围
- [ ] 合规分数 > 80%

### 场景 2: 审阅 + 迭代

**工作流**:
```
/review → 发现问题 → /design-iterate → 生成优化方案
```

**步骤**:
1. 使用 `/review` 审阅现有组件
2. 识别需要改进的地方
3. 使用 `/design-iterate` 规划优化
4. 实施优化
5. 再次 `/review` 验证改进

**检查点**:
- [ ] 审阅发现的问题被迭代设计解决
- [ ] 迭代方案包含所有必要的变更
- [ ] 优化后合规分数提升

### 场景 3: 完整开发生命周期

**工作流**:
```
/design-new → 实现 → /review → /design-iterate → 优化 → /review
```

**步骤**:
1. `/design-new` - 初始设计
2. 实现 MVP
3. `/review` - 检查 MVP 质量
4. `/design-iterate` - 规划功能扩展
5. 实现扩展功能
6. `/review` - 最终质量检查

**检查点**:
- [ ] 每个阶段都有文档输出
- [ ] 质量逐步提升
- [ ] 最终合规分数 > 85%

---

## 测试执行计划

### 环境准备

```bash
# 1. 确保所有 Subagent 配置正确
ls agents/reviewer/design-new-core/SKILL.md
ls agents/reviewer/design-iterate-core/SKILL.md
ls agents/reviewer/review-core/SKILL.md
ls agents/reviewer/dependency-analyzer/SKILL.md
ls agents/reviewer/review-aggregator/SKILL.md

# 2. 确保所有 advisor Subagent 存在
ls agents/advisor/requirement-core/SKILL.md
ls agents/advisor/architect-core/SKILL.md
ls agents/advisor/design-core/SKILL.md
ls agents/advisor/validator-core/SKILL.md
ls agents/advisor/planner-core/SKILL.md

# 3. 确保反模式库完整
ls agents/reviewer/knowledge/antipatterns/schema.json
ls agents/reviewer/knowledge/antipatterns/skill/*.yaml | wc -l  # 预期: 15
ls agents/reviewer/knowledge/antipatterns/command/*.yaml | wc -l  # 预期: 12
ls agents/reviewer/knowledge/antipatterns/hook/*.yaml | wc -l  # 预期: 10
ls agents/reviewer/knowledge/antipatterns/subagent/*.yaml | wc -l  # 预期: 12
ls agents/reviewer/knowledge/antipatterns/mcp/*.yaml | wc -l  # 预期: 8

# 4. 确保输出目录存在
mkdir -p docs/designs
mkdir -p docs/reviews
```

### 执行顺序

| 顺序 | 测试 | 依赖 |
|------|------|------|
| 1 | /design-new 完整流程 | 无 |
| 2 | /design-iterate 差异分析 | 测试1的输出 |
| 3 | /review 递归审阅 | 无 |
| 4 | 命令组合使用 | 测试1-3 |

### 回归测试

确保重构不破坏原有功能：
- [ ] 原有 `/review-migration` 命令仍可用
- [ ] 反模式库可被正确加载
- [ ] 组件类型识别准确

---

## 测试结果记录

### 测试 1: /design-new

| 检查项 | 状态 | 备注 |
|--------|------|------|
| Stage 1 完成 | ⬜ | |
| Stage 2 完成 | ⬜ | |
| Stage 3 完成 | ⬜ | |
| Stage 4 完成 | ⬜ | |
| Stage 5 完成 | ⬜ | |
| 文档生成 | ⬜ | |

**测试日期**: ___________
**测试人员**: ___________
**结果**: ⬜ 通过 / ⬜ 失败

### 测试 2: /design-iterate

| 检查项 | 状态 | 备注 |
|--------|------|------|
| 现状分析 | ⬜ | |
| 差异分析 | ⬜ | |
| 方案生成 | ⬜ | |
| 影响评估 | ⬜ | |
| 实施规划 | ⬜ | |
| 文档生成 | ⬜ | |

**测试日期**: ___________
**测试人员**: ___________
**结果**: ⬜ 通过 / ⬜ 失败

### 测试 3: /review

| 检查项 | 状态 | 备注 |
|--------|------|------|
| 依赖分析 | ⬜ | |
| 并行审阅 | ⬜ | |
| 跨组件检查 | ⬜ | |
| 结果聚合 | ⬜ | |
| 报告生成 | ⬜ | |

**测试日期**: ___________
**测试人员**: ___________
**结果**: ⬜ 通过 / ⬜ 失败

### 测试 4: 命令组合

| 场景 | 状态 | 备注 |
|------|------|------|
| 设计 + 审阅 | ⬜ | |
| 审阅 + 迭代 | ⬜ | |
| 完整生命周期 | ⬜ | |

**测试日期**: ___________
**测试人员**: ___________
**结果**: ⬜ 通过 / ⬜ 失败

---

## 附录

### 快速测试命令

```bash
# 测试 /design-new
echo "测试 /design-new..."
# claude /design-new

# 测试 /design-iterate
echo "测试 /design-iterate..."
# claude /design-iterate commands/deploy.md

# 测试 /review
echo "测试 /review..."
# claude /review commands/deploy.md

# 验证输出
echo "检查输出文件..."
ls -la docs/designs/*.md
ls -la docs/reviews/*.md
```

### 常见问题排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| Stage 执行失败 | Subagent 配置错误 | 检查 SKILL.md 配置 |
| 依赖分析失败 | 文件路径错误 | 检查文件是否存在 |
| 审阅超时 | 组件过多 | 增加超时设置 |
| 报告未生成 | 目录权限 | 检查 docs/ 目录权限 |

---

**文档版本**: 1.0.0
**最后更新**: 2026-02-28
