# CCC 插件测试套件

## 概述

本目录包含 CCC 插件的完整测试套件，用于验证插件的功能、质量和可靠性。

## 测试分类

### 1. 功能测试 (testCases)

验证 CCC 插件的核心创建流程和工作流。

| 测试ID | 名称 | 类别 | 验证内容 |
|--------|------|------|----------|
| TC-001 | 简单技能创建 - TODO 查找器 | simple-skill | Intent → Blueprint → Delivery 流程 |
| TC-002 | 复杂 SubAgent 创建 - 代码审查器 | complex-subagent | 复杂组件创建流程 |
| TC-003 | 数据转换技能 - YAML 转 JSON | data-transform-skill | 数据处理技能创建 |
| TC-004 | 全面项目审查 | comprehensive-review | 审查流程验证 |
| TC-005 | 一键快速工作流 | quick-workflow | 快速创建流程 |

**总计**: 5 个功能测试用例

### 2. 负面测试 (shouldNotTriggerSkills)

验证哪些场景不应触发 CCC 插件。

| 测试ID | 名称 | 验证内容 |
|--------|------|----------|
| NT-001 | 简单文件读取 | 单步骤操作不触发 |
| NT-002 | 简单问题回答 | 通用问题不触发 |
| NT-003 | 基础数学计算 | 基础计算不触发 |
| NT-004 | 空输入边界测试 | 空输入处理 |
| NT-005 | 超大输入边界测试 | 长度限制处理 |
| NT-006 | 异常格式输入测试 | 格式错误处理 |

**总计**: 6 个负面测试用例

### 3. 引用完整性验证测试 (referenceIntegrityTests)

验证 reference-integrity-scanner SubAgent 的引用完整性检测功能。

#### REF-INT-001: 正常插件扫描
- **目标**: 验证正常插件扫描
- **输入**: test-fixtures/reference-integrity/valid-plugin
- **期望**: 完整性评分 = 100，无任何问题
- **断言数量**: 4 个

#### REF-INT-002: 断开引用检测
- **目标**: 验证断开引用检测
- **输入**: test-fixtures/reference-integrity/broken-refs
- **期望**: 检测到 2 个断开引用，评分 < 80
- **断言数量**: 3 个

#### REF-INT-003: 孤儿文件检测
- **目标**: 验证孤儿文件检测
- **输入**: test-fixtures/reference-integrity/orphans
- **期望**: 检测到 1 个孤儿文件（orphan-skill）
- **断言数量**: 3 个

#### REF-INT-004: 循环引用检测
- **目标**: 验证循环引用检测
- **输入**: test-fixtures/reference-integrity/circular
- **期望**: 检测到 1 个循环（A→B→C→A），评分 ≤ 80
- **断言数量**: 4 个

**总计**: 4 个测试用例，14 个断言

## 运行测试

### 方式 1: 使用 /cmd-review（推荐）

```bash
# 在 CCC 插件根目录运行
cd /Users/mzdbxqh/source/component-creator-parent/claude-code-component-creator

# 运行完整审查（包括引用完整性验证）
/cmd-review --with-eval --target=.
```

### 方式 2: 手动运行引用完整性测试

```bash
# 测试正常插件
python agents/reviewer/reference-integrity-scanner/reference_scanner.py \
  ../test-fixtures/reference-integrity/valid-plugin

# 测试断开引用
python agents/reviewer/reference-integrity-scanner/reference_scanner.py \
  ../test-fixtures/reference-integrity/broken-refs

# 测试孤儿文件
python agents/reviewer/reference-integrity-scanner/reference_scanner.py \
  ../test-fixtures/reference-integrity/orphans

# 测试循环引用
python agents/reviewer/reference-integrity-scanner/reference_scanner.py \
  ../test-fixtures/reference-integrity/circular
```

### 方式 3: 使用交互模式

```bash
# 进入交互模式
python agents/reviewer/reference-integrity-scanner/reference_scanner.py \
  --interactive

# 按照提示输入插件路径进行测试
```

## 测试覆盖总结

| 测试类型 | 测试用例数 | 断言数量 | 状态 |
|---------|----------|---------|------|
| 功能测试 | 5 | - | ✅ |
| 负面测试 | 6 | - | ✅ |
| 引用完整性测试 | 4 | 14 | ✅ |
| **总计** | **15** | **14** | **✅** |

## 测试夹具依赖

引用完整性测试依赖以下测试夹具（位于父项目 test-fixtures/ 目录）：

```
component-creator-parent/
└── test-fixtures/
    └── reference-integrity/
        ├── valid-plugin/       # REF-INT-001: 正常插件
        ├── broken-refs/        # REF-INT-002: 断开引用
        ├── orphans/            # REF-INT-003: 孤儿文件
        └── circular/           # REF-INT-004: 循环引用
```

如果测试失败，请确保这些夹具存在且结构正确。

## 期望结果

所有测试应通过（15/15 = 100%）。

### 如果测试失败，请检查：

1. ✅ test-fixtures/ 目录是否存在且包含正确的测试数据
2. ✅ reference-integrity-scanner 是否正确实现
3. ✅ evals.json 中的期望值是否与实际实现一致
4. ✅ Python 依赖是否已安装（PyYAML 等）

## 断言类型说明

evals.json 支持以下断言类型：

- **equals**: 精确匹配
  ```json
  {"type": "equals", "field": "summary.broken_references", "expected": 0}
  ```

- **lessThan**: 小于指定值
  ```json
  {"type": "lessThan", "field": "summary.integrity_score", "expected": 80}
  ```

- **arrayContains**: 数组包含指定元素
  ```json
  {"type": "arrayContains", "field": "issues.orphan_files[*].file_path", "expected": ["skills/orphan-skill/SKILL.md"]}
  ```

## 维护指南

### 添加新测试用例

1. 在 evals.json 中添加测试定义
2. 创建对应的测试夹具（如需要）
3. 更新本 README 文档
4. 运行测试验证通过

### 更新现有测试

1. 修改 evals.json 中的测试定义
2. 更新测试夹具（如需要）
3. 重新运行测试验证
4. 更新文档说明

## 版本历史

- **v1.0.0** (2026-03-14): 初始版本
  - 5 个功能测试用例
  - 6 个负面测试用例
  - 4 个引用完整性测试用例
