"""
引用完整性扫描器辅助函数

注意：这些函数也可以直接在 SKILL.md 的工作流中使用

作者: mzdbxqh
创建时间: 2026-03-14
"""

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
