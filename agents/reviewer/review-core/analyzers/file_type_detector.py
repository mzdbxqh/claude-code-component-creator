# -*- coding: utf-8 -*-
"""
文件类型检测器

根据文件扩展名、shebang 和内容检测文件类型,路由到合适的分析器。

Author: mzdbxqh
"""

import os
from typing import Dict, Optional, List
from pathlib import Path


class FileTypeDetector:
    """文件类型检测器"""

    def __init__(self):
        """初始化检测器"""
        # 扩展名映射
        self.extension_map = {
            '.py': 'python',
            '.sh': 'shell',
            '.bash': 'shell',
            '.zsh': 'shell',
            '.md': 'documentation',
            '.json': 'json',  # 需要进一步判断是否为测试定义
        }

        # 分析器映射
        self.analyzer_map = {
            'python': 'PythonScriptAnalyzer',
            'shell': 'ShellScriptAnalyzer',
            'test-definition': 'TestDefinitionAnalyzer',
            'documentation': 'DocumentationReferenceAnalyzer',
        }

    def detect(self, file_path: str, read_content: bool = False) -> Dict[str, Optional[str]]:
        """
        检测文件类型

        Args:
            file_path: 文件路径
            read_content: 是否读取文件内容进行检测

        Returns:
            检测结果字典:
            - type: 文件类型 (python/shell/test-definition/documentation/skill/agent/unknown)
            - analyzer: 推荐的分析器类名 (如果适用)
            - confidence: 检测置信度 (0.0-1.0)
        """
        path = Path(file_path)
        file_name = path.name
        extension = path.suffix.lower()

        # 特殊文件名检测
        if file_name == 'SKILL.md':
            return {
                'type': 'skill',
                'analyzer': None,  # SKILL.md 有专门的审查流程
                'confidence': 1.0
            }

        if file_name == 'AGENT.md':
            return {
                'type': 'agent',
                'analyzer': None,  # AGENT.md 有专门的审查流程
                'confidence': 1.0
            }

        # 测试定义文件检测
        if self._is_test_definition_file(file_path):
            return {
                'type': 'test-definition',
                'analyzer': self.analyzer_map.get('test-definition'),
                'confidence': 1.0
            }

        # 扩展名检测
        if extension in self.extension_map:
            file_type = self.extension_map[extension]

            # JSON 文件可能是测试定义
            if file_type == 'json':
                file_type = 'unknown'
                analyzer = None
            else:
                analyzer = self.analyzer_map.get(file_type)

            result = {
                'type': file_type,
                'analyzer': analyzer,
                'confidence': 0.9
            }

            # 如果需要,读取内容进行验证
            if read_content and os.path.exists(file_path):
                content_result = self._detect_by_content(file_path)
                if content_result['type'] != 'unknown':
                    result.update(content_result)
                    result['confidence'] = 1.0

            return result

        # 无扩展名文件 - 尝试 shebang 检测
        if read_content and os.path.exists(file_path):
            content_result = self._detect_by_content(file_path)
            if content_result['type'] != 'unknown':
                return content_result

        # 未知类型
        return {
            'type': 'unknown',
            'analyzer': None,
            'confidence': 0.0
        }

    def _is_test_definition_file(self, file_path: str) -> bool:
        """检测是否为测试定义文件"""
        path = Path(file_path)
        file_name = path.name

        # evals.json
        if file_name == 'evals.json':
            return True

        # tests/目录下的 JSON 文件
        if 'test' in file_path.lower() and path.suffix == '.json':
            return True

        return False

    def _detect_by_content(self, file_path: str) -> Dict[str, Optional[str]]:
        """通过文件内容检测类型"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()

                # shebang 检测
                if first_line.startswith('#!'):
                    if 'python' in first_line.lower():
                        return {
                            'type': 'python',
                            'analyzer': self.analyzer_map.get('python'),
                            'confidence': 1.0
                        }
                    elif any(shell in first_line.lower() for shell in ['bash', 'sh', 'zsh', 'ksh']):
                        return {
                            'type': 'shell',
                            'analyzer': self.analyzer_map.get('shell'),
                            'confidence': 1.0
                        }

        except (IOError, UnicodeDecodeError):
            pass

        return {
            'type': 'unknown',
            'analyzer': None,
            'confidence': 0.0
        }

    def batch_detect(self, file_paths: List[str]) -> Dict[str, Dict[str, Optional[str]]]:
        """
        批量检测文件类型

        Args:
            file_paths: 文件路径列表

        Returns:
            字典,键为文件路径,值为检测结果
        """
        results = {}
        for file_path in file_paths:
            results[file_path] = self.detect(file_path)
        return results

    def get_analyzer_for_file(self, file_path: str) -> Optional[str]:
        """
        获取文件对应的分析器类名

        Args:
            file_path: 文件路径

        Returns:
            分析器类名,如果没有合适的分析器则返回 None
        """
        result = self.detect(file_path, read_content=True)
        return result.get('analyzer')

    def is_analyzable(self, file_path: str) -> bool:
        """
        检测文件是否可分析

        Args:
            file_path: 文件路径

        Returns:
            True 如果文件有对应的分析器
        """
        analyzer = self.get_analyzer_for_file(file_path)
        return analyzer is not None
