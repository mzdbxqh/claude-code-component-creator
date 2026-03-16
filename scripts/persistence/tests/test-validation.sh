#!/bin/bash
# checkpoint 验证脚本单元测试

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# 创建隔离的测试目录
TEST_DIR="$(mktemp -d)"
trap "rm -rf \"$TEST_DIR\"" EXIT

WORK_DIR="$TEST_DIR/work"
mkdir -p "$WORK_DIR"
mkdir -p "$WORK_DIR/.checkpoints"

cd "$WORK_DIR"

echo "运行 validation 测试，工作目录: $(pwd)"

# 初始化测试事务
echo ""
echo "准备: 初始化测试事务"
bash "$SCRIPT_DIR/init-transaction.sh" review review-20260316-143022 test-component >/dev/null

# 测试用例 1: 有效的 checkpoint 验证
echo ""
echo "测试 1: 有效的 checkpoint 验证"
result=$(bash "$SCRIPT_DIR/validate-checkpoint.sh" .checkpoints/review-20260316-143022.json)
if [[ ! "$result" =~ "validation passed" ]]; then
    echo "FAIL: 应该验证通过"
    exit 1
fi

if [[ ! "$result" =~ "review-20260316-143022" ]]; then
    echo "FAIL: 输出应包含事务 ID"
    exit 1
fi

echo "PASS: 有效的 checkpoint 验证成功"

# 测试用例 2: 不存在的 checkpoint 文件
echo ""
echo "测试 2: 不存在的 checkpoint 文件"
result=$(bash "$SCRIPT_DIR/validate-checkpoint.sh" .checkpoints/nonexistent.json 2>&1 || true)
if [[ ! "$result" =~ "checkpoint file not found" ]]; then
    echo "FAIL: 应该报告文件不存在"
    exit 1
fi

echo "PASS: 文件不存在错误处理成功"

# 测试用例 3: 无效的 JSON 格式
echo ""
echo "测试 3: 无效的 JSON 格式"
mkdir -p .checkpoints
echo "invalid json content" > .checkpoints/invalid.json
result=$(bash "$SCRIPT_DIR/validate-checkpoint.sh" .checkpoints/invalid.json 2>&1 || true)
if [[ ! "$result" =~ "invalid JSON format" ]]; then
    echo "FAIL: 应该报告 JSON 格式错误"
    exit 1
fi

echo "PASS: JSON 格式验证成功"

# 测试用例 4: 缺少必需字段
echo ""
echo "测试 4: 缺少必需字段"
# 创建缺少 transaction_id 字段的 checkpoint
jq 'del(.transaction_id)' .checkpoints/review-20260316-143022.json > .checkpoints/missing-field.json
result=$(bash "$SCRIPT_DIR/validate-checkpoint.sh" .checkpoints/missing-field.json 2>&1 || true)
if [[ ! "$result" =~ "missing required fields" ]]; then
    echo "FAIL: 应该报告缺少必需字段"
    exit 1
fi

echo "PASS: 缺少字段检测成功"

# 测试用例 5: 验证所有必需字段存在
echo ""
echo "测试 5: 验证所有必需字段存在"
required_fields=(
    "transaction_id"
    "workflow_type"
    "status"
    "current_step"
    "data_directory"
    "key_files"
)

for field in "${required_fields[@]}"; do
    # 创建缺少此字段的 checkpoint 副本
    cp .checkpoints/review-20260316-143022.json ".checkpoints/test-missing-$field.json"
    jq "del(.$field)" ".checkpoints/test-missing-$field.json" > ".checkpoints/test-missing-$field.tmp.json"
    mv ".checkpoints/test-missing-$field.tmp.json" ".checkpoints/test-missing-$field.json"

    # 验证检测失败
    result=$(bash "$SCRIPT_DIR/validate-checkpoint.sh" ".checkpoints/test-missing-$field.json" 2>&1 || true)
    if [[ ! "$result" =~ "missing required fields" ]]; then
        echo "FAIL: 应该检测到缺少字段: $field"
        exit 1
    fi
done

echo "PASS: 所有必需字段检测成功"

# 测试用例 6: 保存文件后的完整性验证
echo ""
echo "测试 6: 保存文件后的完整性验证"
test_content='{"test":"data"}'
echo "$test_content" > /tmp/test.json
bash "$SCRIPT_DIR/save-file.sh" review-20260316-143022 test_key config /tmp/test.json >/dev/null

# 验证包含已保存文件的 checkpoint
result=$(bash "$SCRIPT_DIR/validate-checkpoint.sh" .checkpoints/review-20260316-143022.json)
if [[ ! "$result" =~ "Files:" ]]; then
    echo "FAIL: 输出应包含文件计数"
    exit 1
fi

if [[ ! "$result" =~ "1" ]]; then
    echo "FAIL: 应该识别到 1 个已保存的文件"
    exit 1
fi

echo "PASS: 保存文件后的验证成功"

# 测试用例 7: 缺失的数据文件警告
echo ""
echo "测试 7: 缺失的数据文件警告"
# 手动更新 checkpoint 指向不存在的文件
jq '.key_files.missing_file = "nonexistent/file.json"' .checkpoints/review-20260316-143022.json > .checkpoints/review-20260316-143022.tmp
mv .checkpoints/review-20260316-143022.tmp .checkpoints/review-20260316-143022.json

result=$(bash "$SCRIPT_DIR/validate-checkpoint.sh" .checkpoints/review-20260316-143022.json 2>&1)
if [[ ! "$result" =~ "missing files referenced" ]]; then
    echo "FAIL: 应该警告缺失的数据文件"
    exit 1
fi

if [[ ! "$result" =~ "missing_file" ]]; then
    echo "FAIL: 警告应包含缺失文件的 key"
    exit 1
fi

echo "PASS: 缺失文件警告成功"

# 重新初始化以准备后续测试
rm -rf docs/.checkpoints
bash "$SCRIPT_DIR/init-transaction.sh" review review-20260316-143023 test-component >/dev/null

# 测试用例 8: 验证 status 字段有效值
echo ""
echo "测试 8: 验证 status 字段（应通过各种值）"
for status in "in_progress" "completed" "failed" "paused"; do
    jq --arg status "$status" '.status = $status' .checkpoints/review-20260316-143023.json > .checkpoints/review-20260316-143023.tmp
    mv .checkpoints/review-20260316-143023.tmp .checkpoints/review-20260316-143023.json

    result=$(bash "$SCRIPT_DIR/validate-checkpoint.sh" .checkpoints/review-20260316-143023.json)
    if [[ ! "$result" =~ "validation passed" ]]; then
        echo "FAIL: 应该验证通过 status=$status"
        exit 1
    fi
done

echo "PASS: 各种 status 值验证成功"

# 测试用例 9: 缺少参数
echo ""
echo "测试 9: 缺少参数"
result=$(bash "$SCRIPT_DIR/validate-checkpoint.sh" 2>&1 || true)
if [[ ! "$result" =~ "用法:" ]]; then
    echo "FAIL: 应该输出用法信息"
    exit 1
fi

echo "PASS: 参数验证成功"

# 测试用例 10: 验证摘要信息完整性
echo ""
echo "测试 10: 验证摘要信息完整性"
# 添加多个文件
for i in {1..3}; do
    echo "{\"data\":$i}" > /tmp/test-$i.json
    bash "$SCRIPT_DIR/save-file.sh" review-20260316-143023 file_$i config /tmp/test-$i.json >/dev/null
done

result=$(bash "$SCRIPT_DIR/validate-checkpoint.sh" .checkpoints/review-20260316-143023.json)

# 验证摘要包含所有信息
if [[ ! "$result" =~ "Checkpoint validation passed" ]]; then
    echo "FAIL: 应该包含验证通过消息"
    exit 1
fi

if [[ ! "$result" =~ "Transaction:" ]]; then
    echo "FAIL: 应该输出事务 ID"
    exit 1
fi

if [[ ! "$result" =~ "Status:" ]]; then
    echo "FAIL: 应该输出状态"
    exit 1
fi

if [[ ! "$result" =~ "Step:" ]]; then
    echo "FAIL: 应该输出当前步骤"
    exit 1
fi

if [[ ! "$result" =~ "Files:" ]]; then
    echo "FAIL: 应该输出文件计数"
    exit 1
fi

if [[ ! "$result" =~ "3" ]]; then
    echo "FAIL: 应该识别到 3 个已保存的文件"
    exit 1
fi

echo "PASS: 摘要信息完整性验证成功"

# 测试用例 11: 空的 key_files 对象
echo ""
echo "测试 11: 空的 key_files 对象验证"
jq '.key_files = {}' .checkpoints/review-20260316-143023.json > .checkpoints/review-20260316-143023.tmp
mv .checkpoints/review-20260316-143023.tmp .checkpoints/review-20260316-143023.json

result=$(bash "$SCRIPT_DIR/validate-checkpoint.sh" .checkpoints/review-20260316-143023.json)
if [[ ! "$result" =~ "validation passed" ]]; then
    echo "FAIL: 应该允许空的 key_files"
    exit 1
fi

if [[ ! "$result" =~ "Files: 0" ]]; then
    echo "FAIL: 应该显示文件计数为 0"
    exit 1
fi

echo "PASS: 空 key_files 验证成功"

# 测试用例 12: 验证 current_step 为数字
echo ""
echo "测试 12: 验证 current_step 为数字"
# 设置有效的数字步骤
for step in 0 1 10 100; do
    jq --argjson step "$step" '.current_step = $step' .checkpoints/review-20260316-143023.json > .checkpoints/review-20260316-143023.tmp
    mv .checkpoints/review-20260316-143023.tmp .checkpoints/review-20260316-143023.json

    result=$(bash "$SCRIPT_DIR/validate-checkpoint.sh" .checkpoints/review-20260316-143023.json)
    if [[ ! "$result" =~ "Step: $step" ]]; then
        echo "FAIL: 应该正确显示步骤 $step"
        exit 1
    fi
done

echo "PASS: current_step 数字验证成功"

echo ""
echo "所有 validation 测试通过"
