# CCC 工作流参考

本文档定义 CCC 的三种标准工作流，确保所有文档和命令使用一致的术语。

**版本**: v3.1.4+
**更新日期**: 2026-03-15

---

## 三种标准工作流

### 1. 开发流程（Development Workflow）

**目的**: 从需求到交付的完整开发流程
**步骤**: 7 步
**适用场景**: 新组件开发、新功能实现

```
开发流程（7步）:
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  1. init         创建 Intent（需求定义）                        │
│      ↓                                                         │
│  2. design       生成 Blueprint（设计文档）                     │
│      ↓                                                         │
│  3. implement    实现代码（从 Blueprint）                       │
│      ↓                                                         │
│  4. review       质量审查（161+ 反模式检查）                    │
│      ↓                                                         │
│  5. fix          修复问题（基于审查报告）                       │
│      ↓                                                         │
│  6. validate     验证修复（语法、Schema、Token）                │
│      ↓                                                         │
│  7. build        生成交付物（生产就绪）                         │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**命令序列**:
```bash
/cmd-init              # 第1步：创建 Intent
/cmd-design            # 第2步：生成 Blueprint
/cmd-implement --blueprint=BLP-001.md  # 第3步：实现代码
/cmd-review            # 第4步：质量审查
/cmd-fix               # 第5步：修复问题
/cmd-validate          # 第6步：验证修复
/cmd-build             # 第7步：生成交付物
```

**关键特点**:
- **implement 环节**: 新增的实现步骤，从 Blueprint 生成代码
- **完整追溯**: 从 Intent 到 Delivery 的完整链条
- **质量保障**: review + fix + validate 三重质量检查

---

### 2. 迭代流程（Iteration Workflow）

**目的**: 对现有组件进行重构、优化、升级
**步骤**: 4 步
**适用场景**: 代码重构、性能优化、功能升级

```
迭代流程（4步）:
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  现有代码                                                       │
│      ↓                                                         │
│  1. design-iterate   分析差异，生成迭代计划                     │
│      ↓                                                         │
│  2. implement        应用增量变更（从 Iteration Plan）          │
│      ↓                                                         │
│  3. review           质量审查（检查迭代结果）                    │
│      ↓                                                         │
│  4. fix              修复问题                                   │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**命令序列**:
```bash
/cmd-design-iterate components/my-component/  # 第1步：生成迭代计划
/cmd-implement --plan=ITER-001.md            # 第2步：应用变更
/cmd-review                                  # 第3步：审查结果
/cmd-fix                                     # 第4步：修复问题
```

**关键特点**:
- **增量变更**: 基于现有代码的增量修改
- **差异分析**: design-iterate 自动分析当前 vs 目标状态
- **快速迭代**: 跳过 Intent 和 Blueprint 阶段

---

### 3. 制品迭代流程（Artifact Iteration Workflow）

**目的**: 优化 Blueprint 设计，生成改进版本
**步骤**: 3 步
**适用场景**: 设计优化、架构改进、Blueprint 重构

```
制品迭代流程（3步）:
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  Blueprint v1                                                  │
│      ↓                                                         │
│  1. iterate          优化设计，生成 Blueprint v2                │
│      ↓                                                         │
│  2. review           审查新设计                                 │
│      ↓                                                         │
│  3. build            从 Blueprint v2 生成交付物                 │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**命令序列**:
```bash
/cmd-iterate --artifact-id=BLP-001   # 第1步：优化 Blueprint
/cmd-review                          # 第2步：审查新设计
/cmd-build --artifact-id=BLP-002     # 第3步：生成交付物
```

**关键特点**:
- **设计层迭代**: 在 Blueprint 层面进行优化
- **不涉及代码**: 只修改设计文档，不直接改代码
- **版本递增**: 自动生成 v2、v3 等版本

---

## 工作流选择决策树

```
┌─────────────────────────────────────────────────────────┐
│ 我应该使用哪个工作流？                                   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
           ┌──────────────────────────────┐
           │ 是否从零开始创建新组件？      │
           └──────────────────────────────┘
                    │              │
                是  │              │ 否
                    ▼              ▼
          ┌─────────────┐   ┌─────────────────┐
          │ 开发流程    │   │ 已有什么？       │
          │ (7 步)     │   └─────────────────┘
          └─────────────┘          │
                            ┌──────┴──────┐
                            │             │
                      有代码实现      有 Blueprint
                            │             │
                            ▼             ▼
                    ┌─────────────┐  ┌─────────────┐
                    │ 迭代流程    │  │ 制品迭代    │
                    │ (4 步)     │  │ 流程 (3步)  │
                    └─────────────┘  └─────────────┘
```

**决策问题**:

1. **从零开始？** → 开发流程（7步）
2. **已有代码实现？** → 迭代流程（4步）
3. **只有 Blueprint？** → 制品迭代流程（3步）

---

## 工作流对比

| 特征 | 开发流程 | 迭代流程 | 制品迭代 |
|------|---------|---------|---------|
| **步骤数** | 7 | 4 | 3 |
| **起点** | 需求（Intent） | 现有代码 | 现有 Blueprint |
| **终点** | 交付物 | 修复完成 | 新交付物 |
| **是否生成代码** | ✓ | ✓ | ✓ (从新 Blueprint) |
| **是否需要 Intent** | ✓ | ✗ | ✗ |
| **是否需要 Blueprint** | ✓ | ✗ | ✓ |
| **质量检查** | review + validate | review | review |
| **典型耗时** | 60-90 分钟 | 20-30 分钟 | 15-25 分钟 |

---

## 常见场景映射

| 场景 | 推荐工作流 | 理由 |
|------|-----------|------|
| 创建新的 Skill | 开发流程 | 需要完整的需求分析和设计 |
| 创建新的 SubAgent | 开发流程 | 需要完整的需求分析和设计 |
| 重构现有组件 | 迭代流程 | 已有代码，只需增量修改 |
| 性能优化 | 迭代流程 | 已有代码，只需增量修改 |
| 添加新功能到现有组件 | 迭代流程 | 已有代码，增量添加功能 |
| 优化 Blueprint 设计 | 制品迭代 | 不涉及代码，只优化设计 |
| 架构调整（仅设计层） | 制品迭代 | 不涉及代码，只优化设计 |
| 修复审查发现的问题 | 不需要完整流程 | 直接使用 /cmd-fix |

---

## 工作流命名规范

### ✅ 正确的术语

- **开发流程**（Development Workflow）
- **迭代流程**（Iteration Workflow）
- **制品迭代流程**（Artifact Iteration Workflow）

### ❌ 已废弃的术语

- ~~主工作流~~ → 使用"开发流程"
- ~~完整流程~~ → 使用"开发流程"
- ~~代码迭代~~ → 使用"迭代流程"
- ~~设计迭代~~ → 使用"制品迭代流程"

---

## 工作流状态追踪

CCC 支持通过 `/cmd-status` 追踪工作流执行状态：

```bash
/cmd-status

# 输出示例：
Current Workflow: Development (Step 3/7)
Status: In Progress

Completed:
  ✓ init     - Intent created (INT-001)
  ✓ design   - Blueprint generated (BLP-001)
  ✓ implement - Code implemented

Current:
  ⧗ review   - Quality check in progress

Pending:
  ○ fix
  ○ validate
  ○ build
```

---

## 工作流文档索引

**命令文档**:
- [cmd-init](../skills/cmd-init/SKILL.md) - 开发流程第1步
- [cmd-design](../skills/cmd-design/SKILL.md) - 开发流程第2步
- [cmd-implement](../skills/cmd-implement/SKILL.md) - 开发流程第3步、迭代流程第2步
- [cmd-review](../skills/cmd-review/SKILL.md) - 所有流程都适用
- [cmd-fix](../skills/cmd-fix/SKILL.md) - 所有流程都适用
- [cmd-validate](../skills/cmd-validate/SKILL.md) - 开发流程第6步
- [cmd-build](../skills/cmd-build/SKILL.md) - 开发流程第7步、制品迭代第3步
- [cmd-design-iterate](../skills/cmd-design-iterate/SKILL.md) - 迭代流程第1步
- [cmd-iterate](../skills/cmd-iterate/SKILL.md) - 制品迭代流程第1步

**用户指南**:
- [CCC 最佳实践](best-practices/ccc-best-practices.md)
- [迭代最佳实践](best-practices/iteration-best-practices.md)
- [Review 工作流指南](user-guide/ccc-review-workflow-user-guide.md)
- [Fix 用户指南](user-guide/ccc-fix-user-guide.md)

---

**文档版本**: v3.1.4
**最后更新**: 2026-03-15
**维护者**: CCC 核心团队
