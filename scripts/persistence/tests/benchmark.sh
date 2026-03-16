#!/bin/bash
# 性能基准测试
#
# 用法: bash scripts/persistence/tests/benchmark.sh
# 目的: 测试持久化脚本的性能，验证目标延迟指标
#
# 性能目标:
# - init-transaction: <100ms/事务
# - save-file: <50ms/文件
# - load-file: <30ms/文件
# - update-checkpoint: <20ms/更新

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEST_DIR="$(mktemp -d)"
cd "$TEST_DIR"

echo "=== Persistence Performance Benchmark ==="
echo "测试目录: $TEST_DIR"
echo ""

# 测试 1: 初始化事务性能
echo "Test 1: init-transaction throughput"
echo "初始化 100 个事务..."
start=$(date +%s)
success_count=0
failed_count=0
for i in {0..99}; do
    # 生成唯一的事务 ID（offset 秒后的时间戳）
    base_time=$(date +%s)
    unique_time=$((base_time + i))
    tx_id="review-$(date -r $unique_time +%Y%m%d-%H%M%S)"

    if bash "$SCRIPT_DIR/init-transaction.sh" review "$tx_id" test-component >/dev/null 2>&1; then
        ((success_count++))
    else
        ((failed_count++))
    fi
done
end=$(date +%s)
elapsed_s=$(( end - start ))
elapsed_ms=$(( elapsed_s * 1000 ))
if [[ $success_count -gt 0 ]]; then
    avg_ms=$(( elapsed_ms / success_count ))
else
    avg_ms=0
fi
echo "总耗时: ${elapsed_ms}ms，平均: ${avg_ms}ms/事务 (成功: $success_count/100，失败: $failed_count)"
echo "目标: <100ms/事务"
if [[ $avg_ms -lt 100 ]] && [[ $success_count -ge 90 ]]; then
    echo "✅ PASS"
else
    echo "⚠️  SLOW / FAILED"
fi
echo ""

# 选择一个事务用于后续测试
if [[ $success_count -eq 0 ]]; then
    echo "错误: 无法初始化任何事务，跳过后续测试"
    cd /
    rm -rf "$TEST_DIR"
    echo "基准测试完成 (初始化阶段失败)"
    exit 1
fi

bench_save_tx="review-$(date -r $(($(date +%s) + 100)) +%Y%m%d-%H%M%S)"
bash "$SCRIPT_DIR/init-transaction.sh" review "$bench_save_tx" test-component >/dev/null 2>&1 || true

# 测试 2: 保存小文件性能（100 个 1KB 文件）
echo "Test 2: save-file throughput (1KB files)"
echo '{"data":"test","value":123}' > /tmp/bench-data.json

echo "保存 100 个文件..."
start=$(date +%s)
save_success=0
for i in {1..100}; do
    if bash "$SCRIPT_DIR/save-file.sh" "$bench_save_tx" key-$i config /tmp/bench-data.json >/dev/null 2>&1; then
        ((save_success++))
    fi
done
end=$(date +%s)
elapsed_s=$(( end - start ))
elapsed_ms=$(( elapsed_s * 1000 ))
if [[ $save_success -gt 0 ]]; then
    avg_ms=$(( elapsed_ms / save_success ))
else
    avg_ms=0
fi
echo "总耗时: ${elapsed_ms}ms，平均: ${avg_ms}ms/文件 (成功: $save_success/100)"
echo "目标: <50ms/文件"
if [[ $avg_ms -lt 50 ]] && [[ $save_success -ge 90 ]]; then
    echo "✅ PASS"
else
    echo "⚠️  SLOW"
fi
echo ""

# 测试 3: 加载文件性能
echo "Test 3: load-file throughput"
echo "加载 100 个文件..."
start=$(date +%s)
load_success=0
for i in {1..100}; do
    if bash "$SCRIPT_DIR/load-file.sh" "$bench_save_tx" key-$i >/dev/null 2>&1; then
        ((load_success++))
    fi
done
end=$(date +%s)
elapsed_s=$(( end - start ))
elapsed_ms=$(( elapsed_s * 1000 ))
if [[ $load_success -gt 0 ]]; then
    avg_ms=$(( elapsed_ms / load_success ))
else
    avg_ms=0
fi
echo "总耗时: ${elapsed_ms}ms，平均: ${avg_ms}ms/文件 (成功: $load_success/100)"
echo "目标: <30ms/文件"
if [[ $avg_ms -lt 30 ]] && [[ $load_success -ge 90 ]]; then
    echo "✅ PASS"
else
    echo "⚠️  SLOW"
fi
echo ""

# 测试 4: checkpoint 更新性能
echo "Test 4: update-checkpoint throughput"
echo "更新 checkpoint 100 次..."
start=$(date +%s)
update_success=0
for i in {1..100}; do
    if bash "$SCRIPT_DIR/update-checkpoint.sh" "$bench_save_tx" $i '{"count":'$i'}' >/dev/null 2>&1; then
        ((update_success++))
    fi
done
end=$(date +%s)
elapsed_s=$(( end - start ))
elapsed_ms=$(( elapsed_s * 1000 ))
if [[ $update_success -gt 0 ]]; then
    avg_ms=$(( elapsed_ms / update_success ))
else
    avg_ms=0
fi
echo "总耗时: ${elapsed_ms}ms，平均: ${avg_ms}ms/更新 (成功: $update_success/100)"
echo "目标: <20ms/更新"
if [[ $avg_ms -lt 20 ]] && [[ $update_success -ge 90 ]]; then
    echo "✅ PASS"
else
    echo "⚠️  SLOW"
fi
echo ""

# 清理
cd /
rm -rf "$TEST_DIR"
rm -f /tmp/bench-data.json

echo "基准测试完成"
