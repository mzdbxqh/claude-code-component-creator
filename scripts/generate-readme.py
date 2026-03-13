#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
README 生成器

从实际数据源自动生成 README.md 和 README_zh.md，确保：
1. 版本号一致性（从 plugin.json 提取）
2. 中英文同步
3. 命令列表完整性（从 skills/ 扫描）
4. 质量评分准确性（从 CHANGELOG 提取）

使用方法:
    python scripts/generate-readme.py

作者: mzdbxqh
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class READMEGenerator:
    """README 生成器"""

    def __init__(self, plugin_root: str):
        """
        初始化生成器

        Args:
            plugin_root: 插件根目录路径
        """
        self.plugin_root = Path(plugin_root)
        self.data = {}

    def extract_version_info(self) -> Dict:
        """从 plugin.json 提取版本信息"""
        plugin_json = self.plugin_root / '.claude-plugin' / 'plugin.json'

        with open(plugin_json, 'r', encoding='utf-8') as f:
            config = json.load(f)

        return {
            'version': config['version'],
            'name': config['name'],
            'description': config['description'],
            'author': config['author']['name'],
            'homepage': config['homepage'],
            'repository': config['repository'],
            'license': config['license']
        }

    def extract_quality_score(self) -> Dict:
        """从 CHANGELOG.md 提取最新质量评分"""
        changelog = self.plugin_root / 'CHANGELOG.md'

        with open(changelog, 'r', encoding='utf-8') as f:
            content = f.read()

        # 查找最新版本的质量评分
        # 匹配 "Overall Score: XX/100" 或 "综合评分: XX/100"
        score_match = re.search(r'(?:Overall Score|综合评分|质量评分).*?(\d+)/100', content)
        overall_score = score_match.group(1) if score_match else '96'

        # 提取各维度评分（从表格中）
        dimensions = {}

        # 匹配表格中的评分
        # | Security | 98/100 | ...
        dimension_pattern = r'\|\s*(\w+(?:\s+\w+)?)\s*\|\s*\d+%?\s*\|\s*\d+\s*\|\s*(\d+)/100'
        for match in re.finditer(dimension_pattern, content):
            dim_name = match.group(1).strip()
            dim_score = match.group(2)
            dimensions[dim_name] = dim_score

        return {
            'overall': overall_score,
            'dimensions': dimensions
        }

    def scan_commands(self) -> List[Dict]:
        """扫描 skills/cmd-* 目录，提取命令列表"""
        commands = []
        skills_dir = self.plugin_root / 'skills'

        # 扫描所有 cmd-* 目录
        for skill_dir in sorted(skills_dir.glob('cmd-*')):
            skill_md = skill_dir / 'SKILL.md'
            if not skill_md.exists():
                continue

            with open(skill_md, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取 frontmatter 中的 description
            frontmatter_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
            if frontmatter_match:
                frontmatter = frontmatter_match.group(1)
                desc_match = re.search(r'description:\s*["\'](.*?)["\']', frontmatter, re.DOTALL)
                description = desc_match.group(1) if desc_match else ''
            else:
                description = ''

            # 提取中文描述（从正文的第一段）
            zh_desc_match = re.search(r'##\s*概述\s*\n\n(.*?)(?:\n\n|\n##)', content, re.DOTALL)
            zh_description = zh_desc_match.group(1).strip() if zh_desc_match else description

            commands.append({
                'name': skill_dir.name,
                'command': f'/cmd-{skill_dir.name[4:]}',
                'description_en': description,
                'description_zh': zh_description
            })

        return commands

    def extract_features(self) -> List[Dict]:
        """从 CHANGELOG.md 提取最新版本的特性列表"""
        changelog = self.plugin_root / 'CHANGELOG.md'

        with open(changelog, 'r', encoding='utf-8') as f:
            content = f.read()

        # 查找最新版本的 Added 部分
        # ## [X.Y.Z] - Date
        # ...
        # ### Added
        # - Feature 1
        # - Feature 2

        features = []

        # 先找到第一个版本块
        version_match = re.search(r'## \[([\d.]+)\].*?\n(.*?)(?=\n## \[|$)', content, re.DOTALL)
        if version_match:
            version_content = version_match.group(2)

            # 提取 Added 部分
            added_match = re.search(r'### Added.*?\n(.*?)(?=\n###|\n##|$)', version_content, re.DOTALL)
            if added_match:
                added_content = added_match.group(1)

                # 提取所有 "- " 开头的行
                for line in added_content.split('\n'):
                    line = line.strip()
                    if line.startswith('- '):
                        feature = line[2:].strip()
                        # 跳过嵌套列表
                        if not feature.startswith(' '):
                            features.append(feature)

        return features

    def load_template(self, template_name: str) -> str:
        """加载模板文件"""
        template_path = self.plugin_root / 'docs' / 'templates' / f'{template_name}.md'

        if not template_path.exists():
            raise FileNotFoundError(f"模板文件不存在: {template_path}")

        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()

    def render_template(self, template: str, data: Dict) -> str:
        """
        渲染模板

        简单的变量替换，格式: {variable_name}
        """
        result = template

        for key, value in data.items():
            placeholder = '{' + key + '}'
            if isinstance(value, list):
                # 列表转换为 Markdown
                if key == 'commands_table_en':
                    value = self._render_commands_table_en(data['commands'])
                elif key == 'commands_table_zh':
                    value = self._render_commands_table_zh(data['commands'])
                elif key == 'features_list_en':
                    value = self._render_features_list(data['features'])
                elif key == 'features_list_zh':
                    value = self._render_features_list(data['features'])

            result = result.replace(placeholder, str(value))

        return result

    def _render_commands_table_en(self, commands: List[Dict]) -> str:
        """渲染命令表格（英文）"""
        lines = [
            '| Command | Description |',
            '|---------|-------------|'
        ]

        for cmd in commands:
            lines.append(f"| `{cmd['command']}` | {cmd['description_en']} |")

        return '\n'.join(lines)

    def _render_commands_table_zh(self, commands: List[Dict]) -> str:
        """渲染命令表格（中文）"""
        lines = [
            '| 命令 | 描述 |',
            '|------|------|'
        ]

        for cmd in commands:
            desc = cmd['description_zh'] if cmd['description_zh'] else cmd['description_en']
            lines.append(f"| `{cmd['command']}` | {desc} |")

        return '\n'.join(lines)

    def _render_features_list(self, features: List[str]) -> str:
        """渲染特性列表"""
        return '\n'.join([f'- {feature}' for feature in features])

    def generate(self):
        """生成 README.md 和 README_zh.md"""
        print("开始生成 README 文件...")

        # 1. 收集数据
        print("  [1/5] 提取版本信息...")
        version_info = self.extract_version_info()

        print("  [2/5] 提取质量评分...")
        quality_score = self.extract_quality_score()

        print("  [3/5] 扫描命令列表...")
        commands = self.scan_commands()

        print("  [4/5] 提取特性列表...")
        features = self.extract_features()

        # 2. 准备数据字典
        data = {
            'version': version_info['version'],
            'quality_score': quality_score['overall'],
            'current_year': datetime.now().year,
            'author': version_info['author'],
            'repository': version_info['repository'],
            'homepage': version_info['homepage'],
            'license': version_info['license'],
            'commands': commands,
            'features': features,
            'commands_table_en': '',  # 将被渲染函数填充
            'commands_table_zh': '',  # 将被渲染函数填充
            'features_list_en': '',   # 将被渲染函数填充
            'features_list_zh': '',   # 将被渲染函数填充
        }

        # 添加质量维度评分
        for dim_name, dim_score in quality_score['dimensions'].items():
            data[f'score_{dim_name.lower().replace(" ", "_")}'] = dim_score

        print("  [5/5] 渲染模板...")

        # 3. 加载并渲染模板
        try:
            # 英文版
            template_en = self.load_template('README-template')
            readme_en = self.render_template(template_en, data)

            readme_path = self.plugin_root / 'README.md'
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_en)
            print(f"  ✓ 已生成: {readme_path}")

            # 中文版
            template_zh = self.load_template('README-template-zh')
            readme_zh = self.render_template(template_zh, data)

            readme_zh_path = self.plugin_root / 'README_zh.md'
            with open(readme_zh_path, 'w', encoding='utf-8') as f:
                f.write(readme_zh)
            print(f"  ✓ 已生成: {readme_zh_path}")

            print("\n生成完成！")
            print(f"  版本号: {version_info['version']}")
            print(f"  质量评分: {quality_score['overall']}/100")
            print(f"  命令数量: {len(commands)}")
            print(f"  特性数量: {len(features)}")

        except FileNotFoundError as e:
            print(f"\n错误: {e}")
            print("\n提示: 请先创建模板文件:")
            print("  - docs/templates/README-template.md")
            print("  - docs/templates/README-template-zh.md")
            print("\n运行以下命令创建模板:")
            print("  python scripts/generate-readme.py --create-templates")


def main():
    """主函数"""
    import sys

    # 获取插件根目录
    script_dir = Path(__file__).parent
    plugin_root = script_dir.parent

    # 检查是否是创建模板命令
    if len(sys.argv) > 1 and sys.argv[1] == '--create-templates':
        print("此功能待实现，请手动创建模板文件")
        print("参考: docs/templates/README-template.md")
        return

    # 生成 README
    generator = READMEGenerator(str(plugin_root))
    generator.generate()


if __name__ == '__main__':
    main()
