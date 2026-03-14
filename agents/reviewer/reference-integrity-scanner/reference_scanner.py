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


def validate_references(plugin_dir):
    """
    验证所有引用的有效性（扩展版）

    参数:
        plugin_dir: 插件根目录

    返回:
        dict: 验证结果
    """
    # 枚举所有文件
    file_manifest = enumerate_all_files(plugin_dir)
    all_skills = file_manifest['components']['agents'] + file_manifest['components']['skills']

    # 解析所有组件
    parsed_components = parse_all_skill_files(plugin_dir, all_skills)

    broken_references = []
    issue_id = 1

    # 正向验证：检查每个组件的引用
    for component_name, component_data in parsed_components.items():
        if component_data.get('type') == 'error':
            continue

        skills_refs = component_data.get('skills_references', [])

        for ref in skills_refs:
            target_path = resolve_skill_reference(ref, plugin_dir)

            if target_path is None:
                broken_references.append({
                    'id': f"BR-{issue_id:03d}",
                    'severity': 'error',
                    'source_file': component_data['file_path'],
                    'reference_type': 'skills',
                    'declared_reference': ref,
                    'issue': '目标文件不存在',
                    'fix_suggestion': f"选项 A: 创建 {ref}\n选项 B: 从 skills 字段移除此引用\n选项 C: 修正引用名称"
                })
                issue_id += 1

    # 反向验证：检测孤儿文件
    orphan_files = []
    orphan_id = 1

    # 建立引用者映射
    referenced_files = set()

    for component_name, component_data in parsed_components.items():
        if component_data.get('type') == 'error':
            continue

        skills_refs = component_data.get('skills_references', [])

        for ref in skills_refs:
            target_path = resolve_skill_reference(ref, plugin_dir)
            if target_path:
                # 转换为相对路径
                rel_path = os.path.relpath(target_path, plugin_dir)
                referenced_files.add(rel_path)

    # 检查每个文件是否被引用
    for skill_file in all_skills:
        if skill_file not in referenced_files:
            # 跳过顶层入口（通常不被其他组件引用）
            if 'cmd-' in skill_file:
                continue

            orphan_files.append({
                'id': f"OR-{orphan_id:03d}",
                'severity': 'warning',
                'file_path': skill_file,
                'file_type': 'skill' if 'skills/' in skill_file else 'subagent',
                'issue': '文件未被任何组件引用',
                'potential_users': identify_potential_users(skill_file),
                'fix_suggestion': '添加引用或删除此文件'
            })
            orphan_id += 1

    return {
        'broken_references': broken_references,
        'orphan_files': orphan_files,
        'path_issues': []
    }
