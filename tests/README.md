# CCC 插件测试指南

> **Component Creator Creator (CCC) Plugin Test Suite**

## 为什么要写测试？

1. **验证功能**：确保 CCC 工作流（Intent → Blueprint → Delivery）按预期运行
2. **回归保护**：修改后快速验证未破坏核心功能
3. **文档作用**：测试用例展示如何使用 CCC 创建组件
4. **质量保证**：通过自动化测试确保交付物符合规范

---

## 快速开始

### 运行所有测试

```bash
/ccc:test-sandbox
```

### 运行单个测试

```bash
# 按测试用例 ID 运行
/ccc:test-sandbox --test-case=TC-001

# 按类别运行
/ccc:test-sandbox --category=simple-skill
```

### 干运行验证（不实际执行）

```bash
/ccc:test-sandbox --dry-run
```

---

## 测试目录结构

```
tests/
├── README.md              # 本文件 - 测试指南
├── evals.json             # 测试用例定义（在 evals/ 目录）
├── unit/                  # 单元测试
│   ├── test-functional.md # 功能测试
│   └── test-boundary.md   # 边界测试
├── integration/           # 集成测试
│   └── test-workflow.md   # 完整工作流测试
├── examples/              # 示例组件
│   ├── sample-components/ # 示例技能/命令
│   └── fixtures/          # 测试夹具
└── review/                # 审查测试
    └── test-review.md     # 审查功能测试
```

### 测试用例定义位置

```
evals/
└── evals.json             # 所有测试用例的 JSON 定义
```

---

## 测试类型

| 类型 | 用途 | 文件位置 | 说明 |
|------|------|----------|------|
| **功能测试** | 验证核心功能 | `tests/unit/test-functional.md` | 验证 Intent/Blueprint/Delivery 工作流 |
| **边界测试** | 验证边界情况 | `tests/unit/test-boundary.md` | 空输入、大输入、异常格式 |
| **集成测试** | 验证完整工作流 | `tests/integration/test-workflow.md` | Intent → Blueprint → Delivery 全流程 |
| **示例测试** | 验证示例组件 | `tests/examples/` | 提供正例和反例样本 |
| **审查测试** | 验证审查功能 | `tests/review/test-review.md` | 76+ 反模式检查 |

---

## 测试用例分类

### 1. 简单技能测试 (simple-skill)

测试单阶段、无实现的 Skill 创建。

**示例用例**: TC-001 (TODO 查找器)

```json
{
  "id": "TC-001",
  "name": "简单技能创建 - TODO 查找器",
  "prompt": "我想要一个技能来快速查找项目中的 TODO 注释",
  "category": "simple-skill",
  "expectedWorkflow": ["ccc:intent-core", "ccc:blueprint-core", "ccc:delivery-core"],
  "expectedArtifacts": [
    "docs/ccc/intent/INT-*.yaml",
    "docs/ccc/blueprint/BLP-*.yaml",
    "docs/ccc/delivery/*/SKILL.md"
  ]
}
```

### 2. 复杂 SubAgent 测试 (complex-subagent)

测试多阶段、需要实现代码的 SubAgent 创建。

**示例用例**: TC-002 (代码审查器)

### 3. 数据转换技能测试 (data-transform-skill)

测试涉及数据格式转换的技能。

**示例用例**: TC-003 (YAML 转 JSON)

### 4. 审查功能测试 (comprehensive-review)

测试项目审查功能。

**示例用例**: TC-004 (全面项目审查)

### 5. 快速工作流测试 (quick-workflow)

测试一键快速创建功能。

**示例用例**: TC-005 (一键快速工作流)

---

## 边界测试用例

### NT-004: 空输入边界测试

**目的**: 验证空输入时的错误处理

```json
{
  "id": "NT-004",
  "name": "空输入边界测试",
  "prompt": "",
  "category": "boundary",
  "expectedBehavior": "返回友好的提示信息，说明需要提供输入",
  "expectedOutput": "包含错误说明和用法的提示"
}
```

### NT-005: 超大输入边界测试

**目的**: 验证大输入时的处理能力

```json
{
  "id": "NT-005",
  "name": "超大输入边界测试",
  "prompt": "[超过 10000 字符的详细需求描述...]",
  "category": "boundary",
  "expectedBehavior": "截断处理或分页，返回友好的长度限制提示",
  "expectedOutput": "包含核心需求的摘要和完整处理说明"
}
```

### NT-006: 异常格式输入测试

**目的**: 验证异常输入格式的处理

```json
{
  "id": "NT-006",
  "name": "异常格式输入测试",
  "prompt": "### 无效格式 ### 这不是一个有效的需求描述",
  "category": "boundary",
  "expectedBehavior": "识别无效格式，引导用户提供规范输入",
  "expectedOutput": "包含格式说明和正确示例的提示"
}
```

---

## 如何编写测试用例

### 步骤 1: 复制模板

```bash
# 打开 evals.json
cat evals/evals.json
```

### 步骤 2: 添加新测试用例

```json
{
  "id": "TC-XXX",
  "name": "测试名称",
  "prompt": "测试输入描述",
  "category": "simple-skill|complex-subagent|data-transform|comprehensive-review|quick-workflow|boundary",
  "expectedWorkflow": ["ccc:intent-core", "ccc:blueprint-core"],
  "expectedArtifacts": ["docs/ccc/intent/INT-*.yaml"],
  "qualityThresholds": {
    "intentQuality": 80,
    "blueprintQuality": 85
  }
}
```

### 步骤 3: 运行测试验证

```bash
/ccc:test-sandbox --test-case=TC-XXX
```

---

## 测试执行流程

```
┌─────────────────────────────────────────────────────────┐
│  测试执行流程                                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 加载 evals.json                                     │
│     ↓                                                   │
│  2. 解析测试用例                                        │
│     ↓                                                   │
│  3. 执行测试 (调用 CCC 工作流)                          │
│     ↓                                                   │
│  4. 验证生成的制品                                      │
│     ↓                                                   │
│  5. 生成测试报告                                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 测试报告

### 控制台输出示例

```
🧪 CCC 插件测试报告

测试环境：tests/
测试用例：5
开始时间：2026-03-07 14:30:22

Running Tests...
┌─────────────────────────────────────────────────────┐
│ TC-001: 简单技能创建 - TODO 查找器    ✅ PASSED    │
│   执行时间：1m 45s                                   │
│   生成文件：3 个                                      │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ TC-002: 复杂 SubAgent 创建 - 代码审查器 ✅ PASSED    │
│   执行时间：2m 30s                                   │
│   生成文件：5 个                                      │
└─────────────────────────────────────────────────────┘

Summary:
┌─────────────────────────────────────────────────────┐
│ Total: 5  |  Passed: 5  |  Warn: 0  |  Failed: 0   │
│ Pass Rate: 100%                                      │
│ Average Execution Time: 2m 01s                      │
└─────────────────────────────────────────────────────┘
```

### 文件输出

测试报告保存到：`docs/tests/YYYY-MM-DD-test-report.md`

---

## 测试覆盖率

### 当前覆盖率统计

| 组件类型 | 测试用例数 | 覆盖率 |
|----------|------------|--------|
| Intent Core | 5 | 80% |
| Blueprint Core | 5 | 80% |
| Delivery Core | 5 | 80% |
| Review Core | 1 | 60% |
| Commands | 5 | 70% |

### 覆盖率目标

- **短期目标**: 80% 核心功能覆盖
- **中期目标**: 90% 核心功能覆盖
- **长期目标**: 95% 全功能覆盖

---

## 常见问题

### Q: 测试失败了怎么办？

1. **查看失败详情**
   ```bash
   /ccc:test-sandbox --test-case=TC-XXX --verbose
   ```

2. **检查是否是预期行为变更**
   - 如果是功能改进，更新测试用例
   - 如果是 bug，修复后重新运行

3. **更新测试用例或修复代码**
   ```bash
   # 更新 evals.json
   # 修复代码
   # 重新运行测试
   /ccc:test-sandbox --test-case=TC-XXX
   ```

### Q: 如何添加新测试？

1. 复制现有测试用例结构
2. 修改 `prompt` 和 `expectedOutput`
3. 运行测试验证

### Q: 测试执行太慢怎么办？

1. 使用 `--dry-run` 模式验证测试定义
2. 只运行单个测试：`/ccc:test-sandbox --test-case=TC-XXX`
3. 批量测试时使用 `--parallel` 参数（如支持）

### Q: 如何贡献测试用例？

1. 在 `evals/evals.json` 中添加新用例
2. 运行测试验证
3. 提交 PR（如适用）

---

## 测试夹具

### 示例输入

测试夹具位于 `tests/examples/` 和 `test-fixtures/` 目录：

```
tests/examples/
├── sample-components/
│   ├── good-skill/          # 正例：规范的技能
│   └── problematic-skill/   # 反例：有问题的技能
└── fixtures/
    └── sample-input.txt     # 示例输入

test-fixtures/
├── architecture-review/     # 架构审查测试夹具
└── review/                  # 审查测试夹具
```

### 使用测试夹具

```bash
# 使用示例组件进行测试
/ccc:review --target=tests/examples/sample-components/good-skill
```

---

## 相关文档

- [CCC 插件使用指南](../docs/user-guide/)
- [CCC 工作流文档](../docs/plans/)
- [审查报告模板](../docs/reviews/)

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-03-07 | 初始版本，包含基础测试框架 |

---

**最后更新**: 2026-03-07
**维护者**: CCC Team
