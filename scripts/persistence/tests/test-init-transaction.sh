#!/bin/bash
# 初始化事务脚本单元测试

set -euo pipefail

# 获取脚本路径
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# 创建隔离的测试目录
TEST_DIR="$(mktemp -d)"
trap "rm -rf \"$TEST_DIR\"" EXIT

# 创建工作目录
WORK_DIR="$TEST_DIR/work"
mkdir -p "$WORK_DIR"
mkdir -p "$WORK_DIR/.checkpoints"

cd "$WORK_DIR"

echo "运行 init-transaction 测试，工作目录: $(pwd)"

# 测试用例 1: 正常初始化
echo ""
echo "测试 1: 正常初始化事务"
result=$(bash "$SCRIPT_DIR/init-transaction.sh" review review-20260316-143022 review-aggregator)
if [[ ! "$result" =~ "success" ]]; then
    echo "FAIL: 应该成功初始化事务"
    echo "Result: $result"
    exit 1
fi

if [[ ! -f ".checkpoints/review-20260316-143022.json" ]]; then
    echo "FAIL: checkpoint 文件未创建"
    exit 1
fi

if [[ ! -d "docs/review-20260316-143022/review-aggregator" ]]; then
    echo "FAIL: 数据目录未创建"
    exit 1
fi

# 验证 checkpoint 内容
checkpoint_content=$(cat .checkpoints/review-20260316-143022.json)
if [[ ! "$checkpoint_content" =~ "review-20260316-143022" ]]; then
    echo "FAIL: checkpoint 文件内容不正确"
    exit 1
fi

if [[ ! "$checkpoint_content" =~ '"status"' ]] || [[ ! "$checkpoint_content" =~ '"in_progress"' ]]; then
    echo "FAIL: 初始状态应为 in_progress"
    exit 1
fi

echo "PASS: 正常初始化成功"

# 测试用例 2: 重复初始化检测
echo ""
echo "测试 2: 重复初始化检测"
result2=$(bash "$SCRIPT_DIR/init-transaction.sh" review review-20260316-143022 review-aggregator 2>&1 || true)
if [[ ! "$result2" =~ "already exists" ]]; then
    echo "FAIL: 应该检测到重复的事务"
    echo "Result: $result2"
    exit 1
fi

echo "PASS: 重复初始化检测成功"

# 测试用例 3: 使用默认 component_name（缺少第三个参数）
echo ""
echo "测试 3: 使用默认 component_name"
result3=$(bash "$SCRIPT_DIR/init-transaction.sh" design design-20260316-150000)
if [[ ! "$result3" =~ "success" ]]; then
    echo "FAIL: 应该成功初始化事务（使用默认参数）"
    exit 1
fi

if [[ ! -d "docs/design-20260316-150000/design" ]]; then
    echo "FAIL: 应使用 workflow_type 作为默认的 component_name"
    exit 1
fi

echo "PASS: 默认 component_name 设置成功"

# 测试用例 4: 无效的 component_name（包含路径分隔符）
echo ""
echo "测试 4: 无效的 component_name 验证"
result4=$(bash "$SCRIPT_DIR/init-transaction.sh" review review-20260316-160000 "invalid/name" 2>&1 || true)
if [[ ! "$result4" =~ "Invalid component_name" ]]; then
    echo "FAIL: 应该拒绝包含路径分隔符的 component_name"
    exit 1
fi

echo "PASS: 无效 component_name 验证成功"

# 测试用例 5: 缺少必需参数
echo ""
echo "测试 5: 缺少必需参数"
result5=$(bash "$SCRIPT_DIR/init-transaction.sh" 2>&1 || true)
if [[ ! "$result5" =~ "用法:" ]]; then
    echo "FAIL: 应该输出用法信息"
    exit 1
fi

echo "PASS: 参数验证成功"

# 测试用例 6: 无效的事务 ID 格式
echo ""
echo "测试 6: 无效的事务 ID 格式"
result6=$(bash "$SCRIPT_DIR/init-transaction.sh" review invalid-transaction-id 2>&1 || true)
if [[ ! "$result6" =~ "Invalid transaction ID format" ]]; then
    echo "FAIL: 应该拒绝无效的事务 ID 格式"
    exit 1
fi

echo "PASS: 事务 ID 格式验证成功"

# 测试用例 7: checkpoint 文件内容结构验证
echo ""
echo "测试 7: checkpoint JSON 结构验证"
checkpoint_file=".checkpoints/review-20260316-143022.json"
required_fields=("version" "transaction_id" "workflow_type" "component_name" "status" "current_step" "created_at" "last_updated" "data_directory" "key_files" "statistics")

for field in "${required_fields[@]}"; do
    if ! jq -e ".$field" "$checkpoint_file" >/dev/null 2>&1; then
        echo "FAIL: checkpoint 缺少必需字段: $field"
        exit 1
    fi
done

echo "PASS: checkpoint JSON 结构验证成功"

# 测试用例 8: 全局注册表更新检查
echo ""
echo "测试 8: 全局注册表更新检查"
if [[ ! -f ".checkpoints/registry.json" ]]; then
    echo "FAIL: 应该创建全局注册表"
    exit 1
fi

if ! jq -e '.transactions[] | select(.transaction_id == "review-20260316-143022")' ".checkpoints/registry.json" >/dev/null 2>&1; then
    echo "FAIL: 注册表应包含新初始化的事务"
    exit 1
fi

echo "PASS: 全局注册表更新成功"

echo ""
echo "所有 init-transaction 测试通过"
