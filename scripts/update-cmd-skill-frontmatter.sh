#!/bin/bash
# 批量更新 skills/cmd-*/SKILL.md 的 frontmatter name 字段

set -e

BASE_DIR="/Users/mzdbxqh/source/component-creator-parent/claude-code-component-creator"
cd "$BASE_DIR/skills"

# 遍历所有 cmd-* 目录
for dir in cmd-*; do
  skill_file="$dir/SKILL.md"

  if [ ! -f "$skill_file" ]; then
    echo "⚠️  跳过: $skill_file (文件不存在)"
    continue
  fi

  # 提取原 name 字段
  old_name=$(grep "^name:" "$skill_file" | head -1 | sed 's/name: *//')

  # 生成新 name
  skill_name="${dir}"
  new_name="ccc:${skill_name}"

  echo "更新 $skill_file: $old_name -> $new_name"

  # 使用 sed 替换
  sed -i.bak "0,/^name:.*/s//name: ${new_name}/" "$skill_file"
  rm -f "${skill_file}.bak"
done

echo "✅ frontmatter 更新完成"
