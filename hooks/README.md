# CCC Hooks 配置文档

## 概述

CCC 使用 Hooks 机制在关键执行点进行安全检查和流程控制。本文档说明 CCC 的 Hooks 配置和使用方法。

## 配置文件

**位置**: `hooks/hooks.json`

**格式**:
```json
{
  "hooks": [
    {
      "event": "PreToolUse",
      "script": "hooks/scripts/security-check.sh",
      "timeout": 5000,
      "description": "安全检查：验证工具使用是否符合最小权限原则"
    }
  ]
}
```

## 支持的事件类型

根据 Claude Code 官方规范 (markdown_docs/hooks.md)：

| 事件类型 | 触发时机 | 用途 |
|---------|---------|------|
| `PreToolUse` | 工具使用前 | 安全检查、权限验证 |
| `PostToolUse` | 工具使用后 | 日志记录、结果验证 |
| `prompt` | Prompt 修改 | 提示词预处理 |
| `agent` | SubAgent 行为修改 | Agent 行为控制 |
| `SubagentStart` | SubAgent 启动时 | 初始化检查 |
| `SubagentStop` | SubAgent 停止时 | 清理和日志 |

## 退出代码语义

Hook 脚本使用标准退出代码：

- **0**: 成功，继续执行
- **1**: 失败，中止执行
- **2**: 警告，继续执行但记录

## 当前实现的 Hooks

### 1. PreToolUse 安全检查

**脚本**: `hooks/scripts/security-check.sh`
**功能**:
- 检测危险 Bash 命令（rm -rf /、dd、mkfs 等）
- 检测敏感文件修改（/etc/、.ssh/、credentials 等）
- 根据风险级别返回相应退出代码

**环境变量**:
- `TOOL_NAME`: 要使用的工具名称
- `TOOL_ARGS`: 工具参数（JSON 格式）

**示例输出**:
```
[INFO] PreToolUse Hook: 检查工具: Bash
[INFO] PreToolUse Hook: 安全检查通过
```

或

```
[ERROR] PreToolUse Hook: 检测到危险 Bash 命令: rm -rf /
[ERROR] PreToolUse Hook: 安全检查失败，阻止执行
```

## 使用示例

### 测试 Hook

```bash
# 测试安全检查 Hook
export TOOL_NAME="Bash"
export TOOL_ARGS='{"command": "ls -la"}'
hooks/scripts/security-check.sh
echo "退出代码: $?"  # 应该是 0

# 测试危险命令检测
export TOOL_ARGS='{"command": "rm -rf /"}'
hooks/scripts/security-check.sh
echo "退出代码: $?"  # 应该是 1
```

### 扩展 Hooks

要添加新的 Hook：

1. 创建脚本文件：`hooks/scripts/your-hook.sh`
2. 设置执行权限：`chmod +x hooks/scripts/your-hook.sh`
3. 更新配置：在 `hooks/hooks.json` 中添加条目
4. 测试 Hook 功能

## 最佳实践

1. **超时设置**: 所有 Hooks 应设置合理的 timeout（建议 5000ms）
2. **错误处理**: Hook 脚本应有完善的错误处理
3. **日志记录**: 使用 stderr 输出日志信息
4. **权限最小化**: Hook 脚本仅需要执行权限，不需要其他权限
5. **幂等性**: Hook 多次执行应产生相同结果
6. **快速执行**: Hook 应快速完成，避免阻塞主流程

## 安全考虑

1. **脚本安全**: Hook 脚本应避免执行不可信输入
2. **路径验证**: 验证所有文件路径，防止路径遍历攻击
3. **输入过滤**: 过滤危险字符和命令
4. **日志隐私**: 避免在日志中记录敏感信息

## 故障排除

### Hook 未执行

检查：
1. `hooks/hooks.json` 格式是否正确
2. 脚本路径是否正确
3. 脚本是否有执行权限
4. 事件类型是否拼写正确

### Hook 执行失败

检查：
1. 脚本退出代码是否正确
2. 超时设置是否合理
3. 环境变量是否正确传递
4. 脚本日志输出（stderr）

## 参考

- **官方文档**: markdown_docs/hooks.md
- **CCC 安全实践**: docs/SECURITY.md（待创建）
- **审查报告**: docs/reviews/2026-03-11-ccc-official-compliance/03-hooks-plugin-compliance.md

---

**文档版本**: v1.0
**最后更新**: 2026-03-11
**维护者**: CCC Team
