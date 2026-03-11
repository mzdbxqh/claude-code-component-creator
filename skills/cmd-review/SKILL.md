---
name: ccc:cmd-review
model: sonnet
context: fork
allowed-tools: Bash, Read, Write, Edit, Glob, Grep
description: "质量审查 | 场景: 多流程的检查点"
argument-hint: "[--target=<path>] [--artifact-id=current] [--type=standard|migration] [--linkage-check=true] [--no-arch] [--arch-only] [--lang=zh-cn|en-us|ja-jp]"
---

# /ccc:review

**适用流程**:
- **主工作流**: `design` → **review** → `fix` → `validate` → `build`
- **代码迭代**: `implement` → **review** → `fix`
- **制品迭代**: `iterate` → **review** → `fix` → `build`

Performs comprehensive component quality review using 76+ antipatterns across 8 dimensions.

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
