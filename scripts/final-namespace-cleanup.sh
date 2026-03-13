#!/bin/bash

# 最终清理：处理所有不存在的命令引用

echo "最终清理不存在的命令引用..."
echo "======================================="

# 不存在的命令列表，替换为注释或正确的命令
declare -A NON_EXISTENT_COMMANDS=(
    ["/ccc:clean"]="/cmd-status --clean (计划中)"
    ["/ccc:projects"]="/cmd-status --list-projects (计划中)"
    ["/ccc:link"]="(手动在工件中添加链接)"
    ["/ccc:list"]="/cmd-status"
    ["/ccc:show"]="/cmd-status"
    ["/ccc:import"]="/cmd-init (从模板导入功能计划中)"
)

# 处理通用占位符（保持不变，这些是文档示例）
# /ccc:your-command, /ccc:command, /ccc:xxx 等

# 处理特定文件中的不存在命令
echo "处理cmd-status中的错误引用..."
sed -i.bak 's|/ccc:clean|/cmd-status --clean (计划中)|g' skills/cmd-status/SKILL.md
rm -f skills/cmd-status/SKILL.md.bak

echo "处理cmd-trace中的错误引用..."
sed -i.bak \
    -e 's|/ccc:projects|/cmd-status|g' \
    -e 's|/ccc:link|# 手动链接工件 (功能计划中)|g' \
    -e 's|/ccc:list|/cmd-status|g' \
    skills/cmd-trace/SKILL.md
rm -f skills/cmd-trace/SKILL.md.bak

echo "处理cmd-status-graph中的错误引用..."
sed -i.bak \
    -e 's|/ccc:import|/cmd-init --from-template (计划中)|g' \
    -e 's|/ccc:list|/cmd-status|g' \
    skills/cmd-status-graph/SKILL.md
rm -f skills/cmd-status-graph/SKILL.md.bak

echo "处理cmd-status-trace中的错误引用..."
sed -i.bak \
    -e 's|/ccc:link|# 手动链接工件 (功能计划中)|g' \
    -e 's|/ccc:list|/cmd-status|g' \
    skills/cmd-status-trace/SKILL.md
rm -f skills/cmd-status-trace/SKILL.md.bak

echo "处理cmd-diff中的错误引用..."
sed -i.bak \
    -e 's|/ccc:list|/cmd-status|g' \
    -e 's|/ccc:show|/cmd-status --show-details|g' \
    skills/cmd-diff/SKILL.md
rm -f skills/cmd-diff/SKILL.md.bak

echo "处理README和其他文档中的通用引用..."
# 这些是文档示例，改为通用说明
sed -i.bak \
    -e 's|`/ccc:` commands|`/cmd-*` commands|g' \
    -e 's|`/ccc:`命令|`/cmd-*`命令|g' \
    README.md TROUBLESHOOTING.md
rm -f README.md.bak TROUBLESHOOTING.md.bak

echo "======================================="
echo "清理完成!"
echo ""

# 最终统计
echo "剩余的 /ccc: 引用统计:"
echo "通用占位符 (可接受):"
grep -r '/ccc:xxx\|/ccc:your-command\|/ccc:command\|/ccc:skill-split-advisor' --include='*.md' . | grep -v backups | wc -l | tr -d ' ' | xargs echo "  -"

echo ""
echo "其他引用 (需要人工检查):"
grep -r '/ccc:' --include='*.md' . | grep -v backups | grep -v '/ccc:xxx' | grep -v '/ccc:your-command' | grep -v '/ccc:command' | grep -v '/ccc:skill-split-advisor' | grep -v '计划中' | grep -v 'SubAgent' | grep -v '示例命令' | wc -l | tr -d ' ' | xargs echo "  -"
