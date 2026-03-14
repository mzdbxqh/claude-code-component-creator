"""
reference-integrity-scanner 单元测试

测试范围：
- 文件枚举
- YAML 解析
- 引用验证
- 依赖图构建
- 报告生成
"""

import unittest
import os
import sys
import tempfile
import json
from pathlib import Path

# 添加父目录到路径以便导入 reference_scanner
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestFileEnumeration(unittest.TestCase):
    """测试文件枚举功能"""

    def test_enumerate_skill_files(self):
        """测试枚举 SKILL.md 文件"""
        # 创建临时测试目录
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建测试文件结构
            os.makedirs(f"{tmpdir}/agents/test-agent")
            os.makedirs(f"{tmpdir}/skills/test-skill")

            # 创建 SKILL.md 文件
            Path(f"{tmpdir}/agents/test-agent/SKILL.md").touch()
            Path(f"{tmpdir}/skills/test-skill/SKILL.md").touch()

            # 执行枚举（需要实现的函数）
            from reference_scanner import enumerate_skill_files
            result = enumerate_skill_files(tmpdir)

            # 验证结果
            self.assertEqual(len(result['agents']), 1)
            self.assertEqual(len(result['skills']), 1)
            self.assertIn('agents/test-agent/SKILL.md', result['agents'])
            self.assertIn('skills/test-skill/SKILL.md', result['skills'])

    def test_enumerate_knowledge_files(self):
        """测试枚举知识库文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建知识库文件
            os.makedirs(f"{tmpdir}/knowledge/antipatterns/intent")
            Path(f"{tmpdir}/knowledge/antipatterns/intent/INTENT-001.yaml").touch()

            from reference_scanner import enumerate_knowledge_files
            result = enumerate_knowledge_files(tmpdir)

            self.assertEqual(len(result), 1)
            self.assertIn('knowledge/antipatterns/intent/INTENT-001.yaml', result)


class TestYAMLParsing(unittest.TestCase):
    """测试 YAML 解析功能"""

    def test_parse_valid_frontmatter(self):
        """测试解析有效的 YAML frontmatter"""
        valid_content = """---
name: test-skill
description: "Test skill"
model: sonnet
tools: [Read, Write]
skills:
  - ccc:lib-antipatterns
  - ccc:std-component-selection
---

# Test Skill

Content here...
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(valid_content)
            f.flush()

            from reference_scanner import parse_skill_frontmatter
            result = parse_skill_frontmatter(f.name)

            # 验证解析成功
            self.assertTrue(result['success'])
            self.assertEqual(result['metadata']['name'], 'test-skill')
            self.assertEqual(len(result['metadata']['skills']), 2)
            self.assertIn('ccc:lib-antipatterns', result['metadata']['skills'])

        os.unlink(f.name)

    def test_parse_invalid_frontmatter(self):
        """测试解析无效的 YAML frontmatter"""
        invalid_content = """---
name: test-skill
description: "Missing closing quote
tools: [Read, Write]
---
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(invalid_content)
            f.flush()

            from reference_scanner import parse_skill_frontmatter
            result = parse_skill_frontmatter(f.name)

            # 验证返回错误
            self.assertFalse(result.get('success', False))
            self.assertEqual(result['error'], 'YAML_PARSE_ERROR')
            self.assertIn('severity', result)
            self.assertEqual(result['severity'], 'error')

        os.unlink(f.name)


class TestReferenceValidation(unittest.TestCase):
    """测试引用验证功能"""

    def test_detect_broken_reference(self):
        """测试检测断开的引用"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建一个组件引用不存在的 skill
            os.makedirs(f"{tmpdir}/agents/test-agent")
            skill_content = """---
name: test-agent
skills:
  - ccc:non-existent-skill
---
"""
            with open(f"{tmpdir}/agents/test-agent/SKILL.md", 'w') as f:
                f.write(skill_content)

            from reference_scanner import validate_references
            result = validate_references(tmpdir)

            # 验证检测到断开引用
            self.assertEqual(len(result['broken_references']), 1)
            self.assertEqual(result['broken_references'][0]['declared_reference'],
                            'ccc:non-existent-skill')
            self.assertEqual(result['broken_references'][0]['severity'], 'error')

    def test_detect_orphan_file(self):
        """测试检测孤儿文件"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建三个 skill：
            # - used-skill: 被 test-agent 引用
            # - orphan-skill: 未被引用（孤儿）
            # - cmd-entry: 命令入口（跳过）
            os.makedirs(f"{tmpdir}/skills/used-skill")
            os.makedirs(f"{tmpdir}/skills/orphan-skill")
            os.makedirs(f"{tmpdir}/skills/cmd-entry")
            os.makedirs(f"{tmpdir}/agents/test-agent")

            # 被引用的 skill
            with open(f"{tmpdir}/skills/used-skill/SKILL.md", 'w') as f:
                f.write("---\nname: used-skill\n---\n")

            # 孤儿 skill
            with open(f"{tmpdir}/skills/orphan-skill/SKILL.md", 'w') as f:
                f.write("---\nname: orphan-skill\n---\n")

            # cmd 入口（应该被跳过）
            with open(f"{tmpdir}/skills/cmd-entry/SKILL.md", 'w') as f:
                f.write("---\nname: cmd-entry\n---\n")

            # 引用 used-skill 的 agent（自身也被 cmd-entry 引用，避免成为孤儿）
            agent_content = """---
name: test-agent
skills:
  - ccc:used-skill
---
"""
            with open(f"{tmpdir}/agents/test-agent/SKILL.md", 'w') as f:
                f.write(agent_content)

            from reference_scanner import validate_references
            result = validate_references(tmpdir)

            # 验证检测到孤儿文件
            # 应该只有 orphan-skill（cmd-entry 被跳过，test-agent 未被引用但也算孤儿）
            # 实际上有两个孤儿：orphan-skill 和 test-agent
            orphan_paths = [o['file_path'] for o in result['orphan_files']]

            # orphan-skill 应该在孤儿列表中
            self.assertTrue(any('orphan-skill' in path for path in orphan_paths))

            # cmd-entry 不应该在孤儿列表中
            self.assertFalse(any('cmd-entry' in path for path in orphan_paths))

            # 检查 orphan-skill 的详细信息
            orphan_skill = next(o for o in result['orphan_files'] if 'orphan-skill' in o['file_path'])
            self.assertEqual(orphan_skill['severity'], 'warning')


class TestCircularReferenceDetection(unittest.TestCase):
    """测试循环引用检测"""

    def test_detect_simple_cycle(self):
        """测试检测简单循环（A→B→A）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(f"{tmpdir}/agents/agent-a")
            os.makedirs(f"{tmpdir}/agents/agent-b")

            # A 引用 B
            with open(f"{tmpdir}/agents/agent-a/SKILL.md", 'w') as f:
                f.write("---\nname: agent-a\nskills:\n  - ccc:agent-b\n---\n")

            # B 引用 A（形成循环）
            with open(f"{tmpdir}/agents/agent-b/SKILL.md", 'w') as f:
                f.write("---\nname: agent-b\nskills:\n  - ccc:agent-a\n---\n")

            from reference_scanner import build_dependency_graph, detect_cycles
            graph = build_dependency_graph(tmpdir)
            cycles = detect_cycles(graph)

            # 验证检测到循环
            self.assertEqual(len(cycles), 1)
            self.assertIn('agent-a', cycles[0]['cycle_path'])
            self.assertIn('agent-b', cycles[0]['cycle_path'])
            self.assertEqual(cycles[0]['severity'], 'error')

    def test_detect_complex_cycle(self):
        """测试检测复杂循环（A→B→C→A）"""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(f"{tmpdir}/agents/agent-a")
            os.makedirs(f"{tmpdir}/agents/agent-b")
            os.makedirs(f"{tmpdir}/agents/agent-c")

            # A → B
            with open(f"{tmpdir}/agents/agent-a/SKILL.md", 'w') as f:
                f.write("---\nname: agent-a\nskills:\n  - ccc:agent-b\n---\n")

            # B → C
            with open(f"{tmpdir}/agents/agent-b/SKILL.md", 'w') as f:
                f.write("---\nname: agent-b\nskills:\n  - ccc:agent-c\n---\n")

            # C → A（形成循环）
            with open(f"{tmpdir}/agents/agent-c/SKILL.md", 'w') as f:
                f.write("---\nname: agent-c\nskills:\n  - ccc:agent-a\n---\n")

            from reference_scanner import build_dependency_graph, detect_cycles
            graph = build_dependency_graph(tmpdir)
            cycles = detect_cycles(graph)

            # 验证检测到循环
            self.assertEqual(len(cycles), 1)
            cycle_path = cycles[0]['cycle_path']
            self.assertEqual(len([c for c in cycle_path if c in ['agent-a', 'agent-b', 'agent-c']]), 4)  # A→B→C→A


class TestReportGeneration(unittest.TestCase):
    """测试报告生成"""

    def test_generate_json_report(self):
        """测试生成 JSON 报告"""
        # 创建测试数据
        scan_results = {
            'broken_references': [
                {
                    'id': 'BR-001',
                    'severity': 'error',
                    'source_file': 'agents/test/SKILL.md',
                    'declared_reference': 'ccc:missing',
                    'issue': '目标文件不存在'
                }
            ],
            'orphan_files': [
                {
                    'id': 'OR-001',
                    'severity': 'warning',
                    'file_path': 'skills/orphan/SKILL.md',
                    'issue': '未被引用'
                }
            ],
            'cycles': []
        }

        from reference_scanner import generate_json_report

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            report_path = f.name

        generate_json_report(scan_results, '/test/plugin', report_path)

        # 验证报告生成
        self.assertTrue(os.path.exists(report_path))

        with open(report_path, 'r') as f:
            report = json.load(f)

        # 验证报告结构
        self.assertIn('version', report)
        self.assertIn('summary', report)
        self.assertIn('issues', report)
        self.assertEqual(len(report['issues']['broken_references']), 1)
        self.assertEqual(len(report['issues']['orphan_files']), 1)

        # 验证完整性评分计算
        self.assertIn('integrity_score', report['summary'])
        self.assertLess(report['summary']['integrity_score'], 100)

        os.unlink(report_path)

    def test_generate_markdown_report(self):
        """测试生成 Markdown 报告"""
        # TODO: 实现测试
        pass


if __name__ == '__main__':
    unittest.main()
