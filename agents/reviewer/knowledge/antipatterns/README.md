# 反模式库索引 (Antipatterns Library Index)

> 基于 HANDBOOK 完整手册构建的组件质量检测规则库
> Built from the complete HANDBOOK manual for component quality detection

> **v3.0.0** - 新增 7 个评估维度：意图匹配、LLM 兼容性、安全、环境兼容性、扩展性

---

## 目录结构 (Directory Structure)

```
antipatterns/
├── README.md                    # 本索引文档
├── schema.json                  # 反模式定义规范
│
├── skill/                       # Skill 组件反模式 (15 个)
│   ├── skill-001-description-length.yaml
│   ├── skill-002-name-format.yaml
│   └── ...
│
├── command/                     # Command 组件反模式 (12 个)
│   ├── cmd-001-description-missing.yaml
│   ├── cmd-002-argument-hint-missing.yaml
│   └── ...
│
├── hook/                        # Hook 组件反模式 (10 个)
│   ├── hook-001-event-type-invalid.yaml
│   └── ...
│
├── subagent/                    # Subagent 反模式 (12 个)
│   ├── sub-001-tools-missing.yaml
│   └── ...
│
├── mcp/                         # MCP 组件反模式 (8 个)
│   ├── mcp-001-server-config-invalid.yaml
│   └── ...
│
├── intent/                      # 意图匹配反模式 (4 个) [新增]
│   ├── INTENT-001-missing-trigger-scenario.yaml
│   └── ...
│
├── llm/                         # LLM 兼容性反模式 (3 个) [新增]
│   ├── LLM-001-llm-specific-feature-declaration.yaml
│   └── ...
│
├── security/                    # 安全风险评估反模式 (5 个) [新增]
│   ├── SEC-001-command-injection-check.yaml
│   └── ...
│
├── environment/                 # 环境兼容性反模式 (3 个) [新增]
│   ├── ENV-001-os-compatibility-declaration.yaml
│   └── ...
│
└── scalability/                 # 扩展性反模式 (4 个) [新增]
    ├── SCALE-001-token-usage-awareness.yaml
    └── ...
```

---

## 统计概览 (Statistics Overview)

| 组件类型 | 规则数量 | Error | Warning | Info | 覆盖率 |
|----------|----------|-------|---------|------|--------|
| Skill | 19 | 6 | 8 | 6 | Chapter 4 100% + skill-creator |
| Command | 12 | 5 | 6 | 1 | Chapter 5 100% |
| Hook | 10 | 3 | 7 | 0 | Chapter 6 100% |
| Subagent | 12 | 4 | 8 | 0 | Chapter 7 100% |
| MCP | 8 | 4 | 4 | 0 | Chapter 8 100% |
| **意图匹配** | **4** | **0** | **2** | **2** | **新增** |
| **LLM 兼容性** | **3** | **0** | **3** | **0** | **新增** |
| **安全** | **5** | **2** | **2** | **1** | **新增** |
| **环境兼容性** | **3** | **0** | **0** | **3** | **新增** |
| **扩展性** | **4** | **0** | **4** | **0** | **新增** |
| **描述优化 (skill-creator)** | **2** | **0** | **1** | **1** | **skill-creator** |
| **风格优化 (skill-creator)** | **0** | **0** | **0** | **0** | **skill-creator** |
| **评估测试 (skill-creator)** | **2** | **0** | **1** | **1** | **skill-creator** |
| **脚本 Bundling (skill-creator)** | **0** | **0** | **0** | **0** | **skill-creator** |
| **通用规则** | **3** | **1** | **1** | **1** |
| **总计** | **83** | **23** | **44** | **16** | - |

---

## 新增评估维度 (New Evaluation Dimensions)

### 维度 1：意图匹配 (Intent Matching) - 10%

评估技能是否容易被大模型正确匹配。

| ID | 名称 | 严重程度 | 说明 |
|----|------|----------|------|
| INTENT-001 | missing-trigger-scenario | warning | 技能未定义足够的触发场景 |
| INTENT-002 | insufficient-synonym-coverage | info | 技能描述同义词覆盖不足 |
| INTENT-003 | missing-exclusion-scenario | info | 技能未定义排除场景 |
| INTENT-004 | low-action-word-density | warning | 技能描述缺少动作词 |

---

### 维度 6：LLM 模型兼容性 (LLM Compatibility) - 15%

评估技能是否依赖特定 LLM 功能。

| ID | 名称 | 严重程度 | 说明 |
|----|------|----------|------|
| LLM-001 | llm-specific-feature-declaration | **warning** | LLM 特有功能依赖未声明 |
| LLM-002 | model-blocker-check | **warning** | 存在阻断非目标模型的功能 |
| LLM-003 | llm-model-range | warning | 支持的模型范围未声明 |

**一票否决规则**:
- LLM-001 或 LLM-002 为 error → 整体评估不通过
- 有阻断功能且无降级方案 → 整体评估不通过

---

### 维度 4：安全风险评估 (Security) - 20%

评估技能是否存在安全风险。

| ID | 名称 | 严重程度 | 说明 |
|----|------|----------|------|
| SEC-001 | command-injection-check | **error** | 命令注入风险 |
| SEC-002 | sensitive-data-handling | **error** | 敏感数据处理不当 |
| SEC-003 | path-traversal-prevention | warning | 路径遍历风险防护 |
| SEC-004 | tool-permission-minimization | warning | 工具权限未最小化 |
| SEC-005 | external-service-validation | info | 外部服务输入验证 |

**一票否决规则**:
- 安全维度 <60 分 → 整体评估不通过

---

### 维度 5：环境兼容性 (Environment) - 15%

评估技能是否跨平台兼容。

| ID | 名称 | 严重程度 | 说明 |
|----|------|----------|------|
| ENV-001 | os-compatibility-declaration | info | 操作系统兼容性未声明 |
| ENV-002 | shell-compatibility-check | info | Shell 命令兼容性未说明 |
| ENV-003 | path-separator-handling | info | 路径分隔符处理未说明 |

---

### 维度 7：扩展性 (Scalability) - 10%

评估技能能否处理大规模场景。

| ID | 名称 | 严重程度 | 说明 |
|----|------|----------|------|
| SCALE-001 | token-usage-awareness | warning | Token 使用量意识不足 |
| SCALE-002 | batch-processing-mechanism | warning | 分批处理机制缺失 |
| SCALE-003 | timeout-configuration | warning | 超时配置缺失 |
| SCALE-004 | progress-feedback | info | 进度反馈机制缺失 |

---

## 完整反模式索引 (Complete Antipattern Index)

### Skill 反模式 (15 个)

#### 元数据 (Metadata) - 6 个
| ID | 名称 | 严重程度 | 说明 |
|----|------|----------|------|
| SKILL-001 | description-length | error | 描述长度过短或过长 |
| SKILL-002 | name-format | error | 名称格式无效 |
| SKILL-005 | tools-undeclared | error | 使用了未声明的工具 |
| SKILL-006 | model-mismatch | warning | 模型选择不当 |
| SKILL-007 | context-mode-invalid | error | 无效的 context 模式 |
| SKILL-011 | argument-hint-missing | warning | 缺少 argument-hint |

#### 结构 (Structure) - 6 个
| ID | 名称 | 严重程度 | 说明 |
|----|------|----------|------|
| SKILL-003 | missing-examples | warning | 缺少使用示例 |
| SKILL-010 | no-pitfalls | info | 缺少注意事项/陷阱提示 |
| SKILL-014 | content-length-issues | warning | 内容长度问题 (200 字符 -400 行) |
| SKILL-015 | duplicate-sections | warning | 重复的章节 |
| SKILL-016 | references-integrity | warning | 引用完整性缺失 |

#### 写作风格 (Writing Style) - 2 个 [新增]
| ID | 名称 | 严重程度 | 说明 |
|----|------|----------|------|
| STYLE-001 | missing-why-explanation | info | 缺少原因解释 |
| STYLE-002 | excessive-constraints | info | 过度约束 (MUST/ALWAYS/NEVER) |

#### 评估测试 (Eval) - 2 个 [新增]
| ID | 名称 | 严重程度 | 说明 |
|----|------|----------|------|
| EVAL-001 | missing-test-cases | info | 缺少测试用例 (evals/evals.json) |
| EVAL-002 | poor-test-case-quality | warning | 测试用例质量低下 |

#### 脚本 Bundling - 1 个 [新增]
| ID | 名称 | 严重程度 | 说明 |
|----|------|----------|------|
| SCRIPT-001 | repeated-script-across-tests | info | 跨测试用例的重复脚本 |

#### 工作流 (Workflow) - 2 个
| ID | 名称 | 严重程度 | 说明 |
|----|------|----------|------|
| SKILL-008 | workflow-incomplete | warning | 工作流描述不完整 |
| SKILL-009 | error-handling-missing | warning | 缺少错误处理说明 |

#### 性能 (Performance) - 1 个
| ID | 名称 | 严重程度 | 说明 |
|----|------|----------|------|
| SKILL-004 | token-excessive | warning | Token 使用量过高 |

#### 安全 (Security) - 2 个
| ID | 名称 | 严重程度 | 说明 |
|----|------|----------|------|
| SKILL-012 | context-invalid | error | context 值与 Skill 类型不匹配 |
| SKILL-013 | tools-overprivileged | warning | 工具权限过于宽泛 |

---

### Command 反模式 (12 个)

| ID | 名称 | 严重程度 | 说明 |
|----|------|----------|------|
| CMD-001 | description-missing | error | 缺少描述 |
| CMD-002 | argument-hint-missing | error | 缺少 argument-hint |
| CMD-003 | no-examples | warning | 缺少使用示例 |
| CMD-004 | slash-command-invalid | error | 无效的斜杠命令格式 |
| CMD-005 | parameter-validation-missing | warning | 缺少参数验证 |
| CMD-006 | help-text-unclear | warning | 帮助文本不清晰 |
| CMD-007 | output-format-unspecified | info | 未指定输出格式 |
| CMD-008 | error-handling-missing | error | 缺少错误处理说明 |
| CMD-009 | permission-check-missing | error | 缺少权限检查 |
| CMD-010 | no-usage-examples | warning | 缺少详细使用示例 |
| CMD-011 | subagent-call-undocumented | warning | Subagent 调用未记录 |
| CMD-012 | context-mode-invalid | error | 无效的 context 模式 |

---

### Hook 反模式 (10 个)

| ID | 名称 | 严重程度 | 说明 |
|----|------|----------|------|
| HOOK-001 | event-type-invalid | error | 无效的事件类型 |
| HOOK-002 | handler-missing | error | 缺少处理器定义 |
| HOOK-003 | condition-too-complex | warning | 触发条件过于复杂 |
| HOOK-004 | side-effect-heavy | warning | 副作用过大 |
| HOOK-005 | no-async-handling | warning | 缺少异步处理说明 |
| HOOK-006 | error-not-propagated | error | 错误未正确传播 |
| HOOK-007 | missing-cleanup | warning | 缺少清理逻辑 |
| HOOK-008 | trigger-too-broad | warning | 触发范围过于宽泛 |
| HOOK-009 | no-idempotency | warning | 缺少幂等性保证 |
| HOOK-010 | missing-documentation | warning | 文档不完整 |

---

### Subagent 反模式 (12 个)

| ID | 名称 | 严重程度 | 说明 |
|----|------|----------|------|
| SUB-001 | tools-missing | error | 缺少工具声明 |
| SUB-002 | model-unspecified | warning | 未指定模型 |
| SUB-003 | context-unclear | warning | 上下文模式不清晰 |
| SUB-004 | description-vague | warning | 描述过于模糊 |
| SUB-005 | allowed-tools-overly-broad | warning | 工具权限过于宽泛 |
| SUB-006 | no-task-boundary | error | 缺少任务边界定义 |
| SUB-007 | missing-output-format | warning | 缺少输出格式说明 |
| SUB-008 | recursion-risk | error | 递归调用风险 |
| SUB-009 | no-timeout-handling | warning | 缺少超时处理 |
| SUB-010 | model-mismatch | warning | 模型选择不匹配 |
| SUB-011 | missing-fallback | warning | 缺少降级策略 |
| SUB-012 | state-management-unclear | warning | 状态管理不清晰 |

---

### MCP 反模式 (8 个)

| ID | 名称 | 严重程度 | 说明 |
|----|------|----------|------|
| MCP-001 | server-config-invalid | error | 服务器配置无效 |
| MCP-002 | auth-missing | error | 缺少认证配置 |
| MCP-003 | env-vars-hardcoded | warning | 硬编码环境变量 |
| MCP-004 | timeout-not-set | warning | 未设置超时 |
| MCP-005 | retry-logic-missing | warning | 缺少重试逻辑 |
| MCP-006 | error-handling-missing | error | 缺少错误处理 |
| MCP-007 | tool-schema-invalid | error | 工具 Schema 无效 |
| MCP-008 | no-health-check | warning | 缺少健康检查 |

---

## 评估维度权重 (Evaluation Dimension Weights)

| 维度 | 权重 | 规则数 | 一票否决 |
|------|------|--------|---------|
| 1. 意图匹配 | 10% | 4 | 否 |
| 2. 配置和使用方法 | 15% | 5 | 否 |
| 3. 外部基础设施依赖 | 15% | 12 | 否 |
| 4. 安全风险评估 | 20% | 5 | **是** |
| 5. 环境兼容性 | 15% | 3 | 否 |
| 6. LLM 模型兼容性 | 15% | 3 | **是** |
| 7. 扩展性 | 10% | 4 | 否 |
| **总计** | **100%** | **76** | - |

---

## HANDBOOK 章节映射 (HANDBOOK Chapter Mapping)

| 手册章节 | 反模式目录 | 规则数量 | 覆盖范围 |
|----------|-----------|----------|----------|
| Chapter 4: Skill 规范 | `skill/` | 15 | metadata, structure, workflow |
| Chapter 5: Command 规范 | `command/` | 12 | metadata, arguments, validation |
| Chapter 6: Hook 规范 | `hook/` | 10 | event, handler, lifecycle |
| Chapter 7: Subagent 规范 | `subagent/` | 12 | tools, model, boundaries |
| Chapter 8: MCP 规范 | `mcp/` | 8 | config, auth, schema |
| **扩展规范** | `intent/`, `llm/`, `security/`, `environment/`, `scalability/` | **19** | intent, llm, security, env, scalability |
| **总计** | | **76** | |

---

## 使用指南 (Usage Guide)

### 审阅时加载规则 (Loading Rules During Review)

```python
# 根据组件类型加载基础规则
if component_type == "skill":
    load_antipatterns("skill/*.yaml")
elif component_type == "command":
    load_antipatterns("command/*.yaml")
# ...

# 加载扩展维度规则 (始终加载)
load_antipatterns("intent/*.yaml")
load_antipatterns("llm/*.yaml")
load_antipatterns("security/*.yaml")
load_antipatterns("environment/*.yaml")
load_antipatterns("scalability/*.yaml")
```

### 综合评分计算

```python
# 维度评分
dimension_score = sum(rule_score * weight for rule in dimension)

# 综合评分
overall_score = sum(dimension_score * weight for dimension in dimensions)

# 一票否决检查
if security_dimension < 60:
    overall_score = min(overall_score, 59)  # 不及格
if llm_has_blocker_without_fallback:
    overall_score = min(overall_score, 59)  # 不及格
```

---

## 版本历史 (Version History)

| 版本 | 日期 | 变更 |
|------|------|------|
| **3.0.0** | 2026-03-04 | 新增 7 个评估维度，76 个反模式 |
| 2.0.0 | 2026-02-28 | 重构为组件类型组织，57 个反模式 |
| 1.0.0 | 2026-02-27 | 初始版本，36 个反模式 |

---

**文档版本**: 3.0.0
**最后更新**: 2026-03-04
**基于**: HANDBOOK 完整手册 + 7 个新增评估维度
