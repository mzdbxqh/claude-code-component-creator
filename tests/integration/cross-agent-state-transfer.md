# CCC 插件跨 Agent 状态传递测试

**测试文件**: `cross-agent-state-transfer.md`
**测试目标**: 验证跨 Agent 状态传递的正确性和完整性
**最后更新**: 2026-03-07

---

## 测试用例

### TC-STATE-001: Intent → Blueprint 状态传递

**目的**: 验证 Intent 制品到 Blueprint 的状态传递完整

**前置条件**:
- Intent 制品已生成

**测试步骤**:

1. 生成 Intent 制品
2. 执行 Blueprint Core
3. 比较 Intent 输出和 Blueprint 输入

**预期传递字段**:
```yaml
# Intent 输出 → Blueprint 输入
id: INT-xxx                →  intentId: INT-xxx
requirement.goal           →  requirement.goal
requirement.type           →  componentType
requirement.complexity     →  complexity
questions                  →  questions (5 问框架答案)
testStrategy               →  testStrategy (用于生成 testPlan)
```

**验证命令**:
```bash
# 提取 Intent 输出
cat docs/ccc/intent/INT-*.yaml

# 提取 Blueprint 输入引用
grep "intentId" docs/ccc/blueprint/BLP-*.yaml

# 比较 testStrategy 和 testPlan
grep -A 10 "testStrategy" docs/ccc/intent/INT-*.yaml
grep -A 20 "testPlan" docs/ccc/blueprint/BLP-*.yaml
```

**通过标准**:
- intentId 正确引用
- requirement 完整传递
- testStrategy 正确转换为 testPlan

---

### TC-STATE-002: Blueprint → Delivery 状态传递

**目的**: 验证 Blueprint 制品到 Delivery 的状态传递完整

**前置条件**:
- Blueprint 制品已生成

**测试步骤**:

1. 生成 Blueprint 制品
2. 执行 Delivery Core
3. 比较 Blueprint 输出和 Delivery 输入

**预期传递字段**:
```yaml
# Blueprint 输出 → Delivery 输入
artifactId: BLP-xxx        →  blueprintId: BLP-xxx
stages.stage3              →  SKILL.md (组件定义)
stages.stage5              →  implementation/ (实现代码)
testPlan                   →  tests/ (测试框架)
testPlan.testTypes         →  tests/evals.json
testPlan.testFramework     →  tests/structure
```

**验证命令**:
```bash
# 提取 Blueprint 输出
cat docs/ccc/blueprint/BLP-*.yaml

# 提取 Delivery 制品
cat docs/ccc/delivery/*/SKILL.md

# 比较 testPlan 和 tests/
grep -A 20 "testPlan" docs/ccc/blueprint/BLP-*.yaml
cat docs/ccc/delivery/*/tests/evals.json
```

**通过标准**:
- blueprintId 正确引用
- SKILL.md 基于 stage3 生成
- tests/基于 testPlan 生成

---

### TC-STATE-003: 测试策略完整传递链

**目的**: 验证 testStrategy → testPlan → tests/evals.json 完整传递链

**前置条件**:
- 完整工作流已执行

**测试步骤**:

1. 提取 Intent testStrategy
2. 提取 Blueprint testPlan
3. 提取 Delivery evals.json
4. 验证传递一致性

**预期传递链**:
```
Intent testStrategy
  ↓
  coreScenario → testPlan.testTypes[0].description
  boundaryCases → testPlan.testTypes[1].testCases
  ↓
  Delivery evals.json
  ↓
  testCases[0].category = "functional"
  testCases[1].category = "boundary"
```

**验证命令**:
```bash
# 提取完整传递链
echo "=== Intent testStrategy ==="
grep -A 15 "testStrategy" docs/ccc/intent/INT-*.yaml

echo "=== Blueprint testPlan ==="
grep -A 25 "testPlan" docs/ccc/blueprint/BLP-*.yaml

echo "=== Delivery evals.json ==="
cat docs/ccc/delivery/*/tests/evals.json | head -50
```

**通过标准**:
- testStrategy 完整传递到 testPlan
- testPlan 完整传递到 evals.json
- 测试用例类别正确

---

## 边界测试

### TC-STATE-Boundary-001: 部分字段缺失传递

**目的**: 验证部分字段缺失时的传递处理

**前置条件**:
- Intent 缺少某些字段

**测试步骤**:

1. 模拟 Intent 缺少 testStrategy
2. 执行 Blueprint Core
3. 观察传递处理

**预期行为**:
```
警告：Intent 缺少 testStrategy 字段
处理：生成默认 testPlan
标注：基于假设生成
```

**通过标准**:
- 不中断流程
- 使用默认值
- 标注缺失字段

---

### TC-STATE-Boundary-002: 字段格式不一致处理

**目的**: 验证字段格式不一致时的传递处理

**前置条件**:
- Intent 字段格式与预期不符

**测试步骤**:

1. 模拟 Intent 字段格式异常
2. 执行 Blueprint Core
3. 观察传递处理

**预期行为**:
```
警告：字段格式异常 [字段名]
处理：尝试转换或跳过
建议：修正源文件格式
```

**通过标准**:
- 尝试格式转换
- 转换失败时跳过
- 提供修正建议

---

## 一致性测试

### TC-STATE-Consistency-001: 数据一致性验证

**目的**: 验证跨 Agent 数据一致性

**前置条件**:
- 完整工作流已执行

**测试步骤**:

1. 提取所有制品
2. 比较关键字段
3. 验证一致性

**验证点**:
- componentType 一致 (Skill/SubAgent)
- complexity 一致 (simple/complex)
- testStrategy/testPlan/evals 一致

**验证命令**:
```bash
python3 << 'PYEOF'
import yaml
import json
import glob

# 加载最新制品
intent_files = sorted(glob.glob('docs/ccc/intent/INT-*.yaml'))
blueprint_files = sorted(glob.glob('docs/ccc/blueprint/BLP-*.yaml'))
delivery_dirs = sorted(glob.glob('docs/ccc/delivery/*/'))

if intent_files and blueprint_files and delivery_dirs:
    # 加载 Intent
    with open(intent_files[-1]) as f:
        intent = yaml.safe_load(f)

    # 加载 Blueprint
    with open(blueprint_files[-1]) as f:
        blueprint = yaml.safe_load(f)

    # 验证一致性
    print("=== 一致性验证 ===")
    print(f"Intent ID: {intent.get('id')}")
    print(f"Blueprint intentId: {blueprint.get('intentId')}")
    print(f"匹配：{intent.get('id') == blueprint.get('intentId')}")

    # 加载 Delivery evals.json
    evals_files = glob.glob(f'{delivery_dirs[-1]}tests/evals.json')
    if evals_files:
        with open(evals_files[0]) as f:
            evals = json.load(f)
        print(f"Delivery 测试用例数：{len(evals.get('testCases', []))}")
else:
    print("未找到制品文件")
PYEOF
```

**通过标准**:
- ID 引用一致
- 组件类型一致
- 测试策略一致

---

## 错误传播测试

### TC-STATE-Error-001: 上游错误不传播到下游

**目的**: 验证上游错误不影响下游处理

**前置条件**:
- 模拟 Intent 包含错误

**测试步骤**:

1. 模拟 Intent 包含错误数据
2. 执行工作流
3. 验证下游处理

**预期行为**:
```
Intent: 错误数据
Blueprint: 检测到错误，使用默认值
Delivery: 基于有效的 Blueprint 生成
```

**通过标准**:
- 下游不继承错误
- 使用默认值继续
- 标注错误来源

---

## 测试夹具

### 状态传递场景

**目录**: `fixtures/workflow-scenarios/state-transfer/`

```
fixtures/workflow-scenarios/state-transfer/
├── normal-transfer/           # 正常传递场景
│   ├── intent.yaml
│   ├── blueprint.yaml
│   └── delivery/
├── missing-field-transfer/    # 缺失字段传递场景
│   └── ...
└── format-mismatch-transfer/  # 格式不匹配传递场景
    └── ...
```

---

## 验证命令汇总

```bash
echo "=== 跨 Agent 状态传递验证 ==="

# 1. 验证 ID 引用一致性
echo "1. 验证 ID 引用..."
grep "intentId" docs/ccc/blueprint/BLP-*.yaml | head -1
grep "blueprintId" docs/ccc/delivery/*/metadata.yaml | head -1

# 2. 验证 testStrategy 传递
echo "2. 验证 testStrategy 传递..."
grep -l "testStrategy" docs/ccc/intent/*.yaml | wc -l | xargs -I {} echo "Intent: {} 个文件包含"
grep -l "testPlan" docs/ccc/blueprint/*.yaml | wc -l | xargs -I {} echo "Blueprint: {} 个文件包含"
ls docs/ccc/delivery/*/tests/evals.json 2>/dev/null | wc -l | xargs -I {} echo "Delivery: {} 个文件包含"

# 3. 运行一致性检查
echo "3. 运行一致性检查..."
python3 -c "
import yaml, json, glob
# 简化检查
intent = sorted(glob.glob('docs/ccc/intent/INT-*.yaml'))
bp = sorted(glob.glob('docs/ccc/blueprint/BLP-*.yaml'))
if intent and bp:
    print('✅ 制品文件存在')
else:
    print('❌ 制品文件缺失')
"

echo "=== 验证完成 ==="
```

---

## 测试结果记录

| 测试用例 | 状态 | 执行时间 | 备注 |
|----------|------|----------|------|
| TC-STATE-001 | ⏳ 待执行 | - | Intent→Blueprint 传递 |
| TC-STATE-002 | ⏳ 待执行 | - | Blueprint→Delivery 传递 |
| TC-STATE-003 | ⏳ 待执行 | - | 测试策略传递链 |
| TC-STATE-Boundary-001 | ⏳ 待执行 | - | 缺失字段处理 |
| TC-STATE-Boundary-002 | ⏳ 待执行 | - | 格式不一致处理 |
| TC-STATE-Consistency-001 | ⏳ 待执行 | - | 数据一致性 |
| TC-STATE-Error-001 | ⏳ 待执行 | - | 错误传播 |

---

**测试维护者**: CCC Team
**下次更新**: 添加新测试用例时
