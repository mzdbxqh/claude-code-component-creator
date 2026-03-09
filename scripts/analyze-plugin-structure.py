#!/usr/bin/env python3
"""
CCC 插件结构分析脚本
解析 .claude-plugin/plugin.json，识别所有 commands/和 agents/
"""

import json
import os
import re
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class CommandInfo:
    name: str
    file: str
    description: str
    triggers: list

@dataclass
class AgentInfo:
    name: str
    file: str
    description: str
    context: str
    model: str
    tools: list

def parse_yaml_header(content):
    """解析 YAML header"""
    match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    
    header = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            header[key.strip()] = value.strip().strip('"')
    return header

def extract_triggers(description):
    """从描述中提取触发词"""
    triggers = []
    if '触发' in description:
        triggers = description.split('触发')[-1].replace(':', ':').strip().split('/')
    return triggers

def analyze_plugin_structure():
    base_dir = Path(__file__).parent.parent
    
    # 1. 解析 plugin.json
    plugin_json_path = base_dir / '.claude-plugin' / 'plugin.json'
    try:
        with open(plugin_json_path) as f:
            plugin_meta = json.load(f)
    except FileNotFoundError:
        plugin_meta = {'name': 'N/A', 'version': 'N/A'}
    
    # 2. 扫描 commands/
    commands = []
    commands_dir = base_dir / 'commands'
    if commands_dir.exists():
        for cmd_file in commands_dir.glob('*.md'):
            with open(cmd_file) as f:
                content = f.read()
            header = parse_yaml_header(content)
            
            commands.append(CommandInfo(
                name=header.get('name', ''),
                file=str(cmd_file.relative_to(base_dir)),
                description=header.get('description', ''),
                triggers=extract_triggers(header.get('description_zh', ''))
            ))
    
    # 3. 扫描 agents/
    agents = []
    agents_dir = base_dir / 'agents'
    if agents_dir.exists():
        for agent_file in agents_dir.glob('*/SKILL.md'):
            with open(agent_file) as f:
                content = f.read()
            header = parse_yaml_header(content)
            
            agents.append(AgentInfo(
                name=header.get('name', ''),
                file=str(agent_file.relative_to(base_dir)),
                description=header.get('description', ''),
                context=header.get('context', 'main'),
                model=header.get('model', 'sonnet'),
                tools=header.get('allowed-tools', [])
            ))
    
    # 4. 生成报告
    print("# CCC 插件结构分析报告\n")
    print(f"## 插件元数据")
    print(f"- **名称**: {plugin_meta.get('name', 'N/A')}")
    print(f"- **版本**: {plugin_meta.get('version', 'N/A')}")
    print(f"- **命令数量**: {len(commands)}")
    print(f"- **代理数量**: {len(agents)}\n")
    
    print("## 命令列表\n")
    print("| 命令 | 文件 | 描述 |")
    print("|------|------|------|")
    for cmd in commands:
        desc = cmd.description[:50] + '...' if len(cmd.description) > 50 else cmd.description
        print(f"| {cmd.name} | {cmd.file} | {desc} |")
    
    print("\n## 代理列表 (context: fork = 隔离上下文)\n")
    print("| 代理 | 文件 | Context | 模型 |")
    print("|------|------|---------|------|")
    for agent in agents:
        isolation = "✅" if agent.context == 'fork' else "❌"
        print(f"| {agent.name} | {agent.file} | {agent.context} {isolation} | {agent.model} |")
    
    return report

if __name__ == '__main__':
    analyze_plugin_structure()
