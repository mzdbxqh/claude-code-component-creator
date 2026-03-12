# 审查流程工作流图错误的根因分析

## 问题描述

2026-03-12的审查报告中，核心工作流ASCII图显示：
```
review → (fix / iterate / design-iterate) → validate
```

但正确的流程应该是：
```
主工作流: review → fix → validate
迭代流程: design-iterate → implement → review (回主线)
```

## 根因分析

### 1. Skills的工作流声明是正确的 ✅

所有核心skills都在第13行明确声明了工作流：
- `cmd-design-iterate`: `**完整流程**: 现有代码 → **design-iterate** → implement → review → fix`
- `cmd-implement`: `**完整流程**: design-iterate → **implement** → review → fix`

### 2. 存在两条独立的工作流线

**主工作流**（6步）:
```
init → design → review → fix → validate → build
```

**代码迭代流程**（4步）:
```
现有代码 → design-iterate → implement → review → fix
```

这两条线在`review`节点交汇。

### 3. 问题根源：流程图生成逻辑混淆了两条线

#### 根因1: workflow-discoverer没有结构化的工作流提取逻辑

**现状**:
- workflow-discoverer主要通过Task调用、Skill引用来构建调用图
- **没有**明确的逻辑来解析`**完整流程**:`这种格式化声明
- 依赖LLM自由理解文档内容

**证据**:
```yaml
# agents/reviewer/workflow-discoverer/SKILL.md Line 59
calls = extractTaskCalls(file)      // Task 调用
calls += extractSkillReferences(file) // Skill 引用
calls += extractFileReferences(file)  // @path 引用
```
→ **没有** `extractWorkflowDeclaration(file)` 这样的结构化提取

#### 根因2: architecture-analyzer的流程图生成依赖LLM理解

**现状**:
- Step 2"工作流架构分析"评估"流程清晰度：步骤顺序合理、无跳跃"
- **没有**明确的算法来解析和可视化工作流步骤
- 完全依赖LLM阅读所有skills后综合理解

**证据**:
```yaml
# agents/reviewer/architecture-analyzer/SKILL.md Line 39-45
| 评估项 | 检查内容 | 权重 |
| 流程清晰度 | 步骤顺序合理、无跳跃 | 25% |
```
→ **没有**具体的算法描述如何提取步骤顺序

#### 根因3: 缺少标准化的工作流声明提取规范

**现状**:
- 各skills使用`**完整流程**:`或`**适用流程**:`声明工作流
- 但**没有文档**规定这是必须的标准格式
- **没有验证规则**检查这个声明是否存在和正确
- review流程**没有**反模式规则检查工作流声明

**证据**:
- 19个cmd-* skills中，9个没有工作流声明
- 无法保证所有future skills都会添加这个声明

#### 根因4: 主流程vs迭代流程的关系未明确建模

**现状**:
- 主流程和迭代流程是两条独立的线
- 它们在`review`节点交汇
- 但review-aggregator生成流程图时，**错误地把它们画成并列关系**

**错误理解**:
```
review后有3个选项: fix / iterate / design-iterate (并列)
然后统一汇聚到 validate
```

**正确理解**:
```
主线: review → fix → validate
迭代线: design-iterate → implement → review (回主线)
```

## 杜绝方案

### 方案1: 标准化工作流声明格式 + 结构化提取

**实施步骤**:

1. **定义标准格式** (在std-workflow-attribution中):
```markdown
## 工作流定位

**主工作流**: `step1` → `step2` → **current** → `step3`
或
**迭代流程**: `step1` → **current** → `step2` (回主线@review)
或
**独立工具**: 无固定流程，按需触发
```

2. **创建工作流提取函数**:
```python
def extractWorkflowDeclaration(file_path):
    """
    从SKILL.md中提取工作流声明
    
    Returns:
        {
            "type": "main" | "iteration" | "standalone",
            "steps": ["step1", "step2", ...],
            "current_step": "review",
            "merge_point": "review"  # 迭代流程的汇入点
        }
    """
    content = read(file_path)
    
    # 匹配 **主工作流**: `step1` → **current** → `step2`
    if match := re.search(r'\*\*主工作流\*\*:\s*(.+)', content):
        return parseMainWorkflow(match.group(1))
    
    # 匹配 **迭代流程**: ...
    elif match := re.search(r'\*\*迭代流程\*\*:\s*(.+)', content):
        return parseIterationWorkflow(match.group(1))
    
    # 匹配旧格式 **完整流程**: ...
    elif match := re.search(r'\*\*完整流程\*\*:\s*(.+)', content):
        return parseLegacyWorkflow(match.group(1))
    
    return {"type": "standalone", "steps": [], "current_step": None}
```

3. **更新workflow-discoverer**:
```markdown
### Step 2.5: 提取工作流声明 (新增)

**目标**: 结构化提取每个skill的工作流声明

**操作**:
1. 对每个skill调用 extractWorkflowDeclaration()
2. 区分主工作流、迭代流程、独立工具
3. 识别流程交汇点 (merge_point)
4. 验证声明的完整性和一致性

**输出**: 工作流元数据字典

**错误处理**: 缺少声明的skill标记为WARNING
```

4. **创建反模式规则** (WORKFLOW-001):
```yaml
id: WORKFLOW-001
name: missing-workflow-declaration
severity: warning
category: workflow

description:
  zh: |
    cmd-* skill必须声明工作流定位：
    - **主工作流**: 参与主线流程的步骤
    - **迭代流程**: 参与代码迭代的步骤
    - **独立工具**: 不参与固定流程
    
detection:
  method: regex-match
  pattern: '\*\*(主工作流|迭代流程|独立工具|完整流程|适用流程)\*\*:'
  file_pattern: 'skills/cmd-*/SKILL.md'
  
fix:
  suggestion: |
    在SKILL.md第13行添加工作流声明：
    
    ## 工作流定位
    
    **主工作流**: `design` → **review** → `fix` → `validate` → `build`
    或
    **迭代流程**: `design-iterate` → **implement** → `review` (回主线)
```

### 方案2: 改进architecture-analyzer的流程图生成算法

**实施步骤**:

1. **分离主流程和迭代流程的可视化**:
```markdown
### Step 2.1: 构建主工作流图

**操作**:
1. 提取所有type="main"的workflow声明
2. 按steps顺序排列节点
3. 生成线性流程图

### Step 2.2: 构建迭代流程图

**操作**:
1. 提取所有type="iteration"的workflow声明
2. 识别merge_point (通常是review)
3. 生成分支流程图，标注回归点

### Step 2.3: 合并流程图

**操作**:
1. 以主流程为骨架
2. 在merge_point处添加分支节点
3. 用不同符号区分主线和迭代线
```

2. **改进ASCII流程图渲染**:
```
┌─────────────┐
│   init      │ (主工作流起点)
└──────┬──────┘
       ▼
┌─────────────┐
│   design    │
└──────┬──────┘
       ▼
┌─────────────┐
│   review    │◄──────┐
└──────┬──────┘       │
       │              │
       ├──主流程──────▼
       │        ┌──────────┐
       │        │   fix    │
       │        └────┬─────┘
       │             │
       └─────────────▼
              ┌──────────┐
              │ validate │
              └────┬─────┘
                   ▼
              ┌──────────┐
              │  build   │
              └──────────┘

迭代流程 (独立):
┌──────────────┐
│ 现有代码      │
└───────┬──────┘
        ▼
┌───────────────┐
│design-iterate │
└───────┬───────┘
        ▼
┌───────────────┐
│  implement    │
└───────┬───────┘
        │
        └──→ 回到review (进入主流程)
```

### 方案3: 添加工作流一致性验证

**实施步骤**:

1. **创建一致性检查函数**:
```python
def validateWorkflowConsistency(workflows):
    """
    验证工作流声明的一致性
    
    检查项:
    1. 主工作流的step顺序是否一致
    2. 迭代流程的merge_point是否存在于主流程中
    3. 流程声明是否形成有向无环图(DAG)
    """
    # 主流程一致性
    main_workflows = [w for w in workflows if w['type'] == 'main']
    if not checkMainWorkflowConsistency(main_workflows):
        raise WorkflowInconsistencyError("主工作流步骤顺序不一致")
    
    # 迭代流程汇入点验证
    iter_workflows = [w for w in workflows if w['type'] == 'iteration']
    for iw in iter_workflows:
        if iw['merge_point'] not in main_workflow_steps:
            raise WorkflowInconsistencyError(
                f"迭代流程{iw['name']}的汇入点{iw['merge_point']}不在主流程中"
            )
    
    # 检测循环
    if hasCycle(buildWorkflowGraph(workflows)):
        raise WorkflowInconsistencyError("工作流存在循环依赖")
```

2. **集成到review流程**:
```markdown
## cmd-review执行步骤

Step 4.5: 工作流一致性验证 (新增)
- 提取所有工作流声明
- 调用 validateWorkflowConsistency()
- 发现不一致时标记ERROR
- 在报告中列出具体问题
```

### 方案4: 改进报告模板

**实施步骤**:

1. **创建结构化报告模板**:
```markdown
## 1.2 核心工作流

### 主工作流 (6步)

```
init → design → review → fix → validate → build
```

说明: [各步骤说明]

### 代码迭代流程 (独立)

```
现有代码 → design-iterate → implement → review (回主线)
```

说明: 迭代流程在review节点汇入主工作流

### 其他独立工具

- cmd-status: 查看项目状态
- cmd-diff: 对比版本
- ...
```

2. **report-renderer使用模板渲染**:
```python
def renderWorkflowSection(workflows):
    """
    使用模板渲染工作流章节
    
    Args:
        workflows: 结构化的工作流元数据
    """
    main_wf = [w for w in workflows if w['type'] == 'main']
    iter_wf = [w for w in workflows if w['type'] == 'iteration']
    standalone = [w for w in workflows if w['type'] == 'standalone']
    
    return template.render(
        main_workflow=buildMainWorkflowASCII(main_wf),
        iteration_workflows=[buildIterWorkflowASCII(w) for w in iter_wf],
        standalone_tools=standalone
    )
```

## 优先级建议

1. **P0 (立即修复)**: 方案4 - 改进报告模板
   - 最快见效，直接修正输出
   - 工作量: 2小时

2. **P1 (本周完成)**: 方案1 - 标准化工作流声明
   - 治本方案，建立规范
   - 工作量: 4小时

3. **P1 (本周完成)**: 方案3 - 工作流一致性验证
   - 预防类似问题
   - 工作量: 3小时

4. **P2 (下周完成)**: 方案2 - 改进流程图生成算法
   - 提升质量，但依赖方案1
   - 工作量: 6小时

## 总结

**根本原因**: 
- workflow-discoverer和architecture-analyzer**缺少结构化的工作流提取逻辑**
- 完全依赖LLM自由理解，导致在复杂情况下(主流程+迭代流程)产生混淆

**系统性解决方案**:
- 标准化工作流声明格式
- 添加结构化提取函数
- 分离主流程和迭代流程的可视化
- 添加一致性验证规则

**预期效果**:
- 杜绝类似错误
- 提升工作流分析准确性
- 增强可维护性
