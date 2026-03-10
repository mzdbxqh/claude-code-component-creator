#!/bin/bash
# 批量复制 commands/*.md 到 skills/cmd-*/SKILL.md

set -e

BASE_DIR="/Users/mzdbxqh/source/component-creator-parent/claude-code-component-creator"
cd "$BASE_DIR"

# 定义文件映射关系（原文件名 -> 目标目录名）
declare -A FILE_MAP=(
  ["build.md"]="cmd-build"
  ["design.md"]="cmd-design"
  ["design-iterate.md"]="cmd-design-iterate"
  ["design-new.md"]="cmd-design-new"
  ["diff.md"]="cmd-diff"
  ["fix.md"]="cmd-fix"
  ["implement.md"]="cmd-implement"
  ["init.md"]="cmd-init"
  ["iterate.md"]="cmd-iterate"
  ["quick.md"]="cmd-quick"
  ["review.md"]="cmd-review"
  ["review-migration-plan.md"]="cmd-review-migration-plan"
  ["review-workflow.md"]="cmd-review-workflow"
  ["status.md"]="cmd-status"
  ["status-graph.md"]="cmd-status-graph"
  ["status-trace.md"]="cmd-status-trace"
  ["test-sandbox.md"]="cmd-test-sandbox"
  ["trace.md"]="cmd-trace"
  ["validate.md"]="cmd-validate"
)

# 复制文件
for source_file in "${!FILE_MAP[@]}"; do
  target_dir="${FILE_MAP[$source_file]}"
  echo "复制: commands/$source_file -> skills/$target_dir/SKILL.md"
  cp "commands/$source_file" "skills/$target_dir/SKILL.md"
done

echo "✅ 文件复制完成"
