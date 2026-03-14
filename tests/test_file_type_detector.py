# -*- coding: utf-8 -*-
"""
测试 FileTypeDetector

Author: mzdbxqh
"""

import unittest
import tempfile
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'agents' / 'reviewer' / 'review-core'))

from analyzers.file_type_detector import FileTypeDetector


class TestFileTypeDetector(unittest.TestCase):
    """测试文件类型检测器"""

    def setUp(self):
        """初始化测试"""
        self.detector = FileTypeDetector()

    def test_detect_python_file_by_extension(self):
        """测试通过扩展名检测 Python 文件"""
        result = self.detector.detect('test_script.py')
        self.assertEqual(result['type'], 'python')
        self.assertEqual(result['analyzer'], 'PythonScriptAnalyzer')

    def test_detect_shell_file_by_extension(self):
        """测试通过扩展名检测 Shell 脚本"""
        result = self.detector.detect('deploy.sh')
        self.assertEqual(result['type'], 'shell')
        self.assertEqual(result['analyzer'], 'ShellScriptAnalyzer')

    def test_detect_shell_file_by_shebang(self):
        """测试通过 shebang 检测 Shell 脚本"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='', delete=False) as f:
            f.write('#!/bin/bash\necho "hello"\n')
            f.flush()
            temp_file = f.name

        try:
            result = self.detector.detect(temp_file, read_content=True)
            self.assertEqual(result['type'], 'shell')
        finally:
            import os
            os.unlink(temp_file)

    def test_detect_test_definition_by_name(self):
        """测试检测测试定义文件"""
        result = self.detector.detect('evals/evals.json')
        self.assertEqual(result['type'], 'test-definition')
        self.assertEqual(result['analyzer'], 'TestDefinitionAnalyzer')

    def test_detect_markdown_file(self):
        """测试检测 Markdown 文件"""
        result = self.detector.detect('README.md')
        self.assertEqual(result['type'], 'documentation')
        self.assertEqual(result['analyzer'], 'DocumentationReferenceAnalyzer')

    def test_detect_skill_file(self):
        """测试检测 SKILL.md 文件"""
        result = self.detector.detect('skills/example/SKILL.md')
        self.assertEqual(result['type'], 'skill')
        self.assertIsNone(result['analyzer'])  # SKILL.md 使用专门的审查流程

    def test_detect_agent_file(self):
        """测试检测 AGENT.md 文件"""
        result = self.detector.detect('agents/example/AGENT.md')
        self.assertEqual(result['type'], 'agent')
        self.assertIsNone(result['analyzer'])  # AGENT.md 使用专门的审查流程

    def test_detect_unknown_file(self):
        """测试检测未知文件类型"""
        result = self.detector.detect('data.csv')
        self.assertEqual(result['type'], 'unknown')
        self.assertIsNone(result['analyzer'])

    def test_batch_detect(self):
        """测试批量检测"""
        files = [
            'script.py',
            'deploy.sh',
            'tests/evals.json',
            'README.md',
            'data.txt'
        ]

        results = self.detector.batch_detect(files)

        self.assertEqual(len(results), 5)
        self.assertEqual(results['script.py']['type'], 'python')
        self.assertEqual(results['deploy.sh']['type'], 'shell')
        self.assertEqual(results['tests/evals.json']['type'], 'test-definition')
        self.assertEqual(results['README.md']['type'], 'documentation')
        self.assertEqual(results['data.txt']['type'], 'unknown')


if __name__ == '__main__':
    unittest.main()
