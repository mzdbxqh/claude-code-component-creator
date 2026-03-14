# -*- coding: utf-8 -*-
"""
测试 PythonScriptAnalyzer

Author: mzdbxqh
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'agents' / 'reviewer' / 'review-core'))

from analyzers.python_script_analyzer import PythonScriptAnalyzer


class TestPythonScriptAnalyzer(unittest.TestCase):
    """测试 Python 脚本分析器"""

    def setUp(self):
        """初始化测试"""
        self.analyzer = PythonScriptAnalyzer()

    def test_detect_command_injection(self):
        """测试检测命令注入 (PY-SEC-001)"""
        code = '''
import subprocess
subprocess.call(user_input, shell=True)
'''
        results = self.analyzer.analyze(code)
        self.assertTrue(any(r['rule_id'] == 'PY-SEC-001' for r in results))

    def test_detect_sql_injection(self):
        """测试检测 SQL 注入 (PY-SEC-003)"""
        code = '''
cursor.execute("SELECT * FROM users WHERE name = '" + user_input + "'")
'''
        results = self.analyzer.analyze(code)
        self.assertTrue(any(r['rule_id'] == 'PY-SEC-003' for r in results))

    def test_detect_hardcoded_secret(self):
        """测试检测硬编码敏感数据 (PY-SEC-004)"""
        code = '''
API_KEY = "sk-1234567890abcdef"
password = "admin123"
'''
        results = self.analyzer.analyze(code)
        self.assertTrue(any(r['rule_id'] == 'PY-SEC-004' for r in results))

    def test_detect_missing_docstring(self):
        """测试检测缺少文档字符串 (PY-QUAL-001)"""
        code = '''
def process_data(data):
    return data.strip()
'''
        results = self.analyzer.analyze(code)
        self.assertTrue(any(r['rule_id'] == 'PY-QUAL-001' for r in results))

    def test_detect_function_too_long(self):
        """测试检测函数过长 (PY-QUAL-002)"""
        lines = ['def long_function():']
        lines.extend([f'    line{i} = {i}' for i in range(60)])
        code = '\n'.join(lines)

        results = self.analyzer.analyze(code)
        self.assertTrue(any(r['rule_id'] == 'PY-QUAL-002' for r in results))

    def test_detect_too_many_parameters(self):
        """测试检测参数过多 (PY-QUAL-004)"""
        code = '''
def complex_function(a, b, c, d, e, f, g):
    return a + b + c + d + e + f + g
'''
        results = self.analyzer.analyze(code)
        self.assertTrue(any(r['rule_id'] == 'PY-QUAL-004' for r in results))

    def test_detect_bare_except(self):
        """测试检测裸 except (PY-QUAL-006)"""
        code = '''
try:
    risky_operation()
except:
    pass
'''
        results = self.analyzer.analyze(code)
        self.assertTrue(any(r['rule_id'] == 'PY-QUAL-006' for r in results))

    def test_detect_debug_print(self):
        """测试检测调试 print 语句 (PY-QUAL-010)"""
        code = '''
def process():
    print("debug: processing data")
    return result
'''
        results = self.analyzer.analyze(code)
        self.assertTrue(any(r['rule_id'] == 'PY-QUAL-010' for r in results))

    def test_result_structure(self):
        """测试结果结构"""
        code = 'subprocess.call(cmd, shell=True)'
        results = self.analyzer.analyze(code)

        self.assertIsInstance(results, list)
        if results:
            result = results[0]
            self.assertIn('rule_id', result)
            self.assertIn('message', result)
            self.assertIn('line', result)
            self.assertIn('severity', result)

    def test_valid_code_no_issues(self):
        """测试没有问题的代码"""
        code = '''
"""模块文档字符串"""

def safe_function(data: str) -> str:
    """安全的函数"""
    return data.strip()
'''
        results = self.analyzer.analyze(code)
        # 可能有一些质量建议,但不应有错误
        error_results = [r for r in results if r['severity'] == 'ERROR']
        self.assertEqual(len(error_results), 0)


if __name__ == '__main__':
    unittest.main()
