#!/bin/bash
# 文件保存和加载脚本单元测试

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# 创建隔离的测试目录
TEST_DIR="$(mktemp -d)"
trap "rm -rf \"$TEST_DIR\"" EXIT

WORK_DIR="$TEST_DIR/work"
mkdir -p "$WORK_DIR"
mkdir -p "$WORK_DIR/.checkpoints"

cd "$WORK_DIR"

echo "运行 save-load 测试，工作目录: $(pwd)"

# 初始化测试事务
echo ""
echo "准备: 初始化测试事务"
bash "$SCRIPT_DIR/init-transaction.sh" review review-20260316-143022 test-component >/dev/null

# 测试用例 1: 正常保存文件
echo ""
echo "测试 1: 正常保存文件"
test_content='{"test":"data","value":123}'
echo "$test_content" > /tmp/test-config.json

result=$(bash "$SCRIPT_DIR/save-file.sh" review-20260316-143022 test_list config /tmp/test-config.json)
if [[ ! "$result" =~ "success" ]]; then
    echo "FAIL: 应该成功保存文件"
    exit 1
fi

if [[ ! -f "docs/review-20260316-143022/test-component/test_list.json" ]]; then
    echo "FAIL: 文件未保存到正确位置"
    exit 1
fi

if ! diff -q /tmp/test-config.json "docs/review-20260316-143022/test-component/test_list.json" >/dev/null; then
    echo "FAIL: 保存的文件内容不正确"
    exit 1
fi

echo "PASS: 正常保存文件成功"

# 测试用例 2: 保存到子目录
echo ""
echo "测试 2: 保存文件到子目录"
test_content2='{"type":"intermediate","step":5}'
echo "$test_content2" > /tmp/test-results.json

result=$(bash "$SCRIPT_DIR/save-file.sh" review-20260316-143022 review_results intermediate-result /tmp/test-results.json review-results)
if [[ ! "$result" =~ "success" ]]; then
    echo "FAIL: 应该成功保存文件到子目录"
    exit 1
fi

if [[ ! -f "docs/review-20260316-143022/test-component/review-results/review_results-results.json" ]]; then
    echo "FAIL: 文件未保存到子目录"
    exit 1
fi

echo "PASS: 保存文件到子目录成功"

# 测试用例 3: 保存不存在的文件
echo ""
echo "测试 3: 保存不存在的文件错误处理"
result=$(bash "$SCRIPT_DIR/save-file.sh" review-20260316-143022 nonexistent config /tmp/nonexistent-file.json 2>&1 || true)
if [[ ! "$result" =~ "Content file not found" ]]; then
    echo "FAIL: 应该报告文件不存在错误"
    exit 1
fi

echo "PASS: 文件不存在错误处理成功"

# 测试用例 4: 保存到不存在的事务
echo ""
echo "测试 4: 保存到不存在的事务"
echo '{"test":"data"}' > /tmp/test-file.json
result=$(bash "$SCRIPT_DIR/save-file.sh" nonexistent-20260316-000000 test_key config /tmp/test-file.json 2>&1 || true)
if [[ ! "$result" =~ "Checkpoint not found" ]]; then
    echo "FAIL: 应该报告 checkpoint 不存在"
    exit 1
fi

echo "PASS: 事务不存在错误处理成功"

# 测试用例 5: 加载已保存的文件
echo ""
echo "测试 5: 加载已保存的文件"
loaded_content=$(bash "$SCRIPT_DIR/load-file.sh" review-20260316-143022 test_list)
if [[ ! "$loaded_content" =~ "test" ]]; then
    echo "FAIL: 加载的内容不正确"
    exit 1
fi

if [[ "$loaded_content" != "$test_content" ]]; then
    echo "FAIL: 加载的内容与保存的内容不一致"
    exit 1
fi

echo "PASS: 加载已保存文件成功"

# 测试用例 6: 加载子目录中的文件
echo ""
echo "测试 6: 加载子目录中的文件"
loaded_content2=$(bash "$SCRIPT_DIR/load-file.sh" review-20260316-143022 review_results)
if [[ ! "$loaded_content2" =~ "intermediate" ]]; then
    echo "FAIL: 加载的子目录文件内容不正确"
    exit 1
fi

if [[ "$loaded_content2" != "$test_content2" ]]; then
    echo "FAIL: 加载的子目录文件内容与保存的不一致"
    exit 1
fi

echo "PASS: 加载子目录文件成功"

# 测试用例 7: 加载不存在的 key
echo ""
echo "测试 7: 加载不存在的 key"
result=$(bash "$SCRIPT_DIR/load-file.sh" review-20260316-143022 nonexistent_key 2>&1 || true)
if [[ ! "$result" =~ "not found in checkpoint" ]]; then
    echo "FAIL: 应该报告 key 不存在"
    exit 1
fi

echo "PASS: key 不存在错误处理成功"

# 测试用例 8: 加载从不存在的事务
echo ""
echo "测试 8: 加载从不存在的事务"
result=$(bash "$SCRIPT_DIR/load-file.sh" nonexistent-20260316-000000 test_key 2>&1 || true)
if [[ ! "$result" =~ "checkpoint not found" ]]; then
    echo "FAIL: 应该报告 checkpoint 不存在"
    exit 1
fi

echo "PASS: 事务不存在错误处理成功"

# 测试用例 9: checkpoint 更新验证
echo ""
echo "测试 9: checkpoint 更新验证"
checkpoint_content=$(cat .checkpoints/review-20260316-143022.json)
if ! jq -e '.key_files | keys[]' .checkpoints/review-20260316-143022.json >/dev/null 2>&1; then
    echo "FAIL: checkpoint 应该包含保存的文件信息"
    exit 1
fi

saved_keys=$(jq -r '.key_files | keys | length' .checkpoints/review-20260316-143022.json)
if [[ "$saved_keys" != "2" ]]; then
    echo "FAIL: checkpoint 应该记录 2 个文件，实际: $saved_keys"
    exit 1
fi

echo "PASS: checkpoint 更新验证成功"

# 测试用例 10: 多次保存相同 key（覆盖）
echo ""
echo "测试 10: 多次保存相同 key（覆盖测试）"
new_content='{"test":"updated","version":2}'
echo "$new_content" > /tmp/test-config-updated.json

bash "$SCRIPT_DIR/save-file.sh" review-20260316-143022 test_list config /tmp/test-config-updated.json >/dev/null

loaded_updated=$(bash "$SCRIPT_DIR/load-file.sh" review-20260316-143022 test_list)
if [[ "$loaded_updated" != "$new_content" ]]; then
    echo "FAIL: 覆盖后的文件内容应该更新"
    exit 1
fi

echo "PASS: 多次保存相同 key 成功"

echo ""
echo "所有 save-load 测试通过"
