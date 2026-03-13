#!/bin/bash

# 修复遗留的错误命名空间引用
# 这些是不存在的命令，应该删除或注释掉

echo "修复遗留的错误命名空间引用..."
echo "======================================="

# 处理eval-executor引用（这是SubAgent，不是直接可调用的命令）
echo "处理 /ccc:eval-executor 引用..."
for file in docs/testing-framework.md; do
    if [ -f "$file" ]; then
        sed -i.bak \
            -e 's|/ccc:eval-executor|# /ccc:eval-executor (SubAgent - 通过 /cmd-test-sandbox 调用)|g' \
            "$file"
        rm -f "${file}.bak"
        echo "  ✓ 已处理 $file"
    fi
done

# 处理checkpoint引用（功能计划中，暂无对应命令）
echo "处理 /ccc:checkpoint 引用..."
for file in docs/checkpoint-recovery.md; do
    if [ -f "$file" ]; then
        sed -i.bak \
            -e 's|/ccc:checkpoint|# /ccc:checkpoint (计划中的功能)|g' \
            "$file"
        rm -f "${file}.bak"
        echo "  ✓ 已处理 $file"
    fi
done

# 处理benchmark引用（功能计划中，暂无对应命令）
echo "处理 /ccc:benchmark 引用..."
for file in docs/performance-benchmarking.md; do
    if [ -f "$file" ]; then
        sed -i.bak \
            -e 's|/ccc:benchmark|# /ccc:benchmark (计划中的功能)|g' \
            "$file"
        rm -f "${file}.bak"
        echo "  ✓ 已处理 $file"
    fi
done

# 处理其他错误引用
echo "处理其他错误引用..."
sed -i.bak \
    -e 's|/ccc:analyze|# /ccc:analyze (示例命令)|g' \
    ./agents/reviewer/design-new-core/SKILL.md \
    ./docs/ccc-skill-description-differentiation-plan.md
rm -f ./agents/reviewer/design-new-core/SKILL.md.bak
rm -f ./docs/ccc-skill-description-differentiation-plan.md.bak

echo "======================================="
echo "修复完成!"
echo ""

# 最终检查
remaining=$(grep -r '/ccc:' --include='*.md' . | grep -v backups | grep -v "计划中的功能" | grep -v "SubAgent" | grep -v "示例命令" | wc -l | tr -d ' ')
if [ "$remaining" -gt 0 ]; then
    echo "⚠️  仍有 ${remaining} 处 /ccc: 引用"
    grep -r '/ccc:' --include='*.md' . | grep -v backups | grep -v "计划中的功能" | grep -v "SubAgent" | grep -v "示例命令"
else
    echo "✅ 所有 /ccc: 引用已修复或标注!"
fi
