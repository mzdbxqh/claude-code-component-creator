#!/bin/bash
# CCC PreToolUse Security Check Hook
#
# 功能：在工具使用前进行安全检查
# 退出代码：
#   0 - 允许继续执行
#   1 - 阻止执行
#   2 - 警告但允许执行

# Hook 输入通过环境变量传递：
# - TOOL_NAME: 要使用的工具名称
# - TOOL_ARGS: 工具参数（JSON 格式）

set -e

TOOL_NAME="${TOOL_NAME:-unknown}"
TOOL_ARGS="${TOOL_ARGS:-{}}"

# 日志函数
log_info() {
    echo "[INFO] PreToolUse Hook: $1" >&2
}

log_warn() {
    echo "[WARN] PreToolUse Hook: $1" >&2
}

log_error() {
    echo "[ERROR] PreToolUse Hook: $1" >&2
}

# 安全检查：危险操作检测
check_dangerous_operations() {
    case "$TOOL_NAME" in
        "Bash")
            # 检查是否包含危险命令
            if echo "$TOOL_ARGS" | grep -qE "rm -rf /|dd if=|mkfs|format|:(){ :|:& };:"; then
                log_error "检测到危险 Bash 命令: $TOOL_ARGS"
                return 1
            fi
            ;;
        "Write"|"Edit")
            # 检查是否修改关键文件
            if echo "$TOOL_ARGS" | grep -qE "/etc/|/sys/|/proc/|\.ssh/|credentials"; then
                log_warn "正在修改敏感文件路径"
                return 2
            fi
            ;;
    esac
    return 0
}

# 执行安全检查
log_info "检查工具: $TOOL_NAME"

if check_dangerous_operations; then
    log_info "安全检查通过"
    exit 0
else
    exit_code=$?
    if [ $exit_code -eq 2 ]; then
        log_warn "安全警告，但允许继续"
        exit 2
    else
        log_error "安全检查失败，阻止执行"
        exit 1
    fi
fi
