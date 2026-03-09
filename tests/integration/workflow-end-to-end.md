# CCC 插件端到端工作流测试

**测试文件**: `workflow-end-to-end.md`
**测试目标**: 验证 Intent→Blueprint→Delivery 完整工作流程正确性
**最后更新**: 2026-03-07

---

## 测试用例

### TC-E2E-001: 简单技能完整工作流

**目的**: 验证简单技能从 Intent 到 Delivery 的完整流程

**前置条件**:
- CCC 插件已安装
- 当前目录为 CCC 项目根目录

**测试步骤**:

1. 创建测试需求："创建一个查找 TODO 注释的技能"
2. 执行 `/ccc:quick "创建一个查找 TODO 注释的技能"`
3. 验证生成的所有制品

**预期流程**:
```
Intent Core → Blueprint Core → Delivery Core
    ↓              ↓               ↓
INT-xxx.yaml  →  BLP-xxx.yaml  →  DLV-xxx/
```

**预期产物**:
```
docs/ccc/intent/INT-*.yaml          # Intent 制品
docs/ccc/blueprint/BLP-*.yaml       # Blueprint 制品
docs/ccc/delivery/DLV-*/SKILL.md    # Delivery 制品
docs/ccc/delivery/DLV-*/tests/      # 测试框架
```

**验证命令**:
```bash
# 验证 Intent 制品
ls docs/ccc/intent/INT-*.yaml

# 验证 Blueprint 制品
ls docs/ccc/blueprint/BLP-*.yaml

# 验证 Delivery 制品
ls docs/ccc/delivery/*/SKILL.md

# 验证测试框架
ls docs/ccc/delivery/*/tests/evals.json
ls docs/ccc/delivery/*/tests/README.md
```

**通过标准**:
- 所有制品文件存在
- testPlan 正确传递到 delivery
- 测试框架正确生成

---

### TC-E2E-002: 复杂 SubAgent 完整工作流

**目的**: 验证复杂 SubAgent 从 Intent 到 Delivery 的完整流程

**前置条件**:
- CCC 插件已安装

**测试步骤**:

1. 创建测试需求："需要一个 SubAgent 自动化代码审查流程"
2. 执行 `/ccc:quick "需要一个 SubAgent 自动化代码审查流程，包括读取变更文件、检查编码规范、生成审查报告"`
3. 验证生成的所有制品

**预期流程**:
```
Intent (complex) → Blueprint (complex) → Delivery (with implementation)
```

**预期产物**:
```
docs/ccc/intent/INT-*.yaml
docs/ccc/blueprint/BLP-*.yaml
docs/ccc/delivery/DLV-*/
├── SKILL.md
├── implementation/          # SubAgent 需要实现代码
│   ├── main.py
│   └── utils.py
├── tests/
│   ├── evals.json
│   └── README.md
└── metadata.yaml
```

**验证命令**:
```bash
# 验证实现代码
ls docs/ccc/delivery/*/implementation/

# 验证测试框架
ls docs/ccc/delivery/*/tests/
```

**通过标准**:
- implementation/目录存在
- 测试框架包含集成测试
- 所有制品完整

---

### TC-E2E-003: testStrategy 传递测试

**目的**: 验证 testStrategy 从 Intent 正确传递到 Delivery

**前置条件**:
- CCC 插件已安装

**测试步骤**:

1. 执行完整工作流
2. 检查 Intent 的 testStrategy
3. 检查 Blueprint 的 testPlan
4. 检查 Delivery 的 tests/evals.json
5. 验证数据一致性

**预期数据流**:
```yaml
# Intent testStrategy
testStrategy:
  coreScenario: "查找 TODO 注释"
  boundaryCases:
    - "空目录：返回空列表"
    - "无 TODO: 返回提示"

# Blueprint testPlan (应该基于 testStrategy)
testPlan:
  testTypes:
    - type: "功能测试"
    - type: "边界测试"
      testCases:
        - "空目录测试"
        - "无 TODO 测试"

# Delivery tests/evals.json (应该基于 testPlan)
{
  "testCases": [
    {"category": "functional", ...},
    {"category": "boundary", ...}
  ]
}
```

**验证命令**:
```bash
# 提取 Intent testStrategy
grep -A 10 "testStrategy" docs/ccc/intent/INT-*.yaml

# 提取 Blueprint testPlan
grep -A 20 "testPlan" docs/ccc/blueprint/BLP-*.yaml

# 提取 Delivery evals.json
cat docs/ccc/delivery/*/tests/evals.json
```

**通过标准**:
- testStrategy 完整传递
- testPlan 与 testStrategy 一致
- evals.json 与 testPlan 一致

---

## 边界测试

### TC-E2E-Boundary-001: 模糊需求处理

**目的**: 验证模糊需求在工作流中的处理

**前置条件**:
- CCC 插件已安装

**测试步骤**:

1. 输入模糊需求："做一个很厉害的工具"
2. 执行 `/ccc:quick "做一个很厉害的工具"`
3. 观察各阶段处理

**预期行为**:
```
Intent: 追问澄清或生成带假设的 Intent
Blueprint: 标注基于假设的设计
Delivery: 生成通用框架，标注需手动完善
```

**通过标准**:
- 不中断流程
- 各阶段标注假设
- 提供完善建议

---

### TC-E2E-Boundary-002: 超大需求处理

**目的**: 验证超大需求在工作流中的处理

**前置条件**:
- CCC 插件已安装

**测试步骤**:

1. 输入超大需求（超过 5000 字符）
2. 执行工作流
3. 观察各阶段处理

**预期行为**:
```
Intent: 提取核心需求，标注详细信息参考附录
Blueprint: 基于核心需求设计
Delivery: 生成可扩展框架
```

**通过标准**:
- 核心需求正确提取
- 各阶段处理一致
- 输出完整

---

## 错误恢复测试

### TC-E2E-Error-001: Blueprint 质量低于阈值

**目的**: 验证 Blueprint 质量低于阈值时的处理

**前置条件**:
- 模拟 Blueprint 质量低于 85

**测试步骤**:

1. 执行工作流
2. 模拟 Blueprint 质量低
3. 观察处理

**预期行为**:
```
警告：Blueprint 质量 75/100 低于阈值 85
选项：
1. 继续生成交付物
2. 重新设计
3. 手动改进
```

**通过标准**:
- 提示质量警告
- 提供选项
- 用户可选择继续

---

## 性能测试

### TC-E2E-Performance-001: 完整工作流执行时间

**目的**: 验证完整工作流执行时间

**测试步骤**:

1. 记录开始时间
2. 执行完整工作流
3. 记录结束时间
4. 计算各阶段时间

**预期性能**:
```
Intent Core:    < 1 分钟
Blueprint Core: < 3 分钟
Delivery Core:  < 2 分钟
总计：          < 6 分钟
```

**通过标准**:
- 总时间 < 6 分钟
- 各阶段时间合理

---

## 测试夹具

### 工作流场景样本

**目录**: `fixtures/workflow-scenarios/`

```
fixtures/workflow-scenarios/
├── simple-skill/              # 简单技能场景
│   ├── requirement.txt        # 需求描述
│   ├── expected-intent.yaml   # 预期 Intent
│   ├── expected-blueprint.yaml # 预期 Blueprint
│   └── expected-delivery/     # 预期 Delivery
├── complex-subagent/          # 复杂 SubAgent 场景
│   ├── requirement.txt
│   └── ...
└── data-transform-skill/      # 数据转换技能场景
    └── ...
```

---

## 验证命令汇总

```bash
echo "=== CCC 端到端工作流验证 ==="

# 1. 验证 Intent 制品
echo "1. 验证 Intent 制品..."
ls docs/ccc/intent/INT-*.yaml 2>/dev/null && echo "✅ 存在" || echo "❌ 缺失"

# 2. 验证 Blueprint 制品
echo "2. 验证 Blueprint 制品..."
ls docs/ccc/blueprint/BLP-*.yaml 2>/dev/null && echo "✅ 存在" || echo "❌ 缺失"

# 3. 验证 Delivery 制品
echo "3. 验证 Delivery 制品..."
ls docs/ccc/delivery/*/SKILL.md 2>/dev/null && echo "✅ 存在" || echo "❌ 缺失"

# 4. 验证测试框架
echo "4. 验证测试框架..."
ls docs/ccc/delivery/*/tests/evals.json 2>/dev/null && echo "✅ 存在" || echo "❌ 缺失"
ls docs/ccc/delivery/*/tests/README.md 2>/dev/null && echo "✅ 存在" || echo "❌ 缺失"

# 5. 验证 testStrategy 传递
echo "5. 验证 testStrategy 传递..."
grep -l "testStrategy" docs/ccc/intent/*.yaml 2>/dev/null && echo "✅ Intent 包含" || echo "❌ 缺失"
grep -l "testPlan" docs/ccc/blueprint/*.yaml 2>/dev/null && echo "✅ Blueprint 包含" || echo "❌ 缺失"

echo "=== 验证完成 ==="
```

---

## 测试结果记录

| 测试用例 | 状态 | 执行时间 | 备注 |
|----------|------|----------|------|
| TC-E2E-001 | ⏳ 待执行 | - | 简单技能工作流 |
| TC-E2E-002 | ⏳ 待执行 | - | 复杂 SubAgent 工作流 |
| TC-E2E-003 | ⏳ 待执行 | - | testStrategy 传递 |
| TC-E2E-Boundary-001 | ⏳ 待执行 | - | 模糊需求处理 |
| TC-E2E-Boundary-002 | ⏳ 待执行 | - | 超大需求处理 |
| TC-E2E-Error-001 | ⏳ 待执行 | - | 错误恢复 |
| TC-E2E-Performance-001 | ⏳ 待执行 | - | 性能测试 |

---

**测试维护者**: CCC Team
**下次更新**: 添加新测试用例时
