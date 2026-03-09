---
name: code-reviewer
description: 当用户请求Python、JavaScript或Java代码审查时，执行静态分析和风格检查
version: 1.0.0
context: fork
model: sonnet
allowed-tools:
  - Read
  - Grep
---

# 代码审查工具

专业的代码质量检查工具，支持多种编程语言。

## 工作流程

1. 读取目标代码文件
2. 执行静态分析
3. 检查代码风格
4. 生成审查报告

## 示例

### 示例1: 审查单个文件

**输入**: "请审查 src/main.py"

**输出**: 
```
代码审查报告：
- 发现 2 个问题
- 建议修复...
```

### 示例2: 审查整个目录

**输入**: "审查 src/ 目录下的所有 Python 文件"

**输出**: 审查报告列表

## 常见陷阱

1. **大型项目超时** - 对于超过 100 个文件的项目，建议分批审查
2. **编码问题** - 确保文件使用 UTF-8 编码
3. **权限问题** - 需要读取权限

## 测试

运行以下命令测试：
```bash
# 测试基础功能
echo "请审查 examples/test.py" | claude
```
