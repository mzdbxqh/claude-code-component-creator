# -*- coding: utf-8 -*-
"""
集成测试 - 验证完整的分析流程

Author: mzdbxqh
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'agents' / 'reviewer' / 'review-core'))

from analyzers.file_type_detector import FileTypeDetector
from analyzers.python_script_analyzer import PythonScriptAnalyzer
from analyzers.shell_script_analyzer import ShellScriptAnalyzer
from analyzers.test_definition_analyzer import TestDefinitionAnalyzer


class TestIntegration(unittest.TestCase):
    """集成测试"""

    def setUp(self):
        """初始化测试"""
        self.detector = FileTypeDetector()
        self.test_fixtures_dir = project_root / 'test-fixtures' / 'code-review'

    def test_python_analysis_workflow(self):
        """测试 Python 文件完整分析流程"""
        # 1. 文件类型检测
        python_file = str(self.test_fixtures_dir / 'vulnerable_script.py')
        detection_result = self.detector.detect(python_file)

        self.assertEqual(detection_result['type'], 'python')
        self.assertEqual(detection_result['analyzer'], 'PythonScriptAnalyzer')

        # 2. 读取文件内容
        with open(python_file, 'r', encoding='utf-8') as f:
            code = f.read()

        # 3. 执行分析
        analyzer = PythonScriptAnalyzer()
        results = analyzer.analyze(code)

        # 4. 验证检测结果
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0, "应检测到至少一个问题")

        # 验证检测到的规则
        detected_rules = {r['rule_id'] for r in results}

        # 应检测到的关键问题
        expected_rules = {
            'PY-SEC-001',  # 命令注入
            'PY-SEC-003',  # SQL注入
            'PY-SEC-004',  # 硬编码敏感数据
            'PY-SEC-005',  # 不安全反序列化
            'PY-QUAL-001', # 缺少文档字符串
            'PY-QUAL-002', # 函数过长
            'PY-QUAL-004', # 参数过多
            'PY-QUAL-006', # 裸except
            'PY-QUAL-010', # 调试print
        }

        # 验证至少检测到部分预期问题
        detected_expected = detected_rules & expected_rules
        self.assertGreater(len(detected_expected), 5,
                          f"应检测到至少6个预期问题,实际检测到: {detected_expected}")

        # 验证结果结构
        for result in results:
            self.assertIn('rule_id', result)
            self.assertIn('message', result)
            self.assertIn('line', result)
            self.assertIn('severity', result)
            self.assertIn(result['severity'], ['ERROR', 'WARNING', 'INFO'])

    def test_shell_analysis_workflow(self):
        """测试 Shell 脚本完整分析流程"""
        # 1. 文件类型检测
        shell_file = str(self.test_fixtures_dir / 'bad_deploy.sh')
        detection_result = self.detector.detect(shell_file)

        self.assertEqual(detection_result['type'], 'shell')
        self.assertEqual(detection_result['analyzer'], 'ShellScriptAnalyzer')

        # 2. 读取文件内容
        with open(shell_file, 'r', encoding='utf-8') as f:
            code = f.read()

        # 3. 执行分析
        analyzer = ShellScriptAnalyzer()
        results = analyzer.analyze(code)

        # 4. 验证检测结果
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0, "应检测到至少一个问题")

        # 验证检测到的规则
        detected_rules = {r['rule_id'] for r in results}

        # 应检测到的关键问题
        expected_rules = {
            'SH-SEC-001',  # eval注入
            'SH-SEC-002',  # 路径遍历
            'SH-SEC-003',  # 未引用变量
            'SH-SEC-004',  # 缺少set -e
            'SH-SEC-005',  # 不安全临时文件
            'SH-SEC-006',  # sudo使用
            'SH-SEC-007',  # 危险rm -rf
            'SH-QUAL-002', # 缺少错误处理
            'SH-QUAL-006', # 硬编码路径
        }

        # 验证至少检测到部分预期问题
        detected_expected = detected_rules & expected_rules
        self.assertGreater(len(detected_expected), 5,
                          f"应检测到至少6个预期问题,实际检测到: {detected_expected}")

    def test_test_definition_analysis_workflow(self):
        """测试定义文件完整分析流程"""
        # 1. 文件类型检测
        test_file = str(self.test_fixtures_dir / 'poor_tests.json')
        detection_result = self.detector.detect(test_file)

        # 注意: poor_tests.json 不在 tests/ 目录,可能检测为 json 或 unknown
        # 我们直接使用 TestDefinitionAnalyzer

        # 2. 读取文件内容
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 3. 执行分析
        analyzer = TestDefinitionAnalyzer()
        results = analyzer.analyze(content)

        # 4. 验证检测结果
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0, "应检测到至少一个问题")

        # 验证检测到的规则
        detected_rules = {r['rule_id'] for r in results}

        # 应检测到的关键问题
        expected_rules = {
            'TEST-001',  # 缺少测试用例 (只有1个)
            'TEST-002',  # 断言不完整
            'TEST-005',  # 命名不清晰
            'TEST-006',  # 缺少描述
            'TEST-008',  # 缺少超时
        }

        # 验证至少检测到部分预期问题
        detected_expected = detected_rules & expected_rules
        self.assertGreater(len(detected_expected), 2,
                          f"应检测到至少3个预期问题,实际检测到: {detected_expected}")

    def test_batch_analysis(self):
        """测试批量分析多个文件"""
        files = [
            str(self.test_fixtures_dir / 'vulnerable_script.py'),
            str(self.test_fixtures_dir / 'bad_deploy.sh'),
            str(self.test_fixtures_dir / 'poor_tests.json'),
        ]

        # 检测文件类型
        detection_results = self.detector.batch_detect(files)

        # 验证每个文件都被正确识别
        self.assertEqual(len(detection_results), 3)

        # 执行批量分析
        total_issues = 0
        for file_path in files:
            file_type = detection_results[file_path]['type']
            analyzer_name = detection_results[file_path].get('analyzer')

            if analyzer_name:
                # 读取文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 选择合适的分析器
                if analyzer_name == 'PythonScriptAnalyzer':
                    analyzer = PythonScriptAnalyzer()
                elif analyzer_name == 'ShellScriptAnalyzer':
                    analyzer = ShellScriptAnalyzer()
                elif analyzer_name == 'TestDefinitionAnalyzer':
                    analyzer = TestDefinitionAnalyzer()
                else:
                    continue

                results = analyzer.analyze(content)
                total_issues += len(results)

        # 验证总共检测到足够多的问题
        self.assertGreater(total_issues, 15,
                          f"批量分析应检测到超过15个问题,实际: {total_issues}")


if __name__ == '__main__':
    unittest.main()
