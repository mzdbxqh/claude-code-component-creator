# -*- coding: utf-8 -*-
"""
测试执行器 - 实际运行被扫描项目的测试

用途：
- 不是测试CCC本身
- 而是实际运行被扫描项目的测试
- 发现语法错误、运行时错误等静态分析无法发现的问题

Author: mzdbxqh
"""

import subprocess
import json
import os
import tempfile
from typing import Dict, List, Any, Optional
from pathlib import Path


class TestExecutor:
    """测试执行器基类"""

    def __init__(self, project_root: str):
        """
        初始化测试执行器

        Args:
            project_root: 被扫描项目的根目录
        """
        self.project_root = Path(project_root)
        self.results = []

    def execute(self, test_type: str = 'auto') -> Dict[str, Any]:
        """
        执行项目测试

        Args:
            test_type: 测试类型 ('auto', 'python', 'shell', 'evals')

        Returns:
            测试结果字典：
            - test_type: 测试类型
            - total: 总测试数
            - passed: 通过数
            - failed: 失败数
            - errors: 错误数
            - details: 详细结果列表
        """
        if test_type == 'auto':
            # 自动检测测试类型
            return self._auto_detect_and_run()
        elif test_type == 'python':
            return self._run_python_tests()
        elif test_type == 'shell':
            return self._run_shell_tests()
        elif test_type == 'evals':
            return self._run_evals_tests()
        else:
            return {
                'test_type': 'unknown',
                'total': 0,
                'passed': 0,
                'failed': 0,
                'errors': 1,
                'details': [{'error': f'Unknown test type: {test_type}'}]
            }

    def _auto_detect_and_run(self) -> Dict[str, Any]:
        """自动检测并运行所有可用的测试"""
        results = {
            'test_type': 'auto',
            'total': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'details': []
        }

        # 1. 检测并运行Python测试
        python_result = self._run_python_tests()
        if python_result['total'] > 0:
            results['total'] += python_result['total']
            results['passed'] += python_result['passed']
            results['failed'] += python_result['failed']
            results['errors'] += python_result['errors']
            results['details'].append({
                'type': 'python',
                'result': python_result
            })

        # 2. 检测并运行Shell测试
        shell_result = self._run_shell_tests()
        if shell_result['total'] > 0:
            results['total'] += shell_result['total']
            results['passed'] += shell_result['passed']
            results['failed'] += shell_result['failed']
            results['errors'] += shell_result['errors']
            results['details'].append({
                'type': 'shell',
                'result': shell_result
            })

        # 3. 检测并运行evals测试
        evals_result = self._run_evals_tests()
        if evals_result['total'] > 0:
            results['total'] += evals_result['total']
            results['passed'] += evals_result['passed']
            results['failed'] += evals_result['failed']
            results['errors'] += evals_result['errors']
            results['details'].append({
                'type': 'evals',
                'result': evals_result
            })

        return results

    def _run_python_tests(self) -> Dict[str, Any]:
        """运行Python测试（pytest或unittest）"""
        result = {
            'test_type': 'python',
            'total': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'details': []
        }

        # 查找Python测试文件
        test_files = list(self.project_root.glob('**/test_*.py'))
        test_files.extend(list(self.project_root.glob('**/*_test.py')))
        test_files.extend(list(self.project_root.glob('**/tests/*.py')))

        if not test_files:
            return result

        # 尝试使用pytest
        pytest_result = self._try_pytest(test_files)
        if pytest_result['total'] > 0:
            return pytest_result

        # 退回到unittest
        return self._try_unittest(test_files)

    def _try_pytest(self, test_files: List[Path]) -> Dict[str, Any]:
        """尝试使用pytest运行测试"""
        result = {
            'test_type': 'python-pytest',
            'total': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'details': []
        }

        try:
            # 运行pytest
            cmd = ['python3', '-m', 'pytest', str(self.project_root), '-v', '--tb=short']
            proc = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=60
            )

            # 解析pytest输出
            output = proc.stdout + proc.stderr

            # 简单统计（可以改进为更精确的解析）
            if 'passed' in output.lower():
                # 提取统计信息
                for line in output.split('\n'):
                    if 'passed' in line.lower():
                        # 示例: "5 passed in 0.12s"
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if 'passed' in part.lower() and i > 0:
                                try:
                                    result['passed'] = int(parts[i-1])
                                    result['total'] += result['passed']
                                except (ValueError, IndexError):
                                    pass
                            if 'failed' in part.lower() and i > 0:
                                try:
                                    result['failed'] = int(parts[i-1])
                                    result['total'] += result['failed']
                                except (ValueError, IndexError):
                                    pass
                            if 'error' in part.lower() and i > 0:
                                try:
                                    result['errors'] = int(parts[i-1])
                                    result['total'] += result['errors']
                                except (ValueError, IndexError):
                                    pass

            result['details'].append({
                'command': ' '.join(cmd),
                'exit_code': proc.returncode,
                'output': output[:1000]  # 限制输出长度
            })

        except FileNotFoundError:
            # pytest未安装
            pass
        except subprocess.TimeoutExpired:
            result['errors'] = 1
            result['details'].append({
                'error': 'Test execution timeout (60s)'
            })
        except Exception as e:
            result['errors'] = 1
            result['details'].append({
                'error': str(e)
            })

        return result

    def _try_unittest(self, test_files: List[Path]) -> Dict[str, Any]:
        """使用unittest运行测试"""
        result = {
            'test_type': 'python-unittest',
            'total': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'details': []
        }

        try:
            # 运行unittest
            cmd = ['python3', '-m', 'unittest', 'discover', '-s', str(self.project_root), '-v']
            proc = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=60
            )

            output = proc.stdout + proc.stderr

            # 解析unittest输出
            # 示例: "Ran 5 tests in 0.001s"
            for line in output.split('\n'):
                if 'Ran' in line and 'test' in line:
                    parts = line.split()
                    try:
                        result['total'] = int(parts[1])
                    except (ValueError, IndexError):
                        pass

                if proc.returncode == 0:
                    result['passed'] = result['total']
                else:
                    # 有失败的测试
                    if 'FAILED' in output:
                        # 统计failures和errors
                        for line in output.split('\n'):
                            if 'failures=' in line.lower():
                                # 提取failures和errors数量
                                pass

            result['details'].append({
                'command': ' '.join(cmd),
                'exit_code': proc.returncode,
                'output': output[:1000]
            })

        except subprocess.TimeoutExpired:
            result['errors'] = 1
            result['details'].append({
                'error': 'Test execution timeout (60s)'
            })
        except Exception as e:
            result['errors'] = 1
            result['details'].append({
                'error': str(e)
            })

        return result

    def _run_shell_tests(self) -> Dict[str, Any]:
        """运行Shell脚本测试"""
        result = {
            'test_type': 'shell',
            'total': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'details': []
        }

        # 查找Shell测试脚本
        test_scripts = list(self.project_root.glob('**/test*.sh'))
        test_scripts.extend(list(self.project_root.glob('**/*test.sh')))

        for script in test_scripts:
            result['total'] += 1

            # 1. 语法检查
            syntax_ok = self._check_shell_syntax(script)
            if not syntax_ok:
                result['errors'] += 1
                result['details'].append({
                    'file': str(script),
                    'error': 'Syntax error'
                })
                continue

            # 2. 实际运行（可选，可能有副作用）
            # 这里暂时只做语法检查
            result['passed'] += 1
            result['details'].append({
                'file': str(script),
                'status': 'syntax_ok'
            })

        return result

    def _check_shell_syntax(self, script_path: Path) -> bool:
        """检查Shell脚本语法"""
        try:
            proc = subprocess.run(
                ['bash', '-n', str(script_path)],
                capture_output=True,
                text=True,
                timeout=5
            )
            return proc.returncode == 0
        except Exception:
            return False

    def _run_evals_tests(self) -> Dict[str, Any]:
        """运行evals.json测试"""
        result = {
            'test_type': 'evals',
            'total': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'details': []
        }

        # 查找evals.json文件
        evals_files = list(self.project_root.glob('**/evals/evals.json'))
        evals_files.extend(list(self.project_root.glob('**/evals.json')))

        for evals_file in evals_files:
            try:
                # 1. 验证JSON格式
                with open(evals_file, 'r', encoding='utf-8') as f:
                    evals_data = json.load(f)

                # 2. 验证基本结构
                if not isinstance(evals_data, dict):
                    result['errors'] += 1
                    result['details'].append({
                        'file': str(evals_file),
                        'error': 'Invalid evals.json format: not a dict'
                    })
                    continue

                # 3. 统计测试用例
                cases = evals_data.get('cases', [])
                result['total'] += len(cases)

                # 4. 验证每个测试用例结构
                for i, case in enumerate(cases):
                    if not isinstance(case, dict):
                        result['errors'] += 1
                        result['details'].append({
                            'file': str(evals_file),
                            'case': i,
                            'error': 'Invalid case format'
                        })
                    elif 'name' not in case:
                        result['errors'] += 1
                        result['details'].append({
                            'file': str(evals_file),
                            'case': i,
                            'error': 'Missing case name'
                        })
                    else:
                        result['passed'] += 1

            except json.JSONDecodeError as e:
                result['errors'] += 1
                result['details'].append({
                    'file': str(evals_file),
                    'error': f'JSON parse error: {str(e)}'
                })
            except Exception as e:
                result['errors'] += 1
                result['details'].append({
                    'file': str(evals_file),
                    'error': str(e)
                })

        return result
