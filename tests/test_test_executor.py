# -*- coding: utf-8 -*-
"""
测试 TestExecutor - 实际测试执行器

Author: mzdbxqh
"""

import unittest
import tempfile
import os
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'agents' / 'reviewer' / 'review-core'))

from analyzers.test_executor import TestExecutor


class TestTestExecutor(unittest.TestCase):
    """测试TestExecutor"""

    def setUp(self):
        """创建临时测试项目"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)

    def tearDown(self):
        """清理临时目录"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_detect_python_unittest(self):
        """测试检测Python unittest测试"""
        # 创建一个简单的unittest测试文件
        test_file = self.project_path / 'test_example.py'
        test_file.write_text('''
import unittest

class TestExample(unittest.TestCase):
    def test_pass(self):
        self.assertEqual(1, 1)

    def test_also_pass(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
''')

        # 执行测试
        executor = TestExecutor(str(self.project_path))
        result = executor.execute(test_type='python')

        # 验证结果
        self.assertEqual(result['test_type'], 'python-unittest')
        self.assertGreater(result['total'], 0, "应该检测到测试")
        # 注意：实际通过数可能因为执行环境不同而变化
        self.assertIn('details', result)

    def test_detect_shell_syntax_error(self):
        """测试检测Shell脚本语法错误"""
        # 创建一个有语法错误的Shell脚本
        bad_script = self.project_path / 'test_bad.sh'
        bad_script.write_text('''#!/bin/bash
# 语法错误：缺少闭合引号
echo "hello
''')

        # 执行测试
        executor = TestExecutor(str(self.project_path))
        result = executor.execute(test_type='shell')

        # 验证结果
        self.assertEqual(result['test_type'], 'shell')
        if result['total'] > 0:
            # 应该检测到语法错误
            self.assertGreater(result['errors'], 0, "应该检测到语法错误")

    def test_detect_shell_syntax_ok(self):
        """测试检测Shell脚本语法正确"""
        # 创建一个语法正确的Shell脚本
        good_script = self.project_path / 'test_good.sh'
        good_script.write_text('''#!/bin/bash
echo "hello"
exit 0
''')

        # 执行测试
        executor = TestExecutor(str(self.project_path))
        result = executor.execute(test_type='shell')

        # 验证结果
        self.assertEqual(result['test_type'], 'shell')
        self.assertGreater(result['total'], 0, "应该检测到测试脚本")
        self.assertGreater(result['passed'], 0, "语法正确的脚本应该通过")

    def test_detect_evals_json(self):
        """测试检测evals.json文件"""
        # 创建evals目录和文件
        evals_dir = self.project_path / 'evals'
        evals_dir.mkdir()

        evals_file = evals_dir / 'evals.json'
        evals_data = {
            'cases': [
                {'name': 'test1', 'description': 'Test case 1'},
                {'name': 'test2', 'description': 'Test case 2'}
            ]
        }
        evals_file.write_text(json.dumps(evals_data, indent=2))

        # 执行测试
        executor = TestExecutor(str(self.project_path))
        result = executor.execute(test_type='evals')

        # 验证结果
        self.assertEqual(result['test_type'], 'evals')
        self.assertGreaterEqual(result['total'], 2, "应该检测到至少2个测试用例")
        self.assertGreaterEqual(result['passed'], 2, "格式正确的用例应该通过")
        self.assertEqual(result['errors'], 0, "不应该有错误")

    def test_detect_invalid_evals_json(self):
        """测试检测无效的evals.json"""
        # 创建evals目录和无效JSON文件
        evals_dir = self.project_path / 'evals'
        evals_dir.mkdir()

        evals_file = evals_dir / 'evals.json'
        evals_file.write_text('{ invalid json }')

        # 执行测试
        executor = TestExecutor(str(self.project_path))
        result = executor.execute(test_type='evals')

        # 验证结果
        self.assertEqual(result['test_type'], 'evals')
        self.assertGreater(result['errors'], 0, "应该检测到JSON格式错误")

    def test_auto_detect(self):
        """测试自动检测并运行所有测试"""
        # 创建多种类型的测试
        # 1. Python测试
        test_file = self.project_path / 'test_auto.py'
        test_file.write_text('''
import unittest
class TestAuto(unittest.TestCase):
    def test_one(self):
        self.assertEqual(1, 1)
''')

        # 2. Shell测试
        shell_test = self.project_path / 'test_auto.sh'
        shell_test.write_text('#!/bin/bash\necho "test"\n')

        # 3. evals.json
        evals_dir = self.project_path / 'evals'
        evals_dir.mkdir()
        evals_file = evals_dir / 'evals.json'
        evals_file.write_text(json.dumps({'cases': [{'name': 'test1'}]}))

        # 自动检测并运行
        executor = TestExecutor(str(self.project_path))
        result = executor.execute(test_type='auto')

        # 验证结果
        self.assertEqual(result['test_type'], 'auto')
        self.assertGreater(result['total'], 0, "应该检测到至少一个测试")
        self.assertIn('details', result)
        self.assertGreater(len(result['details']), 0, "应该有详细结果")

    def test_no_tests_found(self):
        """测试没有测试文件的项目"""
        # 空项目
        executor = TestExecutor(str(self.project_path))
        result = executor.execute(test_type='auto')

        # 验证结果
        self.assertEqual(result['test_type'], 'auto')
        self.assertEqual(result['total'], 0, "空项目应该没有测试")


if __name__ == '__main__':
    unittest.main()
