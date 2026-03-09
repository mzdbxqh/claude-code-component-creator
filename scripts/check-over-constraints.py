#!/usr/bin/env python3
"""
CCC 过度约束检查脚本
查找所有 MUST/NEVER/ALWAYS  without 解释（缺少"为什么"）
"""

import re
from pathlib import Path

def check_over_constraints():
    base_dir = Path(__file__).parent.parent
    issues = []
    
    # 扫描所有 SKILL.md 和命令文件
    patterns = [
        (base_dir / 'agents', '**/SKILL.md'),
        (base_dir / 'commands', '**/*.md'),
    ]
    
    # 强约束关键词
    constraint_keywords = ['MUST', 'NEVER', 'ALWAYS', '必须', '禁止', '绝不']
    explanation_keywords = ['为什么', 'because', 'reason', 'why', '为了', '确保', '避免']
    
    for directory, pattern in patterns:
        if not directory.exists():
            continue
        for file in directory.glob(pattern):
            with open(file) as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines, 1):
                # 检查是否包含强约束关键词
                has_constraint = any(kw in line for kw in constraint_keywords)
                has_explanation = any(kw in line.lower() for kw in explanation_keywords)
                
                if has_constraint and not has_explanation:
                    # 检查下一行是否有解释
                    if i < len(lines) and not any(kw in lines[i].lower() for kw in explanation_keywords):
                        issues.append({
                            'file': str(file.relative_to(base_dir)),
                            'line': i,
                            'content': line.strip()
                        })
    
    # 输出报告
    print("# CCC 过度约束检查报告\n")
    print("查找所有 MUST/NEVER/ALWAYS/必须/禁止 没有解释为什么的规则\n")
    
    if not issues:
        print("✅ 未发现过度约束 - 所有强约束都有解释")
    else:
        print(f"发现 {len(issues)} 个可能缺少解释的强约束:\n")
        print("| 文件 | 行号 | 内容 |")
        print("|------|------|------|")
        for issue in issues[:20]:  # 限制输出前 20 个
            content = issue['content'][:60] + '...' if len(issue['content']) > 60 else issue['content']
            print(f"| {issue['file']} | {issue['line']} | {content} |")
        
        if len(issues) > 20:
            print(f"\n... 还有 {len(issues) - 20} 个问题未显示")
    
    return issues

if __name__ == '__main__':
    check_over_constraints()
