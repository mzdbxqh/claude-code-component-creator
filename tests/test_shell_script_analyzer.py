# -*- coding: utf-8 -*-
"""
测试 ShellScriptAnalyzer

Author: mzdbxqh
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'agents' / 'reviewer' / 'review-core'))

from analyzers.shell_script_analyzer import ShellScriptAnalyzer


class TestShellScriptAnalyzer(unittest.TestCase):
    """测试 Shell 脚本分析器"""

    def setUp(self):
        """初始化测试"""
        self.analyzer = ShellScriptAnalyzer()

    def test_detect_eval_injection(self):
        """测试检测 eval 命令注入 (SH-SEC-001)"""
        code = '''#!/bin/bash
eval "$user_input"
'''
        results = self.analyzer.analyze(code)
        self.assertTrue(any(r['rule_id'] == 'SH-SEC-001' for r in results))

    def test_detect_path_traversal(self):
        """测试检测路径遍历 (SH-SEC-002)"""
        code = '''#!/bin/bash
cd "$user_path"
'''
        results = self.analyzer.analyze(code)
        self.assertTrue(any(r['rule_id'] == 'SH-SEC-002' for r in results))

    def test_detect_unquoted_variable(self):
        """测试检测未引用变量 (SH-SEC-003)"""
        code = '''#!/bin/bash
rm -rf $file_path
'''
        results = self.analyzer.analyze(code)
        self.assertTrue(any(r['rule_id'] == 'SH-SEC-003' for r in results))

    def test_detect_missing_set_e(self):
        """测试检测缺少 set -e (SH-SEC-004)"""
        code = '''#!/bin/bash
echo "hello"
'''
        results = self.analyzer.analyze(code)
        self.assertTrue(any(r['rule_id'] == 'SH-SEC-004' for r in results))

    def test_detect_dangerous_rm(self):
        """测试检测危险的 rm -rf (SH-SEC-007)"""
        code = '''#!/bin/bash
rm -rf /$variable/*
'''
        results = self.analyzer.analyze(code)
        self.assertTrue(any(r['rule_id'] == 'SH-SEC-007' for r in results))

    def test_detect_missing_shebang(self):
        """测试检测缺少 shebang (SH-QUAL-001)"""
        code = '''echo "hello"
echo "world"
'''
        results = self.analyzer.analyze(code)
        self.assertTrue(any(r['rule_id'] == 'SH-QUAL-001' for r in results))

    def test_detect_missing_error_handling(self):
        """测试检测缺少错误处理 (SH-QUAL-002)"""
        code = '''#!/bin/bash
cp source dest
'''
        results = self.analyzer.analyze(code)
        self.assertTrue(any(r['rule_id'] == 'SH-QUAL-002' for r in results))

    def test_detect_script_too_long(self):
        """测试检测脚本过长 (SH-QUAL-003)"""
        lines = ['#!/bin/bash']
        lines.extend([f'echo "line {i}"' for i in range(210)])
        code = '\n'.join(lines)

        results = self.analyzer.analyze(code)
        self.assertTrue(any(r['rule_id'] == 'SH-QUAL-003' for r in results))

    def test_detect_hardcoded_path(self):
        """测试检测硬编码路径 (SH-QUAL-006)"""
        code = '''#!/bin/bash
LOG_FILE="/var/log/myapp.log"
'''
        results = self.analyzer.analyze(code)
        self.assertTrue(any(r['rule_id'] == 'SH-QUAL-006' for r in results))

    def test_result_structure(self):
        """测试结果结构"""
        code = 'eval "$cmd"'
        results = self.analyzer.analyze(code)

        self.assertIsInstance(results, list)
        if results:
            result = results[0]
            self.assertIn('rule_id', result)
            self.assertIn('message', result)
            self.assertIn('line', result)
            self.assertIn('severity', result)

    def test_valid_code_with_set_e(self):
        """测试有 set -e 的代码"""
        code = '''#!/bin/bash
set -e
echo "Safe script"
'''
        results = self.analyzer.analyze(code)
        # 不应有 SH-SEC-004 错误
        self.assertFalse(any(r['rule_id'] == 'SH-SEC-004' for r in results))


if __name__ == '__main__':
    unittest.main()
