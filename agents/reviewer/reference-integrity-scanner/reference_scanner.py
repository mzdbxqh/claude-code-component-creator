"""
引用完整性扫描器辅助函数

注意：这些函数也可以直接在 SKILL.md 的工作流中使用

作者: mzdbxqh
创建时间: 2026-03-14
"""

import glob
import os
import re
import yaml
import json
from datetime import datetime


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


def resolve_skill_reference(reference, plugin_dir):
    """
    解析 skill 引用到文件路径

    参数:
        reference: 引用字符串（如 "ccc:lib-antipatterns"）
        plugin_dir: 插件根目录

    返回:
        str: 文件路径，或 None 如果不存在
    """
    # 解析引用格式：ccc:skill-name 或 plugin:skill-name
    if ':' in reference:
        parts = reference.split(':', 1)
        skill_name = parts[1]
    else:
        skill_name = reference

    # 构建可能的路径
    possible_paths = [
        os.path.join(plugin_dir, 'skills', skill_name, 'SKILL.md'),
        os.path.join(plugin_dir, 'agents', skill_name, 'SKILL.md'),
        # 嵌套路径
        os.path.join(plugin_dir, 'agents', '*', skill_name, 'SKILL.md'),
    ]

    for path_pattern in possible_paths:
        if '*' in path_pattern:
            matches = glob.glob(path_pattern)
            if matches:
                return matches[0]
        elif os.path.exists(path_pattern):
            return path_pattern

    return None


def identify_potential_users(orphan_file):
    """
    识别孤儿文件的潜在使用者

    参数:
        orphan_file: 孤儿文件路径

    返回:
        list: 潜在使用者列表
    """
    # 简单启发式规则
    potential = []

    # 根据文件名推断
    if 'architecture' in orphan_file:
        potential.append('architecture-analyzer')
    elif 'linkage' in orphan_file:
        potential.append('linkage-validator')
    elif 'antipatterns' in orphan_file:
        potential.append('review-core')

    return potential


def detect_task_tool_calls(plugin_dir):
    """
    检测 Task tool 调用

    搜索模式:
    - dispatch_subagent(agent="component-name")
    - Task.*subagent.*"component-name"
    - 调用 ccc:component-name

    参数:
        plugin_dir: 插件根目录

    返回:
        dict: 组件名 → 引用信息
    """
    task_calls = {}

    # 枚举所有 markdown 文件
    for root, dirs, files in os.walk(plugin_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, plugin_dir)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 搜索模式1: dispatch_subagent(agent="component-name")
                    pattern1 = r'dispatch_subagent\s*\(\s*agent\s*=\s*["\'](\w+[-\w]*)["\']'
                    for match in re.finditer(pattern1, content):
                        component = match.group(1)
                        if component not in task_calls:
                            task_calls[component] = {
                                'component': component,
                                'reference_type': 'task_call',
                                'referenced_by': []
                            }
                        task_calls[component]['referenced_by'].append({
                            'file': rel_path,
                            'pattern': 'dispatch_subagent'
                        })

                    # 搜索模式2: ccc:component-name (调用、使用等)
                    pattern2 = r'ccc:(\w+[-\w]*)'
                    for match in re.finditer(pattern2, content):
                        component = match.group(1)
                        if component not in task_calls:
                            task_calls[component] = {
                                'component': component,
                                'reference_type': 'workflow_ref',
                                'referenced_by': []
                            }
                        task_calls[component]['referenced_by'].append({
                            'file': rel_path,
                            'pattern': 'ccc: prefix'
                        })

                except Exception as e:
                    # 忽略读取错误
                    pass

    return task_calls


def detect_workflow_references(plugin_dir):
    """
    检测工作流引用

    搜索工作流文档中提到的组件（ccc:component-name 模式）

    参数:
        plugin_dir: 插件根目录

    返回:
        list: 工作流引用列表
    """
    workflow_refs = []

    for root, dirs, files in os.walk(plugin_dir):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, plugin_dir)

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 搜索 ccc: 引用
                    pattern = r'ccc:(\w+[-\w]*)'
                    for match in re.finditer(pattern, content):
                        component = match.group(1)
                        workflow_refs.append({
                            'component': component,
                            'referenced_in': rel_path,
                            'reference_type': 'workflow'
                        })
                except Exception:
                    pass

    return workflow_refs


def comprehensive_reference_scan(plugin_dir):
    """
    综合引用扫描

    整合多种检测方式:
    1. skills: 字段静态声明
    2. Task tool 调用
    3. 工作流引用

    参数:
        plugin_dir: 插件根目录

    返回:
        dict: 综合扫描结果
    """
    # 1. 传统 skills 字段检测
    file_manifest = enumerate_all_files(plugin_dir)
    all_skills = file_manifest['components']['agents'] + file_manifest['components']['skills']

    # 2. Task 调用检测
    task_calls = detect_task_tool_calls(plugin_dir)

    # 3. 工作流引用检测
    workflow_refs = detect_workflow_references(plugin_dir)

    # 构建引用关系映射
    referenced_components = {}

    # 枚举所有组件并初始化
    for skill_file in all_skills:
        full_path = os.path.join(plugin_dir, skill_file)
        parse_result = parse_skill_frontmatter(full_path)

        if parse_result.get('success'):
            metadata = parse_result['metadata']
            component_name = metadata.get('name', 'unknown')

            if component_name not in referenced_components:
                referenced_components[component_name] = {
                    'file_path': skill_file,
                    'referenced_by_methods': [],
                    'referenced_by_files': []
                }

    # 标记 skills 字段引用
    for skill_file in all_skills:
        full_path = os.path.join(plugin_dir, skill_file)
        parse_result = parse_skill_frontmatter(full_path)

        if parse_result.get('success'):
            metadata = parse_result['metadata']
            skills_refs = extract_skill_references(metadata)

            for ref in skills_refs:
                # 提取组件名
                target_name = ref.split(':')[-1] if ':' in ref else ref

                if target_name in referenced_components:
                    if 'skills_field' not in referenced_components[target_name]['referenced_by_methods']:
                        referenced_components[target_name]['referenced_by_methods'].append('skills_field')
                    referenced_components[target_name]['referenced_by_files'].append(skill_file)

    # 添加 Task 调用引用
    for component_name, call_info in task_calls.items():
        if component_name in referenced_components:
            if 'task_call' not in referenced_components[component_name]['referenced_by_methods']:
                referenced_components[component_name]['referenced_by_methods'].append('task_call')
            for ref_by in call_info['referenced_by']:
                if ref_by['file'] not in referenced_components[component_name]['referenced_by_files']:
                    referenced_components[component_name]['referenced_by_files'].append(ref_by['file'])

    # 添加工作流引用
    for ref in workflow_refs:
        component_name = ref['component']
        if component_name in referenced_components:
            if 'workflow_ref' not in referenced_components[component_name]['referenced_by_methods']:
                referenced_components[component_name]['referenced_by_methods'].append('workflow_ref')
            if ref['referenced_in'] not in referenced_components[component_name]['referenced_by_files']:
                referenced_components[component_name]['referenced_by_files'].append(ref['referenced_in'])

    # 识别孤儿组件（未被任何方式引用）
    orphan_files = []
    orphan_id = 1

    for component_name, component_info in referenced_components.items():
        # 跳过顶层入口（cmd-* 命令）
        if component_info['file_path'].startswith('skills/cmd-'):
            continue

        # 检查是否被引用
        if len(component_info['referenced_by_methods']) == 0:
            orphan_files.append({
                'id': f"OR-{orphan_id:03d}",
                'severity': 'warning',
                'file_path': component_info['file_path'],
                'file_type': 'skill' if 'skills/' in component_info['file_path'] else 'subagent',
                'issue': '文件未被任何组件引用',
                'potential_users': identify_potential_users(component_info['file_path']),
                'fix_suggestion': '添加引用或删除此文件'
            })
            orphan_id += 1

    # 检测断开引用
    broken_references = []
    issue_id = 1

    for skill_file in all_skills:
        full_path = os.path.join(plugin_dir, skill_file)
        parse_result = parse_skill_frontmatter(full_path)

        if parse_result.get('success'):
            metadata = parse_result['metadata']
            skills_refs = extract_skill_references(metadata)

            for ref in skills_refs:
                target_path = resolve_skill_reference(ref, plugin_dir)

                if target_path is None:
                    broken_references.append({
                        'id': f"BR-{issue_id:03d}",
                        'severity': 'error',
                        'source_file': skill_file,
                        'reference_type': 'skills',
                        'declared_reference': ref,
                        'issue': '目标文件不存在',
                        'fix_suggestion': f"选项 A: 创建 {ref}\n选项 B: 从 skills 字段移除此引用\n选项 C: 修正引用名称"
                    })
                    issue_id += 1

    return {
        'referenced_components': referenced_components,
        'orphan_files': orphan_files,
        'broken_references': broken_references,
        'path_issues': []
    }


def validate_references(plugin_dir):
    """
    验证所有引用的有效性（使用综合扫描）

    参数:
        plugin_dir: 插件根目录

    返回:
        dict: 验证结果
    """
    # 使用综合扫描
    comp_results = comprehensive_reference_scan(plugin_dir)

    # 循环引用检测
    graph = build_dependency_graph(plugin_dir)
    cycles = detect_cycles(graph)

    return {
        'broken_references': comp_results['broken_references'],
        'orphan_files': comp_results['orphan_files'],
        'path_issues': comp_results.get('path_issues', []),
        'referenced_components': comp_results.get('referenced_components', {}),
        'cycles': cycles,
        'graph': graph
    }


def build_dependency_graph(plugin_dir):
    """
    构建引用依赖图

    参数:
        plugin_dir: 插件根目录

    返回:
        dict: {'nodes': [...], 'edges': [...]}
    """
    file_manifest = enumerate_all_files(plugin_dir)
    all_skills = file_manifest['components']['agents'] + file_manifest['components']['skills']
    parsed_components = parse_all_skill_files(plugin_dir, all_skills)

    graph = {
        'nodes': [],
        'edges': []
    }

    # 添加节点
    for component_name, component_data in parsed_components.items():
        if component_data.get('type') == 'error':
            continue

        graph['nodes'].append({
            'id': component_name,
            'type': component_data.get('type'),
            'file': component_data.get('file_path')
        })

    # 添加边（引用关系）
    for component_name, component_data in parsed_components.items():
        if component_data.get('type') == 'error':
            continue

        skills_refs = component_data.get('skills_references', [])

        for ref in skills_refs:
            # 提取目标组件名
            target_name = ref.split(':')[-1] if ':' in ref else ref

            graph['edges'].append({
                'from': component_name,
                'to': target_name,
                'type': 'skills_reference'
            })

    return graph


def detect_cycles(graph):
    """
    检测引用图中的循环依赖

    参数:
        graph: 依赖图 {'nodes': [...], 'edges': [...]}

    返回:
        list: 检测到的循环列表
    """
    # 构建邻接表
    adj = {}
    for node in graph['nodes']:
        adj[node['id']] = []

    for edge in graph['edges']:
        from_node = edge['from']
        to_node = edge['to']
        if from_node in adj and to_node in adj:
            adj[from_node].append(to_node)

    # DFS 检测循环
    visited = set()
    stack = []
    cycles = []

    def dfs(node, path):
        if len(path) > 20:
            # 深度过大
            return [{
                'code': 'EXCESSIVE_DEPTH',
                'severity': 'warning',
                'message': f"引用深度过大: {len(path)} 层",
                'cycle_path': path
            }]

        if node in stack:
            # 检测到循环
            cycle_start = stack.index(node)
            cycle = stack[cycle_start:] + [node]
            return [{
                'code': 'CIRCULAR_REFERENCE',
                'severity': 'error',
                'message': "检测到循环引用",
                'cycle_path': cycle,
                'cycle_length': len(cycle) - 1,
                'affected_components': cycle[:-1],
                'fix_suggestion': f"打破循环：移除 {cycle[-2]} → {cycle[-1]} 的引用"
            }]

        if node in visited:
            return []

        visited.add(node)
        stack.append(node)

        node_cycles = []
        for child in adj.get(node, []):
            node_cycles.extend(dfs(child, path + [node]))

        stack.pop()
        return node_cycles

    for node in adj.keys():
        if node not in visited:
            cycles.extend(dfs(node, []))

    return cycles


def calculate_integrity_score(issues):
    """
    计算完整性评分（0-100）

    扣分规则（优化后 v3.2.1）:
    - 断开引用: -10 分/个（高优先级问题）
    - 真正的孤儿文件: -2 分/个（通过综合检测后仍未引用）
    - 路径问题: -1 分/个
    - 循环引用: -20 分/个（严重问题）

    改进说明:
    v3.2.0: 仅检测 skills 字段，误报率高
    v3.2.1: 综合检测（skills + task_call + workflow_ref），误报率低
    """
    score = 100
    score -= len(issues.get('broken_references', [])) * 10
    score -= len(issues.get('orphan_files', [])) * 2
    score -= len(issues.get('path_issues', [])) * 1
    score -= len(issues.get('cycles', [])) * 20

    return max(0, score)


def generate_json_report(scan_results, plugin_path, output_path):
    """
    生成 JSON 报告

    Args:
        scan_results: 扫描结果
        plugin_path: 插件路径
        output_path: 输出文件路径
    """
    # 统计
    broken_refs = scan_results.get('broken_references', [])
    orphan_files = scan_results.get('orphan_files', [])
    path_issues = scan_results.get('path_issues', [])
    cycles = scan_results.get('cycles', [])

    total_issues = len(broken_refs) + len(orphan_files) + len(path_issues) + len(cycles)
    integrity_score = calculate_integrity_score(scan_results)

    # 构建报告
    report = {
        'version': '1.0.0',
        'scan_date': datetime.now().isoformat(),
        'plugin_path': plugin_path,
        'plugin_name': os.path.basename(plugin_path),

        'summary': {
            'total_issues': total_issues,
            'broken_references': len(broken_refs),
            'orphan_files': len(orphan_files),
            'path_issues': len(path_issues),
            'circular_references': len(cycles),
            'integrity_score': integrity_score
        },

        'issues': {
            'broken_references': broken_refs,
            'orphan_files': orphan_files,
            'path_issues': path_issues,
            'circular_references': cycles
        },

        'reference_graph': scan_results.get('graph', {}),

        'scan_metadata': {
            'scanner_version': '1.0.0',
            'scan_options': {}
        }
    }

    # 写入文件
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)


def generate_markdown_report(scan_results, plugin_path, output_path):
    """
    生成 Markdown 报告

    Args:
        scan_results: 扫描结果
        plugin_path: 插件路径
        output_path: 输出文件路径
    """
    broken_refs = scan_results.get('broken_references', [])
    orphan_files = scan_results.get('orphan_files', [])
    path_issues = scan_results.get('path_issues', [])
    cycles = scan_results.get('cycles', [])

    integrity_score = calculate_integrity_score(scan_results)
    score_grade = 'A' if integrity_score >= 90 else 'B' if integrity_score >= 80 else 'C'

    # 构建 Markdown 内容
    lines = [
        '# 引用完整性扫描报告',
        '',
        f'**扫描日期**: {datetime.now().strftime("%Y-%m-%d")}',
        f'**插件路径**: {plugin_path}',
        f'**完整性评分**: {integrity_score}/100 ({score_grade})',
        '',
        '---',
        '',
        '## 执行摘要',
        '',
        '### 问题统计',
        '',
        '| 严重性 | 数量 | 说明 |',
        '|--------|------|------|',
        f'| **Error** | {len(broken_refs) + len(cycles)} | 必须修复 |',
        f'| **Warning** | {len(orphan_files)} | 建议修复 |',
        f'| **Info** | {len(path_issues)} | 可选优化 |',
        '',
        '---',
        ''
    ]

    # 断开引用章节
    if broken_refs:
        lines.extend([
            '## 🔴 断开的引用 ({} 个)'.format(len(broken_refs)),
            '',
        ])

        for ref in broken_refs:
            source_file = ref.get('source_file', 'unknown')
            source_line = ref.get('source_line', '')
            location = f"{source_file}:{source_line}" if source_line else source_file

            lines.extend([
                f"### {ref['id']}: {ref.get('declared_reference', 'unknown')}",
                '',
                f"**文件**: `{location}`",
                '',
                f"**问题**: {ref.get('issue', '')}",
                '',
                '**修复建议**:',
                ref.get('fix_suggestion', ''),
                '',
                '---',
                ''
            ])

    # 孤儿文件章节
    if orphan_files:
        lines.extend([
            '## ⚠️ 孤儿文件 ({} 个)'.format(len(orphan_files)),
            '',
        ])

        for orphan in orphan_files:
            lines.extend([
                f"### {orphan['id']}: {orphan.get('file_path', 'unknown')}",
                '',
                f"**问题**: {orphan.get('issue', '')}",
                '',
                f"**潜在使用者**: {', '.join(orphan.get('potential_users', []))}",
                '',
                f"**修复建议**: {orphan.get('fix_suggestion', '')}",
                '',
                '---',
                ''
            ])

    # 循环引用章节
    if cycles:
        lines.extend([
            '## 🔴 循环引用 ({} 个)'.format(len(cycles)),
            '',
        ])

        for cycle in cycles:
            cycle_path = cycle.get('cycle_path', [])
            path_str = ' → '.join(cycle_path)

            lines.extend([
                f"### 循环路径: {path_str}",
                '',
                f"**修复建议**: {cycle.get('fix_suggestion', '')}",
                '',
                '---',
                ''
            ])

    # 写入文件
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

