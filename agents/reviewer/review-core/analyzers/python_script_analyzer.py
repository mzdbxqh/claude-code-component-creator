# -*- coding: utf-8 -*-
"""
Python 脚本分析器

使用 AST 解析 Python 代码,检测安全和质量问题。

Author: mzdbxqh
"""

import ast
import re
from typing import List, Dict, Any


class PythonScriptAnalyzer:
    """Python 脚本分析器"""

    def __init__(self):
        """初始化分析器"""
        self.results = []

    def analyze(self, code: str) -> List[Dict[str, Any]]:
        """
        分析 Python 代码

        Args:
            code: Python 源代码字符串

        Returns:
            检测结果列表,每个结果包含:
            - rule_id: 规则ID
            - message: 问题描述
            - line: 行号
            - severity: 严重程度 (ERROR/WARNING/INFO)
        """
        self.results = []

        try:
            tree = ast.parse(code)
            self._analyze_tree(tree, code)
        except SyntaxError as e:
            # Python 语法错误
            self.results.append({
                'rule_id': 'PY-SYNTAX-ERROR',
                'message': f'Python 语法错误: {str(e)}',
                'line': e.lineno if hasattr(e, 'lineno') else 1,
                'severity': 'ERROR'
            })

        return self.results

    def _analyze_tree(self, tree: ast.AST, code: str):
        """分析 AST 树"""
        lines = code.split('\n')

        for node in ast.walk(tree):
            # PY-SEC-001: 命令注入检测
            self._check_command_injection(node)

            # PY-SEC-003: SQL 注入检测
            self._check_sql_injection(node, lines)

            # PY-SEC-004: 硬编码敏感数据
            self._check_hardcoded_secrets(node)

            # PY-SEC-005: 不安全的反序列化
            self._check_unsafe_deserialization(node)

            # PY-QUAL-001: 缺少文档字符串
            self._check_missing_docstring(node)

            # PY-QUAL-002: 函数过长
            self._check_function_length(node, lines)

            # PY-QUAL-004: 参数过多
            self._check_too_many_parameters(node)

            # PY-QUAL-006: 裸 except
            self._check_bare_except(node)

            # PY-QUAL-007: 全局变量滥用
            self._check_global_abuse(node)

            # PY-QUAL-010: 调试 print 语句
            self._check_debug_print(node)

    def _check_command_injection(self, node: ast.AST):
        """检测命令注入 (PY-SEC-001)"""
        if isinstance(node, ast.Call):
            # subprocess.call/run/Popen with shell=True
            if isinstance(node.func, ast.Attribute):
                if (hasattr(node.func, 'value') and
                    isinstance(node.func.value, ast.Name) and
                    node.func.value.id == 'subprocess' and
                    node.func.attr in ['call', 'run', 'Popen', 'check_output']):

                    # 检查 shell=True
                    for keyword in node.keywords:
                        if keyword.arg == 'shell' and isinstance(keyword.value, ast.Constant):
                            if keyword.value.value is True:
                                self.results.append({
                                    'rule_id': 'PY-SEC-001',
                                    'message': '检测到命令注入风险: subprocess 使用 shell=True',
                                    'line': node.lineno,
                                    'severity': 'ERROR'
                                })

    def _check_sql_injection(self, node: ast.AST, lines: List[str]):
        """检测 SQL 注入 (PY-SEC-003)"""
        if isinstance(node, ast.Call):
            # cursor.execute() 使用字符串拼接
            if isinstance(node.func, ast.Attribute) and node.func.attr == 'execute':
                if node.args:
                    arg = node.args[0]
                    # 检查字符串拼接
                    if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add):
                        self.results.append({
                            'rule_id': 'PY-SEC-003',
                            'message': '检测到 SQL 注入风险: 使用字符串拼接构造 SQL 语句',
                            'line': node.lineno,
                            'severity': 'ERROR'
                        })

    def _check_hardcoded_secrets(self, node: ast.AST):
        """检测硬编码敏感数据 (PY-SEC-004)"""
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    var_name = target.id.lower()
                    # 检测敏感变量名
                    if any(keyword in var_name for keyword in
                           ['password', 'passwd', 'pwd', 'secret', 'api_key', 'apikey', 'token']):
                        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                            self.results.append({
                                'rule_id': 'PY-SEC-004',
                                'message': f'检测到硬编码敏感数据: {target.id}',
                                'line': node.lineno,
                                'severity': 'ERROR'
                            })

    def _check_unsafe_deserialization(self, node: ast.AST):
        """检测不安全的反序列化 (PY-SEC-005)"""
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                # pickle.loads, yaml.load (without safe_load)
                if (hasattr(node.func, 'value') and
                    isinstance(node.func.value, ast.Name)):
                    module = node.func.value.id
                    func = node.func.attr

                    if module == 'pickle' and func in ['loads', 'load']:
                        self.results.append({
                            'rule_id': 'PY-SEC-005',
                            'message': '检测到不安全的反序列化: pickle.loads/load',
                            'line': node.lineno,
                            'severity': 'ERROR'
                        })
                    elif module == 'yaml' and func == 'load':
                        self.results.append({
                            'rule_id': 'PY-SEC-005',
                            'message': '检测到不安全的反序列化: yaml.load (应使用 safe_load)',
                            'line': node.lineno,
                            'severity': 'ERROR'
                        })

    def _check_missing_docstring(self, node: ast.AST):
        """检测缺少文档字符串 (PY-QUAL-001)"""
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            # 检查是否有 docstring
            has_docstring = (ast.get_docstring(node) is not None)

            if not has_docstring:
                node_type = "函数" if isinstance(node, ast.FunctionDef) else "类"
                self.results.append({
                    'rule_id': 'PY-QUAL-001',
                    'message': f'{node_type} {node.name} 缺少文档字符串',
                    'line': node.lineno,
                    'severity': 'WARNING'
                })

    def _check_function_length(self, node: ast.AST, lines: List[str]):
        """检测函数过长 (PY-QUAL-002)"""
        if isinstance(node, ast.FunctionDef):
            # 计算函数行数
            start_line = node.lineno
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line

            func_length = end_line - start_line + 1

            if func_length > 50:
                self.results.append({
                    'rule_id': 'PY-QUAL-002',
                    'message': f'函数 {node.name} 过长 ({func_length} 行, 建议 ≤50 行)',
                    'line': node.lineno,
                    'severity': 'WARNING'
                })

    def _check_too_many_parameters(self, node: ast.AST):
        """检测参数过多 (PY-QUAL-004)"""
        if isinstance(node, ast.FunctionDef):
            param_count = len(node.args.args)

            if param_count > 5:
                self.results.append({
                    'rule_id': 'PY-QUAL-004',
                    'message': f'函数 {node.name} 参数过多 ({param_count} 个, 建议 ≤5 个)',
                    'line': node.lineno,
                    'severity': 'WARNING'
                })

    def _check_bare_except(self, node: ast.AST):
        """检测裸 except (PY-QUAL-006)"""
        if isinstance(node, ast.ExceptHandler):
            if node.type is None:
                self.results.append({
                    'rule_id': 'PY-QUAL-006',
                    'message': '检测到裸 except,应指定具体异常类型',
                    'line': node.lineno,
                    'severity': 'WARNING'
                })

    def _check_global_abuse(self, node: ast.AST):
        """检测全局变量滥用 (PY-QUAL-007)"""
        if isinstance(node, ast.Global):
            self.results.append({
                'rule_id': 'PY-QUAL-007',
                'message': f'检测到全局变量使用: {", ".join(node.names)}',
                'line': node.lineno,
                'severity': 'INFO'
            })

    def _check_debug_print(self, node: ast.AST):
        """检测调试 print 语句 (PY-QUAL-010)"""
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == 'print':
                self.results.append({
                    'rule_id': 'PY-QUAL-010',
                    'message': '检测到调试 print() 语句',
                    'line': node.lineno,
                    'severity': 'INFO'
                })
