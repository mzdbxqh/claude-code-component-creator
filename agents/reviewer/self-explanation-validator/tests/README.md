# Self-Explanation Validator 测试用例

本目录包含 self-explanation-validator 的测试 fixtures。

## 目录结构

```
tests/
├── README.md           # 本文件
└── fixtures/
    ├── good-report.md  # 高质量报告示例（期望评分 ≥90）
    └── bad-report.md   # 低质量报告示例（期望评分 <70）
```

## 测试用例说明

### good-report.md

**目的**: 验证 validator 能识别高质量、自解释的报告

**特点**:
- ✓ 包含所有 11 个必需章节
- ✓ 无外部引用（无"参见 README"等）
- ✓ 结构清晰（22 个章节）
- ✓ 信息一致（组件数量匹配）

**期望验证结果**:
- 完整性检查: 100% (40/40)
- 自包含性检查: 100% (30/30)
- 结构清晰度检查: 100% (20/20)
- 信息准确性检查: 100% (10/10)
- **最终评分**: 100/100 (A+)

### bad-report.md

**目的**: 验证 validator 能检测低质量报告的问题

**特点**:
- ✗ 缺失"插件概述"章节（核心问题）
- ✗ 包含多个外部引用（"详见文档"、"参见 README.md"）
- ✗ 结构简单（仅 4 个一级章节）
- ✗ 无插件概述信息

**期望验证结果**:
- 完整性检查: 0% (0/40，缺失所有插件概述子章节)
- 自包含性检查: 0% (0/30，多个外部引用)
- 结构清晰度检查: 0% (0/20，章节数不足)
- 信息准确性检查: 0% (0/10，无组件统计信息)
- **最终评分**: 0-10/100 (F)

## 测试执行方式

### 方式 1: 手动调用 SubAgent

```bash
# 测试 good-report.md
Task(
  agent="self-explanation-validator",
  args={
    "report": "tests/fixtures/good-report.md",
    "profile": null
  }
)
# 期望: 评分 ≥90, 评级 A

# 测试 bad-report.md
Task(
  agent="self-explanation-validator",
  args={
    "report": "tests/fixtures/bad-report.md",
    "profile": null
  }
)
# 期望: 评分 <70, 评级 F
```

### 方式 2: 使用 Bash 脚本（临时实现）

```bash
# 运行验证脚本
/tmp/validate-report.sh tests/fixtures/good-report.md
# 期望退出码: 0 (通过)

/tmp/validate-report.sh tests/fixtures/bad-report.md
# 期望退出码: 1 (不通过)
```

## 验证维度详解

### 1. 完整性检查 (40%)

必需章节清单:
- [ ] `## 一、插件概述`
- [ ] `### 1.1 基本信息`
- [ ] `### 1.2 核心功能`
- [ ] `### 1.3 架构设计`
- [ ] `#### 组件分类体系`
- [ ] `#### 工作流运行机制`
- [ ] `### 1.4 使用方式`
- [ ] `#### 斜杠命令`
- [ ] `### 1.5 核心设计理念`
- [ ] `### 1.6 系统要求`
- [ ] `## 二、执行摘要`

**评分规则**:
- 每缺失 1 个章节: -40/11 ≈ -3.6 分
- 全部存在: +40 分

### 2. 自包含性检查 (30%)

外部引用模式:
- "参见 README.md"
- "详见文档"
- "参考 ARCHITECTURE.md"
- "see documentation"
- "refer to README"

**评分规则**:
- 每发现 1 个外部引用: -10 分
- 最多扣 30 分（3+ 个引用）

### 3. 结构清晰度检查 (20%)

**评分规则**:
- 章节数 ≥10: +20 分
- 章节数 <10: 0 分

### 4. 信息准确性检查 (10%)

验证组件数量一致性:
- 插件概述中的 Skills 数量
- 组件扫描中的 Skills 数量

**评分规则**:
- 一致: +10 分
- 不一致: 0 分

## 评分阈值

| 评分区间 | 评级 | 说明 |
|---------|------|------|
| 90-100 | A | 优秀，报告自解释性强 |
| 80-89 | B | 良好，可独立阅读 |
| 70-79 | C | 及格，基本可读 |
| 60-69 | D | 不及格，需要改进 |
| 0-59 | F | 严重问题，必须修复 |

## 改进建议示例

### good-report.md 的建议

无（已经是 A+ 级别）

### bad-report.md 的建议

1. **补充缺失章节**:
   - 添加"## 一、插件概述"章节
   - 补充所有 10 个子章节（1.1-1.7）

2. **移除外部引用**:
   - 将"详见文档"的内容内联到报告中
   - 将"参见 README.md"的内容直接包含
   - 避免引用"ARCHITECTURE.md"

3. **增加章节深度**:
   - 每个一级章节应包含至少 2-3 个子章节
   - 使用层级标题组织内容

4. **添加组件统计信息**:
   - 在插件概述中添加组件统计表
   - 在组件扫描结果中验证统计一致性

## 相关文档

- [Validation Criteria](../docs/validation-criteria.md)
- [Design Document](../../../../docs/superpowers/specs/2026-03-13-plugin-profiler-design.md)
- [Report Template](../../review-report-renderer/SKILL.md)
