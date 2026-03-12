---
name: cmd-review
model: sonnet
context: fork
disable-model-invocation: true
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, Task]
description: "执行组件质量审查，覆盖76+反模式和8维度。触发：审查/评审/验证。输出问题清单和改进建议。"
argument-hint: "[--target=<path>] [--artifact-id=current] [--type=standard|migration] [--linkage-check=true] [--no-arch] [--arch-only] [--lang=zh-cn|en-us|ja-jp]"
---

# /ccc:review

**适用流程**:
- **主工作流**: `design` → **review** → `fix` → `validate` → `build`
- **代码迭代**: `implement` → **review** → `fix`
- **制品迭代**: `iterate` → **review** → `fix` → `build`

Performs comprehensive component quality review using 76+ antipatterns across 8 dimensions.

## 模型要求

- **推荐**: Claude Opus 4.5+ (最高质量,全面审查)
- **可用**: Claude Sonnet 4.5+ (高效能,标准审查)
- **最小**: Claude Sonnet 4.5+ (最低要求)

### 功能需求
- 需要支持 Tool Use (Bash, Read, Write, Edit, Glob, Grep, Task)
- 需要支持多轮对话和复杂分析
- 需要处理 76+ 条反模式规则
- 建议上下文窗口 >= 200K tokens (处理大型代码库审查)

## Usage

```bash
# 审查整个项目目录（推荐）
/ccc:review --target=/path/to/project

# 审查当前工作目录
/ccc:review --target=.

# 审查 CCC 工件（向后兼容）
/ccc:review --artifact-id=DLV-001                    # 完整审查
/ccc:review --artifact-id=BLP-003 --type=migration   # 迁移计划审查
/ccc:review --artifact-id=DLV-001 --no-arch          # 跳过架构分析
/ccc:review --artifact-id=DLV-001 --lang=en-us       # 英文输出
```

## Global Parameters

| 参数 | 值 | 默认值 | 说明 |
|------|-----|--------|------|
| `--target` | 路径 | 当前目录 | 审查目标目录，自动扫描所有技能/命令/代理文件 |
| `--lang` | `zh-cn`, `en-us`, `ja-jp` | `zh-cn` | 输出语言 |
| `--with-eval` | `true`/`false` | `false` | 执行 Eval 机制，对比 with-skill vs baseline |
| `--eval-only` | `true`/`false` | `false` | 仅执行 Eval，跳过其他检查 |

## 8 个评估维度（默认全部开启）

| 维度 | 权重 | 规则数 | 说明 |
|------|------|--------|------|
| 1. 意图匹配 | 10% | 4 | 触发场景、同义词覆盖、排除场景、动作词密度 |
| 2. 配置和使用方法 | 15% | 5 | 前置配置、示例质量、错误处理 |
| 3. 外部基础设施依赖 | 15% | 12 | 运行时依赖、外部 API、工具链、环境变量 |
| 4. 安全风险评估 | 20% | 5 | 命令注入、敏感数据、路径遍历、权限最小化 |
| 5. 环境兼容性 | 15% | 3 | OS 兼容性、Shell 兼容性、路径分隔符 |
| 6. LLM 模型兼容性 | 15% | 3 | 特有功能声明、阻断功能检查、模型范围 |
| 7. 扩展性 | 10% | 4 | Token 使用、分批处理、超时配置、进度反馈 |
| 8. 可测试性 | 15% | 5 | 测试定义/测试框架/测试夹具/测试文档/功能可验证 |
| **架构分析 (L1+L2)** | **额外** | **15** | **默认开启，可用 `--no-arch` 禁用** |

### 禁用维度

| 参数 | 说明 |
|------|------|
| `--no-arch` | 仅禁用架构分析 (L1+L2)，7 个维度仍然开启 |
| `--arch-only` | 仅运行架构检查，跳过其他维度 |

**注意**: 8 个评估维度始终默认开启，无法单独禁用某个维度。如需快速审查，使用 `--no-arch`。

---

## Workflow

### 输入要求
- **必需参数**: `--target=<path>` 审查目标目录（可选，默认当前目录）或 `--artifact-id=<id>` CCC 工件 ID
- **可选参数**:
  - `--lang=zh-cn|en-us|ja-jp` 输出语言
  - `--with-eval=true|false` 执行 Eval 机制
  - `--no-arch` 跳过架构分析
  - `--arch-only` 仅运行架构检查
- **前置条件**:
  - 目标目录包含可审查的组件文件（skills/、commands/、agents/）
  - 或指定的 CCC 工件存在

### 执行步骤

**Step 1: 扫描目标**
- 扫描目标目录或加载指定工件
- 识别所有可审查组件（Skill、Command、Agent、Hook）
- 统计组件数量和类型分布
- **错误处理**: 目标不存在时提示检查路径；无可审查组件时报告并退出

**Step 2: 加载反模式规则**
- 从规则库加载 76+ 条反模式规则
- 按维度分类（intent、config、dependency、security、environment、llm、scalability、testability）
- **新增：根据组件类型加载类型特定规则（三层防护体系-评审环节）**
  - cmd-* skills: 加载工作流规则（WORKFLOW-002），排除触发场景规则（INTENT-001,002,003）
  - std-* skills: 加载触发场景规则（INTENT-*），排除工作流规则（WORKFLOW-002）
  - lib-* skills: 加载知识库规则（LIB-*），排除触发场景和工作流规则
- 加载架构分析规则（L1+L2，15条）
- 验证规则完整性
- **错误处理**: 规则文件缺失时使用内置规则；规则解析失败时跳过该规则并记录警告

**类型特定规则加载逻辑**:

```python
def loadAntipatterns(component_type, skill_name):
    """
    根据skill类型加载不同的反模式规则

    Args:
        component_type: 'skill' | 'command' | 'agent' | 'hook'
        skill_name: e.g., 'cmd-review', 'std-workflow-attribution'

    Returns:
        适用的反模式规则列表
    """
    if component_type != 'skill':
        return load_standard_antipatterns(component_type)

    # Skill组件需要区分cmd/std/lib
    if skill_name.startswith('cmd-'):
        return load_cmd_antipatterns()
    elif skill_name.startswith('std-'):
        return load_std_antipatterns()
    elif skill_name.startswith('lib-'):
        return load_lib_antipatterns()
    else:
        # 未遵循命名规范
        return load_standard_antipatterns('skill')

def load_cmd_antipatterns():
    """cmd-* skills专用规则集"""
    return [
        'antipatterns/skill/*.yaml',           # 通用Skill规则
        'antipatterns/workflow/WORKFLOW-002.yaml',  # cmd专用工作流规则
        '!antipatterns/intent/INTENT-001.yaml',     # 排除触发场景规则
        '!antipatterns/intent/INTENT-002.yaml',     # 排除同义词规则
        '!antipatterns/intent/INTENT-003.yaml',     # 排除排除场景规则
    ]

def load_std_antipatterns():
    """std-* skills专用规则集"""
    return [
        'antipatterns/skill/*.yaml',      # 通用规则
        'antipatterns/intent/*.yaml',     # 强制触发场景规则
        '!antipatterns/workflow/WORKFLOW-002.yaml',  # 排除工作流规则
    ]

def load_lib_antipatterns():
    """lib-* skills专用规则集"""
    return [
        'antipatterns/skill/*.yaml',      # 通用规则
        'antipatterns/library/*.yaml',    # lib专用规则
        '!antipatterns/intent/*.yaml',    # 排除触发场景规则
        '!antipatterns/workflow/*.yaml',  # 排除工作流规则
    ]
```

**Step 3: 执行 8 维度评估**
- 依次执行 8 个评估维度检测
- 每个维度独立评分（0-100）
- 记录发现的问题（P0 Error、P1 Warning、P2 Info）
- 标记问题所在文件和行号
- **错误处理**: 单个维度检测失败时记录并继续其他维度；检测超时时使用已收集结果

**Step 4: 执行架构分析（可选）**
- 分析工作流结构（L1）
- 分析组件关系和职责（L2）
- 检测循环依赖和隐式调用
- 生成调用图和依赖图
- **错误处理**: 使用 `--no-arch` 跳过此步骤；架构分析失败时标记为"未完成"并继续

**Step 5: 计算综合评分**
- 汇总各维度评分
- 按权重计算综合评分（0-100）
- 确定评级（优秀 A+、良好 B+、需改进 C、不足 D）
- 统计问题总数和优先级分布
- **错误处理**: 评分计算异常时使用保守评分；缺失维度时按比例调整权重

**Step 6: 生成审查报告**
- 创建详细审查报告文件
- 包含执行摘要、维度评分、问题清单、改进建议
- 输出控制台摘要
- 保存报告到 docs/reviews/
- **错误处理**: 报告生成失败时输出到控制台；目录不存在时自动创建

### 预期输出
- **主要制品**: `docs/reviews/YYYY-MM-DD-<project>-comprehensive-review.md`
- **审查报告结构**:
  - 执行摘要（综合评分、问题统计、评级）
  - 评估维度评分（8 个维度详细得分和问题）
  - 架构分析结果（工作流图、组件关系、循环依赖）
  - 问题清单（按优先级和文件分组）
  - 改进建议（修复优先级、行动计划）
  - 历史对比（如有历史审查记录）
- **控制台输出**: 综合评分、关键问题摘要、报告路径
- **可选输出**: Eval 结果（benchmark.json、benchmark.md）

### 错误处理
- **目标不存在** → 提示检查路径或使用 `/ccc:status` 查看可用工件
- **无可审查组件** → 报告"目录中无可审查组件"并列出支持的组件类型
- **规则加载失败** → 使用内置规则继续，标记为"部分规则模式"
- **维度检测超时** → 使用已收集结果，标记该维度为"部分完成"
- **报告生成失败** → 至少输出控制台摘要，保存临时结果到 /tmp
- **通用错误** → 保存已完成的分析结果，提供恢复命令

---

## SubAgents 协作

本工作流使用以下 SubAgents 进行任务分解和并行执行：

### 核心 Agents
- **ccc:reviewer-core**: 审查协调器，负责整体审查流程编排
- **ccc:review-core**: 智能审阅核心，基于组件类型加载反模式库执行深度质量检查
- **ccc:architecture-analyzer**: 架构分析器，执行 L1+L2 架构分析（工作流/组件/职责/协作/命令）
- **ccc:dependency-analyzer**: 依赖分析器，检查链路验证（调用图/循环依赖/隐式调用）
- **ccc:linkage-validator**: 链路验证器，验证 skills 字段引用完整性
- **ccc:review-aggregator**: 审查结果聚合器，汇总多维度审查结果
- **ccc:report-renderer**: 报告渲染器，生成最终的审查报告

### 辅助 Agents
- **ccc:workflow-discoverer**: 工作流发现器，识别工作流模式和阶段
- **ccc:eval-executor**: Eval 执行器，运行测试用例和基准测试
- **ccc:eval-grader**: Eval 评分器，对测试结果打分
- **ccc:eval-parser**: Eval 解析器，解析 evals.json 测试定义

### 调度策略
- **串行执行**: cmd-review → ccc:reviewer-core → ccc:review-aggregator → ccc:report-renderer
- **并行执行**:
  - 8 维度检查并行：意图匹配、配置、依赖、安全、环境、LLM、扩展性、可测试性
  - 架构分析并行：architecture-analyzer + dependency-analyzer + linkage-validator
  - Eval 执行并行（可选）：eval-executor + eval-grader + eval-parser
- **错误处理**: 单个维度失败不影响其他维度，继续执行并在报告中标记

### Agent 输入输出
| Agent | 输入 | 输出 |
|-------|------|------|
| ccc:reviewer-core | 审查目标路径/工件 ID + 参数 | 审查任务分解 |
| ccc:review-core | 组件文件 + 反模式规则 | 单个组件审查结果（JSON）|
| ccc:architecture-analyzer | 所有组件 | 架构分析报告 |
| ccc:dependency-analyzer | 所有组件 | 依赖关系图和问题 |
| ccc:linkage-validator | 所有组件 | 链路验证结果 |
| ccc:review-aggregator | 所有审查结果 | 聚合评分和问题清单 |
| ccc:report-renderer | 聚合结果 | Markdown 审查报告 |
| ccc:eval-executor | 测试定义 | 测试执行结果 |

### 调用示例
```
用户: /ccc:review --target=/path/to/project
  ↓
cmd-review 解析参数和扫描目标
  ↓
调用 ccc:reviewer-core (编排审查流程)
  ↓
并行执行多维度检查:
  - ccc:review-core (8 维度规则检查) × N 个组件
  - ccc:architecture-analyzer (L1+L2 分析)
  - ccc:dependency-analyzer (链路验证)
  - ccc:linkage-validator (引用检查)
  - eval-executor (可选，测试执行)
  ↓
调用 review-aggregator (聚合结果)
  ↓
调用 report-renderer (生成报告)
  ↓
cmd-review 输出摘要和报告路径
```

### Eval 机制（可选）
当使用 `--with-eval` 参数时，审查流程会额外执行 Eval 机制：
```
cmd-review --with-eval
  ↓
eval-parser 解析 evals/evals.json
  ↓
eval-executor 执行测试用例 (with-skill vs baseline)
  ↓
eval-grader 评分和对比
  ↓
结果合并到审查报告的可测试性维度
```

---

## 第 8 维度：可测试性检查

### 检查项

| 检查项 | 权重 | 检查内容 |
|--------|------|----------|
| 测试定义 | 25% | 是否有 evals.json 定义测试用例？ |
| 测试框架 | 25% | 是否有 tests/ 目录和测试文件？ |
| 测试夹具 | 15% | 是否有 test-fixtures/ 目录？ |
| 测试文档 | 15% | 是否有测试指南 README？ |
| 功能可验证 | 20% | 输入→输出是否清晰可验证？ |

### 评分标准

| 分数 | 状态 | 说明 |
|------|------|------|
| 90-100 | ✅ 优秀 | 测试完整，覆盖率高，文档齐全 |
| 70-89 | ✅ 良好 | 基本测试覆盖，有文档 |
| 50-69 | ⚠️ 需改进 | 有部分测试，但不完整 |
| <50 | ❌ 不足 | 缺少测试框架或文档 |

### 常见问题代码

| 问题代码 | 问题描述 | 建议 |
|----------|----------|------|
| TEST-001 | 缺少测试用例定义 | 创建 evals/evals.json |
| TEST-002 | 功能不可验证 | 明确预期输出格式 |
| TEST-003 | 缺少边界测试 | 添加空输入、大输入测试 |
| TEST-004 | 缺少测试文档 | 添加 tests/README.md |

## 使用方式

### 模式 1: 审查整个项目目录（推荐）

```bash
# 审查指定目录
/ccc:review --target=/Users/xqh/clawd/opensource/glaf4/GTMC-GLAF4-CC-SKILL

# 审查当前工作目录
/ccc:review --target=.

# 审查上级目录
/ccc:review --target=..
```

**审查范围**:
- `skills/**/*.md` - 所有技能定义
- `commands/**/*.md` - 所有命令定义
- `agents/**/*.md` - 所有子代理定义
- `hooks/**` - 所有钩子配置

**输出**:
- 控制台：审查摘要和关键问题
- 文件：`docs/reviews/YYYY-MM-DD-<project>-comprehensive-review.md`

### 模式 2: 审查 CCC 工件（向后兼容）

```bash
/ccc:review --artifact-id=DLV-001                    # 完整审查
/ccc:review --artifact-id=BLP-003 --type=migration   # 迁移计划审查
/ccc:review --artifact-id=DLV-001 --no-arch          # 跳过架构分析
```

### 模式 3: 交互式审查

```bash
/ccc:review
```

不带参数运行时，**默认执行最全面的审查**：
- 扫描当前工作目录下所有组件
- 启用所有 7 个评估维度
- 启用链路验证（调用图、循环依赖、隐式调用）
- 启用架构分析（5 维度：工作流/组件/职责/协作/命令）
- 生成完整审查报告

```
审查模式：全面审查（默认）

审查范围:
- skills/**/*.md - 所有技能定义
- commands/**/*.md - 所有命令定义
- agents/**/*.md - 所有子代理定义
- hooks/** - 所有钩子配置

评估维度：全部启用 (8/8 + 链路 + 架构)
- [x] 意图匹配 (INTENT)
- [x] 配置和使用方法 (CONFIG)
- [x] 外部基础设施依赖 (DEPEND)
- [x] 安全风险评估 (SECURITY)
- [x] 环境兼容性 (ENV)
- [x] LLM 模型兼容性 (LLM)
- [x] 扩展性 (SCALE)
- [x] **可测试性 (TEST)** - 测试定义/框架/夹具/文档
- [x] 链路验证 (LINKAGE) - 调用图/循环依赖/隐式调用
- [x] 架构分析 (ARCH) - 工作流/组件/职责/协作/命令

如需自定义，请使用参数：
- /ccc:review --target=/path - 审查指定目录
- /ccc:review --no-arch - 跳过架构分析和链路验证
- /ccc:review --artifact-id=xxx - 审查 CCC 工件
```

---

## 输出规格

### 报告结构 (增强版)

**第一部分：插件概述**
- 插件定位（名称、类型、核心功能）
- 核心工作流（阶段图、输入输出、使用示例）
- 架构概览（组件统计、协作关系）

**第二部分：审查结果**
- 执行摘要（综合评分、问题统计）
- 评估维度评分（8 个维度 + 架构 + 工作流）
- 规则验证（规则加载状态、验证详情）
- 组件合规性检查
- 问题清单

**第三部分：改进建议**
- 修复优先级（P0/P1/P2）
- 改进行动计划

**第四部分：审查结论**
- 综合评估
- 审查通过项
- 历史对比


### 控制台输出

```
审查报告：GTMC-GLAF4-CC-SKILL

综合评分：87/100 (良好 B+)

维度评分:
┌────────────────────┬───────┬──────────┐
│ 维度               │ 得分  │ 权重     │
├────────────────────┼───────┼──────────┤
│ 意图匹配           │ 85/100│ 10%      │
│ 配置和使用方法     │ 88/100│ 15%      │
│ 外部基础设施依赖   │ 82/100│ 15%      │
│ 安全风险评估       │ 90/100│ 20%      │
│ 环境兼容性         │ 85/100│ 15%      │
│ LLM 模型兼容性     │ 92/100│ 15%      │
│ 扩展性             │ 80/100│ 10%      │
│ 架构分析 (L1+L2)  │ 95/100│ 额外     │
└────────────────────┴───────┴──────────┘

发现的问题:
  ⚠️ INTENT-001: 触发场景不足 (skills/xxx/SKILL.md)
  ⚠️ LLM-002: 阻断功能无降级方案 (skills/yyy/SKILL.md)

修复建议:
  1. 为 skills/xxx 添加触发场景说明
  2. 为 skills/yyy 添加降级方案

状态：通过 (有警告)
完整报告：docs/reviews/2026-03-04-GTMC-GLAF4-CC-SKILL-comprehensive-review.md
```

### 文件输出

| 属性 | 值 |
|------|-----|
| **目录** | `docs/reviews/` |
| **文件名** | `YYYY-MM-DD-<project>-comprehensive-review.md` |
| **格式** | Markdown |
| **覆盖** | 否（时间戳确保唯一性） |

---

## 示例

### 示例 1: 审查整个插件项目

```bash
/ccc:review --target=/Users/xqh/clawd/opensource/glaf4/GTMC-GLAF4-CC-SKILL
```

**审查流程**:
1. 扫描目标目录下所有 `.md` 文件
2. 识别组件类型 (Skill/Command/Agent/Hook)
3. 加载 76+ 条反模式规则：
   - `intent/*.yaml` (4 条)
   - `security/*.yaml` (5 条)
   - `llm/*.yaml` (3 条)
   - `environment/*.yaml` (3 条)
   - `scalability/*.yaml` (4 条)
   - `skill/*.yaml` (15 条)
   - `command/*.yaml` (12 条)
   - `hook/*.yaml` (10 条)
   - `subagent/*.yaml` (12 条)
   - `architecture/*.yaml` (15 条)
4. 执行检测并生成评分
5. 生成详细审查报告

### 示例 2: 快速审查（跳过架构分析）

```bash
/ccc:review --target=. --no-arch
```

**适用场景**: 只需要检查基础合规性，不需要架构分析。

### 示例 3: 仅架构分析

```bash
/ccc:review --target=. --arch-only
```

**适用场景**: 只需要检查架构问题，不需要检查文档合规性。

### 模式 4: 执行 Eval 机制

```bash
/ccc:review --target=skills/xxx --with-eval
```

**输出**:
- 审查报告
- benchmark.json
- benchmark.md

**适用场景**: 需要对比 with-skill 和 baseline 的性能差异。
