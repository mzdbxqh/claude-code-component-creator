#!/bin/bash

# SH-QUAL-002: 缺少错误处理 (无 set -e)

# SH-QUAL-006: 硬编码路径
LOG_FILE="/var/log/myapp.log"
DATA_DIR="/opt/myapp/data"

# SH-SEC-001: eval 命令注入
user_input="$1"
eval "$user_input"

# SH-SEC-002: 路径遍历
user_path="$2"
cd "$user_path"

# SH-SEC-003: 未引用变量
file_to_delete="$3"
rm -rf $file_to_delete

# SH-SEC-007: 危险的 rm -rf 使用变量
cleanup_dir="$4"
rm -rf /$cleanup_dir/*

# SH-SEC-005: 不安全的临时文件
tmpfile="/tmp/myapp.tmp"
echo "data" > $tmpfile

# SH-SEC-006: sudo 使用
sudo systemctl restart myapp

# SH-QUAL-003: 脚本会过长,这里只是示例
# 实际测试时会生成 >200 行

echo "Done"
