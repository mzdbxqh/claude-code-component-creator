# {plugin_name} 审查报告

**审查日期**: {review_date}
**审查对象**: `{target_path}`
**审查类型**: {review_type}
**审查员**: {reviewer}
**报告版本**: {report_version}

---

## 第一部分：插件概述

### 1.1 插件定位

| 属性 | 值 |
|------|-----|
| **插件名称** | {plugin_name} |
| **插件类型** | {plugin_type} |
| **版本** | {version} |
| **核心功能** | {core_function} |

**插件描述**:
{plugin_description}

**解决的核心问题**:
{problem_solved}

**适用场景**:
{use_cases}

**核心价值**:
{core_value}

---

### 1.2 核心工作流

```
{workflow_diagram}
```

#### 工作流阶段说明

| 阶段 | 命令/组件 | 输入 | 输出 | 说明 |
|------|-----------|------|------|------|
{workflow_stages}

#### 典型使用场景

**场景 1: {scenario_1_name}**

```bash
{scenario_1_command}
```

{scenario_1_description}

**场景 2: {scenario_2_name}**

```bash
{scenario_2_command}
```

{scenario_2_description}

---

### 1.3 架构概览

#### 组件统计

| 组件类型 | 数量 | 说明 |
|----------|------|------|
| **Commands** | {commands_count} | 用户交互入口 |
| **Agents/Skills** | {agents_count} | 专用任务执行器 |
| **Hooks** | {hooks_count} | 钩子配置 |
| **规则文件** | {rules_count} | 审查规则 |

#### 核心组件

| 组件名称 | 类型 | 用途 |
|----------|------|------|
{core_components}

#### 组件协作关系

```
{component_collaboration_diagram}
```

---

## 第二部分：审查结果

### 2.1 执行摘要

| 属性 | 值 |
|------|-----|
| **综合评分** | **{overall_score}/100** ({grade}) |
| **审查范围** | {review_scope} |
| **组件总数** | {total_components} |
| **规则总数** | {total_rules} |
| **问题总数** | {total_issues} (Error: {error_count}, Warning: {warning_count}, Info: {info_count}) |
| **审查状态** | {review_status} |

---

### 2.2 评估维度评分

| 维度 | 权重 | 得分 | 等级 | 说明 |
|------|------|------|------|------|
{dimension_scores}

---

### 2.3 规则验证

#### 规则加载状态

| 规则类别 | 规则数 | 状态 |
|----------|--------|------|
{rule_categories}

#### 规则验证详情

{rule_details}

---

### 2.4 组件合规性检查

#### Commands 检查

| 检查项 | 通过数 | 总数 | 通过率 |
|--------|--------|------|--------|
{command_checks}

#### Agents/Skills 检查

| 检查项 | 通过数 | 总数 | 通过率 |
|--------|--------|------|--------|
{agent_checks}

#### 测试框架检查

| 检查项 | 状态 | 说明 |
|--------|------|------|
{test_framework_checks}

---

### 2.5 问题清单

#### 问题汇总

| 级别 | 数量 | 说明 |
|------|------|------|
| Error | {error_count} | {error_description} |
| Warning | {warning_count} | {warning_description} |
| Info | {info_count} | {info_description} |

#### Error 级别问题

{error_issues}

#### Warning 级别问题

| ID | 组件 | 规则 | 问题 | 建议 |
|----|------|------|------|------|
{warning_issues}

#### Info 级别问题

| ID | 组件 | 规则 | 问题 | 建议 |
|----|------|------|------|------|
{info_issues}

---

## 第三部分：改进建议

### 3.1 修复优先级

#### P0 (阻塞): 必须修复

{p0_issues}

#### P1 (重要): 建议修复

{p1_issues}

#### P2 (可选): 持续改进

{p2_issues}

### 3.2 改进行动计划

| 优先级 | 任务 | 预计工时 | 负责人 | 截止日期 |
|--------|------|----------|--------|----------|
{action_plan}

---

## 第四部分：审查结论

### 4.1 综合评估

```
┌─────────────────────────────────────────────────────────┐
│                   最终评估结果                           │
├─────────────────────────────────────────────────────────┤
│  合规评分：{score}/100 ({grade})                         │
│  架构质量：{architecture_score}/100 ({architecture_grade}) │
│  文档质量：{documentation_score}/100 ({documentation_grade}) │
│  测试覆盖：{test_score}/100 ({test_grade})               │
├─────────────────────────────────────────────────────────┤
│  综合等级：{final_grade} - {final_recommendation}        │
│  问题统计：Error: {error_count}, Warning: {warning_count}, Info: {info_count} │
└─────────────────────────────────────────────────────────┘
```

### 4.2 审查通过项

| 检查项 | 状态 |
|--------|------|
{pass_items}

### 4.3 历史对比

| 审查日期 | 审查类型 | 综合评分 | 等级 | 问题数 |
|----------|----------|----------|------|--------|
{history_comparison}

**趋势**: {trend}

---

## 附录

### A. 审查规则来源

本次审查基于 {total_rules} 条反模式规则。

### B. 审查文件清单

{file_list}

### C. Git 提交验证

```
{git_commits}
```

---

**审查完成时间**: {completion_time}
**审查工具**: {review_tool}
**审查员**: {reviewer}
**报告文件**: `{report_path}`
**状态**: {final_status}
