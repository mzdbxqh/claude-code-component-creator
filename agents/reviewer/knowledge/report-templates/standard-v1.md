# {{report_title}}

**生成时间**: {{timestamp}}
**检查对象**: {{target_path}}
**检查类型**: {{review_type}}
**检查工具**: {{tool_version}}

---

## 执行摘要

| 指标 | 值 |
|-----|---|
| **质量评级** | {{grade}} ({{score}}/100) |
| **架构评分** | {{architecture_grade}} ({{architecture_score}}/100) |
| **检查状态** | {{status}} |
| **检查项总计** | {{total_checks}} |
| **通过** | {{passed_checks}} ✓ |
| **未通过** | {{failed_checks}} ✗ |
| **错误数** | {{error_count}} |
| **警告数** | {{warning_count}} |

{{#if blockers}}
### ⚠️ 阻塞性问题
{{#each blockers}}
- {{this}}
{{/each}}
{{/if}}

{{#if architecture_skipped}}
### ⚠️ 架构分析已跳过
{{architecture_skipped_reason}}
{{/if}}

---

## 分类检查详情

### 2.1 元数据合规 (Metadata)

| 检查 ID | 检查项 | 状态 | 权重 | 备注 |
|-------|-------|------|------|------|
| META-001 | 名称格式 | {{meta_001_status}} | 5% | {{meta_001_note}} |
| META-002 | 描述长度 | {{meta_002_status}} | 5% | {{meta_002_note}} |
| META-003 | 参数提示 | {{meta_003_status}} | 5% | {{meta_003_note}} |
| META-004 | 上下文模式 | {{meta_004_status}} | 5% | {{meta_004_note}} |
| META-005 | 模型指定 | {{meta_005_status}} | 5% | {{meta_005_note}} |

**小计**: {{meta_passed}}/5 通过 (权重：25%)

---

### 2.2 文档完整性 (Documentation)

| 检查 ID | 检查项 | 状态 | 权重 | 备注 |
|-------|-------|------|------|------|
| DOC-001 | 使用示例 | {{doc_001_status}} | 10% | {{doc_001_note}} |
| DOC-002 | 错误处理文档 | {{doc_002_status}} | 10% | {{doc_002_note}} |
| DOC-003 | 输出规范 | {{doc_003_status}} | 5% | {{doc_003_note}} |
| DOC-004 | 注意事项 | {{doc_004_status}} | 5% | {{doc_004_note}} |

**小计**: {{doc_passed}}/4 通过 (权重：30%)

---

### 2.3 安全规范 (Security)

| 检查 ID | 检查项 | 状态 | 权重 | 备注 |
|-------|-------|------|------|------|
| SEC-001 | 最小权限原则 | {{sec_001_status}} | 10% | {{sec_001_note}} |
| SEC-002 | 工具权限声明 | {{sec_002_status}} | 5% | {{sec_002_note}} |

**小计**: {{sec_passed}}/2 通过 (权重：15%)

---

### 2.4 工作流定义 (Workflow)

| 检查 ID | 检查项 | 状态 | 权重 | 备注 |
|-------|-------|------|------|------|
| FLOW-001 | 工作流完整性 | {{flow_001_status}} | 10% | {{flow_001_note}} |
| FLOW-002 | 输出格式规范 | {{flow_002_status}} | 5% | {{flow_002_note}} |

**小计**: {{flow_passed}}/2 通过 (权重：15%)

---

### 2.5 链路验证 (Linkage)

| 检查 ID | 检查项 | 状态 | 权重 | 备注 |
|-------|-------|------|------|------|
| LINK-001 | 调用链完整 | {{link_001_status}} | 10% | {{link_001_note}} |
| LINK-002 | IO 匹配 | {{link_002_status}} | 5% | {{link_002_note}} |

**小计**: {{link_passed}}/2 通过 (权重：15%)

---

### 2.6 架构分析 (Architecture)

{{#if architecture_analysis}}
**总体评分**: {{architecture_grade}} ({{architecture_score}}/100)

| 维度 | 评分 | 等级 | 状态 |
|------|------|------|------|
| 工作流划分 | {{workflow_partitioning_score}} | {{workflow_partitioning_grade}} | {{workflow_partitioning_status}} |
| 组件粒度 | {{component_granularity_score}} | {{component_granularity_grade}} | {{component_granularity_status}} |
| 职责分离 | {{responsibility_separation_score}} | {{responsibility_separation_grade}} | {{responsibility_separation_status}} |
| 协作效率 | {{collaboration_efficiency_score}} | {{collaboration_efficiency_grade}} | {{collaboration_efficiency_status}} |
| 命令设计 | {{command_design_score}} | {{command_design_grade}} | {{command_design_status}} |

{{#if architecture_antipatterns}}
**发现的架构问题**:

{{#each architecture_antipatterns}}
- [{{this.severity}}] {{this.id}}: {{this.message}}
  - 建议：{{this.suggestion}}
{{/each}}
{{/if}}

{{#if architecture_recommendations}}
**架构优化建议**:

{{#each architecture_recommendations}}
- [{{this.priority}}] {{this.title}}
  - 操作：{{this.action}}
{{/each}}
{{/if}}

{{else}}
_架构分析已跳过 (--no-arch 参数指定)_
{{/if}}

**小计**: {{architecture_passed}}/{{architecture_total}} 通过 (权重：20%)

---

## 问题详情

### 错误级别 (Errors)

{{#each errors}}
#### {{id}}: {{title}}

| 属性 | 值 |
|-----|---|
| **文件** | {{file}} |
| **行号** | {{line}} |
| **分类** | {{category}} |
| **描述** | {{description}} |

**修复建议**:
{{fix_suggestion}}

**参考**:
- 手册章节：{{handbook_ref}}
- 相关规则：{{related_rules}}

---
{{/each}}

### 警告级别 (Warnings)

{{#each warnings}}
#### {{id}}: {{title}}

| 属性 | 值 |
|-----|---|
| **文件** | {{file}} |
| **行号** | {{line}} |
| **分类** | {{category}} |
| **描述** | {{description}} |

**修复建议**:
{{fix_suggestion}}

---
{{/each}}

### 信息级别 (Info)

{{#each infos}}
- **{{id}}**: {{description}} ({{file}}:{{line}})
{{/each}}

---

## 正向发现

{{#each positives}}
- ✓ {{finding}} ({{file}})
{{/each}}

---

## 行动建议

### 高优先级 (P0 - 阻塞性)

{{#each p0_actions}}
1. [ ] **{{title}}** ({{id}})
   - 文件：{{file}}
   - 操作：{{action}}
{{/each}}

### 中优先级 (P1 - 建议修复)

{{#each p1_actions}}
1. [ ] **{{title}}** ({{id}})
   - 文件：{{file}}
   - 操作：{{action}}
{{/each}}

### 低优先级 (P2 - 可选优化)

{{#each p2_actions}}
1. [ ] **{{title}}** ({{id}})
   - 文件：{{file}}
   - 操作：{{action}}
{{/each}}

---

## 附录

### A. 检查清单汇总

| 分类 | 通过 | 未通过 | 总计 | 通过率 |
|-----|-----|-------|-----|-------|
| 元数据 | {{meta_passed}} | {{meta_failed}} | 5 | {{meta_rate}}% |
| 文档 | {{doc_passed}} | {{doc_failed}} | 4 | {{doc_rate}}% |
| 安全 | {{sec_passed}} | {{sec_failed}} | 2 | {{sec_rate}}% |
| 工作流 | {{flow_passed}} | {{flow_failed}} | 2 | {{flow_rate}}% |
| 链路 | {{link_passed}} | {{link_failed}} | 2 | {{link_rate}}% |
| 架构 | {{architecture_passed}} | {{architecture_failed}} | {{architecture_total}} | {{architecture_rate}}% |
| **总计** | **{{total_passed}}** | **{{total_failed}}** | **{{grand_total}}** | **{{total_rate}}%** |

### B. 文件清单

{{#each files}}
- {{path}} ({{type}})
{{/each}}

---

*报告生成于 {{timestamp}} | Claude Code Component Creator Review System*
