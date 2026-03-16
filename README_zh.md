# Claude Code Component Creator (CCC)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-3.4.0-blue.svg)](https://github.com/mzdbxqh/claude-code-component-creator)
[![Quality Score](https://img.shields.io/badge/quality-96%2F100-brightgreen.svg)](docs/reviews/)

一个强大的 Claude Code 插件，通过结构化的 Intent/Blueprint/Delivery 工作流创建高质量组件和技能。

[English Documentation](README.md)

## 特性

- **三阶段工作流**: Intent → Blueprint → Delivery 确保设计质量
- **77+ 反模式检查**: 跨 8 个维度的全面质量审查
- **元反思框架**: 4 维度自我评估确保质量
- **双模型验证**: Sonnet 生成，Haiku 验证
- **可追溯矩阵**: 从需求到实现的完整追踪
- **外部状态管理**: 工作流状态存储在 YAML 文件中
- **并行处理**: 大型项目 3.75x-6.8x 加速
- **Token 预算透明**: 完整的成本估算和优化指南
- **检查点恢复**: 从中断处恢复长时间运行的工作流
- **性能基准测试**: 内置性能测试框架
- **插件画像框架**: 自动插件画像，标准化元数据提取

## 快速开始

### 安装

1. 安装 [Claude Code](https://claude.ai/code)
2. 克隆此仓库:
```bash
git clone https://github.com/mzdbxqh/claude-code-component-creator.git
```
3. 在 Claude Code 中加载插件

### 安装详情

#### 前置要求
- **Claude Code**: 版本 0.1.0 或更高
- **操作系统**: macOS、Linux 或 Windows（通过 WSL）
- **Git**: 用于克隆和版本控制
- **Node.js**: （可选）用于一些高级功能

#### 插件目录结构
```
claude-code-component-creator/
├── agents/          # SubAgent 定义
├── skills/          # Skill 定义
├── hooks/           # Hook 配置
├── docs/            # 文档
└── test-fixtures/   # 示例组件
```

#### 验证
安装后，验证插件已加载:
```bash
# 列出所有可用命令
/help

# 你应该能看到 /cmd-* 命令
```

#### 常见安装问题
- **插件未找到**: 确保插件目录在 Claude Code 的插件路径中
- **权限错误**: 检查目录权限（目录 755，文件 644）
- **路径问题**: 使用绝对路径或确保相对路径正确

更多帮助请查看 [故障排除](#故障排除)。

### 创建第一个组件

```bash
# 一个命令完成整个工作流
/cmd-quick

# 或分步执行
/cmd-init          # 创建意图
/cmd-design        # 生成蓝图
/cmd-build         # 创建交付物
/cmd-review        # 质量检查
```

## 核心工作流

```
Intent（构建什么）
  ↓
Blueprint（如何构建）
  ↓
Delivery（实现）
  ↓
Review（质量保证）
```

## 命令



详见 [完整命令参考](skills/)。

## 配置

CCC 可以通过多种方式配置：

### 插件配置

创建 `.claude-plugin/config.json` 自定义插件行为:
```json
{
  "name": "claude-code-component-creator",
  "version": "3.4.0",
  "settings": {
    "default_model": "sonnet",
    "artifacts_dir": ".ccc/artifacts",
    "review_threshold": 80
  }
}
```

### 环境变量

CCC 遵循以下环境变量:
- `CCC_ARTIFACTS_DIR`: 覆盖默认工件目录（默认: `.ccc/artifacts`）
- `CCC_REVIEW_THRESHOLD`: 最低审查通过分数（默认: 80）
- `CCC_DEFAULT_MODEL`: SubAgent 默认模型（默认: `sonnet`）
- `SLASH_COMMAND_TOOL_CHAR_BUDGET`: skill 描述最大字符数（默认: 16000）

### 工作流状态

工作流状态存储在 YAML 文件中:
```
.ccc/artifacts/
├── intent-*.yaml       # Intent 工件
├── blueprint-*.yaml    # Blueprint 工件
└── delivery-*.yaml     # Delivery 工件
```

### Hooks 配置

在 `hooks/config.json` 中配置 hooks:
```json
{
  "hooks": [
    {
      "event": "PreToolUse",
      "matcher": {"tool": "Bash"},
      "type": "command",
      "command": "security-check.sh"
    }
  ]
}
```

详见 [Hooks 文档](docs/hooks.md)。

## 插件画像框架

CCC 引入了自动插件画像系统，通过全面的插件元数据增强审查报告。

### 概述

当你对插件运行 `/cmd-review` 时，CCC 现在会自动:
1. 提取插件元数据（名称、版本、定位、架构）
2. 分析组件结构（skills、agents、hooks）
3. 识别工作流机制和激活模式
4. 评估文档完整性（0-100 分）
5. 生成标准化插件画像（JSON + Markdown）
6. 在审查报告中嵌入"插件概览"章节

### 插件画像输出

```
docs/profile/
├── plugin-profile.json       # 结构化元数据（JSON Schema 验证）
└── plugin-profile.md          # 人类可读报告
```

### 画像内容

插件画像包含:

- **元信息**: 名称、版本、定位、基础框架
- **架构设计**: 组件统计、分类系统、工作流机制
- **使用方式**: 斜杠命令、自动激活 skills
- **核心理念**: 设计原则和理由
- **系统要求**: 平台、依赖、兼容性
- **质量指标**: 文档完整性评分和建议

### 新审查参数

| 参数 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `--skip-profiling` | boolean | false | 跳过插件画像（高级用户） |
| `--profile-only` | boolean | false | 仅生成画像，跳过质量审查 |
| `--profile-output` | path | docs/profile/ | 画像输出目录 |

### 使用示例

```bash
# 标准审查（含画像）
/cmd-review

# 仅画像模式（无质量审查）
/cmd-review --profile-only

# 审查不含画像
/cmd-review --skip-profiling

# 自定义输出目录
/cmd-review --profile-output=custom/path/
```

### 自解释验证

审查报告现在包含自动自解释验证:

- **完整性检查** (40%): 所有必需章节都存在
- **自包含检查** (30%): 无外部引用
- **结构清晰度** (20%): 清晰的标题层次
- **信息准确性** (10%): 跨章节数据一致

报告评分 0-100，并提供改进建议。

### 优势

- **改进报告清晰度**: 报告现在可以独立阅读和理解
- **更好的插件理解**: 深入细节前的全面概览
- **质量透明度**: 客观评分文档完整性
- **标准化元数据**: 所有插件的一致画像

详见 [插件画像文档](agents/profiler/plugin-profiler/SKILL.md)。

## 质量维度

CCC 达到 **96/100** 总体质量评分，跨 8 个维度进行全面检查:

| 维度 | 权重 | 规则数 | 评分 | 描述 |
|------|------|--------|------|------|
| Intent 匹配 | 10% | 4 | 95/100 | 触发场景、同义词、排除项 |
| 配置 | 15% | 5 | 97/100 | 设置要求、示例、错误处理 |
| 依赖 | 15% | 12 | 94/100 | 运行时依赖、外部 API、工具链 |
| 安全 | 20% | 7 | 98/100 | 命令注入防护、审计日志 |
| 环境 | 15% | 3 | 93/100 | OS/shell 兼容性、路径分隔符 |
| LLM 兼容性 | 15% | 3 | 96/100 | Token 预算、模型优化 |
| 可扩展性 | 10% | 4 | 96/100 | 并行处理、批处理、超时 |
| 可测试性 | 额外 | 20 | 95/100 | 测试覆盖率、evals.json 框架 |

## 文档

- [迁移指南](docs/v3-migration-guide.md) - 从 v2.0 升级到 v3.0
- [最佳实践](docs/best-practices/ccc-best-practices.md) - 使用指南
- [用户指南](docs/user-guide/) - 详细命令文档
- [模板](docs/templates/) - Intent/Blueprint/Delivery 模板
- [发布工作流](docs/github-release-workflow.md) - 标准发布流程

## 示例

查看 [test-fixtures/](test-fixtures/) 获取示例组件。

## 开发

```bash
# 运行测试
/cmd-test-sandbox

# 审查插件质量
/cmd-review
```

## 故障排除

### 常见问题

#### 插件未加载

**症状**: `/cmd-*` 命令不可用

**解决方案**:
1. 验证插件目录在 Claude Code 的插件路径中
2. 检查目录结构是否正确
3. 重启 Claude Code
4. 检查 SKILL.md 文件中的语法错误:
   ```bash
   yamllint skills/*/SKILL.md agents/*/SKILL.md
   ```

#### 命令执行失败

**症状**: 命令启动但失败并显示错误

**解决方案**:
1. 检查 SKILL.md frontmatter 中的命令权限
2. 验证所有必需工具都在 `allowed-tools` 或 `tools` 列表中
3. 检查日志获取详细错误消息
4. 如果可用，尝试使用 `--verbose` 标志

#### 审查失败评分低

**症状**: `/cmd-review` 显示许多错误

**解决方案**:
1. 仔细阅读审查报告 - 它显示具体问题
2. 首先关注 ERROR 级别的问题
3. 检查官方文档了解违反的标准
4. 使用 `/cmd-fix` 自动修复某些问题:
   ```bash
   /cmd-fix --report review-report.md
   ```

详见 [TROUBLESHOOTING.md](TROUBLESHOOTING.md) 获取完整故障排除指南。

## 贡献

欢迎贡献！详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

MIT License - 详见 [LICENSE](LICENSE)。

Copyright (c) 2026 showme.cc

## 维护者

- **mzdbxqh** - [GitHub](https://github.com/mzdbxqh/claude-code-component-creator)

## 变更日志

详见 [CHANGELOG.md](CHANGELOG.md) 获取版本历史。

---

**版本**: 3.4.0 | **质量评分**: 96/100 | **许可证**: MIT
