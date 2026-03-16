#!/bin/bash
# checkpoint 更新脚本单元测试

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# 创建隔离的测试目录
TEST_DIR="$(mktemp -d)"
trap "rm -rf \"$TEST_DIR\"" EXIT

WORK_DIR="$TEST_DIR/work"
mkdir -p "$WORK_DIR"
mkdir -p "$WORK_DIR/.checkpoints"

cd "$WORK_DIR"

echo "运行 checkpoint-update 测试，工作目录: $(pwd)"

# 初始化测试事务
echo ""
echo "准备: 初始化测试事务"
bash "$SCRIPT_DIR/init-transaction.sh" review review-20260316-143022 test-component >/dev/null

# 测试用例 1: 更新步骤
echo ""
echo "测试 1: 更新当前步骤"
result=$(bash "$SCRIPT_DIR/update-checkpoint.sh" review-20260316-143022 5 '{"reviews_completed":10}')
if [[ ! "$result" =~ "success" ]]; then
    echo "FAIL: 应该成功更新 checkpoint"
    exit 1
fi

current_step=$(jq -r '.current_step' .checkpoints/review-20260316-143022.json)
if [[ "$current_step" != "5" ]]; then
    echo "FAIL: 步骤应该更新为 5，实际: $current_step"
    exit 1
fi

echo "PASS: 更新步骤成功"

# 测试用例 2: 统计信息合并
echo ""
echo "测试 2: 统计信息合并"
result=$(bash "$SCRIPT_DIR/update-checkpoint.sh" review-20260316-143022 6 '{"reviews_completed":5,"errors_found":2}')
if [[ ! "$result" =~ "success" ]]; then
    echo "FAIL: 应该成功更新统计信息"
    exit 1
fi

# 验证统计信息已合并（jq 中 + 对对象进行合并，后面的值覆盖前面的）
statistics=$(jq '.statistics' .checkpoints/review-20260316-143022.json)
reviews_completed=$(echo "$statistics" | jq -r '.reviews_completed // 0')
errors_found=$(echo "$statistics" | jq -r '.errors_found // 0')

if [[ "$reviews_completed" != "5" ]]; then
    echo "FAIL: 统计信息应合并更新，期望 reviews_completed=5，实际: $reviews_completed"
    exit 1
fi

if [[ "$errors_found" != "2" ]]; then
    echo "FAIL: 新的统计字段应添加，期望 errors_found=2，实际: $errors_found"
    exit 1
fi

echo "PASS: 统计信息合并成功"

# 测试用例 3: 多次更新步骤
echo ""
echo "测试 3: 多次更新步骤（序列更新）"
for step in 7 8 9 10; do
    result=$(bash "$SCRIPT_DIR/update-checkpoint.sh" review-20260316-143022 $step '{}')
    if [[ ! "$result" =~ "success" ]]; then
        echo "FAIL: 步骤 $step 更新失败"
        exit 1
    fi
done

final_step=$(jq -r '.current_step' .checkpoints/review-20260316-143022.json)
if [[ "$final_step" != "10" ]]; then
    echo "FAIL: 最终步骤应为 10，实际: $final_step"
    exit 1
fi

echo "PASS: 序列更新步骤成功"

# 测试用例 4: 更新不存在的 checkpoint
echo ""
echo "测试 4: 更新不存在的 checkpoint"
result=$(bash "$SCRIPT_DIR/update-checkpoint.sh" nonexistent-20260316-000000 5 '{}' 2>&1 || true)
if [[ ! "$result" =~ "Checkpoint not found" ]]; then
    echo "FAIL: 应该报告 checkpoint 不存在"
    exit 1
fi

echo "PASS: checkpoint 不存在错误处理成功"

# 测试用例 5: 无效的 JSON 统计信息
echo ""
echo "测试 5: 无效的 JSON 统计信息"
result=$(bash "$SCRIPT_DIR/update-checkpoint.sh" review-20260316-143022 11 'invalid json' 2>&1 || true)
if [[ ! "$result" =~ "Invalid JSON" ]]; then
    echo "FAIL: 应该报告无效的 JSON"
    exit 1
fi

echo "PASS: JSON 验证成功"

# 测试用例 6: 缺少必需参数
echo ""
echo "测试 6: 缺少必需参数"
result=$(bash "$SCRIPT_DIR/update-checkpoint.sh" 2>&1 || true)
if [[ ! "$result" =~ "用法:" ]]; then
    echo "FAIL: 应该输出用法信息"
    exit 1
fi

echo "PASS: 参数验证成功"

# 测试用例 7: last_updated 时间戳更新
echo ""
echo "测试 7: last_updated 时间戳更新"
before_update=$(jq -r '.last_updated' .checkpoints/review-20260316-143022.json)
sleep 1
bash "$SCRIPT_DIR/update-checkpoint.sh" review-20260316-143022 12 '{"timestamp_test":true}' >/dev/null
after_update=$(jq -r '.last_updated' .checkpoints/review-20260316-143022.json)

if [[ "$before_update" == "$after_update" ]]; then
    echo "FAIL: last_updated 应该在每次更新时改变"
    exit 1
fi

echo "PASS: last_updated 时间戳更新成功"

# 测试用例 8: 保持现有统计信息
echo ""
echo "测试 8: 保持现有统计信息（对象合并测试）"
# 设置初始统计
bash "$SCRIPT_DIR/update-checkpoint.sh" review-20260316-143022 13 '{"count":10,"total":100}' >/dev/null

# 再次更新，添加新的统计字段
bash "$SCRIPT_DIR/update-checkpoint.sh" review-20260316-143022 14 '{"average":10}' >/dev/null

# 验证所有统计字段都保留（jq 的 + 对对象进行合并）
statistics=$(jq '.statistics' .checkpoints/review-20260316-143022.json)
count=$(echo "$statistics" | jq -r '.count // 0')
total=$(echo "$statistics" | jq -r '.total // 0')
average=$(echo "$statistics" | jq -r '.average // 0')

if [[ "$count" != "10" || "$total" != "100" || "$average" != "10" ]]; then
    echo "FAIL: 统计信息未正确保留和合并"
    echo "  count: $count (期望: 10)"
    echo "  total: $total (期望: 100)"
    echo "  average: $average (期望: 10)"
    exit 1
fi

echo "PASS: 统计信息对象合并成功"

# 测试用例 9: 大型统计对象处理
echo ""
echo "测试 9: 大型统计对象处理"
large_stats='{"items":[1,2,3,4,5],"nested":{"a":10,"b":20},"status":"complete"}'
bash "$SCRIPT_DIR/update-checkpoint.sh" review-20260316-143022 15 "$large_stats" >/dev/null

# 验证复杂统计对象已保存
statistics=$(jq '.statistics' .checkpoints/review-20260316-143022.json)
items_length=$(echo "$statistics" | jq -r '.items | length // 0')
nested_a=$(echo "$statistics" | jq -r '.nested.a // 0')

if [[ "$items_length" != "5" || "$nested_a" != "10" ]]; then
    echo "FAIL: 大型统计对象处理失败"
    exit 1
fi

echo "PASS: 大型统计对象处理成功"

# 测试用例 10: 步骤回退（非严格递增）
echo ""
echo "测试 10: 步骤可以回退（非严格递增验证）"
current=$(jq -r '.current_step' .checkpoints/review-20260316-143022.json)
bash "$SCRIPT_DIR/update-checkpoint.sh" review-20260316-143022 10 '{"backtrack_allowed":true}' >/dev/null

new_step=$(jq -r '.current_step' .checkpoints/review-20260316-143022.json)
if [[ "$new_step" != "10" ]]; then
    echo "FAIL: 步骤回退应该被允许"
    exit 1
fi

echo "PASS: 步骤回退验证成功"

echo ""
echo "所有 checkpoint-update 测试通过"
