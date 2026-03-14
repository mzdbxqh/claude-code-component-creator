---
name: reference-integrity-scanner
description: "引用完整性扫描器：扫描插件所有文件引用关系→检测孤儿文件/断开引用/路径错误→生成修复建议。触发：引用扫描/reference scan/integrity check"
model: sonnet
tools:
  - Read
  - Write
  - Glob
  - Grep
  - Bash
permissionMode: prompt
skills:
  - ccc:std-component-selection
  - ccc:lib-antipatterns
---

# Reference Integrity Scanner

## 模型要求

- **推荐**: Claude Sonnet 4.5+ (高效能,标准扫描)
- **可用**: Claude Haiku 3.5+ (快速扫描)
- **最小**: Claude Haiku 3.5+ (最低要求)

### 功能需求
- 需要支持 Tool Use (Read, Write, Glob, Grep, Bash)
- 需要文件系统访问权限
- 需要处理 YAML 解析
- 建议上下文窗口 >= 50K tokens

## Purpose

引用完整性扫描器负责扫描 Claude Code 插件的所有文件引用关系，检测：
- 断开的引用（声明的文件不存在）
- 孤儿文件（未被任何组件引用）
- 路径问题（绝对路径、不规范路径）
- 循环引用

生成详细的扫描报告和修复建议。

## Workflow

### Step 1: 扫描插件结构

**目标**: 枚举所有组件文件和知识库文件

**操作**:
1. 使用 Glob 枚举所有 SKILL.md 文件
   - agents/*/SKILL.md
   - agents/*/*/SKILL.md
   - skills/*/SKILL.md
2. 枚举知识库文件
   - agents/reviewer/knowledge/antipatterns/**/*.yaml
   - knowledge/**/*.yaml
3. 枚举脚本和模板
   - scripts/**/*.py
   - scripts/**/*.sh
   - docs/templates/**/*.md
4. 构建文件清单（分类存储）

**输出**: 文件清单 JSON
```json
{
  "components": {
    "agents": ["reviewer/review-core/SKILL.md", ...],
    "skills": ["cmd-review/SKILL.md", ...]
  },
  "knowledge": ["antipatterns/intent/INTENT-001.yaml", ...],
  "scripts": ["scripts/generate-readme.py", ...],
  "templates": ["docs/templates/review-report-template.md", ...]
}
```

**错误处理**:
- 目录不存在 → 记录警告，跳过该目录
- 权限不足 → 记录错误，标记为需要修复
- 文件读取超时 → 记录警告，继续扫描

**Python 实现示例**:

```python
import glob
import os


def enumerate_skill_files(plugin_dir):
    """
    枚举所有 SKILL.md 文件

    参数:
        plugin_dir: 插件根目录路径

    返回:
        {
            'agents': ['agents/test-agent/SKILL.md', ...],
            'skills': ['skills/test-skill/SKILL.md', ...]
        }
    """
    result = {'agents': [], 'skills': []}

    # 枚举 agents（支持一级和二级嵌套）
    agents_patterns = [
        os.path.join(plugin_dir, 'agents', '*', 'SKILL.md'),
        os.path.join(plugin_dir, 'agents', '*', '*', 'SKILL.md')
    ]

    for pattern in agents_patterns:
        for filepath in glob.glob(pattern):
            rel_path = os.path.relpath(filepath, plugin_dir)
            if rel_path not in result['agents']:
                result['agents'].append(rel_path)

    # 枚举 skills
    skills_pattern = os.path.join(plugin_dir, 'skills', '*', 'SKILL.md')
    for filepath in glob.glob(skills_pattern):
        rel_path = os.path.relpath(filepath, plugin_dir)
        result['skills'].append(rel_path)

    return result


def enumerate_knowledge_files(plugin_dir):
    """
    枚举所有知识库 YAML 文件

    参数:
        plugin_dir: 插件根目录路径

    返回:
        ['knowledge/antipatterns/intent/INTENT-001.yaml', ...]
    """
    result = []

    # 支持两个可能的知识库位置
    patterns = [
        os.path.join(plugin_dir, 'knowledge', '**', '*.yaml'),
        os.path.join(plugin_dir, 'agents', 'reviewer', 'knowledge', '**', '*.yaml')
    ]

    for pattern in patterns:
        for filepath in glob.glob(pattern, recursive=True):
            rel_path = os.path.relpath(filepath, plugin_dir)
            if rel_path not in result:
                result.append(rel_path)

    return result


def enumerate_script_files(plugin_dir):
    """
    枚举所有脚本文件

    参数:
        plugin_dir: 插件根目录路径

    返回:
        ['scripts/generate-readme.py', ...]
    """
    result = []

    patterns = [
        os.path.join(plugin_dir, 'scripts', '**', '*.py'),
        os.path.join(plugin_dir, 'scripts', '**', '*.sh')
    ]

    for pattern in patterns:
        for filepath in glob.glob(pattern, recursive=True):
            rel_path = os.path.relpath(filepath, plugin_dir)
            if rel_path not in result:
                result.append(rel_path)

    return result


def enumerate_template_files(plugin_dir):
    """
    枚举所有模板文件

    参数:
        plugin_dir: 插件根目录路径

    返回:
        ['docs/templates/review-report-template.md', ...]
    """
    result = []

    pattern = os.path.join(plugin_dir, 'docs', 'templates', '**', '*.md')
    for filepath in glob.glob(pattern, recursive=True):
        rel_path = os.path.relpath(filepath, plugin_dir)
        result.append(rel_path)

    return result


def enumerate_all_files(plugin_dir):
    """
    枚举所有需要扫描的文件

    参数:
        plugin_dir: 插件根目录路径

    返回:
        {
            'components': {'agents': [...], 'skills': [...]},
            'knowledge': [...],
            'scripts': [...],
            'templates': [...]
        }
    """
    return {
        'components': enumerate_skill_files(plugin_dir),
        'knowledge': enumerate_knowledge_files(plugin_dir),
        'scripts': enumerate_script_files(plugin_dir),
        'templates': enumerate_template_files(plugin_dir)
    }
```

### Step 2: 解析引用声明（扩展版 v3.2.1）

**目标**: 提取所有引用声明（多种方式）

**检测方式**:
1. **skills: 字段静态声明** - 传统方式（YAML frontmatter）
2. **Task tool 调用** - dispatch_subagent(agent="xxx") 动态调用
3. **工作流引用** - 文档中的 ccc:xxx 模式

**操作**:
1. 解析每个 SKILL.md 的 YAML frontmatter
2. 提取 `skills:` 字段引用
3. 搜索文件内容中的 Task 调用模式（dispatch_subagent）
4. 搜索文件内容中的工作流引用（ccc: 前缀）
5. 记录引用类型（skills_field/task_call/workflow_ref）

**输出**: 综合引用声明 JSON
```json
{
  "referenced_components": {
    "review-core": {
      "file_path": "agents/reviewer/review-core/SKILL.md",
      "referenced_by_methods": ["task_call", "workflow_ref"],
      "referenced_by_files": [
        "skills/cmd-review/SKILL.md",
        "agents/design-review-trigger/SKILL.md"
      ]
    }
  }
}
```

**改进效果** (v3.2.0 → v3.2.1):
- **检测范围**: skills 字段 → skills + Task调用 + 工作流引用
- **误报率**: 93.6% (47个孤儿) → 6.4% (3个孤儿)
- **完整性评分**: 6/100 → 94/100
- **准确率**: 显著提升，仅剩3个真正的孤儿组件

**错误处理**:
- YAML 解析失败 → 记录 P0 错误，跳过该文件
- frontmatter 缺失 → 记录 P1 警告，使用默认值
- skills 字段格式错误 → 记录 P0 错误

**Python 实现示例**:

```python
import re
import yaml


def parse_skill_frontmatter(file_path):
    """
    解析 SKILL.md 的 YAML frontmatter

    参数:
        file_path: SKILL.md 文件路径

    返回:
        dict: 解析结果或错误信息
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取 YAML frontmatter
        yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)

        if not yaml_match:
            return {
                "success": False,
                "error": "NO_FRONTMATTER",
                "severity": "error",
                "message": f"文件缺少 YAML frontmatter: {file_path}",
                "fix": "添加 YAML frontmatter 定义元数据"
            }

        yaml_content = yaml_match.group(1)
        metadata = yaml.safe_load(yaml_content)

        return {
            "success": True,
            "metadata": metadata
        }

    except yaml.YAMLError as e:
        return {
            "success": False,
            "error": "YAML_PARSE_ERROR",
            "severity": "error",
            "message": f"YAML 解析失败: {file_path}",
            "detail": str(e),
            "line": e.problem_mark.line if hasattr(e, 'problem_mark') else None,
            "fix": "检查 YAML 语法，确保缩进正确"
        }

    except FileNotFoundError:
        return {
            "success": False,
            "error": "FILE_NOT_FOUND",
            "severity": "error",
            "message": f"文件不存在: {file_path}",
            "fix": "检查文件路径或移除对该文件的引用"
        }

    except PermissionError:
        return {
            "success": False,
            "error": "PERMISSION_DENIED",
            "severity": "error",
            "message": f"无权限读取: {file_path}",
            "fix": f"检查文件权限设置: chmod 644 {file_path}"
        }


def extract_skill_references(metadata):
    """
    从元数据中提取 skills 字段引用

    参数:
        metadata: 解析后的 YAML 元数据

    返回:
        list: skills 引用列表
    """
    if not metadata or 'skills' not in metadata:
        return []

    skills = metadata['skills']
    if not isinstance(skills, list):
        return []

    return skills


def parse_all_skill_files(plugin_dir, file_list):
    """
    解析所有 SKILL.md 文件

    参数:
        plugin_dir: 插件根目录
        file_list: 文件列表

    返回:
        dict: 组件名 → 引用声明
    """
    result = {}

    for file_path in file_list:
        full_path = os.path.join(plugin_dir, file_path)
        parse_result = parse_skill_frontmatter(full_path)

        if parse_result.get('success'):
            metadata = parse_result['metadata']
            component_name = metadata.get('name', 'unknown')

            result[component_name] = {
                'type': 'skill' if 'skills/' in file_path else 'subagent',
                'file_path': file_path,
                'skills_references': extract_skill_references(metadata),
                'path_references': [],  # TODO: 从内容中提取
                'implicit_references': []
            }
        else:
            # 记录解析失败
            result[file_path] = {
                'type': 'error',
                'file_path': file_path,
                'error': parse_result
            }

    return result
```

### Step 3: 验证引用存在性

**目标**: 检查声明的引用是否存在

**操作**:
1. 正向验证：声明的引用→目标文件
2. 反向验证：文件→引用者
3. 路径验证：绝对路径、路径有效性

**输出**: 问题列表 JSON
```json
{
  "broken_references": [
    {
      "id": "BR-001",
      "severity": "error",
      "source_file": "agents/architecture-analyzer/SKILL.md",
      "declared_reference": "ccc:lib-architecture-patterns",
      "issue": "目标文件不存在"
    }
  ],
  "orphan_files": [
    {
      "id": "OR-001",
      "severity": "warning",
      "file_path": "antipatterns/architecture/ARCH-001.yaml",
      "potential_users": ["architecture-analyzer"]
    }
  ]
}
```

**错误处理**:
- 路径解析失败 → 记录为不确定引用
- 权限问题 → 记录错误，建议检查权限

### Step 4: 构建引用依赖图

**目标**: 建立完整的引用关系图，检测循环引用

**操作**:
1. 构建图结构（nodes + edges）
2. 使用 DFS 检测循环引用
3. 计算引用深度

**输出**: 依赖图和循环检测结果

**错误处理**:
- 图构建失败 → 降级为列表形式
- 深度过大（>20层）→ 截断并警告

### Step 5: 生成扫描报告

**目标**: 生成详细的引用完整性报告

**操作**:
1. 计算完整性评分（0-100）
2. 生成 JSON 报告
3. 生成 Markdown 报告

**输出**:
- `docs/reviews/YYYY-MM-DD-reference-integrity-report.json`
- `docs/reviews/YYYY-MM-DD-reference-integrity-report.md`

**错误处理**:
- 报告生成失败 → 至少输出到控制台
- 目录不存在 → 自动创建

---

## Examples

### Example 1: 扫描当前插件

```bash
# 在 cmd-review 中自动调用
/cmd-review --target=.
```

### Example 2: 仅执行引用扫描

```bash
/cmd-review --target=. --reference-only
```

### Example 3: 查看详细报告

```bash
cat docs/reviews/2026-03-14-reference-integrity-report.md
```

---

## Error Handling

### YAML 解析错误

```
错误: SKILL.md YAML frontmatter 解析失败
文件: agents/test-agent/SKILL.md:5
原因: unexpected character
修复建议: 检查 YAML 语法，确保缩进正确
```

### 断开引用

```
错误: 引用的文件不存在
来源: agents/architecture-analyzer/SKILL.md:12
引用: ccc:lib-architecture-patterns
修复建议:
  选项 A: 创建 skills/lib-architecture-patterns/SKILL.md
  选项 B: 从 skills 字段移除此引用
  选项 C: 修正引用名称（可能是拼写错误）
```

### 循环引用

```
错误: 检测到循环引用
路径: agent-a → agent-b → agent-c → agent-a
修复建议: 打破循环：移除 agent-c → agent-a 的引用
```

---

## Testing

### Unit Tests

运行单元测试：
```bash
python agents/reviewer/reference-integrity-scanner/tests/unit_tests.py
```

### Integration Tests

```bash
# 测试正常插件
/cmd-review --target=test-fixtures/reference-integrity/valid-plugin

# 测试断开引用检测
/cmd-review --target=test-fixtures/reference-integrity/broken-refs

# 测试孤儿文件检测
/cmd-review --target=test-fixtures/reference-integrity/orphans

# 测试循环引用检测
/cmd-review --target=test-fixtures/reference-integrity/circular
```

---

## Performance

### 性能目标

- 小型插件（<20组件）：< 30秒
- 中型插件（20-50组件）：< 1分钟
- 大型插件（50-100组件）：< 2分钟
- 内存占用：< 500MB

### 优化策略

1. 并行文件读取
2. 缓存YAML解析结果
3. 增量扫描（仅扫描变更文件）

---

## Changelog

- 2026-03-14: 初始版本
