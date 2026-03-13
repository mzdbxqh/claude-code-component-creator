#!/usr/bin/env python3
"""
Command Pattern Detector

检测 Command 文件的模式类型 (Alias vs Workflow)。

用于 LEGACY-001 规则的智能迁移分类。

Author: mzdbxqh
Created: 2026-03-13
"""

import re
from pathlib import Path
from typing import Literal


class CommandPatternDetector:
    """
    Command 模式检测器

    分类 Command 为两种模式:
    - Alias Pattern: 简单的 Skill 快捷方式
    - Workflow Pattern: 包含独立工作流逻辑
    """

    def __init__(self):
        """初始化检测器"""
        pass

    def detect(self, command_file_path: str) -> Literal['alias', 'workflow', 'unknown']:
        """
        检测 Command 文件的模式类型

        Args:
            command_file_path: Command 文件的路径 (commands/xxx.md)

        Returns:
            'alias': Alias Pattern (快捷方式)
            'workflow': Workflow Pattern (工作流)
            'unknown': 无法确定

        检测算法:
        - alias_score >= 3 → 'alias'
        - workflow_score >= 2 → 'workflow'
        - 否则 → 'unknown'
        """
        try:
            content = Path(command_file_path).read_text(encoding='utf-8')
        except FileNotFoundError:
            return 'unknown'
        except Exception as e:
            print(f"Error reading file {command_file_path}: {e}")
            return 'unknown'

        # 计算两种模式的评分
        alias_score = self._calculate_alias_score(content)
        workflow_score = self._calculate_workflow_score(content)

        # 分类决策
        if alias_score >= 3:
            return 'alias'
        elif workflow_score >= 2:
            return 'workflow'
        else:
            return 'unknown'

    def _calculate_alias_score(self, content: str) -> int:
        """
        计算 Alias Pattern 评分

        Alias 指标 (每项 +1 分):
        1. 文件大小 <100 行
        2. 单一 Skill 引用
        3. 无复杂逻辑
        4. Description 简短
        5. 无条件语句

        Args:
            content: Command 文件内容

        Returns:
            Alias 评分 (0-5)
        """
        score = 0
        lines = content.split('\n')
        line_count = len(lines)

        # 指标 1: 文件大小 <100 行
        if line_count < 100:
            score += 1

        # 指标 2: 单一 Skill 引用
        # 检测 "调用 XXX Skill" 或 "invoke XXX" 等模式
        skill_references = re.findall(
            r'(?:调用|invoke|call|使用|use)\s+(\w+[-\w]*)\s+(?:Skill|skill|技能)',
            content,
            re.IGNORECASE
        )
        if len(set(skill_references)) == 1:  # 去重后只有一个
            score += 1

        # 指标 3: 无复杂逻辑
        # 检测是否缺少多行代码块、多步骤、复杂说明
        code_blocks = re.findall(r'```[\s\S]*?```', content)
        has_numbered_steps = bool(re.search(r'^\s*\d+\.\s', content, re.MULTILINE))

        if len(code_blocks) <= 1 and not has_numbered_steps:
            score += 1

        # 指标 4: Description 简短
        # 提取 description 字段
        desc_match = re.search(r'description:\s*(.+)', content)
        if desc_match:
            description = desc_match.group(1).strip()
            # Description 少于 50 字符
            if len(description) < 50:
                score += 1

        # 指标 5: 无条件语句
        # 检测 if/else/switch 等条件关键词
        conditional_patterns = [
            r'\b(?:if|else|elif|switch|case|when)\b',
            r'如果|否则|当|选择'
        ]
        has_conditionals = any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in conditional_patterns
        )
        if not has_conditionals:
            score += 1

        return score

    def _calculate_workflow_score(self, content: str) -> int:
        """
        计算 Workflow Pattern 评分

        Workflow 指标 (每项 +1 分):
        1. 存在编号步骤
        2. 包含条件分支
        3. 多个 SubAgent 调用
        4. 详细工作流说明
        5. 文件大小 >200 行

        Args:
            content: Command 文件内容

        Returns:
            Workflow 评分 (0-5)
        """
        score = 0
        lines = content.split('\n')
        line_count = len(lines)

        # 指标 1: 存在编号步骤
        # 匹配 "1. XXX" 或 "步骤 1:" 等格式
        has_numbered_steps = bool(re.search(r'^\s*\d+\.\s', content, re.MULTILINE))
        step_headers = re.findall(r'(?:步骤|Step|阶段|Phase)\s*\d+', content, re.IGNORECASE)

        if has_numbered_steps or len(step_headers) >= 2:
            score += 1

        # 指标 2: 包含条件分支
        # 检测 if/else/switch 等条件关键词
        conditional_patterns = [
            r'\b(?:if|else|elif|switch|case|when)\b',
            r'如果|否则|当|选择|根据'
        ]
        has_conditionals = any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in conditional_patterns
        )
        if has_conditionals:
            score += 1

        # 指标 3: 多个 SubAgent 调用
        # 检测 Task tool 调用或明确的 SubAgent 引用
        subagent_patterns = [
            r'(?:调用|invoke|call)\s+(\w+[-\w]*?)(?:\s+SubAgent|\s+代理)',
            r'Task\s+tool',
            r'subagent_type:\s*["\']?(\w+[-\w]*)',
        ]
        subagent_refs = []
        for pattern in subagent_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            subagent_refs.extend(matches)

        if len(set(subagent_refs)) >= 2:  # 去重后至少 2 个不同的 SubAgent
            score += 1

        # 指标 4: 详细工作流说明
        # 检测工作流相关章节
        workflow_sections = re.findall(
            r'#+\s+(?:工作流|Workflow|流程|Process|步骤|Steps)',
            content,
            re.IGNORECASE
        )
        # 检测代码块数量 (详细的工作流通常包含多个示例)
        code_blocks = re.findall(r'```[\s\S]*?```', content)

        if len(workflow_sections) >= 1 or len(code_blocks) >= 3:
            score += 1

        # 指标 5: 文件大小 >200 行
        if line_count > 200:
            score += 1

        return score

    def get_detailed_analysis(self, command_file_path: str) -> dict:
        """
        获取详细的分析结果

        Args:
            command_file_path: Command 文件路径

        Returns:
            dict: {
                'pattern': 'alias' | 'workflow' | 'unknown',
                'alias_score': int,
                'workflow_score': int,
                'line_count': int,
                'skill_references': List[str],
                'subagent_count': int,
                'has_conditionals': bool,
                'has_numbered_steps': bool,
            }
        """
        try:
            content = Path(command_file_path).read_text(encoding='utf-8')
        except Exception as e:
            return {
                'pattern': 'unknown',
                'error': str(e)
            }

        alias_score = self._calculate_alias_score(content)
        workflow_score = self._calculate_workflow_score(content)

        # 确定模式
        if alias_score >= 3:
            pattern = 'alias'
        elif workflow_score >= 2:
            pattern = 'workflow'
        else:
            pattern = 'unknown'

        # 提取详细信息
        lines = content.split('\n')

        # Skill 引用
        skill_references = re.findall(
            r'(?:调用|invoke|call|使用|use)\s+(\w+[-\w]*)\s+(?:Skill|skill|技能)',
            content,
            re.IGNORECASE
        )

        # SubAgent 引用
        subagent_patterns = [
            r'(?:调用|invoke|call)\s+(\w+[-\w]*?)(?:\s+SubAgent|\s+代理)',
            r'subagent_type:\s*["\']?(\w+[-\w]*)',
        ]
        subagent_refs = []
        for pattern_str in subagent_patterns:
            matches = re.findall(pattern_str, content, re.IGNORECASE)
            subagent_refs.extend(matches)

        # 条件语句
        conditional_patterns = [
            r'\b(?:if|else|elif|switch|case|when)\b',
            r'如果|否则|当|选择'
        ]
        has_conditionals = any(
            re.search(pattern_str, content, re.IGNORECASE)
            for pattern_str in conditional_patterns
        )

        # 编号步骤
        has_numbered_steps = bool(re.search(r'^\s*\d+\.\s', content, re.MULTILINE))

        return {
            'pattern': pattern,
            'alias_score': alias_score,
            'workflow_score': workflow_score,
            'line_count': len(lines),
            'skill_references': list(set(skill_references)),
            'subagent_count': len(set(subagent_refs)),
            'has_conditionals': has_conditionals,
            'has_numbered_steps': has_numbered_steps,
        }


# 便利函数
def detect_command_pattern(command_file_path: str) -> Literal['alias', 'workflow', 'unknown']:
    """
    便利函数: 检测 Command 模式

    Args:
        command_file_path: Command 文件路径

    Returns:
        'alias' | 'workflow' | 'unknown'
    """
    detector = CommandPatternDetector()
    return detector.detect(command_file_path)


if __name__ == '__main__':
    # 测试代码
    import sys

    if len(sys.argv) < 2:
        print("Usage: python pattern_detector.py <command_file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    detector = CommandPatternDetector()

    # 获取详细分析
    analysis = detector.get_detailed_analysis(file_path)

    print("=" * 60)
    print("Command Pattern Detection Result")
    print("=" * 60)
    print(f"File: {file_path}")
    print(f"Pattern: {analysis['pattern'].upper()}")
    print(f"Line count: {analysis.get('line_count', 'N/A')}")
    print(f"Alias score: {analysis.get('alias_score', 'N/A')}")
    print(f"Workflow score: {analysis.get('workflow_score', 'N/A')}")
    print(f"Skill references: {', '.join(analysis.get('skill_references', [])) or 'None'}")
    print(f"SubAgent count: {analysis.get('subagent_count', 0)}")
    print(f"Has conditionals: {analysis.get('has_conditionals', False)}")
    print(f"Has numbered steps: {analysis.get('has_numbered_steps', False)}")
    print("=" * 60)
