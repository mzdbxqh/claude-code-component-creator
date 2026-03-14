# -*- coding: utf-8 -*-
"""
Shell 脚本分析器

使用正则表达式匹配检测 Shell 脚本的安全和质量问题。

Author: mzdbxqh
"""

import re
from typing import List, Dict, Any


class ShellScriptAnalyzer:
    """Shell 脚本分析器"""

    def __init__(self):
        """初始化分析器"""
        self.results = []

    def analyze(self, code: str) -> List[Dict[str, Any]]:
        """
        分析 Shell 脚本

        Args:
            code: Shell 源代码字符串

        Returns:
            检测结果列表,每个结果包含:
            - rule_id: 规则ID
            - message: 问题描述
            - line: 行号
            - severity: 严重程度 (ERROR/WARNING/INFO)
        """
        self.results = []
        lines = code.split('\n')

        # SH-SEC-001: eval 命令注入
        self._check_eval_injection(lines)

        # SH-SEC-002: 路径遍历
        self._check_path_traversal(lines)

        # SH-SEC-003: 未引用变量
        self._check_unquoted_variables(lines)

        # SH-SEC-004: 缺少 set -e
        self._check_missing_set_e(lines)

        # SH-SEC-005: 不安全的临时文件
        self._check_unsafe_temp_files(lines)

        # SH-SEC-006: sudo 滥用
        self._check_sudo_abuse(lines)

        # SH-SEC-007: 危险的 rm -rf
        self._check_dangerous_rm(lines)

        # SH-SEC-008: source 不可信脚本
        self._check_unsafe_source(lines)

        # SH-QUAL-001: 缺少 shebang
        self._check_missing_shebang(lines)

        # SH-QUAL-002: 缺少错误处理
        self._check_missing_error_handling(lines)

        # SH-QUAL-003: 脚本过长
        self._check_script_too_long(lines)

        # SH-QUAL-004: 未使用的函数
        self._check_unused_functions(lines)

        # SH-QUAL-005: 缺少注释
        self._check_missing_comments(lines)

        # SH-QUAL-006: 硬编码路径
        self._check_hardcoded_paths(lines)

        return self.results

    def _check_eval_injection(self, lines: List[str]):
        """检测 eval 命令注入 (SH-SEC-001)"""
        pattern = r'\beval\s+["\']?\$'
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                self.results.append({
                    'rule_id': 'SH-SEC-001',
                    'message': '检测到 eval 命令注入风险',
                    'line': i,
                    'severity': 'ERROR'
                })

    def _check_path_traversal(self, lines: List[str]):
        """检测路径遍历 (SH-SEC-002)"""
        pattern = r'\bcd\s+["\']?\$'
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                self.results.append({
                    'rule_id': 'SH-SEC-002',
                    'message': '检测到路径遍历风险: cd 使用用户输入',
                    'line': i,
                    'severity': 'WARNING'
                })

    def _check_unquoted_variables(self, lines: List[str]):
        """检测未引用变量 (SH-SEC-003)"""
        # 检测 rm/mv/cp 等命令使用未引用的变量
        pattern = r'\b(rm|mv|cp|chmod|chown)\s+[^"\']*\$\w+'
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                # 排除已引用的情况
                if not re.search(r'"\$\w+"', line):
                    self.results.append({
                        'rule_id': 'SH-SEC-003',
                        'message': '检测到未引用的变量,可能导致命令注入',
                        'line': i,
                        'severity': 'WARNING'
                    })

    def _check_missing_set_e(self, lines: List[str]):
        """检测缺少 set -e (SH-SEC-004)"""
        has_set_e = any(re.search(r'^\s*set\s+-[a-zA-Z]*e', line) for line in lines)
        has_shebang = lines and lines[0].startswith('#!')

        if has_shebang and not has_set_e:
            self.results.append({
                'rule_id': 'SH-SEC-004',
                'message': '脚本缺少 set -e,错误可能被忽略',
                'line': 1,
                'severity': 'WARNING'
            })

    def _check_unsafe_temp_files(self, lines: List[str]):
        """检测不安全的临时文件 (SH-SEC-005)"""
        # 检测使用 /tmp/固定名称
        pattern = r'/tmp/[a-zA-Z0-9_-]+'
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                # 检查是否使用 mktemp
                if 'mktemp' not in line:
                    self.results.append({
                        'rule_id': 'SH-SEC-005',
                        'message': '检测到不安全的临时文件使用,应使用 mktemp',
                        'line': i,
                        'severity': 'WARNING'
                    })

    def _check_sudo_abuse(self, lines: List[str]):
        """检测 sudo 滥用 (SH-SEC-006)"""
        pattern = r'\bsudo\s+'
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                self.results.append({
                    'rule_id': 'SH-SEC-006',
                    'message': '检测到 sudo 使用,确认是否必需',
                    'line': i,
                    'severity': 'INFO'
                })

    def _check_dangerous_rm(self, lines: List[str]):
        """检测危险的 rm -rf (SH-SEC-007)"""
        # 检测 rm -rf 使用变量
        pattern = r'\brm\s+-[a-zA-Z]*r[a-zA-Z]*f?\s+[^"\']*\$'
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                self.results.append({
                    'rule_id': 'SH-SEC-007',
                    'message': '检测到危险的 rm -rf 使用变量',
                    'line': i,
                    'severity': 'ERROR'
                })

    def _check_unsafe_source(self, lines: List[str]):
        """检测 source 不可信脚本 (SH-SEC-008)"""
        pattern = r'\b(source|\.) \$'
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                self.results.append({
                    'rule_id': 'SH-SEC-008',
                    'message': '检测到 source 不可信脚本',
                    'line': i,
                    'severity': 'WARNING'
                })

    def _check_missing_shebang(self, lines: List[str]):
        """检测缺少 shebang (SH-QUAL-001)"""
        if not lines or not lines[0].startswith('#!'):
            # 如果脚本只有1-2行,可能是片段
            if len(lines) > 2:
                self.results.append({
                    'rule_id': 'SH-QUAL-001',
                    'message': '脚本缺少 shebang',
                    'line': 1,
                    'severity': 'WARNING'
                })

    def _check_missing_error_handling(self, lines: List[str]):
        """检测缺少错误处理 (SH-QUAL-002)"""
        has_set_e = any(re.search(r'^\s*set\s+-[a-zA-Z]*e', line) for line in lines)
        has_error_check = any(re.search(r'\|\||&&|\$\?', line) for line in lines)

        if not has_set_e and not has_error_check:
            # 检查是否有可能失败的命令
            risky_commands = ['cp', 'mv', 'rm', 'mkdir', 'curl', 'wget']
            has_risky_command = any(
                any(re.search(rf'\b{cmd}\b', line) for cmd in risky_commands)
                for line in lines
            )

            if has_risky_command:
                self.results.append({
                    'rule_id': 'SH-QUAL-002',
                    'message': '脚本缺少错误处理机制',
                    'line': 1,
                    'severity': 'WARNING'
                })

    def _check_script_too_long(self, lines: List[str]):
        """检测脚本过长 (SH-QUAL-003)"""
        if len(lines) > 200:
            self.results.append({
                'rule_id': 'SH-QUAL-003',
                'message': f'脚本过长 ({len(lines)} 行, 建议 ≤200 行)',
                'line': 1,
                'severity': 'INFO'
            })

    def _check_unused_functions(self, lines: List[str]):
        """检测未使用的函数 (SH-QUAL-004)"""
        # 查找函数定义
        functions = {}
        for i, line in enumerate(lines, 1):
            match = re.search(r'^(\w+)\s*\(\)', line)
            if match:
                func_name = match.group(1)
                functions[func_name] = i

        # 检查函数是否被调用
        code_text = '\n'.join(lines)
        for func_name, line_no in functions.items():
            # 查找函数调用 (排除定义行)
            pattern = rf'\b{func_name}\b'
            matches = list(re.finditer(pattern, code_text))

            # 如果只有一次匹配(定义本身),则未使用
            if len(matches) <= 1:
                self.results.append({
                    'rule_id': 'SH-QUAL-004',
                    'message': f'函数 {func_name} 未被使用',
                    'line': line_no,
                    'severity': 'INFO'
                })

    def _check_missing_comments(self, lines: List[str]):
        """检测缺少注释 (SH-QUAL-005)"""
        if len(lines) < 5:
            return  # 短脚本不要求注释

        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        comment_ratio = comment_lines / len(lines) if lines else 0

        if comment_ratio < 0.1:  # 注释少于10%
            self.results.append({
                'rule_id': 'SH-QUAL-005',
                'message': f'脚本注释不足 ({comment_ratio*100:.1f}%, 建议 ≥10%)',
                'line': 1,
                'severity': 'INFO'
            })

    def _check_hardcoded_paths(self, lines: List[str]):
        """检测硬编码路径 (SH-QUAL-006)"""
        # 检测绝对路径赋值
        pattern = r'^\s*[A-Z_]+\s*=\s*"?/[a-zA-Z/]+'
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                self.results.append({
                    'rule_id': 'SH-QUAL-006',
                    'message': '检测到硬编码路径,建议使用配置文件或环境变量',
                    'line': i,
                    'severity': 'INFO'
                })
