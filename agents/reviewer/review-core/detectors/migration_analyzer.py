#!/usr/bin/env python3
"""
Migration Analyzer

分析 Command 到 Skill 的迁移状态。

扫描 commands/ 目录，分类每个 Command，检查迁移进度。

用于 LEGACY-001 规则的智能迁移报告生成。

Author: mzdbxqh
Created: 2026-03-13
"""

from pathlib import Path
from typing import Dict, List, Literal, TypedDict
import os

from .pattern_detector import CommandPatternDetector


class CommandInfo(TypedDict):
    """Command 信息数据结构"""
    name: str
    path: str
    pattern: Literal['alias', 'workflow', 'unknown']
    migration_status: Literal['completed', 'pending', 'partial']
    target_path: str  # skills/cmd-{name}/ (如已迁移)
    file_size: int  # 行数
    subagent_count: int
    skill_references: List[str]


class MigrationResult(TypedDict):
    """迁移分析结果"""
    total_count: int
    alias_commands: List[CommandInfo]
    workflow_commands: List[CommandInfo]
    migration_status: Dict[str, any]


class MigrationAnalyzer:
    """
    迁移分析器

    扫描 commands/ 目录，分析每个 Command 的:
    - 模式类型 (alias vs workflow)
    - 迁移状态 (completed vs pending vs partial)
    - 详细信息 (文件大小、SubAgent 数量等)
    """

    def __init__(self):
        """初始化迁移分析器"""
        self.pattern_detector = CommandPatternDetector()

    def analyze(self, plugin_root: str) -> MigrationResult:
        """
        分析插件的 Command 迁移状态

        Args:
            plugin_root: 插件根目录路径

        Returns:
            MigrationResult: 完整的迁移分析结果

        工作流程:
        1. 扫描 commands/ 目录
        2. 对每个 Command 调用 pattern_detector.detect()
        3. 检查迁移状态 (skills/cmd-* 是否存在)
        4. 分类到 alias_commands 或 workflow_commands
        5. 计算迁移进度
        """
        plugin_root_path = Path(plugin_root)
        commands_dir = plugin_root_path / 'commands'

        # 检查 commands/ 目录是否存在
        if not commands_dir.exists() or not commands_dir.is_dir():
            return {
                'total_count': 0,
                'alias_commands': [],
                'workflow_commands': [],
                'migration_status': {
                    'completed': [],
                    'pending': [],
                    'progress': '0/0 migrated'
                }
            }

        # 扫描所有 .md 文件
        command_files = list(commands_dir.glob('*.md'))

        alias_commands = []
        workflow_commands = []
        completed_commands = []
        pending_commands = []

        for command_file in command_files:
            # 提取 Command 名称 (去掉 .md 后缀)
            command_name = command_file.stem

            # 获取详细分析
            analysis = self.pattern_detector.get_detailed_analysis(str(command_file))

            # 检查迁移状态
            migration_status = self._check_migration_status(
                command_name,
                plugin_root_path
            )

            # 构建 CommandInfo
            command_info: CommandInfo = {
                'name': command_name,
                'path': str(command_file.relative_to(plugin_root_path)),
                'pattern': analysis['pattern'],
                'migration_status': migration_status,
                'target_path': f'skills/cmd-{command_name}/',
                'file_size': analysis.get('line_count', 0),
                'subagent_count': analysis.get('subagent_count', 0),
                'skill_references': analysis.get('skill_references', []),
            }

            # 分类到对应列表
            if analysis['pattern'] == 'alias':
                alias_commands.append(command_info)
            elif analysis['pattern'] == 'workflow':
                workflow_commands.append(command_info)
            else:
                # Unknown pattern: 默认归类为 workflow (保守策略)
                workflow_commands.append(command_info)

            # 统计迁移状态
            if migration_status == 'completed':
                completed_commands.append(command_name)
            else:
                pending_commands.append(command_name)

        # 计算迁移进度
        total_count = len(command_files)
        completed_count = len(completed_commands)
        progress = f'{completed_count}/{total_count} migrated'

        return {
            'total_count': total_count,
            'alias_commands': alias_commands,
            'workflow_commands': workflow_commands,
            'migration_status': {
                'completed': completed_commands,
                'pending': pending_commands,
                'progress': progress
            }
        }

    def _check_migration_status(
        self,
        command_name: str,
        plugin_root: Path
    ) -> Literal['completed', 'pending', 'partial']:
        """
        检查单个 Command 的迁移状态

        Args:
            command_name: Command 名称
            plugin_root: 插件根目录

        Returns:
            'completed': skills/cmd-{name}/ 存在且包含 SKILL.md
            'partial': skills/cmd-{name}/ 存在但不完整
            'pending': 尚未迁移

        判断逻辑:
        - 目录存在 + SKILL.md 存在 → completed
        - 目录存在 + SKILL.md 不存在 → partial
        - 目录不存在 → pending
        """
        target_dir = plugin_root / 'skills' / f'cmd-{command_name}'
        skill_file = target_dir / 'SKILL.md'

        if not target_dir.exists():
            return 'pending'

        if skill_file.exists():
            return 'completed'

        return 'partial'

    def generate_migration_report(
        self,
        plugin_root: str,
        language: Literal['zh', 'en'] = 'zh'
    ) -> str:
        """
        生成迁移报告 (Markdown 格式)

        Args:
            plugin_root: 插件根目录
            language: 报告语言 ('zh' 或 'en')

        Returns:
            str: Markdown 格式的迁移报告
        """
        result = self.analyze(plugin_root)

        if language == 'zh':
            return self._generate_report_zh(result)
        else:
            return self._generate_report_en(result)

    def _generate_report_zh(self, result: MigrationResult) -> str:
        """生成中文迁移报告"""
        report_lines = [
            "# Command 迁移分析报告",
            "",
            "## 概览",
            "",
            f"- 检测到 Command 数量: {result['total_count']}",
            f"- Alias Pattern: {len(result['alias_commands'])}",
            f"- Workflow Pattern: {len(result['workflow_commands'])}",
            f"- 已迁移: {len(result['migration_status']['completed'])}",
            f"- 待迁移: {len(result['migration_status']['pending'])}",
            f"- 迁移进度: {result['migration_status']['progress']}",
            "",
            "---",
            ""
        ]

        # Alias Pattern Commands
        if result['alias_commands']:
            report_lines.extend([
                f"## Alias Pattern Commands ({len(result['alias_commands'])} 个)",
                ""
            ])

            for cmd in result['alias_commands']:
                status_emoji = "✅" if cmd['migration_status'] == 'completed' else "⏳"
                report_lines.extend([
                    f"### {cmd['name']} {status_emoji}",
                    "",
                    f"- **路径**: `{cmd['path']}`",
                    f"- **模式**: Alias (快捷方式)",
                    f"- **目标 Skill**: {', '.join(cmd['skill_references']) if cmd['skill_references'] else '未检测到'}",
                    f"- **迁移状态**: {cmd['migration_status']}",
                    "",
                    "**建议操作**:",
                    f"1. 删除 `{cmd['path']}`",
                    f"2. 在 README.md 中添加说明:",
                    "   ```markdown",
                    f"   - `/{cmd['name']}` - {cmd['skill_references'][0] if cmd['skill_references'] else 'XXX'} 的快捷命令",
                    "   ```",
                    "",
                    "---",
                    ""
                ])

        # Workflow Pattern Commands
        if result['workflow_commands']:
            report_lines.extend([
                f"## Workflow Pattern Commands ({len(result['workflow_commands'])} 个)",
                ""
            ])

            for cmd in result['workflow_commands']:
                status_emoji = "✅" if cmd['migration_status'] == 'completed' else "⏳"
                report_lines.extend([
                    f"### {cmd['name']} {status_emoji}",
                    "",
                    f"- **路径**: `{cmd['path']}`",
                    f"- **模式**: Workflow (工作流)",
                    f"- **文件大小**: {cmd['file_size']} 行",
                    f"- **SubAgent 调用**: {cmd['subagent_count']} 个",
                    f"- **迁移状态**: {cmd['migration_status']}",
                    f"- **目标路径**: `{cmd['target_path']}`",
                    "",
                    "**建议操作**:",
                    f"1. 创建目录: `mkdir -p {cmd['target_path']}`",
                    f"2. 迁移文件: `cp {cmd['path']} {cmd['target_path']}SKILL.md`",
                    "3. 更新 frontmatter (name, context 等)",
                    "4. 迁移测试文件 (如有)",
                    f"5. 删除原 Command: `rm {cmd['path']}`",
                    "6. 更新 README 和 CHANGELOG",
                    "",
                    "---",
                    ""
                ])

        # Summary
        report_lines.extend([
            "## 迁移优先级建议",
            "",
            "**P0 (立即迁移)**:",
        ])

        # 优先迁移 workflow commands
        high_priority = [
            f"- {cmd['name']} (Workflow)"
            for cmd in result['workflow_commands']
            if cmd['migration_status'] == 'pending'
        ][:3]  # 最多显示 3 个

        if high_priority:
            report_lines.extend(high_priority)
        else:
            report_lines.append("- (无)")

        report_lines.extend([
            "",
            "**P1 (1-2周内迁移)**:",
        ])

        medium_priority = [
            f"- {cmd['name']} (Alias)"
            for cmd in result['alias_commands']
            if cmd['migration_status'] == 'pending'
        ]

        if medium_priority:
            report_lines.extend(medium_priority)
        else:
            report_lines.append("- (无)")

        report_lines.extend([
            "",
            "## 注意事项",
            "",
            "1. **向后兼容性**: 确保迁移后用户体验不变",
            "2. **测试覆盖**: 每个迁移后的 Skill 都应通过测试",
            "3. **文档更新**: 同步更新 README 和用户文档",
            "4. **渐进迁移**: 可以逐个迁移，不必一次性完成",
            ""
        ])

        return '\n'.join(report_lines)

    def _generate_report_en(self, result: MigrationResult) -> str:
        """生成英文迁移报告"""
        report_lines = [
            "# Command Migration Analysis Report",
            "",
            "## Overview",
            "",
            f"- Total Commands detected: {result['total_count']}",
            f"- Alias Pattern: {len(result['alias_commands'])}",
            f"- Workflow Pattern: {len(result['workflow_commands'])}",
            f"- Migrated: {len(result['migration_status']['completed'])}",
            f"- Pending: {len(result['migration_status']['pending'])}",
            f"- Migration progress: {result['migration_status']['progress']}",
            "",
            "---",
            ""
        ]

        # Alias Pattern Commands
        if result['alias_commands']:
            report_lines.extend([
                f"## Alias Pattern Commands ({len(result['alias_commands'])})",
                ""
            ])

            for cmd in result['alias_commands']:
                status_emoji = "✅" if cmd['migration_status'] == 'completed' else "⏳"
                report_lines.extend([
                    f"### {cmd['name']} {status_emoji}",
                    "",
                    f"- **Path**: `{cmd['path']}`",
                    f"- **Pattern**: Alias (Shortcut)",
                    f"- **Target Skill**: {', '.join(cmd['skill_references']) if cmd['skill_references'] else 'Not detected'}",
                    f"- **Migration status**: {cmd['migration_status']}",
                    "",
                    "**Recommended actions**:",
                    f"1. Delete `{cmd['path']}`",
                    f"2. Add to README.md:",
                    "   ```markdown",
                    f"   - `/{cmd['name']}` - Shortcut for {cmd['skill_references'][0] if cmd['skill_references'] else 'XXX'}",
                    "   ```",
                    "",
                    "---",
                    ""
                ])

        # Workflow Pattern Commands
        if result['workflow_commands']:
            report_lines.extend([
                f"## Workflow Pattern Commands ({len(result['workflow_commands'])})",
                ""
            ])

            for cmd in result['workflow_commands']:
                status_emoji = "✅" if cmd['migration_status'] == 'completed' else "⏳"
                report_lines.extend([
                    f"### {cmd['name']} {status_emoji}",
                    "",
                    f"- **Path**: `{cmd['path']}`",
                    f"- **Pattern**: Workflow",
                    f"- **File size**: {cmd['file_size']} lines",
                    f"- **SubAgent calls**: {cmd['subagent_count']}",
                    f"- **Migration status**: {cmd['migration_status']}",
                    f"- **Target path**: `{cmd['target_path']}`",
                    "",
                    "**Recommended actions**:",
                    f"1. Create directory: `mkdir -p {cmd['target_path']}`",
                    f"2. Migrate file: `cp {cmd['path']} {cmd['target_path']}SKILL.md`",
                    "3. Update frontmatter (name, context, etc.)",
                    "4. Migrate test files (if any)",
                    f"5. Delete original Command: `rm {cmd['path']}`",
                    "6. Update README and CHANGELOG",
                    "",
                    "---",
                    ""
                ])

        # Summary
        report_lines.extend([
            "## Migration Priority Recommendations",
            "",
            "**P0 (Immediate)**:",
        ])

        # Prioritize workflow commands
        high_priority = [
            f"- {cmd['name']} (Workflow)"
            for cmd in result['workflow_commands']
            if cmd['migration_status'] == 'pending'
        ][:3]

        if high_priority:
            report_lines.extend(high_priority)
        else:
            report_lines.append("- (None)")

        report_lines.extend([
            "",
            "**P1 (Within 1-2 weeks)**:",
        ])

        medium_priority = [
            f"- {cmd['name']} (Alias)"
            for cmd in result['alias_commands']
            if cmd['migration_status'] == 'pending'
        ]

        if medium_priority:
            report_lines.extend(medium_priority)
        else:
            report_lines.append("- (None)")

        report_lines.extend([
            "",
            "## Important Notes",
            "",
            "1. **Backward compatibility**: Ensure no change in user experience",
            "2. **Test coverage**: Each migrated Skill should pass tests",
            "3. **Documentation update**: Sync update README and user docs",
            "4. **Gradual migration**: Can migrate one by one, no need all at once",
            ""
        ])

        return '\n'.join(report_lines)


# 便利函数
def analyze_migration(plugin_root: str) -> MigrationResult:
    """
    便利函数: 分析迁移状态

    Args:
        plugin_root: 插件根目录

    Returns:
        MigrationResult
    """
    analyzer = MigrationAnalyzer()
    return analyzer.analyze(plugin_root)


def generate_migration_report(
    plugin_root: str,
    language: Literal['zh', 'en'] = 'zh'
) -> str:
    """
    便利函数: 生成迁移报告

    Args:
        plugin_root: 插件根目录
        language: 报告语言

    Returns:
        str: Markdown 格式报告
    """
    analyzer = MigrationAnalyzer()
    return analyzer.generate_migration_report(plugin_root, language)


if __name__ == '__main__':
    # 测试代码
    import sys

    if len(sys.argv) < 2:
        print("Usage: python migration_analyzer.py <plugin_root> [language]")
        print("  language: zh (default) or en")
        sys.exit(1)

    plugin_root = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else 'zh'

    analyzer = MigrationAnalyzer()

    # 生成迁移报告
    report = analyzer.generate_migration_report(plugin_root, language)
    print(report)
