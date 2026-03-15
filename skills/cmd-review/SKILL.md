---
name: cmd-review
model: sonnet
context: fork
disable-model-invocation: true
allowed-tools: [Bash, Read, Write, Edit, Glob, Grep, Task]
description: "开发流程第4步。执行组件质量审查，覆盖161+反模式和8维度。触发：审查/评审/验证。承接implement的代码，发现问题输出给fix。"
argument-hint: "[--target=<path>] [--artifact-id=current] [--type=standard|migration] [--linkage-check=true] [--no-arch] [--arch-only] [--lang=zh-cn|en-us|ja-jp] [--skip-profiling=false] [--profile-only=false] [--profile-output=docs/profile/] [--no-reference-check=false] [--reference-only=false] [--interactive=false]"
---

# /cmd-review

**适用流程**:
- **开发流程**: `init` → `design` → `implement` → **review** → `fix` → `validate` → `build`
- **迭代流程**: `design-iterate` → `implement` → **review** → `fix`
- **制品迭代**: `iterate` → **review** → `build`
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

## 资源预算

### Token 使用估计

| 场景 | 输入 Token | 输出 Token | 总计 | 成本估计 | 说明 |
|------|-----------|-----------|------|----------|------|
| 单个组件 | 5K-10K | 3K-6K | 8K-16K | $0.06-$0.13 | 基础审查 |
| 小型项目 (5-10组件) | 20K-40K | 10K-20K | 30K-60K | $0.25-$0.50 | 标准审查 |
| 中型项目 (10-20组件) | 40K-80K | 20K-40K | 60K-120K | $0.50-$1.00 | 全面审查 |
| 大型项目 (20+组件) | 80K-150K | 40K-80K | 120K-230K | $1.00-$2.00 | 深度审查 |

**成本基准**: Claude Sonnet 4.5 (输入: $3/MTok, 输出: $15/MTok)

### Token 使用分解

**阶段 1: 组件扫描与加载** (5K-20K tokens)
- Glob 文件查找 (1K-3K)
- 组件元数据提取 (2K-8K)
- SKILL.md 内容读取 (2K-9K)

**阶段 2: 反模式规则加载** (8K-15K tokens)
- 76+ 条反模式定义
- 类型特定规则过滤 (cmd-*/std-*/lib-*)
- 严重性和分类信息

**阶段 3: SubAgent 并行审查** (20K-100K tokens)
- **review-core**: 每个组件 2K-5K
  - 8维度质量检查
  - 反模式匹配和验证
- **architecture-analyzer**: 10K-20K
  - 工作流架构分析
  - 组件协作评估
- **dependency-analyzer**: 5K-15K
  - 依赖关系构建
  - 循环依赖检测
- **linkage-validator**: 5K-15K
  - 调用链验证
  - 参数匹配检查

**阶段 4: 结果聚合与报告** (5K-20K tokens)
- review-aggregator 收集结果 (2K-5K)
- report-renderer 生成 Markdown (3K-15K)

### 成本详细分解

**按项目规模**:

| 项目规模 | 组件数 | 平均 Token | 成本/次 | 月度成本 (4次) |
|---------|-------|-----------|--------|---------------|
| 小型 | 5-10 | 45K | $0.38 | $1.50 |
| 中型 | 10-20 | 90K | $0.75 | $3.00 |
| 大型 | 20-50 | 175K | $1.50 | $6.00 |
| 超大 | 50+ | 300K+ | $2.50+ | $10.00+ |

**按审查维度**:

| 审查模式 | Token 节省 | 成本节省 | 说明 |
|---------|-----------|----------|------|
| 全维度 (默认) | 0% | $0.00 | 8个维度全部审查 |
| 核心维度 (--dims=核心) | 30% | 30% | 仅审查4个核心维度 |
| 单一维度 (--dims=intent) | 70% | 70% | 仅审查指定维度 |

### 优化建议

**1. 选择性审查**

减少审查范围以降低 Token 使用：

```bash
# 仅审查核心维度（节省 30% Token）
/cmd-review --dims=intent,config,architecture,testability

# 仅审查变更的组件（增量审查）
/cmd-review --changed-only --since=last-commit

# 跳过低优先级组件
/cmd-review --exclude=lib-* --exclude=test-*
```

**2. 并行处理优化**

启用并行模式减少总体耗时（不减少 Token）：

```bash
# 并行审查多个组件（加快速度）
/cmd-review --parallel --max-workers=4
```

**3. 增量审查策略**

仅审查变更部分：

```bash
# 基于 git diff 的增量审查
/cmd-review --incremental --base=main

# 复用上次审查结果
/cmd-review --resume=last-review-id
```

**4. Token 预算控制**

设置 Token 上限防止意外成本：

```bash
# 设置最大 Token 限制
/cmd-review --max-tokens=50000

# 超出预算时提前终止
/cmd-review --budget-limit=100000 --stop-on-limit
```

**5. 分层审查策略**

先快速审查，再深度审查：

```bash
# 第一轮：快速扫描（低 Token）
/cmd-review --quick --dims=intent,config

# 第二轮：深度审查问题组件（高 Token）
/cmd-review --detailed --only=failed-components
```

### Token 使用监控

审查过程中会实时输出 Token 使用情况：

```
[INFO] Review started: 15 components
[INFO] Token usage: component scanning (8,234 tokens)
[INFO] Token usage: antipattern loading (12,456 tokens)
[INFO] Token usage: review-core batch 1 (23,567 tokens)
[INFO] Token usage: review-core batch 2 (21,345 tokens)
[INFO] Token usage: architecture-analyzer (15,678 tokens)
[INFO] Token usage: report generation (6,789 tokens)
[INFO] Total tokens used: 88,069 (estimated cost: $0.73)
[INFO] Projected monthly cost (4 reviews): $2.92
```

### 性能与成本权衡

| 策略 | Token 使用 | 审查质量 | 适用场景 |
|------|-----------|----------|----------|
| 快速审查 | 低 (30%) | 基础 | CI/CD 预检查 |
| 标准审查 | 中 (100%) | 全面 | 定期质量检查 |
| 深度审查 | 高 (150%) | 深入 | 发版前审查 |

## Usage

```bash
# 审查整个项目目录（推荐）
/cmd-review --target=/path/to/project

# 审查当前工作目录
/cmd-review --target=.

# 审查 CCC 工件（向后兼容）
/cmd-review --artifact-id=DLV-001                    # 完整审查
/cmd-review --artifact-id=BLP-003 --type=migration   # 迁移计划审查
/cmd-review --artifact-id=DLV-001 --no-arch          # 跳过架构分析
/cmd-review --artifact-id=DLV-001 --lang=en-us       # 英文输出
```

## Global Parameters

| 参数 | 值 | 默认值 | 说明 |
|------|-----|--------|------|
| `--target` | 路径 | 当前目录 | 审查目标目录，自动扫描所有技能/命令/代理文件 |
| `--lang` | `zh-cn`, `en-us`, `ja-jp` | `zh-cn` | 输出语言 |
| `--with-eval` | `true`/`false` | `false` | 执行 Eval 机制，对比 with-skill vs baseline |
| `--eval-only` | `true`/`false` | `false` | 仅执行 Eval，跳过其他检查 |
| `--parallel` | `true`/`false` | `false` | 启用并行审查模式（推荐用于 10+ 组件） |
| `--max-workers` | 数字 | `4` | 并行模式下的最大并发数（1-8，需要 `--parallel=true`） |
| `--batch-size` | 数字 | `10` | 每批处理的组件数量（防止内存溢出） |
| `--skip-profiling` | `true`/`false` | `false` | 跳过插件画像生成（高级用户） |
| `--profile-only` | `true`/`false` | `false` | 仅生成插件画像，不进行质量审查 |
| `--profile-output` | 路径 | `docs/profile/` | 插件画像输出目录 |
| `--no-reference-check` | `true`/`false` | `false` | 跳过引用完整性扫描 |
| `--reference-only` | `true`/`false` | `false` | 仅执行引用扫描，跳过其他检查 |
| `--interactive` | `true`/`false` | `false` | 启用交互模式，通过多选菜单选择要执行的检查项 |

### 并行处理说明

**性能对比**:

| 模式 | 10 组件 | 50 组件 | 100 组件 | 说明 |
|------|---------|---------|----------|------|
| 串行 (默认) | ~15 分钟 | ~75 分钟 | ~150 分钟 | 稳定但慢 |
| 并行 (4 workers) | ~4 分钟 | ~20 分钟 | ~40 分钟 | 3.75x 加速 |
| 并行 (8 workers) | ~3 分钟 | ~12 分钟 | ~22 分钟 | 6.8x 加速 |

**推荐配置**:
- **小型项目 (<10 组件)**: 使用默认串行模式
- **中型项目 (10-50 组件)**: `--parallel --max-workers=4`
- **大型项目 (50+ 组件)**: `--parallel --max-workers=8 --batch-size=20`

**注意事项**:
1. 并行模式会消耗更多内存（约 2-4GB per worker）
2. Token 成本不变，但速度显著提升
3. 并行模式可能导致输出顺序不一致
4. 某些平台可能限制并发 API 调用

**并行审查示例**:

```bash
# 启用并行模式（默认 4 workers）
/cmd-review --parallel

# 指定并发数
/cmd-review --parallel --max-workers=8

# 大型项目配置
/cmd-review --target=. --parallel --max-workers=8 --batch-size=20

# 增量并行审查
/cmd-review --changed-only --parallel --max-workers=4
```

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
| **9. 组件规范 (新增)** | **额外** | **69** | **skill/subagent/hook/workflow 专用规则** |
| **10. 遗留检测 (新增)** | **额外** | **23** | **Command 迁移、命名规范、特定场景检测** |
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

**Step 0: 生成插件画像**
- **条件**: 如果 `--skip-profiling=false`（默认开启）
- **目标**: 提取插件完整画像，确保报告自解释性

**执行流程**:

1. **检查缓存**
   - 检查缓存文件是否存在: `$profile_output/plugin-profile.json`
   - 验证缓存有效性（基于 README.md 和 CLAUDE.md 修改时间）
   - 如果缓存有效，加载缓存的画像并跳到 Step 1

2. **调用 plugin-profiler SubAgent**
   ```
   result = dispatch_subagent(
     agent="plugin-profiler",
     args={
       "target": target_dir,
       "output": "both"  # JSON + Markdown
     }
   )

   profile = result.profile  # JSON 对象
   doc_score = result.quality_metrics.documentation_completeness.score
   ```

3. **验证画像完整性**
   - 检查必需字段: `meta.name`, `meta.positioning`, `architecture.component_types`, `usage.slash_commands`, `requirements.system`
   - 如果缺失必需字段，记录警告但继续流程

4. **输出画像文件**
   - 保存 JSON: `$profile_output/plugin-profile.json`
   - 保存 Markdown: `$profile_output/plugin-profile.md`
   - 记录到审查上下文: `review_context["plugin_profile"] = profile`
   - 记录文档完整性评分: `review_context["doc_completeness_score"] = doc_score`

5. **提前终止选项**
   - 如果 `--profile-only=true`，输出画像路径和评分后退出
   - 否则继续到 Step 1

**输出**:
- `plugin-profile.json`: 结构化画像数据
- `plugin-profile.md`: 可读性画像报告
- `review_context["plugin_profile"]`: 供后续 Step 使用

**错误处理**:
- 画像生成失败时记录警告，继续执行常规审查流程
- 缓存检查失败时，重新生成画像

---

**Step 0.5: 交互模式选择（可选，v3.2.0）**
- **条件**: 如果 `--interactive=true` 参数设置
- **目标**: 让用户通过多选菜单选择要执行的检查项
- **操作**:
  1. 使用 AskUserQuestion 工具显示多选菜单
  2. 用户选择要执行的检查项（可多选）
  3. 根据用户选择设置执行标志
  4. 继续执行选中的检查项

**选项清单**:
```yaml
questions:
  - question: "请选择要执行的质量检查项（可多选）："
    header: "检查项选择"
    multiSelect: true
    options:
      - label: "引用完整性扫描"
        description: "检测断开引用、孤儿文件、循环依赖（推荐）"
      - label: "8 维度质量评估"
        description: "意图匹配、配置、依赖、安全、环境、LLM、扩展性、可测试性"
      - label: "架构分析 (L1+L2)"
        description: "工作流结构、组件关系、职责分析"
      - label: "依赖分析"
        description: "依赖关系图、循环依赖检测"
      - label: "链路验证"
        description: "调用链验证、参数匹配检查"
```

**执行标志设置**:
```python
# 根据用户选择设置标志
enable_reference_check = "引用完整性扫描" in user_selections
enable_8_dimensions = "8 维度质量评估" in user_selections
enable_architecture = "架构分析 (L1+L2)" in user_selections
enable_dependency = "依赖分析" in user_selections
enable_linkage = "链路验证" in user_selections

# 如果用户未选择任何项，默认执行所有检查
if not user_selections:
    enable_all = True
```

**输出**: 执行标志配置
**错误处理**: 用户取消选择时提示确认或使用默认配置

---

**Step 1: 扫描目标**
- 扫描目标目录或加载指定工件
- 识别所有可审查组件（Skill、Command、Agent、Hook）
- 统计组件数量和类型分布
- **错误处理**: 目标不存在时提示检查路径；无可审查组件时报告并退出

**Step 2: 加载反模式规则**
- 从规则库加载 161 条反模式规则（完整覆盖）
- **基础 8 维度**（39 条）：intent、config、dependency、security、environment、llm、scalability、testability
- **组件专用规则**（69 条）：skill、subagent、hook、workflow
- **通用和特定规则**（23 条）：common、description、legacy、library、plugin、mcp 等
- **架构和链路规则**（30 条）：通过专门 SubAgent 加载
  - architecture/ (21 rules) - 通过 architecture-analyzer 加载
  - linkage/ (9 rules) - 通过 linkage-validator 加载
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

**Step 3.5: 执行引用完整性扫描（新增 v3.2.0）**
- **条件**: 如果 `enable_reference_check=true` 或 `--reference-only=true`（默认启用，除非 `--no-reference-check=true`）
- 调用 reference-integrity-scanner SubAgent 扫描插件引用关系
- 检测断开引用、孤儿文件、循环依赖
- 生成引用完整性报告
- 将扫描结果合并到最终审查报告
- **错误处理**: 扫描失败时记录警告并继续；检测到 P0 问题时在报告中高亮标注

**执行流程**:
```
IF --no-reference-check 参数未设置 THEN
  CALL reference-integrity-scanner
    args: plugin_dir

  IF 扫描成功 THEN
    MERGE 扫描结果到 review_context
    IF 发现断开引用或循环依赖 THEN
      标记为 P0 问题
    END IF
  ELSE
    记录警告：引用扫描失败
  END IF
END IF
```

**输出**:
- reference_integrity_report.json
- reference_integrity_report.md
- review_context["reference_issues"] 更新

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
- **新增（v3.1.0）**: 如果 Step 0 生成了插件画像，在报告开头自动添加"插件概述"章节
- 输出控制台摘要
- 保存报告到 docs/reviews/
- **错误处理**: 报告生成失败时输出到控制台；目录不存在时自动创建

**Step 7: 验证报告自解释性（可选）**
- 调用 self-explanation-validator SubAgent 验证报告质量
- 检查 4 个维度：完整性（40%）、自包含性（30%）、结构清晰度（20%）、信息准确性（10%）
- 评分范围：0-100
- 如果评分 < 80，输出改进建议
- **错误处理**: 验证失败不影响主流程，仅记录警告

**验证执行逻辑**:

```python
# Step 6 完成后
report_md = read_file(report_path)

# 调用 validator（如果画像存在）
if review_context.get("plugin_profile"):
    validation = dispatch_subagent(
        agent="self-explanation-validator",
        args={
            "report": report_path,
            "profile": review_context["plugin_profile"]
        }
    )

    if validation.score < 80:
        print(f"⚠️ 报告自解释性评分较低: {validation.score}/100")
        print("改进建议:")
        for rec in validation.recommendations:
            print(f"  - {rec}")
    else:
        print(f"✓ 报告自解释性评分: {validation.score}/100 (优秀)")

# 在报告末尾附加验证评分
report_md += f"\n\n---\n\n**报告自解释性评分**: {validation.score}/100\n"
write_file(report_path, report_md)
```

### 预期输出
- **主要制品**: `docs/reviews/YYYY-MM-DD-<project>-comprehensive-review.md`
- **审查报告结构**:
  - **插件概述（如有画像）**: 基本信息、核心功能、架构设计、使用方式、核心设计理念、系统要求、文档完整性评估（v3.1.0 新增）
  - 执行摘要（综合评分、问题统计、评级）
  - 评估维度评分（8 个维度详细得分和问题）
  - 架构分析结果（工作流图、组件关系、循环依赖）
  - 问题清单（按优先级和文件分组）
  - 改进建议（修复优先级、行动计划）
  - 历史对比（如有历史审查记录）
  - **报告自解释性评分（如有画像）**: 0-100 评分和改进建议（v3.1.0 新增）
- **控制台输出**: 综合评分、关键问题摘要、报告路径、报告自解释性评分
- **可选输出**:
  - Eval 结果（benchmark.json、benchmark.md）
  - 插件画像（docs/profile/plugin-profile.json, plugin-profile.md）

### 错误处理
- **目标不存在** → 提示检查路径或使用 `/cmd-status` 查看可用工件
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
- **ccc:reference-integrity-scanner**: 引用完整性扫描器，检测断开引用、孤儿文件和循环依赖（v3.2.0新增）
- **ccc:review-aggregator**: 审查结果聚合器，汇总多维度审查结果
- **ccc:report-renderer**: 报告渲染器，生成最终的审查报告

### 辅助 Agents
- **ccc:workflow-discoverer**: 工作流发现器，识别工作流模式和阶段
- **ccc:eval-executor**: Eval 执行器，运行测试用例和基准测试
- **ccc:eval-grader**: Eval 评分器，对测试结果打分
- **ccc:eval-parser**: Eval 解析器，解析 evals.json 测试定义

### 调度策略

**串行模式（默认）**:
- cmd-review → ccc:reviewer-core → ccc:review-aggregator → ccc:report-renderer
- 组件逐个审查，每个组件完成后再审查下一个
- 适用场景：小型项目（<10 组件）、资源受限环境

**并行模式（`--parallel=true`）**:

**层级 1: 维度内并行**
- 8 维度检查并行：意图匹配、配置、依赖、安全、环境、LLM、扩展性、可测试性
- 每个维度独立执行，互不阻塞

**层级 2: 组件间并行**
- review-core 并行审查多个组件（根据 `--max-workers` 配置）
- 示例：4 workers 同时审查 4 个组件
- 批次处理：每批处理 `--batch-size` 个组件（默认 10）

**层级 3: 分析并行**
- architecture-analyzer + dependency-analyzer + linkage-validator 并行执行
- Eval 执行并行（可选）：eval-executor + eval-grader + eval-parser

**并行执行流程**:

```
用户: /cmd-review --parallel --max-workers=4
  ↓
Step 1: 扫描组件（发现 50 个组件）
  ↓
Step 2: 分批处理（批次大小=10）
  ↓
Batch 1 (组件 1-10):
  ├─ Worker 1: 审查组件 1-3
  ├─ Worker 2: 审查组件 4-6
  ├─ Worker 3: 审查组件 7-9
  └─ Worker 4: 审查组件 10
  ↓
Batch 2 (组件 11-20):
  ├─ Worker 1: 审查组件 11-13
  ├─ Worker 2: 审查组件 14-16
  ├─ Worker 3: 审查组件 17-19
  └─ Worker 4: 审查组件 20
  ↓
... (依次处理所有批次)
  ↓
Step 3: 并行架构分析
  ├─ architecture-analyzer
  ├─ dependency-analyzer
  └─ linkage-validator
  ↓
Step 4: 聚合和报告
  ↓
输出最终报告
```

**性能对比**:

| 组件数 | 串行模式 | 并行 (4 workers) | 并行 (8 workers) | 加速比 |
|--------|---------|-----------------|-----------------|--------|
| 10 | 15分钟 | 4分钟 | 3分钟 | 3.75x |
| 50 | 75分钟 | 20分钟 | 12分钟 | 6.25x |
| 100 | 150分钟 | 40分钟 | 22分钟 | 6.8x |

**错误处理**:
- 单个维度失败不影响其他维度，继续执行并在报告中标记
- 单个组件失败不阻塞其他组件，记录错误并继续
- 某个 worker 超时时自动重试或跳过该组件
- 并行模式失败时自动降级到串行模式

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
用户: /cmd-review --target=/path/to/project
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

**默认行为**（不带参数运行时）:
- 执行最全面的审查（所有检查项）
- 包含：引用完整性扫描 + 8 维度评估 + 架构分析 + 依赖分析 + 链路验证
- 生成完整审查报告

**交互模式**（`--interactive` 参数）:
- 显示多选菜单
- 用户选择要执行的检查项
- 仅执行选中的检查项

**快捷模式**（特定参数）:
- `--reference-only`: 仅执行引用扫描
- `--arch-only`: 仅执行架构分析
- `--no-arch`: 跳过架构分析
- `--no-reference-check`: 跳过引用扫描

### 模式 1: 审查整个项目目录（推荐）

```bash
# 审查指定目录
/cmd-review --target=/Users/xqh/clawd/opensource/glaf4/GTMC-GLAF4-CC-SKILL

# 审查当前工作目录
/cmd-review --target=.

# 审查上级目录
/cmd-review --target=..
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
/cmd-review --artifact-id=DLV-001                    # 完整审查
/cmd-review --artifact-id=BLP-003 --type=migration   # 迁移计划审查
/cmd-review --artifact-id=DLV-001 --no-arch          # 跳过架构分析
```

### 模式 3: 交互式审查

```bash
/cmd-review
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
- /cmd-review --target=/path - 审查指定目录
- /cmd-review --no-arch - 跳过架构分析和链路验证
- /cmd-review --artifact-id=xxx - 审查 CCC 工件
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
/cmd-review --target=/Users/xqh/clawd/opensource/glaf4/GTMC-GLAF4-CC-SKILL
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
/cmd-review --target=. --no-arch
```

**适用场景**: 只需要检查基础合规性，不需要架构分析。

### 示例 3: 仅架构分析

```bash
/cmd-review --target=. --arch-only
```

**适用场景**: 只需要检查架构问题，不需要检查文档合规性。

### 示例 4: 引用完整性检查（v3.2.0 新增）

```bash
# 完整审查（包含引用扫描）
/cmd-review --target=.

# 仅执行引用扫描
/cmd-review --target=. --reference-only

# 跳过引用扫描
/cmd-review --target=. --no-reference-check
```

**适用场景**:
- **完整审查**: 全面审查，包含引用完整性扫描
- **仅引用扫描**: 快速检测断开引用、孤儿文件、循环依赖
- **跳过引用扫描**: 仅执行其他维度检查，节省时间

**输出**:
- reference_integrity_report.json
- reference_integrity_report.md
- 合并到综合审查报告

### 示例 5: 交互模式（v3.2.0 新增）

```bash
# 启用交互模式，手动选择检查项
/cmd-review --target=. --interactive

# 示例输出：
# ┌─────────────────────────────────────────────────────┐
# │ 请选择要执行的质量检查项（可多选）:                   │
# ├─────────────────────────────────────────────────────┤
# │ □ 引用完整性扫描                                      │
# │   检测断开引用、孤儿文件、循环依赖（推荐）             │
# │                                                       │
# │ ☑ 8 维度质量评估                                      │
# │   意图匹配、配置、依赖、安全、环境、LLM、扩展性、可测试性 │
# │                                                       │
# │ ☑ 架构分析 (L1+L2)                                    │
# │   工作流结构、组件关系、职责分析                       │
# │                                                       │
# │ □ 依赖分析                                            │
# │   依赖关系图、循环依赖检测                             │
# │                                                       │
# │ □ 链路验证                                            │
# │   调用链验证、参数匹配检查                             │
# └─────────────────────────────────────────────────────┘

# 根据选择执行对应的检查项
```

**使用场景**:
- **快速检查**: 只选择 "引用完整性扫描" + "8 维度质量评估"
- **深度审查**: 选择所有检查项
- **针对性检查**: 根据已知问题选择特定检查项

### 模式 4: 执行 Eval 机制

```bash
/cmd-review --target=skills/xxx --with-eval
```

**输出**:
- 审查报告
- benchmark.json
- benchmark.md

**适用场景**: 需要对比 with-skill 和 baseline 的性能差异。
