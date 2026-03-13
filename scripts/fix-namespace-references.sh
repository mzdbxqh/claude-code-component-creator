#!/bin/bash

# 修复所有文档中的命名空间引用
# 将 /ccc:xxx 替换为 /cmd-xxx

set -e

echo "开始修复命名空间引用..."
echo "======================================="

# 统计变量
total_files=0
total_replacements=0

# 遍历所有Markdown文件（排除备份）
find . -name "*.md" -type f ! -path "*/backups/*" ! -name "*.bak" | while read -r file; do
    # 检查文件是否包含 /ccc: 引用
    if grep -q "/ccc:" "$file" 2>/dev/null; then
        echo "处理: $file"

        # 创建临时文件
        tmp_file="${file}.fixing_namespace"

        # 执行所有替换（按最长优先）
        sed \
            -e 's|/ccc:review-migration-plan|/cmd-review-migration-plan|g' \
            -e 's|/ccc:review-workflow|/cmd-review-workflow|g' \
            -e 's|/ccc:design-iterate|/cmd-design-iterate|g' \
            -e 's|/ccc:design-new|/cmd-design-new|g' \
            -e 's|/ccc:status-trace|/cmd-status-trace|g' \
            -e 's|/ccc:status-graph|/cmd-status-graph|g' \
            -e 's|/ccc:test-sandbox|/cmd-test-sandbox|g' \
            -e 's|/ccc:quick|/cmd-quick|g' \
            -e 's|/ccc:init|/cmd-init|g' \
            -e 's|/ccc:design|/cmd-design|g' \
            -e 's|/ccc:build|/cmd-build|g' \
            -e 's|/ccc:implement|/cmd-implement|g' \
            -e 's|/ccc:iterate|/cmd-iterate|g' \
            -e 's|/ccc:review|/cmd-review|g' \
            -e 's|/ccc:fix|/cmd-fix|g' \
            -e 's|/ccc:validate|/cmd-validate|g' \
            -e 's|/ccc:status|/cmd-status|g' \
            -e 's|/ccc:trace|/cmd-trace|g' \
            -e 's|/ccc:diff|/cmd-diff|g' \
            "$file" > "$tmp_file"

        # 统计本文件的替换次数
        old_count=$(grep -o "/ccc:" "$file" 2>/dev/null | wc -l | tr -d ' ')
        new_count=$(grep -o "/ccc:" "$tmp_file" 2>/dev/null | wc -l | tr -d ' ')
        replacements=$((old_count - new_count))

        if [ $replacements -gt 0 ]; then
            mv "$tmp_file" "$file"
            total_files=$((total_files + 1))
            total_replacements=$((total_replacements + replacements))
            echo "  ✓ 完成 ${replacements} 处替换"
        else
            rm -f "$tmp_file"
            echo "  - 无需替换"
        fi
    fi
done

echo "======================================="
echo "修复完成!"
echo ""
echo "请验证修复结果:"
echo "  git diff README.md | head -50"
echo "  git diff README_zh.md | head -50"
echo ""

# 检查是否还有遗漏
remaining=$(find . -name "*.md" -type f ! -path "*/backups/*" ! -name "*.bak" -exec grep -l "/ccc:" {} \; 2>/dev/null | wc -l | tr -d ' ')
if [ "$remaining" -gt 0 ]; then
    echo "⚠️  警告: 仍有 ${remaining} 个文件包含 /ccc: 引用"
    echo "运行以下命令查看:"
    echo "  grep -r '/ccc:' --include='*.md' . | grep -v backups"
else
    echo "✅ 所有 /ccc: 引用已修复!"
fi
