# CCC Skill Description差异化设计方案（简化版）

## 核心原则

**不同类型的Skill，Description侧重点不同**：

1. **cmd-* skills（用户手动触发）**：
   - ❌ 不需要触发词（用户直接调用/ccc:xxx）
   - ✅ 侧重工作流位置说明（第几步、输入输出、承接关系）
   
2. **std-* skills（LLM自动匹配）**：
   - ✅ 必须有触发词和场景（LLM判断是否触发）
   - ❌ 不需要工作流信息（LLM不关心）
   
3. **lib-* skills（SubAgent加载）**：
   - ✅ 说明知识库内容结构
   - ❌ 不需要触发词（SubAgent显式加载）

---

## 一、调整Description规范

### 1.1 cmd-* Skills的Description模板

**格式**:
```
主工作流第X步。[核心功能]。承接[上一步]，输出[制品]给[下一步]。
```

**示例**:

```yaml
# cmd-init
description: "主工作流第1步。4问框架分析需求，创建Intent制品。无前置依赖，输出给design。"

# cmd-design  
description: "主工作流第2步。5阶段流程生成Blueprint设计文档。承接init的Intent，输出给review。"

# cmd-review
description: "主工作流第3步。76+反模式检查，生成审查报告。承接design的Blueprint，发现问题输出给fix，无问题输出给validate。"

# cmd-fix
description: "主工作流第4步。根据审查报告修复问题。承接review的问题清单，修复后输出给validate。"

# cmd-validate
description: "主工作流第5步。验证制品YAML、Schema和Token预算。承接fix/review，输出给build。"

# cmd-build
description: "主工作流第6步（终点）。生成生产就绪的交付物。承接validate的合格制品，输出最终Delivery。"

# cmd-design-iterate
description: "代码迭代流程起点。分析现有组件差异，生成增量改进方案。独立流程，输出给implement。"

# cmd-implement
description: "代码迭代流程第2步。执行迭代计划，应用增量变更。承接design-iterate，输出给review（回到主流程）。"
```

**独立工具**（不参与固定流程）:
```yaml
# cmd-status
description: "独立工具。查看项目和制品状态，无前后依赖。"

# cmd-diff
description: "独立工具。对比不同版本的制品，无前后依赖。"
```

### 1.2 std-* Skills的Description模板

**格式**:
```
[知识类型]。[触发场景/动作词]。[应用范围]。
```

**示例**:

```yaml
# std-component-selection
description: "组件选型决策规则。当设计或审阅插件时，判断应使用cmd-/std-/lib-哪种Skill类型。"

# std-naming-rules
description: "命名规范检查标准。当创建或审阅组件时，验证命名是否符合Skill/Subagent规范。"

# std-workflow-attribution
description: "工作流归属标注规范。当审查组件时，检查工作流定位标注是否清晰。"

# std-evidence-chain
description: "证据链规范。当设计或审阅组件时，确保从需求到实现的完整追溯性。"
```

### 1.3 lib-* Skills的Description模板

**格式**:
```
[知识库类型]，[内容数量]定义覆盖[范围]。由Subagent通过skills字段加载。[用途]。
```

**示例**:

```yaml
# lib-antipatterns
description: "反模式知识库，84个定义覆盖8维度。由Subagent通过skills字段加载。用于质量检查。"

# lib-design-patterns
description: "设计模式知识库，CCC 5阶段设计流程模式。由Subagent通过skills字段加载。用于架构设计。"
```

---

## 二、调整反模式规则

### 2.1 创建cmd-* skills专用规则

**文件**: `antipatterns/workflow/WORKFLOW-002-cmd-skill-description-format.yaml`

```yaml
id: WORKFLOW-002
name: cmd-skill-description-missing-workflow-info
severity: warning
component_type: skill
applies_to: cmd-*

title:
  zh: "cmd-* skill的description未说明工作流位置"
  en: "cmd-* skill description missing workflow position"

description:
  zh: |
    cmd-* skill是用户手动触发的，description应该侧重说明：
    - 在工作流中的位置（第几步）
    - 承接哪个步骤的输出
    - 输出给哪个步骤

    **不需要包含**:
    - 触发词（用户直接调用 /ccc:xxx）
    - 同义词（不需要LLM匹配）

    **推荐格式**:
    ```
    [工作流类型]第X步。[核心功能]。承接[上一步]，输出给[下一步]。
    ```

detection:
  method: regex-match
  pattern: '(主工作流|迭代流程|独立工具).*(第\d+步|起点|终点|承接|输出给)'
  file_pattern: 'skills/cmd-*/SKILL.md'
  negative_match: true  # 不匹配则警告

examples:
  bad:
    zh: |
      错误示例:
      ```yaml
      description: "设计组件。触发：设计/创建/制作。生成Blueprint。"
      ```

      问题：
      - 有触发词（无意义，用户直接调用 /cmd-design）
      - 没有工作流位置说明
      - 用户不知道何时应该使用

  good:
    zh: |
      正确示例:
      ```yaml
      description: "主工作流第2步。5阶段流程生成Blueprint设计文档。承接init的Intent，输出给review。"
      ```

      优点：
      - 明确位置（第2步）
      - 说明输入（Intent）和输出（Blueprint）
      - 说明前后关系（承接init，输出给review）

fix:
  suggestion:
    zh: |
      修改description，按照以下模板：

      **主工作流cmd skills**:
      ```
      主工作流第X步。[功能]。承接[前一步]，输出给[下一步]。
      ```

      **迭代流程cmd skills**:
      ```
      [流程名]第X步。[功能]。承接[前一步]，输出给[下一步]。
      ```

      **独立工具cmd skills**:
      ```
      独立工具。[功能]，无前后依赖。
      ```

tags: ["workflow", "cmd-skill", "description", "clarity"]
```

### 2.2 修改std-* skills的强制规则

保留现有的INTENT-001、INTENT-004等规则，但只应用于std-* skills。

在规则中添加：
```yaml
applies_to: std-*
```

### 2.3 创建lib-* skills专用规则

**文件**: `antipatterns/library/LIB-002-description-format.yaml`

```yaml
id: LIB-002
name: lib-skill-description-format
severity: warning
component_type: skill
applies_to: lib-*

title:
  zh: "lib-* skill的description格式不规范"
  en: "lib-* skill description format non-standard"

description:
  zh: |
    lib-* skill的description应该说明：
    - 知识库类型
    - 内容数量/规模
    - 覆盖范围
    - 加载方式（Subagent通过skills字段）

    **推荐格式**:
    ```
    [知识库类型]，[数量]定义覆盖[范围]。由Subagent通过skills字段加载。[用途]。
    ```

detection:
  method: regex-match
  pattern: '(知识库|定义覆盖|由Subagent|通过skills字段加载)'
  file_pattern: 'skills/lib-*/SKILL.md'

examples:
  bad:
    zh: |
      错误:
      ```yaml
      description: "反模式定义。检查代码质量。"
      ```

      问题：
      - 未说明是知识库
      - 未说明规模
      - 未说明加载方式

  good:
    zh: |
      正确:
      ```yaml
      description: "反模式知识库，84个定义覆盖8维度。由Subagent通过skills字段加载。用于质量检查。"
      ```

tags: ["library", "lib-skill", "description", "format"]
```

---

## 三、修改cmd-review的扫描逻辑

### 3.1 类型特定规则加载

在 `skills/cmd-review/SKILL.md` 的Step 3中修改：

```markdown
### Step 3: 执行8维度评估（改进）

**操作**:

```python
def loadAntipatterns(component):
    """
    根据组件类型和命名前缀加载适用的反模式规则
    """
    component_type = component['type']  # skill, command, agent, hook
    component_name = component['name']  # e.g., cmd-design, std-naming-rules

    if component_type == 'skill':
        # Skill组件需要区分cmd/std/lib
        if component_name.startswith('cmd-'):
            return load_cmd_skill_antipatterns()
        elif component_name.startswith('std-'):
            return load_std_skill_antipatterns()
        elif component_name.startswith('lib-'):
            return load_lib_skill_antipatterns()
        else:
            return load_generic_skill_antipatterns()
    else:
        return load_standard_antipatterns(component_type)

def load_cmd_skill_antipatterns():
    """
    cmd-* skills专用规则集
    
    重点:
    - 工作流位置说明检查
    - argument-hint完整性
    - allowed-tools声明
    
    排除:
    - INTENT-001 (触发场景) - cmd不需要
    - INTENT-002 (同义词) - cmd不需要
    - INTENT-003 (排除场景) - cmd不需要
    """
    return [
        'antipatterns/skill/*.yaml',      # 通用Skill规则
        'antipatterns/workflow/WORKFLOW-002.yaml',  # cmd专用工作流规则
        '!antipatterns/intent/INTENT-001.yaml',  # 排除触发场景规则
        '!antipatterns/intent/INTENT-002.yaml',  # 排除同义词规则
        '!antipatterns/intent/INTENT-003.yaml',  # 排除排除场景规则
    ]

def load_std_skill_antipatterns():
    """
    std-* skills专用规则集
    
    重点:
    - 触发场景必须明确 (INTENT-001)
    - 动作词密度检查 (INTENT-004)
    - 同义词覆盖 (INTENT-002)
    
    排除:
    - WORKFLOW-002 (工作流位置) - std不需要
    """
    return [
        'antipatterns/skill/*.yaml',      # 通用Skill规则
        'antipatterns/intent/*.yaml',     # 强制触发场景规则
        '!antipatterns/workflow/WORKFLOW-002.yaml',  # 排除工作流规则
    ]

def load_lib_skill_antipatterns():
    """
    lib-* skills专用规则集
    
    重点:
    - 知识库索引检查 (LIB-001)
    - Description格式检查 (LIB-002)
    - 知识库结构验证
    
    排除:
    - INTENT-* (触发场景) - lib不需要
    - WORKFLOW-* (工作流) - lib不参与
    """
    return [
        'antipatterns/skill/*.yaml',      # 通用Skill规则
        'antipatterns/library/*.yaml',    # lib专用规则
        '!antipatterns/intent/*.yaml',    # 排除触发场景规则
        '!antipatterns/workflow/*.yaml',  # 排除工作流规则
    ]
```
```

---

## 四、修改architecture-analyzer的流程图生成

### 4.1 从cmd-* skills的description提取工作流

在 `agents/reviewer/architecture-analyzer/SKILL.md` 的Step 2中添加：

```markdown
### Step 2.1: 提取工作流结构（改进）

**操作**:

```python
def extractWorkflowFromCmdSkills(skills):
    """
    从cmd-* skills的description中提取工作流结构
    
    解析模式:
    - "主工作流第X步" → 主工作流
    - "代码迭代流程" → 迭代流程
    - "独立工具" → 不参与流程
    
    解析关系:
    - "承接[X]" → 识别前置步骤
    - "输出给[Y]" → 识别后续步骤
    """
    main_workflow = []
    iteration_workflow = []
    standalone = []

    for skill in skills:
        if not skill['name'].startswith('cmd-'):
            continue

        desc = skill['description']

        # 提取工作流类型和位置
        if match := re.search(r'主工作流第(\d+)步', desc):
            step_num = int(match.group(1))
            main_workflow.append({
                'step': step_num,
                'skill': skill['name'],
                'name': extract_function_name(desc),
                'input': extract_input(desc),   # 从"承接X"提取
                'output': extract_output(desc),  # 从"输出给Y"提取
            })

        elif re.search(r'(代码)?迭代流程', desc):
            iteration_workflow.append({
                'skill': skill['name'],
                'name': extract_function_name(desc),
                'input': extract_input(desc),
                'output': extract_output(desc),
            })

        elif re.search(r'独立工具', desc):
            standalone.append({
                'skill': skill['name'],
                'name': extract_function_name(desc),
            })

    # 按步骤号排序主工作流
    main_workflow.sort(key=lambda x: x['step'])

    # 识别迭代流程的汇入点
    for iw in iteration_workflow:
        if 'review' in iw['output'].lower():
            iw['merge_point'] = 'review'

    return {
        'main': main_workflow,
        'iteration': iteration_workflow,
        'standalone': standalone
    }

def extract_input(description):
    """从"承接X"提取输入"""
    if match := re.search(r'承接(\w+)', description):
        return match.group(1)
    return None

def extract_output(description):
    """从"输出给Y"提取输出"""
    if match := re.search(r'输出给(\w+)', description):
        return match.group(1)
    return None
```
```

### 4.2 生成分离的流程图

```python
def renderWorkflowASCII(workflow_data):
    """
    生成分离的主流程和迭代流程图
    """
    main_wf = workflow_data['main']
    iter_wf = workflow_data['iteration']
    standalone = workflow_data['standalone']

    # 渲染主工作流
    main_ascii = f"""
### 主工作流 ({len(main_wf)}步)

```
"""
    for i, step in enumerate(main_wf):
        main_ascii += f"┌{'─' * 30}┐\n"
        main_ascii += f"│ 第{step['step']}步: {step['name']:<20} │\n"
        main_ascii += f"│ ({step['skill']:<28})│\n"
        if step['input']:
            main_ascii += f"│ 输入: {step['input']:<22} │\n"
        if step['output']:
            main_ascii += f"│ 输出: {step['output']:<22} │\n"
        main_ascii += f"└{'─' * 15}┬{'─' * 15}┘\n"
        if i < len(main_wf) - 1:
            main_ascii += "               ↓\n"
    main_ascii += "```\n"

    # 渲染迭代流程
    iter_ascii = f"""
### 代码迭代流程（独立）

```
"""
    for step in iter_wf:
        iter_ascii += f"┌{'─' * 30}┐\n"
        iter_ascii += f"│ {step['name']:<28} │\n"
        iter_ascii += f"│ ({step['skill']:<28})│\n"
        iter_ascii += f"└{'─' * 15}┬{'─' * 15}┘\n"
        iter_ascii += "               ↓\n"
    if iter_wf:
        merge_point = iter_wf[-1].get('merge_point', 'review')
        iter_ascii += f"         回到主流程 ({merge_point})\n"
    iter_ascii += "```\n"

    # 渲染独立工具
    standalone_text = f"""
### 独立工具

以下工具不参与固定工作流，按需触发：

"""
    for tool in standalone:
        standalone_text += f"- **{tool['name']}** (`{tool['skill']}`)\n"

    return main_ascii + iter_ascii + standalone_text
```

---

## 五、实施计划（简化版）

### Phase 1: 调整Description (2小时)

1. 修改所有cmd-* skills的description
   - 添加工作流位置说明
   - 移除触发词
2. 验证std-* skills的description包含触发词
3. 验证lib-* skills的description说明知识库结构

### Phase 2: 创建类型特定规则 (2小时)

1. 创建WORKFLOW-002（cmd-* description检查）
2. 修改INTENT-001等规则，添加applies_to: std-*
3. 创建LIB-001、LIB-002（lib-* 专用规则）

### Phase 3: 修改cmd-review扫描逻辑 (2小时)

1. 实现类型特定的规则加载函数
2. 更新Step 3的规则加载逻辑
3. 测试三种类型skill的扫描结果

### Phase 4: 改进architecture-analyzer (2小时)

1. 实现从description提取工作流的函数
2. 修改流程图生成逻辑
3. 测试流程图准确性

### Phase 5: 更新报告模板 (1小时)

1. 修改report-renderer使用新的流程图
2. 确保主流程和迭代流程分离显示
3. 测试报告生成

**总工作量**: 9小时（比原方案减少3小时）

---

## 六、总结

### 核心改进

1. **Description差异化设计**:
   - cmd-* → 工作流位置和关系
   - std-* → 触发词和场景
   - lib-* → 知识库内容结构

2. **类型特定验证规则**:
   - cmd-* skills不检查触发场景
   - std-* skills强制触发场景
   - lib-* skills强制索引文档

3. **智能工作流提取**:
   - 从cmd-* description中提取工作流
   - 无需额外的配置文件
   - 降低维护成本

### 优势

| 维度 | 原方案（元数据文件） | 新方案（Description差异化） |
|------|---------------------|---------------------------|
| 额外文件 | ❌ 需要workflows.yaml | ✅ 无需额外文件 |
| Description负担 | ⚠️ Description仍受限 | ✅ 按类型优化利用 |
| 维护成本 | ❌ 高（两处同步） | ✅ 低（单一来源） |
| 可扩展性 | ✅ 强 | ✅ 强 |
| 实施难度 | ⚠️ 中等 | ✅ 简单 |

### 验证效果

修改后的description示例：

**cmd-design（改进前）**:
```yaml
description: "5阶段设计流程生成Blueprint。触发：设计/创建方案。从Intent创建详细设计。主工作流第2步。"
```

**cmd-design（改进后）**:
```yaml
description: "主工作流第2步。5阶段流程生成Blueprint设计文档。承接init的Intent，输出给review。"
```

↓ architecture-analyzer能够提取：
- 工作流类型: 主工作流
- 步骤号: 2
- 输入: Intent (来自init)
- 输出: Blueprint (给review)

↓ 生成准确的流程图：
```
第1步: 需求分析 (cmd-init)
  输出: Intent
       ↓
第2步: Blueprint设计 (cmd-design)  ← 自动识别位置
  输入: Intent
  输出: Blueprint
       ↓
第3步: 质量审查 (cmd-review)
  输入: Blueprint
```
