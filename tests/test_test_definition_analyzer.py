# -*- coding: utf-8 -*-
"""
测试 TestDefinitionAnalyzer

Author: mzdbxqh
"""

import unittest
import json
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'agents' / 'reviewer' / 'review-core'))

from analyzers.test_definition_analyzer import TestDefinitionAnalyzer


class TestTestDefinitionAnalyzer(unittest.TestCase):
    """测试测试定义分析器"""

    def setUp(self):
        """初始化测试"""
        self.analyzer = TestDefinitionAnalyzer()

    def test_detect_missing_test_cases(self):
        """测试检测缺少测试用例 (TEST-001)"""
        test_def = {
            "name": "Test suite",
            "cases": []
        }
        results = self.analyzer.analyze(json.dumps(test_def))
        self.assertTrue(any(r['rule_id'] == 'TEST-001' for r in results))

    def test_detect_incomplete_assertions(self):
        """测试检测断言不完整 (TEST-002)"""
        test_def = {
            "cases": [{
                "name": "test_example",
                "assertions": []
            }]
        }
        results = self.analyzer.analyze(json.dumps(test_def))
        self.assertTrue(any(r['rule_id'] == 'TEST-002' for r in results))

    def test_detect_missing_negative_tests(self):
        """测试检测缺少负面测试 (TEST-004)"""
        test_def = {
            "cases": [
                {"name": "test_success", "assertions": [{"type": "equals"}]},
                {"name": "test_valid", "assertions": [{"type": "equals"}]}
            ]
        }
        results = self.analyzer.analyze(json.dumps(test_def))
        self.assertTrue(any(r['rule_id'] == 'TEST-004' for r in results))

    def test_detect_unclear_naming(self):
        """测试检测命名不清晰 (TEST-005)"""
        test_def = {
            "cases": [{
                "name": "test1",
                "assertions": [{"type": "equals"}]
            }]
        }
        results = self.analyzer.analyze(json.dumps(test_def))
        self.assertTrue(any(r['rule_id'] == 'TEST-005' for r in results))

    def test_detect_missing_description(self):
        """测试检测缺少描述 (TEST-006)"""
        test_def = {
            "cases": [{
                "name": "test_valid_input",
                "assertions": [{"type": "equals"}]
                # 缺少 description 字段
            }]
        }
        results = self.analyzer.analyze(json.dumps(test_def))
        self.assertTrue(any(r['rule_id'] == 'TEST-006' for r in results))

    def test_detect_single_assertion_type(self):
        """测试检测单一断言类型 (TEST-007)"""
        test_def = {
            "cases": [
                {"name": "test1", "assertions": [{"type": "equals"}]},
                {"name": "test2", "assertions": [{"type": "equals"}]},
                {"name": "test3", "assertions": [{"type": "equals"}]}
            ]
        }
        results = self.analyzer.analyze(json.dumps(test_def))
        self.assertTrue(any(r['rule_id'] == 'TEST-007' for r in results))

    def test_detect_missing_timeout(self):
        """测试检测缺少超时设置 (TEST-008)"""
        test_def = {
            "cases": [{
                "name": "test_async_operation",
                "assertions": [{"type": "equals"}]
                # 缺少 timeout 字段
            }]
        }
        results = self.analyzer.analyze(json.dumps(test_def))
        self.assertTrue(any(r['rule_id'] == 'TEST-008' for r in results))

    def test_detect_json_format_error(self):
        """测试检测 JSON 格式错误 (TEST-010)"""
        invalid_json = '{"cases": [{"name": "test1"'  # 缺少闭合括号
        results = self.analyzer.analyze(invalid_json)
        self.assertTrue(any(r['rule_id'] == 'TEST-010' for r in results))

    def test_result_structure(self):
        """测试结果结构"""
        test_def = {"cases": []}
        results = self.analyzer.analyze(json.dumps(test_def))

        self.assertIsInstance(results, list)
        if results:
            result = results[0]
            self.assertIn('rule_id', result)
            self.assertIn('message', result)
            self.assertIn('line', result)
            self.assertIn('severity', result)

    def test_valid_test_definition(self):
        """测试有效的测试定义"""
        test_def = {
            "cases": [
                {
                    "name": "test_valid_input_success",
                    "description": "测试有效输入成功场景",
                    "timeout": 5000,
                    "assertions": [
                        {"type": "equals", "expected": "success"},
                        {"type": "contains", "expected": "result"}
                    ]
                },
                {
                    "name": "test_invalid_input_failure",
                    "description": "测试无效输入失败场景",
                    "timeout": 3000,
                    "assertions": [
                        {"type": "error", "expected": "ValidationError"}
                    ]
                }
            ]
        }
        results = self.analyzer.analyze(json.dumps(test_def))
        # 应该没有 ERROR 级别的问题
        error_results = [r for r in results if r['severity'] == 'ERROR']
        self.assertEqual(len(error_results), 0)


if __name__ == '__main__':
    unittest.main()
