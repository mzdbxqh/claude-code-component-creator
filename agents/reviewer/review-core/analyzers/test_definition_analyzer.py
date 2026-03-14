# -*- coding: utf-8 -*-
"""
测试定义分析器

解析 JSON 格式的测试定义,检测测试质量问题。

Author: mzdbxqh
"""

import json
from typing import List, Dict, Any


class TestDefinitionAnalyzer:
    """测试定义分析器"""

    def __init__(self):
        """初始化分析器"""
        self.results = []

    def analyze(self, content: str) -> List[Dict[str, Any]]:
        """
        分析测试定义

        Args:
            content: JSON 格式的测试定义字符串

        Returns:
            检测结果列表,每个结果包含:
            - rule_id: 规则ID
            - message: 问题描述
            - line: 行号
            - severity: 严重程度 (ERROR/WARNING/INFO)
        """
        self.results = []

        # TEST-010: JSON 格式错误
        try:
            test_def = json.loads(content)
        except json.JSONDecodeError as e:
            self.results.append({
                'rule_id': 'TEST-010',
                'message': f'JSON 格式错误: {str(e)}',
                'line': e.lineno if hasattr(e, 'lineno') else 1,
                'severity': 'ERROR'
            })
            return self.results

        # 检查必需字段
        if not isinstance(test_def, dict):
            self.results.append({
                'rule_id': 'TEST-010',
                'message': '测试定义必须是 JSON 对象',
                'line': 1,
                'severity': 'ERROR'
            })
            return self.results

        cases = test_def.get('cases', [])

        # TEST-001: 缺少测试用例
        self._check_missing_test_cases(cases)

        # 检查每个测试用例
        for i, case in enumerate(cases):
            case_line = i + 1  # 估算行号

            # TEST-002: 断言不完整
            self._check_incomplete_assertions(case, case_line)

            # TEST-005: 测试命名不清晰
            self._check_unclear_naming(case, case_line)

            # TEST-006: 缺少测试描述
            self._check_missing_description(case, case_line)

            # TEST-008: 缺少超时设置
            self._check_missing_timeout(case, case_line)

        # TEST-003: 测试覆盖率低
        self._check_low_coverage(cases)

        # TEST-004: 缺少负面测试
        self._check_missing_negative_tests(cases)

        # TEST-007: 单一断言类型
        self._check_single_assertion_type(cases)

        # TEST-009: 缺少前置条件
        self._check_missing_prerequisites(cases)

        return self.results

    def _check_missing_test_cases(self, cases: List[Dict]):
        """检测缺少测试用例 (TEST-001)"""
        if not cases or len(cases) == 0:
            self.results.append({
                'rule_id': 'TEST-001',
                'message': '测试定义缺少测试用例',
                'line': 1,
                'severity': 'ERROR'
            })

    def _check_incomplete_assertions(self, case: Dict, line: int):
        """检测断言不完整 (TEST-002)"""
        assertions = case.get('assertions', [])

        if not assertions or len(assertions) == 0:
            self.results.append({
                'rule_id': 'TEST-002',
                'message': f'测试用例 {case.get("name", "unknown")} 缺少断言',
                'line': line,
                'severity': 'ERROR'
            })
        else:
            # 检查断言是否有必需字段
            for assertion in assertions:
                if 'type' not in assertion:
                    self.results.append({
                        'rule_id': 'TEST-002',
                        'message': f'测试用例 {case.get("name", "unknown")} 的断言缺少 type 字段',
                        'line': line,
                        'severity': 'ERROR'
                    })

    def _check_low_coverage(self, cases: List[Dict]):
        """检测测试覆盖率低 (TEST-003)"""
        if len(cases) < 3:
            self.results.append({
                'rule_id': 'TEST-003',
                'message': f'测试用例数量不足 ({len(cases)} 个, 建议 ≥3 个)',
                'line': 1,
                'severity': 'WARNING'
            })

    def _check_missing_negative_tests(self, cases: List[Dict]):
        """检测缺少负面测试 (TEST-004)"""
        # 检查是否有失败/错误/异常相关的测试
        negative_keywords = ['fail', 'error', 'invalid', 'exception', 'negative', 'bad']

        has_negative_test = any(
            any(keyword in case.get('name', '').lower() for keyword in negative_keywords)
            for case in cases
        )

        if not has_negative_test and len(cases) > 0:
            self.results.append({
                'rule_id': 'TEST-004',
                'message': '缺少负面测试用例 (错误/异常/边界场景)',
                'line': 1,
                'severity': 'WARNING'
            })

    def _check_unclear_naming(self, case: Dict, line: int):
        """检测测试命名不清晰 (TEST-005)"""
        name = case.get('name', '')

        # 检查名称长度
        if len(name) < 10:
            self.results.append({
                'rule_id': 'TEST-005',
                'message': f'测试用例名称过短: {name} (建议使用描述性名称)',
                'line': line,
                'severity': 'WARNING'
            })

        # 检查是否只是数字或单个单词
        if name.isdigit() or ('_' not in name and len(name.split()) == 1):
            self.results.append({
                'rule_id': 'TEST-005',
                'message': f'测试用例名称不清晰: {name}',
                'line': line,
                'severity': 'WARNING'
            })

    def _check_missing_description(self, case: Dict, line: int):
        """检测缺少测试描述 (TEST-006)"""
        if 'description' not in case or not case['description']:
            self.results.append({
                'rule_id': 'TEST-006',
                'message': f'测试用例 {case.get("name", "unknown")} 缺少描述',
                'line': line,
                'severity': 'INFO'
            })

    def _check_single_assertion_type(self, cases: List[Dict]):
        """检测单一断言类型 (TEST-007)"""
        # 收集所有断言类型
        assertion_types = set()

        for case in cases:
            assertions = case.get('assertions', [])
            for assertion in assertions:
                assertion_type = assertion.get('type')
                if assertion_type:
                    assertion_types.add(assertion_type)

        # 如果只有一种断言类型
        if len(assertion_types) == 1 and len(cases) > 2:
            self.results.append({
                'rule_id': 'TEST-007',
                'message': f'测试仅使用单一断言类型: {list(assertion_types)[0]} (建议多样化)',
                'line': 1,
                'severity': 'INFO'
            })

    def _check_missing_timeout(self, case: Dict, line: int):
        """检测缺少超时设置 (TEST-008)"""
        if 'timeout' not in case:
            self.results.append({
                'rule_id': 'TEST-008',
                'message': f'测试用例 {case.get("name", "unknown")} 缺少超时设置',
                'line': line,
                'severity': 'WARNING'
            })

    def _check_missing_prerequisites(self, cases: List[Dict]):
        """检测缺少前置条件 (TEST-009)"""
        # 检查是否有 setup/teardown/prerequisites
        has_setup = any(
            'setup' in case or 'prerequisites' in case or 'preconditions' in case
            for case in cases
        )

        if not has_setup and len(cases) > 3:
            self.results.append({
                'rule_id': 'TEST-009',
                'message': '测试定义缺少前置条件或清理步骤',
                'line': 1,
                'severity': 'INFO'
            })
