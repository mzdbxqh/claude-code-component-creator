#!/usr/bin/env python3
"""
CCC 跨 Command 工作流链路分析脚本
识别多个 commands 串联的完整工作流链路
"""

import re
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class WorkflowChain:
    entry_command: str
    chain: list
    artifacts: list

def parse_yaml_header(content):
    """解析 YAML header"""
    match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    return dict(re.findall(r'(\S+):\s*"?([^"\n]+)"?', match.group(1)))

def extract_command_calls(content):
    """提取文件中调用的其他命令"""
    calls = []
    # 匹配 /ccc:xxx 调用
    for match in re.finditer(r'/ccc:(\w+)', content):
        calls.append(f"ccc:{match.group(1)}")
    return list(set(calls))

def extract_artifacts(content):
    """提取文件中引用的 artifacts"""
    artifacts = []
    patterns = [
        r'docs/ccc/intent/[^`\s]+',
        r'docs/ccc/blueprint/[^`\s]+',
        r'docs/ccc/delivery/[^`\s]+'
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, content):
            artifacts.append(match.group())
    return list(set(artifacts))

def trace_command_chain(entry_cmd, commands_map, visited=None, depth=0):
    """递归追踪命令调用链"""
    if visited is None:
        visited = set()
    if entry_cmd in visited or depth > 10:
        return []
    
    visited.add(entry_cmd)
    chain = [entry_cmd]
    
    if entry_cmd in commands_map:
        cmd_content = commands_map[entry_cmd]
        called_commands = extract_command_calls(cmd_content)
        for called in called_commands:
            sub_chain = trace_command_chain(called, commands_map, visited.copy(), depth + 1)
            chain.extend(sub_chain)
    
    return chain

def analyze_command_workflows():
    base_dir = Path(__file__).parent.parent
    commands_dir = base_dir / 'commands'
    
    # 加载所有命令
    commands_map = {}
    commands_list = []
    
    for cmd_file in commands_dir.glob('*.md'):
        with open(cmd_file) as f:
            content = f.read()
        header = parse_yaml_header(content)
        
        cmd_name = header.get('name', '')
        commands_map[cmd_name] = content
        commands_list.append({
            'name': cmd_name,
            'file': str(cmd_file.name),
            'description': header.get('description', ''),
            'description_zh': header.get('description_zh', '')
        })
    
    # 识别入口命令
    entry_keywords = ['快速', '创建', '生成', '审查', '一键', '开始']
    entry_commands = [
        cmd for cmd in commands_list
        if any(kw in cmd.get('description_zh', '') for kw in entry_keywords)
    ]
    
    # 追踪每个入口命令的调用链
    workflow_chains = []
    for entry in entry_commands:
        chain = trace_command_chain(entry['name'], commands_map)
        artifacts = extract_artifacts(commands_map.get(entry['name'], ''))
        workflow_chains.append(WorkflowChain(
            entry_command=entry['name'],
            chain=chain,
            artifacts=artifacts
        ))
    
    # 生成报告
    print("# CCC 跨 Command 工作流链路分析报告\n")
    print("## 工作流分类\n")
    print("### 核心工作流\n")
    print("| 工作流 | 入口命令 | 调用链长度 | 产物 |")
    print("|--------|---------|-----------|------|")
    for wf in workflow_chains:
        artifacts_preview = ', '.join(wf.artifacts[:2]) if wf.artifacts else 'N/A'
        print(f"| {wf.entry_command} | {wf.entry_command} | {len(wf.chain)} | {artifacts_preview} |")
    
    print("\n## 完整工作流调用图\n")
    print("```mermaid")
    print("graph TD")
    for wf in workflow_chains:
        for i, cmd in enumerate(wf.chain):
            if i > 0:
                print(f"    {wf.chain[i-1]} --> {cmd}")
    print("```")
    
    return {
        'entry_commands': [asdict(c) for c in entry_commands],
        'workflow_chains': [asdict(w) for w in workflow_chains]
    }

if __name__ == '__main__':
    analyze_command_workflows()
