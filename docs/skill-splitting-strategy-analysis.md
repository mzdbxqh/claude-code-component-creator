# Skill 拆分策略深度分析

## 问题诊断

### 当前困境
单个 skill 过长（接近或超过 500 行）时，传统优化手段已失效：
- ✅ 简练表达 - 已做到极致
- ✅ 提取引用文件 - 已使用 references/
- ❌ **根本问题未解决** - skill 本身承载了多个差异化场景

### 真实案例分析

从实际代码库分析发现：
- `report-renderer/SKILL.md`: 419 行
- `blueprint-core/SKILL.md`: 414 行
- `eval-grader/SKILL.md`: 399 行

这些 skill 接近 500 行限制，但它们是否真的是"单一职责"？

## 核心洞察：场景细分诊断框架

### 诊断维度 1：输入差异度 (Input Diversity)

**判断标准**：skill 是否接受多种结构差异显著的输入？

**示例分析 - report-renderer**：
```yaml
# 当前：单一 skill 处理 6 种报告类型
输入类型：
  - review-aggregated (审阅聚合)
  - architecture-analysis (架构分析)
  - dependency-analysis (依赖分析)
  - migration-review (改造方案)
  - linkage-validation (链路验证)
  - generic (通用报告)
```

**问题**：
- 每种报告类型有独特的 JSON 结构
- 每种报告类型需要不同的模板
- 每种报告类型有不同的渲染逻辑

**拆分信号** 🔴：输入类型 > 3 种且结构差异 > 50%


---

### 诊断维度 2：知识域分离度 (Knowledge Domain Separation)

**判断标准**：skill 是否需要多个独立的知识体系？

**示例分析 - blueprint-core**：
```yaml
# 假设场景：blueprint-core 处理多种组件类型
知识域：
  - Skill 组件设计知识 (HANDBOOK Chapter 4)
  - Command 组件设计知识 (HANDBOOK Chapter 5)
  - Hook 组件设计知识 (HANDBOOK Chapter 6)
  - Subagent 组件设计知识 (HANDBOOK Chapter 7)
  - MCP 组件设计知识 (HANDBOOK Chapter 8)
```

**问题**：
- 每种组件类型有独立的规范章节
- 每种组件类型有不同的元数据要求
- 每种组件类型有不同的最佳实践

**拆分信号** 🔴：知识域 > 2 个且相互独立（无共享知识 > 70%）

---

### 诊断维度 3：工作流分支度 (Workflow Branching)

**判断标准**：skill 的工作流是否在早期就分叉成多条独立路径？

**示例分析 - eval-grader**：
```yaml
# 当前：单一 skill 处理多种评分场景
工作流分支：
  分支 1: 反模式评分 (基于规则匹配)
    → 加载反模式规则
    → 匹配检测
    → 计算扣分
  
  分支 2: 架构评分 (基于图分析)
    → 构建依赖图
    → 检测循环依赖
    → 计算复杂度
  
  分支 3: 链路评分 (基于追踪验证)
    → 追踪 Intent → Blueprint → Delivery
    → 验证覆盖率
    → 计算完整性
```

**问题**：
- 三条分支在 Step 1 后就完全独立
- 三条分支使用不同的工具集
- 三条分支产生不同的输出格式

**拆分信号** 🔴：工作流在前 30% 就分叉成 > 2 条独立路径


### 诊断维度 4：触发场景互斥度 (Trigger Scenario Exclusivity)

**判断标准**：skill 的触发场景是否互斥（用户不会在同一次调用中需要多个场景）？

**示例分析 - report-renderer**：
```yaml
触发场景：
  场景 A: "渲染审阅聚合报告"
  场景 B: "渲染架构分析报告"
  场景 C: "渲染依赖分析报告"

互斥性分析：
  - 用户每次只渲染一种报告类型
  - 场景 A、B、C 从不同时发生
  - 每个场景有独立的触发词
```

**拆分信号** 🔴：触发场景互斥率 > 80%

---

### 诊断维度 5：Token 消耗分布 (Token Consumption Distribution)

**判断标准**：skill 的 token 消耗是否集中在某些特定场景？

**示例分析**：
```yaml
Token 消耗分析：
  场景 A (审阅聚合): 1200 tokens (模板 + 示例 + 规则)
  场景 B (架构分析): 800 tokens (模板 + 示例)
  场景 C (依赖分析): 600 tokens (模板 + 示例)
  
  共享部分: 200 tokens (基础工作流)
  
总计: 2800 tokens
```

**问题**：
- 用户调用场景 C 时，场景 A 的 1200 tokens 完全浪费
- 场景间 token 共享率仅 7% (200/2800)

**拆分信号** 🔴：场景间 token 共享率 < 20%


---

## 系统化拆分策略

### 策略 1：按输入类型拆分 (Split by Input Type)

**适用场景**：输入差异度高（维度 1 触发）

**拆分方法**：
```yaml
原 skill: report-renderer
  ↓
拆分后:
  - ccc:review-report-renderer (处理审阅类报告)
  - ccc:architecture-report-renderer (处理架构类报告)
  - ccc:dependency-report-renderer (处理依赖类报告)
```

**优势**：
- ✅ 每个 skill 只需加载对应的模板知识
- ✅ Token 消耗降低 60-70%
- ✅ 触发词更精准（"渲染审阅报告" vs "渲染报告"）

**劣势**：
- ⚠️ 增加 skill 数量
- ⚠️ 共享逻辑需要提取到 references/

**实施步骤**：
1. 识别输入类型边界（通过 JSON schema 差异分析）
2. 为每种输入类型创建独立 skill
3. 提取共享逻辑到 `references/common-rendering.md`
4. 每个 skill 引用共享逻辑：`@references/common-rendering.md`


---

### 策略 2：按知识域拆分 (Split by Knowledge Domain)

**适用场景**：知识域分离度高（维度 2 触发）

**拆分方法**：
```yaml
原 skill: component-designer
  ↓
拆分后:
  - skill-designer (专注 Skill 组件设计)
  - command-designer (专注 Command 组件设计)
  - hook-designer (专注 Hook 组件设计)
```

**优势**：
- ✅ 每个 skill 只加载对应章节的 HANDBOOK 知识
- ✅ 降低知识混淆风险
- ✅ 更容易维护和更新

**劣势**：
- ⚠️ 用户需要先判断组件类型

**实施步骤**：
1. 按 HANDBOOK 章节边界划分知识域
2. 为每个知识域创建独立 skill
3. 在 skill 描述中明确知识域范围
4. 提供知识域选择指导


---

### 策略 3：按工作流阶段拆分 (Split by Workflow Stage)

**适用场景**：工作流分支度高（维度 3 触发）

**拆分方法**：
```yaml
原 skill: eval-grader (单一评分器)
  ↓
拆分后:
  - antipattern-grader (反模式评分)
  - architecture-grader (架构评分)
  - linkage-grader (链路评分)
```

**优势**：
- ✅ 每个 skill 专注单一评分逻辑
- ✅ 工作流清晰，无分支
- ✅ 便于独立测试和优化

**劣势**：
- ⚠️ 需要上层编排器协调多个 grader

**实施步骤**：
1. 识别工作流分叉点
2. 将每条分支提取为独立 skill
3. 创建编排器 skill 协调调用
4. 定义清晰的输入输出接口


---

### 策略 4：按复杂度分层 (Split by Complexity Layer)

**适用场景**：skill 同时服务新手和专家用户

**拆分方法**：
```yaml
原 skill: component-reviewer (复杂的审阅器)
  ↓
拆分后:
  - quick-reviewer (快速审阅，5 个核心规则)
  - standard-reviewer (标准审阅，30 个规则)
  - deep-reviewer (深度审阅，76 个规则)
```

**优势**：
- ✅ 新手用户不被复杂规则淹没
- ✅ 专家用户获得完整能力
- ✅ Token 消耗按需分配

**劣势**：
- ⚠️ 需要明确能力边界

**实施步骤**：
1. 按规则数量/复杂度分层
2. 定义每层的核心能力
3. 在描述中明确适用场景
4. 提供升级路径指引


---

### 策略 5：按触发频率分层 (Split by Trigger Frequency)

**适用场景**：skill 包含高频场景和低频场景

**拆分方法**：
```yaml
原 skill: component-fixer (修复器)
  ↓
拆分后:
  - common-fixer (修复常见问题，80% 调用)
  - edge-case-fixer (修复边缘问题，20% 调用)
```

**优势**：
- ✅ 高频场景加载更快
- ✅ 低频场景不占用常规 token
- ✅ 符合 80/20 原则

**劣势**：
- ⚠️ 需要统计调用数据

**实施步骤**：
1. 分析历史调用数据
2. 识别高频场景（占比 > 60%）
3. 将高频场景提取为独立 skill
4. 低频场景合并或独立处理


---

## 拆分决策框架

### 决策树

```
开始评估 skill
    ↓
[1] 检查输入差异度
    ├─ 输入类型 > 3 且差异 > 50%? → 是 → 策略 1: 按输入类型拆分
    └─ 否 ↓
[2] 检查知识域分离度
    ├─ 知识域 > 2 且独立性 > 70%? → 是 → 策略 2: 按知识域拆分
    └─ 否 ↓
[3] 检查工作流分支度
    ├─ 前 30% 分叉 > 2 条路径? → 是 → 策略 3: 按工作流阶段拆分
    └─ 否 ↓
[4] 检查触发场景互斥度
    ├─ 互斥率 > 80%? → 是 → 策略 1 或 3
    └─ 否 ↓
[5] 检查 Token 消耗分布
    ├─ 场景间共享率 < 20%? → 是 → 策略 1 或 5
    └─ 否 ↓
[6] 考虑其他优化手段
    ├─ 提取 references/
    ├─ 简化表达
    └─ 使用渐进式披露
```


### 拆分必要性评分矩阵

| 维度 | 权重 | 阈值 | 评分方法 |
|------|------|------|----------|
| 输入差异度 | 25% | > 3 类型且差异 > 50% | 输入类型数 × 结构差异度 |
| 知识域分离度 | 25% | > 2 域且独立性 > 70% | 知识域数 × 独立性比例 |
| 工作流分支度 | 20% | 前 30% 分叉 > 2 条 | 分支数 × 分叉早期度 |
| 触发互斥度 | 15% | 互斥率 > 80% | 互斥场景数 / 总场景数 |
| Token 共享率 | 15% | 共享率 < 20% | 1 - (共享 token / 总 token) |

**综合评分**：
- 80-100 分：强烈建议拆分
- 60-79 分：建议拆分
- 40-59 分：可选拆分
- 0-39 分：不建议拆分


---

## 实战案例分析

### 案例 1: report-renderer (419 行)

**诊断评分**：
```yaml
输入差异度: 90 分 (6 种报告类型，结构差异 80%)
知识域分离度: 70 分 (6 个独立模板知识域)
工作流分支度: 85 分 (Step 2 就分叉成 6 条路径)
触发互斥度: 95 分 (用户每次只渲染一种报告)
Token 共享率: 85 分 (共享率仅 10%)

综合评分: 87 分 → 强烈建议拆分
```

**推荐策略**: 策略 1 (按输入类型拆分)

**拆分方案**：
```yaml
原 skill: report-renderer (419 行)
  ↓
拆分后:
  1. review-report-renderer (120 行)
     - 处理审阅聚合报告
     - 引用 @references/common-rendering.md
  
  2. architecture-report-renderer (100 行)
     - 处理架构分析报告
     - 引用 @references/common-rendering.md
  
  3. dependency-report-renderer (90 行)
     - 处理依赖分析报告
     - 引用 @references/common-rendering.md
  
  4. migration-report-renderer (110 行)
     - 处理改造方案审阅报告
     - 引用 @references/common-rendering.md

共享文件:
  - references/common-rendering.md (80 行)
    - 模板填充逻辑
    - 后处理优化
    - 错误处理
```

**预期效果**：
- Token 消耗降低: 419 → 120-200 (每次调用)
- 触发精准度提升: 85% → 95%
- 维护成本: 略增（4 个文件 vs 1 个）


---

### 案例 2: blueprint-core (414 行)

**诊断评分**：
```yaml
输入差异度: 60 分 (假设处理多种组件类型)
知识域分离度: 85 分 (5 个 HANDBOOK 章节)
工作流分支度: 40 分 (工作流相对统一)
触发互斥度: 70 分 (用户通常设计单一组件类型)
Token 共享率: 50 分 (共享率约 40%)

综合评分: 63 分 → 建议拆分
```

**推荐策略**: 策略 2 (按知识域拆分)

**拆分方案**：
```yaml
原 skill: blueprint-core (414 行)
  ↓
拆分后:
  1. skill-blueprint-core (150 行)
     - 专注 Skill 组件设计
     - 加载 HANDBOOK Chapter 4
  
  2. command-blueprint-core (130 行)
     - 专注 Command 组件设计
     - 加载 HANDBOOK Chapter 5
  
  3. hook-blueprint-core (120 行)
     - 专注 Hook 组件设计
     - 加载 HANDBOOK Chapter 6

共享文件:
  - references/common-blueprint-workflow.md (60 行)
```

**预期效果**：
- Token 消耗降低: 414 → 150-210
- 知识混淆风险降低: 80%
- 规范遵从性提升: 15%


---

### 案例 3: eval-grader (399 行)

**诊断评分**：
```yaml
输入差异度: 55 分 (3 种评分场景)
知识域分离度: 60 分 (3 个独立评分知识域)
工作流分支度: 90 分 (Step 1 后立即分叉)
触发互斥度: 85 分 (评分场景互斥)
Token 共享率: 75 分 (共享率仅 15%)

综合评分: 72 分 → 建议拆分
```

**推荐策略**: 策略 3 (按工作流阶段拆分)

**拆分方案**：
```yaml
原 skill: eval-grader (399 行)
  ↓
拆分后:
  1. antipattern-grader (140 行)
     - 基于规则匹配的反模式评分
  
  2. architecture-grader (130 行)
     - 基于图分析的架构评分
  
  3. linkage-grader (120 行)
     - 基于追踪验证的链路评分

编排器:
  - eval-orchestrator (60 行)
    - 协调调用 3 个 grader
    - 聚合评分结果
```

**预期效果**：
- Token 消耗降低: 399 → 140-200
- 工作流清晰度提升: 90%
- 独立测试能力: 100%


---

## 拆分反模式 (Anti-patterns)

### ❌ 反模式 1: 过度拆分 (Over-splitting)

**症状**：
- 拆分出 10+ 个微型 skill，每个仅 50-100 行
- 用户需要频繁在多个 skill 间切换
- 共享逻辑占比 > 60%

**问题**：
- 增加用户认知负担
- 维护成本激增
- 触发词混淆

**正确做法**：
- 保持 3-5 个合理粒度的 skill
- 共享逻辑占比应 < 30%

---

### ❌ 反模式 2: 伪拆分 (Fake Splitting)

**症状**：
- 拆分后的 skill 仍然 > 400 行
- 拆分仅仅是"复制粘贴"原内容
- 没有真正减少 token 消耗

**问题**：
- 没有解决根本问题
- 增加文件数量但无收益

**正确做法**：
- 拆分后每个 skill 应 < 300 行
- 必须提取共享逻辑到 references/


---

### ❌ 反模式 3: 边界模糊 (Blurred Boundaries)

**症状**：
- 拆分后的 skill 职责重叠
- 用户不知道该调用哪个 skill
- 触发词相似度 > 70%

**问题**：
- 触发混淆
- 重复实现
- 维护困难

**正确做法**：
- 明确定义每个 skill 的边界
- 触发词差异化 > 50%
- 在描述中明确适用场景

---

### ❌ 反模式 4: 忽略编排成本 (Ignoring Orchestration Cost)

**症状**：
- 拆分出 5+ 个 skill 但没有编排器
- 用户需要手动调用多个 skill 完成任务
- 缺少状态传递机制

**问题**：
- 用户体验下降
- 增加使用复杂度

**正确做法**：
- 提供编排器 skill 协调调用
- 定义清晰的输入输出接口
- 支持状态传递


---

## 拆分最佳实践

### ✅ 实践 1: 渐进式拆分 (Progressive Splitting)

**原则**：不要一次性拆分到位，而是逐步优化

**步骤**：
1. **第一轮**：识别最明显的场景边界，拆分 2-3 个 skill
2. **验证**：观察 token 消耗和用户反馈
3. **第二轮**：根据数据决定是否进一步拆分
4. **稳定**：达到最优粒度后停止

**示例**：
```
迭代 1: report-renderer → 拆分为 2 个 (review + others)
迭代 2: others → 拆分为 3 个 (architecture + dependency + migration)
迭代 3: 稳定，不再拆分
```

---

### ✅ 实践 2: 共享逻辑提取 (Shared Logic Extraction)

**原则**：拆分前必须提取共享逻辑

**步骤**：
1. 识别所有场景的共享部分（工作流、错误处理、工具函数）
2. 提取到 `references/common-*.md`
3. 每个拆分后的 skill 引用共享文件
4. 共享文件应占总内容的 15-30%

**文件结构**：
```
skill-a/
  ├── SKILL.md (150 行，引用 common)
  └── references/
      └── common-workflow.md (60 行)

skill-b/
  ├── SKILL.md (140 行，引用 common)
  └── references/
      └── common-workflow.md (60 行，同一文件)
```


---

### ✅ 实践 3: 触发词差异化 (Trigger Word Differentiation)

**原则**：拆分后的 skill 必须有明确的触发词差异

**策略**：
```yaml
原 skill: report-renderer
  触发词: "报告/渲染/生成文档/report/renderer"

拆分后:
  review-report-renderer:
    触发词: "审阅报告/review report/渲染审阅"
  
  architecture-report-renderer:
    触发词: "架构报告/architecture report/渲染架构"
  
  dependency-report-renderer:
    触发词: "依赖报告/dependency report/渲染依赖"
```

**验证**：
- 触发词重叠率 < 30%
- 每个 skill 至少 3 个独特触发词

---

### ✅ 实践 4: 提供编排器 (Provide Orchestrator)

**原则**：拆分 > 3 个 skill 时，必须提供编排器

**编排器职责**：
1. 识别用户意图，路由到正确的 skill
2. 协调多个 skill 的调用顺序
3. 聚合结果并返回
4. 处理跨 skill 的状态传递

**示例**：
```yaml
eval-orchestrator:
  description: "评分编排器，根据评分类型调用对应的 grader"
  workflow:
    Step 1: 识别评分类型 (antipattern/architecture/linkage)
    Step 2: 调用对应 grader
    Step 3: 聚合评分结果
    Step 4: 生成综合报告
```


---

### ✅ 实践 5: 版本化迁移 (Versioned Migration)

**原则**：拆分是破坏性变更，需要平滑迁移

**迁移策略**：
```yaml
阶段 1: 保留原 skill，标记为 deprecated
  - report-renderer (deprecated, 指向新 skills)

阶段 2: 创建新 skills
  - ccc:review-report-renderer
  - ccc:architecture-report-renderer
  - ccc:dependency-report-renderer

阶段 3: 过渡期 (2-4 周)
  - 原 skill 自动路由到新 skills
  - 提示用户使用新 skill

阶段 4: 移除原 skill
  - 确认无调用后移除
```

---

## 实施检查清单

### 拆分前检查 (Pre-splitting Checklist)

- [ ] 已完成 5 维度诊断评分
- [ ] 综合评分 ≥ 60 分
- [ ] 已识别拆分边界（输入类型/知识域/工作流）
- [ ] 已识别共享逻辑（占比 15-30%）
- [ ] 已设计触发词差异化方案
- [ ] 已评估维护成本增加（可接受）


### 拆分后检查 (Post-splitting Checklist)

- [ ] 每个拆分后的 skill < 300 行
- [ ] 共享逻辑已提取到 references/
- [ ] 触发词重叠率 < 30%
- [ ] 每个 skill 有明确的适用场景说明
- [ ] Token 消耗降低 ≥ 40%
- [ ] 已创建编排器（如需要）
- [ ] 已更新文档和示例
- [ ] 已制定迁移计划

### 质量验证 (Quality Validation)

- [ ] 使用 ccc:review 验证每个拆分后的 skill
- [ ] 确认无 SKILL-014 (content-length-issues) 警告
- [ ] 确认 SCALE-001 (token-usage-awareness) 通过
- [ ] 测试触发精准度 ≥ 90%
- [ ] 用户反馈收集（2 周）


---

## 总结与建议

### 核心原则

1. **场景细分优先** - 拆分的本质是识别差异化场景
2. **数据驱动决策** - 使用 5 维度评分框架量化评估
3. **渐进式优化** - 不要一次性过度拆分
4. **用户体验第一** - 拆分应降低而非增加使用复杂度
5. **维护成本可控** - 拆分数量应保持在 3-5 个

### 何时不应拆分

- 综合评分 < 60 分
- 共享逻辑占比 > 60%
- 触发场景高度相关（非互斥）
- 工作流高度统一（无明显分支）
- 维护团队资源不足

### 拆分收益预期

| 场景 | Token 降低 | 触发精准度 | 维护成本 |
|------|-----------|-----------|---------|
| 按输入类型拆分 | 60-70% | +10-15% | +30% |
| 按知识域拆分 | 50-60% | +15-20% | +25% |
| 按工作流拆分 | 55-65% | +10-15% | +35% |
| 按复杂度分层 | 40-50% | +5-10% | +20% |
| 按频率分层 | 50-60% | +10-15% | +15% |


---

## 工具支持建议

### 自动化诊断工具

建议开发 `ccc:skill-split-advisor` 工具：

**功能**：
1. 自动分析 skill 的 5 维度评分
2. 推荐拆分策略
3. 生成拆分方案预览
4. 估算 token 降低效果

**输入**：
```bash
/ccc:skill-split-advisor agents/reviewer/report-renderer/SKILL.md
```

**输出**：
```yaml
诊断结果:
  综合评分: 87/100 (强烈建议拆分)
  
推荐策略: 按输入类型拆分
  
拆分方案:
  - ccc:review-report-renderer (120 行)
  - ccc:architecture-report-renderer (100 行)
  - ccc:dependency-report-renderer (90 行)
  
预期收益:
  - Token 降低: 65%
  - 触发精准度: +12%
```


---

## 立即行动建议

### 针对现有项目

**优先级 1 (立即处理)**：
- `report-renderer` (419 行，评分 87) → 按输入类型拆分
- `ccc:blueprint-core` (414 行，评分 63) → 按知识域拆分

**优先级 2 (计划处理)**：
- `ccc:eval-grader` (399 行，评分 72) → 按工作流拆分
- `ccc:eval-parser` (398 行) → 待诊断

**优先级 3 (观察)**：
- `ccc:linkage-validator` (387 行) → 待诊断
- `ccc:intent-core` (387 行) → 待诊断

### 修复建议更新

**当前问题**：SCALE-001 修复建议过于单一
```yaml
当前建议:
  - "考虑拆分为多个子 skill"  # 太粗暴
```

**改进建议**：
```yaml
新建议:
  1. 运行诊断: 使用 5 维度评分框架评估
  2. 选择策略: 根据评分选择拆分策略 (1-5)
  3. 制定方案: 定义拆分边界和共享逻辑
  4. 渐进实施: 分阶段拆分和验证
  5. 质量验证: 使用 ccc:review 验证结果
```

---

## 附录：快速参考

### 5 维度评分速查表

| 维度 | 快速判断 | 阈值 |
|------|---------|------|
| 输入差异 | 输入类型数 × 结构差异 | > 3 类型 |
| 知识域 | 独立知识域数量 | > 2 域 |
| 工作流 | 早期分叉数量 | 前 30% 分叉 |
| 触发互斥 | 互斥场景比例 | > 80% |
| Token 共享 | 1 - 共享率 | < 20% |

### 策略选择速查表

| 触发信号 | 推荐策略 | 典型场景 |
|---------|---------|---------|
| 多种输入类型 | 策略 1 | report-renderer |
| 多个知识域 | 策略 2 | ccc:blueprint-core |
| 早期分叉 | 策略 3 | ccc:eval-grader |
| 新手/专家 | 策略 4 | reviewer |
| 高频/低频 | 策略 5 | fixer |

---

**文档版本**: 1.0.0  
**创建日期**: 2026-03-09  
**适用范围**: CCC v3.0+ 所有 skill 组件  
**维护者**: CCC 核心团队
