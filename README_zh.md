# Claude Code Component Creator (CCC)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)](https://github.com/mzdbxqh/claude-code-component-creator)

一个强大的 Claude Code 插件，用于创建高质量的组件和技能，采用结构化的 Intent/Blueprint/Delivery 工作流。

[English Documentation](README.md)

## 功能特性

- **三阶段工作流**: Intent → Blueprint → Delivery 确保设计质量
- **76+ 反模式检查**: 8 个维度的全面质量审查
- **元反射框架**: 4 维度自我评估，确保质量
- **双模型验证**: Sonnet 生成，Haiku 验证
- **可追溯性矩阵**: 从需求到实现的完整追踪
- **外部状态管理**: 工作流状态存储在 YAML 文件中

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
# 一键完整工作流
/ccc:quick

# 或分步执行
/ccc:init          # 创建意图
/ccc:design        # 生成蓝图
/ccc:build         # 创建交付物
/ccc:review        # 质量检查
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
| `/ccc:init` | 使用 4 问框架创建意图制品 |
| `/ccc:design` | 从意图生成蓝图 |
| `/ccc:build` | 创建生产就绪的交付物 |
| `/ccc:review` | 全面质量审查（76+ 检查项）|
| `/ccc:quick` | 一键执行完整工作流 |
| `/ccc:iterate` | 迭代现有蓝图 |
| `/ccc:status` | 显示项目工作流状态 |
| `/ccc:trace` | 生成可追溯性矩阵 |
| `/ccc:validate` | 使用外部工具验证制品 |

查看 [完整命令参考](commands/) 了解详情。

## 质量评估维度

| 维度 | 权重 | 规则数 | 说明 |
|------|------|--------|------|
| 意图匹配 | 10% | 4 | 触发场景、同义词、排除场景 |
| 配置和使用 | 15% | 5 | 前置配置、示例质量、错误处理 |
| 外部依赖 | 15% | 12 | 运行时依赖、外部 API、工具链 |
| 安全风险 | 20% | 5 | 命令注入、敏感数据、权限 |
| 环境兼容性 | 15% | 3 | OS/Shell 兼容性、路径分隔符 |
| LLM 兼容性 | 15% | 3 | 模型特定功能、阻断检查 |
| 扩展性 | 10% | 4 | Token 使用、分批处理、超时 |
| 架构分析 | 额外 | 15 | 工作流/组件/职责设计 |

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
/ccc:test-sandbox

# 审查插件质量
/ccc:review
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
