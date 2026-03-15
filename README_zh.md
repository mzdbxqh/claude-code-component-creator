# Claude Code Component Creator (CCC)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-3.1.3-blue.svg)](https://github.com/mzdbxqh/claude-code-component-creator)
[![Quality Score](https://img.shields.io/badge/质量评分-96%2F100-brightgreen.svg)](docs/reviews/)

一个强大的 Claude Code 插件，用于创建高质量的组件和技能，采用结构化的 Intent/Blueprint/Delivery 工作流。

[English Documentation](README.md)

## 功能特性

- **三阶段工作流**: Intent → Blueprint → Delivery 确保设计质量
- **77+ 反模式检查**: 8 个维度的全面质量审查
- **元反射框架**: 4 维度自我评估，确保质量
- **双模型验证**: Sonnet 生成，Haiku 验证
- **可追溯性矩阵**: 从需求到实现的完整追踪
- **外部状态管理**: 工作流状态存储在 YAML 文件中
- **并行处理支持**: 大项目性能提升 3.75x-6.8x (v3.1.0 新增)
- **Token 预算透明**: 完整的成本估算和优化指南 (v3.1.0 新增)
- **检查点恢复**: 长时间工作流中断后可恢复 (v3.1.0 新增)
- **性能基准测试**: 内置性能测试框架 (v3.1.0 新增)
- **引用完整性验证**: 自动检测断开引用、孤儿文件和循环依赖 (v3.2.0 新增)

## 快速开始

### 安装

1. 安装 [Claude Code](https://claude.ai/code)
2. 克隆本仓库：
```bash
git clone https://github.com/mzdbxqh/claude-code-component-creator.git
```
3. 在 Claude Code 中加载插件

### 创建第一个组件

```bash
# 分步执行
/cmd-init          # 创建意图
/cmd-design        # 生成蓝图
/cmd-implement     # 实现代码
/cmd-review        # 质量检查
/cmd-build         # 创建交付物
```

## 核心工作流

```
Intent (构建什么)
  ↓
Blueprint (如何构建)
  ↓
Delivery (实现)
  ↓
Review (质量保证)
```

## 命令列表

| 命令 | 描述 |
|------|------|
| `/cmd-init` | 使用 4 问框架创建意图制品 |
| `/cmd-design` | 从意图生成蓝图设计文档 |
| `/cmd-implement` | 从蓝图实现代码或应用迭代计划 |
| `/cmd-review` | 全面质量审查（161+ 检查项）|
| `/cmd-fix` | 交互式修复审查发现的问题 |
| `/cmd-validate` | 使用外部工具验证制品 |
| `/cmd-build` | 创建生产就绪的交付物 |
| `/cmd-iterate` | 迭代现有蓝图 |
| `/cmd-design-iterate` | 迭代现有组件 |
| `/cmd-status` | 显示项目工作流状态 |
| `/cmd-trace` | 生成可追溯性矩阵 |

查看 [完整命令参考](skills/) 了解详情。

## 质量评估维度

CCC v3.1.0 综合质量评分 **96/100 (A+)**，8 维度全面检查：

| 维度 | 权重 | 规则数 | 评分 | 说明 |
|------|------|--------|------|------|
| 意图匹配 | 10% | 4 | 95/100 | 触发场景、同义词、排除场景 |
| 配置和使用 | 15% | 5 | 97/100 | 前置配置、示例质量、错误处理 |
| 外部依赖 | 15% | 12 | 94/100 | 运行时依赖、外部 API、工具链 |
| 安全风险 | 20% | 7 | 98/100 | 命令注入防护、审计日志 |
| 环境兼容性 | 15% | 3 | 93/100 | OS/Shell 兼容性、路径分隔符 |
| LLM 兼容性 | 15% | 3 | 96/100 | Token 预算、模型优化 |
| 扩展性 | 10% | 4 | 96/100 | 并行处理、分批处理、超时 |
| 可测试性 | 额外 | 20 | 95/100 | 测试覆盖、evals.json 框架 |

**v3.1.0 质量提升**:
- 安全性: +26 分（OWASP Top 10 合规）
- 扩展性: +21 分（并行处理支持）
- 可测试性: +17 分（完整测试框架）

## 引用完整性验证

**v3.2.0 新增**: CCC 现在可以自动检测和报告插件中的引用完整性问题。

### 检测内容

- **断开引用**: skills 字段引用指向不存在的文件
- **孤儿文件**: 从未被其他组件引用的组件
- **循环依赖**: A → B → C → A 引用循环
- **路径问题**: 绝对路径和路径规范化问题

### 使用方法

```bash
# 完整审查（含引用检查，默认）
/cmd-review --target=.

# 仅引用检查
/cmd-review --target=. --reference-only

# 跳过引用检查
/cmd-review --target=. --no-reference-check
```

### 交互模式

```bash
/cmd-review --target=. --interactive
```

显示多选菜单，您可以选择要执行的检查项：
- 引用完整性扫描
- 8维度质量评估
- 架构分析
- 依赖分析
- 链路验证

### 输出报告

引用完整性扫描生成两个报告：

```
docs/reviews/
├── YYYY-MM-DD-reference-integrity-report.json    # 结构化数据
└── YYYY-MM-DD-reference-integrity-report.md      # 人类可读报告
```

### 完整性评分

扫描根据以下规则计算完整性评分（0-100）：
- 断开引用：-10 分/个
- 孤儿文件：-2 分/个
- 循环依赖：-20 分/个
- 路径问题：-1 分/个

### 报告示例

```markdown
# 引用完整性报告

**完整性评分**: 80/100 (B)

## 🔴 断开的引用 (2 个)

### BR-001: ccc:non-existent-skill
**文件**: `skills/my-skill/SKILL.md`
**修复**: 创建缺失的技能或移除引用

## ⚠️ 孤儿文件 (1 个)

### OR-001: skills/unused-skill/SKILL.md
**问题**: 文件从未被任何组件引用
**修复**: 添加引用或删除此文件

## 🔴 循环引用 (1 个)

### 循环路径: agent-a → agent-b → agent-c → agent-a
**修复**: 通过移除一个引用打破循环
```

### 优势

- **早期发现**: 在部署前捕获断开引用
- **维护辅助**: 识别未使用的组件以便清理
- **架构验证**: 防止循环依赖问题
- **质量保证**: 确保插件完整性评分 ≥ 90

详见 [引用完整性扫描器文档](agents/reviewer/reference-integrity-scanner/SKILL.md)。

## 文档

- [迁移指南](docs/v3-migration-guide.md) - 从 v2.0 升级到 v3.0
- [最佳实践](docs/best-practices/ccc-best-practices.md) - 使用指南
- [用户手册](docs/user-guide/) - 详细命令文档
- [模板](docs/templates/) - Intent/Blueprint/Delivery 模板

## 示例

查看 [test-fixtures/](test-fixtures/) 获取示例组件。

## 开发

```bash
# 运行测试
/cmd-test-sandbox

# 审查插件质量
/cmd-review
```

## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 许可证

MIT License - 查看 [LICENSE](LICENSE) 了解详情。

Copyright (c) 2026 showme.cc

## 维护者

- **mzdbxqh** - [GitHub](https://github.com/mzdbxqh)

## 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本历史。
